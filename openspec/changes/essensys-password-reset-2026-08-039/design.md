## Context

Voir `proposal.md` — Why pour la motivation et l'incident déclencheur.

État actuel des briques concernées :

- `essensys-user-portal-backend/internal/identity/routes.go` monte `Mount(r, users, cfg)` avec `/auth/register`, `/auth/login`, `/auth/logout`, les callbacks OAuth, puis un groupe protégé par `middleware.UserJWTWithStore`. Aucune route de réinitialisation.
- `internal/data/user_store.go` fournit `GetUserByEmail`, `GetUserByID` et `UpdateUser(userID, firstName, lastName, passwordHash)` — la réécriture d'empreinte est donc déjà possible, mais l'API force à repasser prénom/nom.
- `internal/notify` expose `Configured()`, `Send(to, subject, bodyHTML)`, `Render(text, vars)` et `TemplateVars`. `internal/data/email_template_store.go` expose `Get(slug)`, l'upsert et `LogSend(...)`. La composition modèle + variables + envoi + log est aujourd'hui concentrée dans `internal/admin/transactional.go` (`sendTemplateEmail`, `buildTemplateVars`), donc **côté admin**, inaccessible depuis `identity`.
- `internal/turnstile.Verifier` et `middleware.NewRateLimiter(limit, window)` existent et sont déjà utilisés par `Register` (change `essensys-turnstile-registration-2026-07-036`).
- Le frontend `essensys-support-site/site/src/pages/Login.jsx` appelle `/api/auth/login` en `fetch` direct, `Register.jsx` porte déjà le chargement explicite du widget Turnstile et la logique `resetTurnstile()` réutilisable.
- Le modèle `password_reset` de `migrations/006_email_templates.sql` est `enabled = false` et son corps contient `{{temporary_password}}` — il devra être réécrit autour de `{{reset_url}}`.

Contraintes structurantes :

- Ces pages d'authentification n'existent **que** dans `essensys-support-site` ; `essensys-user-portal-frontend` n'a pas de page de login. La règle de synchronisation des jumeaux UI ne s'applique donc pas ici.
- Le protocole legacy IoT est hors périmètre et ne doit pas être touché.
- Le SMTP de production n'est pas garanti actif : la conception doit rester correcte quand l'envoi est indisponible.

## Goals / Non-Goals

**Goals:**

- Un parcours de récupération complet et autonome, sans intervention humaine dans le cas nominal.
- Aucun secret réutilisable transmis par courriel : un lien à usage unique, pas un mot de passe temporaire.
- Aucune énumération de comptes exploitable via cet endpoint, y compris par analyse temporelle.
- Extraction de la composition de courriels transactionnels hors du paquet `admin`, pour que `identity` puisse l'utiliser sans dépendance croisée.
- Chemin de déblocage manuel pour le support, tracé dans le journal d'audit.

**Non-Goals:**

- Vérification d'adresse email à l'inscription (double opt-in) — problème connexe, justifiant sa propre change.
- Authentification à deux facteurs, questions de sécurité, rotation forcée des mots de passe.
- Révocation des JWT déjà émis lors d'une réinitialisation : les jetons sont sans état et à durée de vie courte ; une liste de révocation serait un chantier distinct.
- Activation des fournisseurs OAuth (`OAUTH_PROVIDERS_ENABLED` reste à `false`).
- Politique de mot de passe renforcée au-delà des 8 caractères déjà appliqués à l'inscription.

## Decisions

### D1 — Lien à usage unique plutôt que mot de passe temporaire

Le modèle `password_reset` existant véhicule `{{temporary_password}}`. Nous le réécrivons autour de `{{reset_url}}`.

Rationale : un mot de passe temporaire envoyé en clair reste valide jusqu'à ce que l'utilisateur le change, survit dans la boîte mail et dans les journaux du relais SMTP, et impose d'écrire une empreinte bcrypt d'un secret que le serveur a connu en clair. Un jeton à usage unique et à durée de vie de 60 minutes limite la fenêtre d'exposition et laisse l'utilisateur choisir un secret que le serveur ne stocke que haché.

Alternative écartée : conserver le mot de passe temporaire pour ne pas toucher au modèle d'email — rejetée pour les raisons ci-dessus, d'autant que le modèle est aujourd'hui désactivé et n'a jamais servi, donc sa réécriture ne casse rien.

### D2 — Jeton opaque en base plutôt que JWT signé

Table `password_reset_tokens` :

```sql
CREATE TABLE password_reset_tokens (
    id           SERIAL PRIMARY KEY,
    user_id      INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash   CHAR(64) NOT NULL UNIQUE,   -- SHA-256 hex du jeton
    expires_at   TIMESTAMPTZ NOT NULL,
    consumed_at  TIMESTAMPTZ,
    invalidated_at TIMESTAMPTZ,
    request_ip   VARCHAR(64),
    consumed_ip  VARCHAR(64),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

Le jeton est 32 octets de `crypto/rand` encodés en `base64.RawURLEncoding` (43 caractères sûrs pour URL). Seul `sha256(token)` est persisté.

Rationale : un JWT signé serait sans état mais **non révocable**, ce qui rend impossibles l'usage unique (spec `password-reset-consume`) et l'invalidation des jetons antérieurs (spec `password-reset-request`). Ces deux exigences imposent un état côté serveur. SHA-256 suffit pour le stockage (contrairement à un mot de passe, un jeton de 256 bits n'est pas attaquable par dictionnaire, donc bcrypt serait un coût inutile sur un chemin appelé à chaud).

Trois états distincts (`consumed_at`, `invalidated_at`, `expires_at`) plutôt qu'un unique booléen : ils permettent de distinguer dans les diagnostics un lien périmé d'un lien déjà utilisé d'un lien écrasé par une demande plus récente.

### D3 — Latence uniforme sur l'endpoint de demande

`POST /api/auth/password/forgot` exécute la même quantité de travail dans les deux branches :

1. Vérification Turnstile et rate limit d'abord, avant toute requête base.
2. `GetUserByEmail` — la requête est exécutée dans les deux cas (index sur `email`, coût constant).
3. Génération du jeton et écriture en base **uniquement** si le compte existe ; sinon, une génération de 32 octets aléatoires jetée à la poubelle absorbe l'écart.
4. L'envoi du courriel est confié à une goroutine détachée avec un `context.Background()` borné par timeout : la latence SMTP (souvent > 500 ms) ne doit pas fuiter dans la réponse.
5. Réponse `202` avec un corps littéral constant, écrit sans branchement.

Rationale : la spec exige un écart de médianes < 50 ms. L'incident Emilien montre précisément qu'une différence de latence est exploitable — sur `/auth/login`, les 78–139 ms du bcrypt nous ont servi à *prouver* que l'email existait. Le même raisonnement s'appliquerait à un attaquant sur cet endpoint.

Alternative écartée : file d'attente persistante pour l'envoi — surdimensionné pour un volume de quelques réinitialisations par mois. La goroutine détachée perd les envois en cas de redémarrage du service, mitigé par le fait que le jeton reste valide et qu'une nouvelle demande est possible.

### D4 — Extraction d'un paquet `internal/mailtpl`

`admin.sendTemplateEmail` et `admin.buildTemplateVars` sont déplacés dans un nouveau paquet `internal/mailtpl`, exposant :

```go
type Sender struct { templates *data.EmailTemplateStore; audit AuditSink; inventory Inventory }
func (s *Sender) Send(slug string, user *domain.User, extra notify.TemplateVars, actor Actor) Result
```

`internal/admin` conserve des méthodes de façade qui délèguent, afin de ne pas réécrire ses appelants (`handlers.go:241`, `handlers.go:308`, `email_handlers.go`).

Rationale : `identity` ne peut pas importer `admin` (dépendance inversée : `admin` traite des opérations privilégiées). Dupliquer la composition dans `identity` créerait deux chemins divergents pour le rendu et la journalisation d'envoi. Le paramètre `extra` permet d'injecter `reset_url` et `expires_in` sans polluer `buildTemplateVars` avec des variables spécifiques à la réinitialisation.

Alternative écartée : laisser `identity` appeler directement `notify.Send` — perdrait le respect du drapeau `enabled` du modèle et l'écriture dans `email_send_log`, deux comportements exigés par la spec `password-reset-notification`.

### D5 — Limitation à deux niveaux : IP et compte

- Par IP : `middleware.NewRateLimiter(5, time.Hour)` sur `/auth/password/forgot`, `(10, time.Hour)` sur `/auth/password/reset`, en réutilisant le motif de `registerRateLimitMiddleware`.
- Par compte : requête de comptage sur `password_reset_tokens` (3 jetons émis par heure maximum), appliquée **après** la réponse uniforme pour ne pas devenir un oracle d'existence.

Rationale : la limite par IP seule laisse un attaquant distribué inonder la boîte d'une victime ; la limite par compte seule laisse un attaquant depuis une IP unique sonder de nombreuses adresses. Les deux sont nécessaires. Le point délicat est que la limite par compte ne doit pas changer le corps ni le code de la réponse — d'où l'exigence explicite dans la spec.

### D6 — Nouvelle méthode `UpdatePasswordHash` sur `UserStore`

`UpdateUser(userID, firstName, lastName, passwordHash)` force à relire et réécrire prénom et nom pour changer une empreinte, avec un risque d'écrasement concurrent. Nous ajoutons :

```go
func (s *UserStore) UpdatePasswordHash(userID int, passwordHash string) error
```

La réinitialisation s'exécute dans une transaction unique : consommation du jeton (`UPDATE ... WHERE token_hash = $1 AND consumed_at IS NULL AND invalidated_at IS NULL AND expires_at > NOW()`), vérification que exactement une ligne est affectée, réécriture de l'empreinte, invalidation des jetons frères. Le `UPDATE` conditionnel avec contrôle du nombre de lignes affectées est ce qui garantit l'usage unique face à deux requêtes concurrentes.

### D7 — Aucune connexion automatique après réinitialisation

L'utilisateur est redirigé vers le formulaire de connexion et doit saisir son nouveau mot de passe.

Rationale : émettre un JWT à la sortie du parcours ferait du lien email un vecteur de connexion directe — quiconque intercepte le lien obtiendrait une session. Une saisie de plus est un coût minime et confirme que l'utilisateur a bien mémorisé le mot de passe qu'il vient de choisir.

### D8 — Le champ de confirmation à l'inscription reste purement côté client

`Register.jsx` compare les deux champs avant d'émettre la requête ; le corps envoyé à `/auth/register` reste inchangé.

Rationale : la confirmation traite une erreur de saisie, pas une menace. L'envoyer au serveur élargirait le contrat d'API sans bénéfice de sécurité, puisqu'un client malveillant peut de toute façon envoyer ce qu'il veut. C'est la cause racine de l'incident et le correctif le moins cher de la change.

## Risks / Trade-offs

- **SMTP inactif en production** → Le parcours en libre-service est inopérant si `notify.Configured()` est faux. Mitigation : l'action admin (`admin-password-reset-assist`) remonte explicitement `email_sent: false` avec le motif, et la tâche de vérification de l'envoi réel sur `mon.essensys.fr` est un jalon bloquant du plan avant annonce de la fonctionnalité aux utilisateurs.
- **Modèle `password_reset` livré désactivé** → Une bascule oubliée de `enabled` rend la fonctionnalité silencieusement inerte. Mitigation : la migration `013` réécrit le corps du modèle **et** passe `enabled = true`, et un test d'intégration vérifie qu'un jeton émis produit une ligne `sent` dans `email_send_log`.
- **Perte d'un envoi au redémarrage du service** (goroutine détachée, cf. D3) → L'utilisateur ne reçoit rien. Mitigation : le jeton reste valide, une nouvelle demande est possible immédiatement, et la limite par compte de 3/heure laisse de la marge.
- **Réécriture de `admin.sendTemplateEmail` (D4)** → Régression possible sur les envois `user_welcome`, `device_allocation` et `role_updated`, qui sont les seuls chemins d'envoi aujourd'hui utilisés. Mitigation : la façade `admin` conserve des signatures identiques, et les tests existants du paquet `admin` doivent passer sans modification avant d'ajouter le chemin de réinitialisation.
- **Lien de réinitialisation pré-cliqué par un antivirus ou un scanner de liens de messagerie** → Un jeton à usage unique peut être consommé avant l'utilisateur. Mitigation : la pré-validation (`GET .../validate`) est explicitement sans effet de bord et seule la requête `POST` consomme le jeton ; les scanners n'émettent pas de `POST`.
- **`FRONTEND_URL` mal configurée** → Le lien envoyé pointe vers un hôte erroné. Mitigation : repli sur `https://mon.essensys.fr`, et une tâche de vérification de la valeur déployée dans `essensys-ansible`.
- **Lignes de jetons accumulées** → Croissance lente d'une table sans intérêt historique. Mitigation : purge des lignes de plus de 30 jours, exécutée paresseusement à chaque émission plutôt que via une tâche planifiée dédiée.

## Migration Plan

1. **Base** : appliquer `013_password_reset_tokens.sql` — création de la table, puis `UPDATE email_templates` du modèle `password_reset` (corps autour de `{{reset_url}}`, `enabled = true`, `auto_send` non pertinent pour ce slug). Migration purement additive : aucun risque sur les données existantes.
2. **Backend** : déployer `essensys-cloud-backend` (service systemd sur `mon.essensys.fr`). Les nouvelles routes sont inertes tant que le frontend ne les appelle pas.
3. **Vérification hors utilisateur** : depuis l'admin, déclencher une réinitialisation sur un compte de test, vérifier la ligne `sent` dans `email_send_log` et la réception effective du courriel.
4. **Frontend** : construire et déployer `essensys-support-site` avec les nouvelles routes et le lien sur `Login.jsx`.
5. **Résolution de l'incident** : déclencher la réinitialisation pour `emilienbieber67260@gmail.com` (`users.id=12`) et confirmer une connexion réussie dans les journaux.
6. **Rollback** : retirer le lien de `Login.jsx` et redéployer le frontend suffit à fermer le parcours en libre-service ; les routes backend restent sans effet et la table peut demeurer en place. Aucun retour arrière de schéma nécessaire.

## Open Questions

- Faut-il notifier l'utilisateur par un second courriel « votre mot de passe a été modifié » après une réinitialisation réussie ? Utile pour détecter un détournement de compte, mais suppose un nouveau slug de modèle. Décidable après mise en service sans toucher aux specs ni au découpage des tâches.
- La purge des jetons de plus de 30 jours doit-elle migrer vers une tâche planifiée si le volume croît ? Sans objet au volume actuel.
