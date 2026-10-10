## Context

Voir proposal.md (section Why). Ce qui existe aujourd'hui et contraint la conception :

- **Backend** (`essensys-user-portal-backend`, Go, chi v5, sqlx/lib/pq) :
  - les routes sont montées sous `/api` par des `Mount(r, …)` par domaine ;
  - les routes utilisateur passent par `middleware.UserJWTWithStore(users)` (`internal/middleware/user_status.go`), qui recharge l'utilisateur et renvoie 401 (inconnu), 403 (compte interdit) ou 409 `password_change_required` ;
  - le JWT (HS256) ne porte que l'email (`sub`) et le rôle ; l'id s'obtient avec `users.GetUserByEmail` ;
  - les migrations `migrations/NNN_*.sql` sont rejouées à chaque démarrage et doivent être idempotentes (la dernière est `014_temporary_password.sql`) ;
  - la configuration passe par `internal/config` avec `Validate()` en fail-closed ;
  - les tests utilisent `go test`, `httptest` et `go-sqlmock`, avec des fakes écrits à la main ;
  - le seul client HTTP sortant testable sur ce modèle est `internal/turnstile` (URL surchargeable).
- **Site** (`essensys-support-site/site`, React, Vite) :
  - le jeton `adminToken` est lu dans `localStorage`/`sessionStorage` ;
  - les appels sont des `fetch('/api/…')` directs avec `Authorization: Bearer` ;
  - `passwordChangeGuard.js` intercepte les 409 ;
  - les tests Playwright couvrent les projets `desktop`, `iphone` et `ipad`, avec l'API simulée par `page.route`.
- **Déploiement** (`essensys-ansible`) :
  - l'environnement est rendu par `roles/cloud_backend/templates/cloud-backend.env.j2` ;
  - les secrets sont dans `secrets/cloud/essensys.sops.yaml`, chargés par `roles/sops_load` ;
  - la clé privée Apple OAuth sert de précédent : un fichier 0600 écrit depuis SOPS, et l'environnement pointe vers son chemin.
- **Manifests** : les schémas `features/schema/feature.schema.json` du backend et du site sont des copies anciennes. Ils refusent le bloc `github` et la clé `tests.junit`. La référence est `essensys-feature-lifecycle/features/schema/feature.schema.json`.

## Goals / Non-Goals

**Goals**
- Un utilisateur connecté signale un problème en moins de 2 minutes, sans compte GitHub.
- Aucune donnée personnelle dans un dépôt public. Le contenu sensible est refusé à la source.
- La fonction se déploie avant même que la GitHub App existe : les signalements restent alors « en attente d'envoi ».

**Non-Goals**
- Pas de pièces jointes (captures, logs) dans cette version, pour réduire le risque de données personnelles.
- Pas de fil de discussion entre l'utilisateur et le mainteneur sur le site. Le mainteneur répond sur GitHub ; l'utilisateur ne voit que l'état.
- Pas de notification par email du changement d'état (évolution possible plus tard).
- Pas de modification des routes gateway, du firmware ni de la table d'échange.

## Decisions

### Backend

**D1. Nouveau package `internal/support`**, monté dans le bloc `ConsolidatedMode` du routeur, derrière `UserJWTWithStore`.
- Routes : `POST /api/support/reports` (création) et `GET /api/support/reports` (liste des signalements du compte).
- Le contrôle 401/403/409 est réutilisé tel quel.
- *Alternative écartée* : le mettre dans `identity`. Ce package est déjà gros, et le support a sa propre dépendance externe (GitHub).

**D2. Table `support_reports`** (migration `015_support_reports.sql`, `CREATE TABLE IF NOT EXISTS`). Colonnes :
- `id SERIAL`, `public_ref` (ex. `R-7K3F9Q`, unique), `user_id INT REFERENCES users(id) ON DELETE CASCADE` ;
- `kind` (`bug` | `incident`), `title`, `payload JSONB` (champs du formulaire) ;
- `status` (`pending` | `open` | `resolved` | `closed`) ;
- `repo`, `issue_number`, `issue_url`, `attempts`, `last_error`, `created_at`, `updated_at`, `synced_at` ;
- index sur `(user_id, created_at DESC)` et sur `status`.

Minimisation : une fois l'issue créée, `payload` est vidé (`'{}'`). Le contenu vit alors seulement sur GitHub. `last_error` ne contient jamais de contenu utilisateur, seulement un code HTTP et un message GitHub tronqué.

**D3. Limite par compte en base, pas en mémoire.**
- Contrôle : `SELECT count(*) FROM support_reports WHERE user_id=$1 AND created_at > now() - interval '24 hours'`. À 5 ou plus, réponse 429 avec `retry_after`, calculé à partir du plus ancien des 5.
- Cette limite survit aux redémarrages et compte aussi les signalements `pending`.
- *Alternative écartée* : le `RateLimiter` en mémoire existant, perdu à chaque redéploiement.

**D4. Détection des contenus sensibles** (`internal/support/sensitive.go`). Ce sont des expressions régulières sur le titre et chaque texte libre, après normalisation (minuscules, accents retirés). Catégories :
- `password` : « mot de passe », « mdp », « password », « pwd », « passcode », « code d'accès » suivis de `:` ou `=` et d'un mot ;
- `secret` : JWT `eyJ…\.…\.…`, `-----BEGIN … PRIVATE KEY-----`, `ghp_`, `github_pat_`, `sk-`, `AKIA…`, `NRAK-`, et toute chaîne hexadécimale ou base64 de 32 caractères ou plus ;
- `postal_address` : numéro, éventuel « bis/ter », type de voie (rue, avenue, bd, boulevard, chemin, allée, impasse, place, route, quai, cours, lieu-dit) et nom ; ou code postal à 5 chiffres suivi d'un mot ;
- `email` : adresse email.

Le refus répond 422 `{error:"sensitive_content", field, category}`. Le texte détecté n'est jamais renvoyé ni journalisé : le log ne mentionne que `audit action=SUPPORT_REPORT_REJECTED category=… field=…`. Le site affiche aussi l'avertissement, mais c'est le serveur qui fait foi.

*Faux positifs acceptés* : « 25 s » ou un numéro de version ne déclenchent pas les règles (tests dédiés). Une chaîne hexadécimale longue dans un log collé est refusée volontairement.

**D5. Référence pseudonyme `U-`** : `"U-" + base32(HMAC-SHA256(SUPPORT_PSEUDONYM_KEY, user_id))[:8]`.
- Elle est stable pour un compte et ne peut pas être reconstituée sans la clé.
- `SUPPORT_PSEUDONYM_KEY` passe par `checkSecret` (16 caractères minimum).
- *Alternative écartée* : l'id brut, énumérable et corrélable.

**D6. Contenu de l'issue.**
- Titre : `[Bug] <titre>` ou `[Incident] <titre>`.
- Corps : un tableau des champs fermés (application, version, mode), puis des sections `### Ce qui se passe`, `### Ce qui était attendu`, `### Étapes`, puis le pied « Signalé depuis www.essensys.fr par un utilisateur Essensys (U-xxxx, réf. R-xxxx) ».
- Le texte utilisateur est neutralisé :
  - `@` devient `@` + U+200B, pour qu'aucune mention ne notifie personne ;
  - `#123` reste tel quel ;
  - les blocs HTML sont échappés ;
  - chaque texte est limité à 4 000 caractères.
- Labels `bug` ou `incident`, plus `via-portal`. Type d'issue `Bug` (paramètre REST `type`) pour les bugs, `Support` pour les incidents (s'il n'existe pas, on omet le type).

**D7. Client GitHub App** (`internal/support/github.go`).
- Le JWT d'App est signé en RS256 avec `golang-jwt/jwt/v4`, déjà en dépendance (iat −60 s, exp +9 min). Il est échangé contre un jeton d'installation (`POST /app/installations/{id}/access_tokens`), mis en cache jusqu'à 5 minutes avant son expiration.
- Créations :
  - issue : `POST /repos/{owner}/{repo}/issues` ;
  - ajout au Project : mutation GraphQL `addProjectV2ItemById` (projet `SUPPORT_PROJECT_ID`).
- La base URL est surchargeable (`GITHUB_API_URL`), sur le modèle de `turnstile.Client`, pour les tests httptest. Timeout de 10 s.
- *Alternative écartée* : `go-github` et `ghinstallation`. Ces deux dépendances couvriraient trois appels seulement.
- *Alternative écartée* : un jeton personnel (PAT), lié à une personne et trop large.

**D8. Envoi asynchrone et resynchronisation** : un worker `support.Syncer`, démarré dans `main.go`, tourne toutes les 5 minutes, avec un verrou Postgres `pg_try_advisory_lock` pour éviter les doublons si deux instances tournent.
- Les `pending` (avec moins de 10 tentatives, et un recul exponentiel) sont créés sur GitHub.
- Les `open` dont `synced_at` date de plus de 10 minutes sont relus avec `GET /repos/{o}/{r}/issues/{n}`. `closed` et `state_reason=completed` donnent `resolved` ; une autre raison donne `closed`.
- Le `POST` tente une création immédiate. En cas d'échec, il répond quand même 201 avec `status: "pending"`.
- Le délai d'au plus 15 minutes de la spec est garanti par la période de 5 minutes et le seuil de 10 minutes.

**D9. Configuration.**
- Variables : `GITHUB_APP_ID`, `GITHUB_APP_INSTALLATION_ID`, `GITHUB_APP_PRIVATE_KEY_FILE`, `SUPPORT_PSEUDONYM_KEY`, `SUPPORT_PUBLIC_REPO` (défaut `essensys-hub/essensys-support-site`), `SUPPORT_PRIVATE_REPO` (défaut `essensys-hub/essensys-support`), `SUPPORT_PROJECT_ID`, `GITHUB_API_URL` (défaut `https://api.github.com`).
- Si l'App n'est pas configurée, la fonction reste active et les signalements restent `pending`. Un avertissement au démarrage le signale.
- `SUPPORT_PSEUDONYM_KEY` est obligatoire en production consolidée (fail-closed), car la référence `U-` doit être stable dès le premier signalement.

### Site

**D10. Page `/signaler?type=bug|incident`** dans `Layout`.
- Sans jeton : invitation à se connecter, avec retour sur cette page.
- Avec jeton : le formulaire.
  - Les champs reprennent l'essentiel des modèles GitHub existants, simplifié pour un utilisateur final. Pour un bug : application, version, mode, titre, ce qui se passe, ce qui était attendu, étapes. Pour un incident : depuis quand, impact, titre, ce qui se passe, ce qui a déjà été essayé.
  - Le bandeau d'avertissement (texte de la spec) est placé au-dessus du premier champ libre, avec `role="note"`.
  - Les compteurs de caractères sont visibles.
  - Les erreurs 400 et 422 s'affichent sous le champ concerné, sans perdre la saisie. Le 429 est affiché avec l'heure de nouvelle tentative.
- Les cartes de l'accueil (`Home.jsx`) pointent vers `/signaler?type=…` quand l'utilisateur est connecté.

**D11. « Mes signalements »** est une section de `Profile.jsx`, alimentée par `GET /api/support/reports`.
- Elle affiche référence, type, titre, date et état (pastille).
- Un lien GitHub n'apparaît que pour `kind=bug`. L'API ne renvoie pas `issue_url` pour un incident, pour ne jamais exposer le dépôt privé.

### Infra (Ansible)

**D12. Secrets.**
- Dans le fichier SOPS cloud : `vault_github_app_id`, `vault_github_app_installation_id`, `vault_github_app_private_key_content` et `vault_support_pseudonym_key`.
- La clé privée est écrite dans `{{ cloud_backend_install_dir }}/secrets/github-app.pem` (dossier 0700, fichier 0600, `no_log`), sur le modèle de `apple_oauth_key.yml`.
- Le template d'environnement reçoit les nouvelles variables.
- `vault_support_pseudonym_key` est ajouté à `sops_required_cloud_keys`. Les clés GitHub App ne le sont pas, car la fonction marche sans elles (D9).

### Tests et non-régression

**D13.**
- **Go** : tests unitaires `httptest` + `sqlmock`, et un faux serveur GitHub (`httptest.Server`). Les tests de non-régression s'appellent `TestNR_backend_<n>_…`, précédés du commentaire `// NR: NR-backend-<n> essensys-hub/essensys-feature-lifecycle#15`. La CI produit un JUnit avec `go-junit-report`, consolidé par `nonreg_report.py`.
- **Playwright** : `e2e/support-reports.spec.js`, matrice desktop, iPhone et iPad, API simulée par `page.route` (aucun backend ni armoire réels : c'est le mode `no-armoire`). Les titres de test non-régression portent `NR-site-<n>`.
- **Manifests** : les schémas du backend et du site sont alignés sur la référence (bloc `github`, `tests.junit`).

## Risks / Trade-offs

- [Faux positifs du filtre sensible, qui frustrent l'utilisateur] → Message précis par catégorie, saisie conservée, jeu de tests de textes techniques légitimes. On ajuste les règles en exploitation.
- [Faux négatifs : une adresse ou un mot de passe passent quand même] → L'avertissement, le dépôt privé pour les incidents et la relecture par un mainteneur, qui peut masquer un commentaire ou supprimer l'issue (action humaine).
- [Spam ou abus par un compte] → 5 signalements par 24 h par compte, réservé aux comptes valides. Les comptes interdits sont déjà rejetés par `UserJWTWithStore`.
- [Clé privée de la GitHub App compromise] → Droits minimaux (Issues sur deux dépôts, Projects sur l'org), fichier 0600, jamais dans les logs. Rotation possible depuis les réglages de l'App.
- [GitHub indisponible] → États `pending` et resynchronisation (D8).
- [Le worker tourne sur deux instances] → Verrou consultatif Postgres.
- [Filtrage côté site seulement pour les modèles GitHub] → Hors périmètre, assumé : les contributeurs avec un compte GitHub gardent l'accès direct.

## Migration Plan

1. Action humaine, admin de l'org :
   - créer le dépôt privé `essensys-support` et les labels `incident` et `via-portal` ;
   - créer la GitHub App « Essensys Support » : permissions Issues lecture/écriture sur `essensys-support-site` et `essensys-support`, Projects lecture/écriture au niveau de l'org, aucun webhook ;
   - l'installer, puis transmettre l'App ID, l'Installation ID et la clé `.pem`, à ranger dans SOPS.
2. Ansible : ajouter les secrets SOPS et le template, puis déployer le backend. La migration 015 s'applique au démarrage.
3. Déployer le site.
4. Vérifier en production avec un compte de test : un bug apparaît dans le dépôt public, anonymisé ; un incident apparaît dans le dépôt privé.
5. **Retour arrière** :
   - redéployer le tag précédent du site, ce qui ramène les cartes vers GitHub ;
   - côté backend, la table reste mais n'est plus utilisée, puisque la migration est additive ;
   - suspendre l'App si nécessaire.

## Open Questions

- Le nom exact de la GitHub App et son logo (en attente du choix de logo, voir le dossier INPI).
- Le texte de la page « confidentialité » à compléter pour mentionner les signalements. Cela relève de la documentation et ne change pas les specs.
