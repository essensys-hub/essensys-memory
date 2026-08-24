## 1. Socle base de données et stockage des jetons

- [x] 1.1 Créer `essensys-user-portal-backend/migrations/013_password_reset_tokens.sql` avec la table décrite dans `design.md` (D2) et les index sur `token_hash` et `user_id` ; vérifier en appliquant la migration sur une base locale et en contrôlant `\d password_reset_tokens`
- [x] 1.2 Dans la même migration, réécrire le modèle `password_reset` de `email_templates` autour de `{{reset_url}}` et `{{expires_in}}`, retirer `{{temporary_password}}`, et passer `enabled = true` ; vérifier par `SELECT slug, enabled, body_html FROM email_templates WHERE slug='password_reset'`
- [x] 1.3 Créer `internal/data/password_reset_store.go` avec `EnsureTableExists`, `Create(userID, tokenHash, expiresAt, requestIP)`, `ConsumeByHash(tokenHash, ip)` en `UPDATE` conditionnel retournant le `user_id`, `GetByHash`, `InvalidateForUser(userID)` et `PurgeOlderThan(d)` ; vérifier par tests unitaires du paquet `data`
- [x] 1.4 Écrire un test de concurrence sur `ConsumeByHash` (deux goroutines, même jeton) et vérifier qu'exactement une consommation réussit
- [x] 1.5 Ajouter `UserStore.UpdatePasswordHash(userID, hash)` (D6) et vérifier par un test que prénom et nom ne sont pas modifiés

## 2. Extraction du service de courriel transactionnel

- [x] 2.1 Créer `internal/mailtpl` (`Sender.Send`, `BaseUserVars`, `PortalURL`, `SupportEmail`) reprenant le rendu, l'envoi et le journal `email_send_log` depuis `internal/admin/transactional.go` ; `go build ./...` et `go vet ./...` passent. **Écart assumé** : `buildTemplateVars` et `enrichDeviceVars` restent dans `internal/admin`, car elles dépendent de `AdminInventoryStore` que le parcours public n'a pas ; seule la part commune (`BaseUserVars`) est partagée. Le journal d'audit reste chez l'appelant : seul `admin` sait quel administrateur agit
- [x] 2.2 `admin.sendTemplateEmailWithVars` délègue à `mailtpl.Sender.Send` ; `go test ./internal/admin/...` passe **sans modification des tests existants**
- [ ] 2.3 Ajouter à `mailtpl` un test vérifiant qu'un modèle désactivé n'envoie rien mais produit une ligne `failed` dans le journal d'envoi

## 3. Endpoint de demande de réinitialisation

- [x] 3.1 Handler `ForgotPassword` dans `internal/identity/forgot_password.go` (fichier dédié plutôt que `password_reset.go`, déjà occupé par validation et consommation) : validation de l'email, vérification Turnstile, résolution du compte, émission du jeton, réponse `202` à corps constant ; tests couvrant compte existant, compte inconnu, compte interdit et email invalide. L'email n'est **pas** normalisé en minuscules, `UserStore.GetUserByEmail` faisant une correspondance exacte : replier la casse ici échouerait à trouver des comptes qui se connectent normalement
- [x] 3.2 Génération déjà fournie par `pwreset.Generate` (32 octets `crypto/rand`, `base64.RawURLEncoding`, `sha256` seul persisté) ; couvert par `internal/pwreset/token_test.go`
- [x] 3.3 `PasswordResetStore.Issue` invalide les jetons antérieurs ; vérifié en production : l'émission du jeton `id=2` a basculé `id=1` en `invalidated`
- [x] 3.4 Envoi asynchrone via `Handlers.dispatch` (goroutine par défaut, remplaçable en test) ; les tests observent la planification sans dépendre d'une goroutine qui leur survivrait. **Écart** : pas de timeout explicite sur la goroutine, l'échéance restant celle du client SMTP
- [ ] 3.5 Travail factice implémenté (`pwreset.Burn` dans les branches inconnue, interdite et bridée) ; le test de latence sur 20 appels reste à écrire
- [x] 3.6 Route `POST /auth/password/forgot` montée avec `RateLimiter(5, time.Hour)` par IP — plus stricte que la consommation, une demande envoyant un courriel à un tiers. **Écart** : le déclenchement du `429` n'est pas couvert par un test
- [x] 3.7 Limite de 3 jetons par heure et par compte, sans modifier corps ni code de réponse ; couvert par `TestForgotThrottlesPerAccount`
- [x] 3.8 `PASSWORD_RESET_REQUESTED` journalisé sans jeton ni empreinte, vérifié en production. **Écart** : `PASSWORD_RESET_BLOCKED_RATELIMIT` n'est écrit que dans le journal du service par le middleware, pas dans `audit_logs`, celui-ci n'ayant pas accès au magasin d'audit

## 4. Endpoints de validation et de consommation

- [x] 4.1 Implémenter `GET /auth/password/reset/validate` renvoyant `valid` et l'email masqué, avec les codes `200` / `410 expired` / `410 used` / `400 invalid` ; vérifier par tests de handler pour chaque état
- [x] 4.2 Vérifier par test que la pré-validation répétée d'un jeton valide ne le consomme pas et ne compte pas comme tentative
- [x] 4.3 Implémenter `POST /auth/password/reset` en transaction unique (consommation conditionnelle, contrôle du nombre de lignes, réécriture bcrypt, invalidation des jetons frères) ; vérifier par test que la connexion avec le nouveau mot de passe réussit ensuite
- [x] 4.4 Implémenter les règles de robustesse (minimum 8 caractères, refus d'un mot de passe identique à l'actuel) **sans consommer le jeton** en cas de rejet ; vérifier par test que le même lien reste utilisable après un rejet
- [x] 4.5 Traiter le cas du compte interdit entre l'émission et la consommation (`403 account_forbidden`, jeton invalidé, mot de passe inchangé) et vérifier par test
- [x] 4.6 Vérifier par test que la seconde soumission du même jeton renvoie `400 invalid_token` et que le mot de passe issu de la première consommation reste en vigueur
- [x] 4.7 Monter les deux routes avec `RateLimiter(10, time.Hour)` sur la consommation, journaliser `PASSWORD_RESET_COMPLETED` et `PASSWORD_RESET_TOKEN_INVALID` ; vérifier par test d'audit
- [x] 4.8 Envoi branché sur `mailtpl` avec `reset_url` et `expires_in` ; `{{temporary_password}}` épinglé vide, couvert par `TestResetVarsCarryTheLinkAndSuppressTheOldMarker`. **Correction de l'énoncé** : le lien ne doit pas être construit depuis l'URL publique du portail. `FRONTEND_URL` vaut `https://mon.essensys.fr/` en production, qui sert le portail et n'a pas de route `/reset-password` — le lien répondait `200` par le repli SPA puis n'affichait rien. Le lien lit désormais `PASSWORD_RESET_BASE_URL` (`https://www.essensys.fr`) et ignore `FRONTEND_URL` ; régression épinglée par `TestResetLinkIgnoresPortalFrontendURL`
- [x] 4.9 Ajouter la purge paresseuse des jetons de plus de 30 jours à l'émission et vérifier par test que les lignes anciennes disparaissent

## 5. Action administrateur d'assistance

- [x] 5.1 Implémenter `POST /api/admin/users/{id}/password-reset` dans `internal/admin`, réservé au rôle administrateur, réutilisant l'émission de jeton du paquet `identity` ou un service partagé ; vérifier par tests couvrant `200`, `401`, `403`, `404` et `409 account_forbidden`
- [x] 5.2 Vérifier par test que la réponse ne contient ni jeton, ni empreinte, ni lien exploitable, et qu'elle porte `email_sent` avec le motif en cas d'échec
- [x] 5.3 Journaliser `PASSWORD_RESET_REQUESTED_BY_ADMIN` avec l'administrateur appelant et le compte visé ; vérifier par test d'audit
- [x] 5.4 Ajouter l'action « Envoyer un lien de réinitialisation » avec confirmation dans `essensys-support-site/site/src/pages/UserManager.jsx`, désactivée pour les comptes interdits ; vérifier manuellement sur la console d'administration
- [x] 5.5 Exécuter `go test ./...` dans `essensys-user-portal-backend` et vérifier que la suite complète passe

## 6. Parcours frontend de récupération

- [x] 6.1 Widget Turnstile extrait vers `site/src/hooks/useTurnstile.js`, utilisé par `Register.jsx` et `ForgotPassword.jsx` ; le marqueur `data-essensys-turnstile` garantit un seul script, un double chargement laissant `window.turnstile` à moitié initialisé sans rendu de widget. Vérifié sur un build local portant la clé de test Cloudflare `1x00000000000000000000AA` : widget rendu et jeton produit sur les deux pages
- [x] 6.2 `site/src/pages/ForgotPassword.jsx` créé (saisie email pré-remplie, Turnstile, confirmation neutre, `429`, retour vers la connexion) ; états vérifiés localement puis en production
- [x] 6.3 Créer `site/src/pages/ResetPassword.jsx` avec pré-validation du jeton avant affichage des champs, double saisie, indicateur de longueur, bascule d'affichage en clair, succès puis redirection vers la connexion sous 3 secondes sans connexion automatique ; vérifier manuellement chaque état
- [x] 6.4 Déclarer les routes `/forgot-password` et `/reset-password` dans `site/src/App.jsx` hors du `Layout`, comme `/login` ; vérifier que les URL directes se chargent
- [x] 6.5 Lien « Mot de passe oublié ? » ajouté sous le champ mot de passe de `Login.jsx`, sur la même ligne que « Se souvenir de moi », transmettant l'email saisi en paramètre d'URL ; pré-remplissage vérifié localement et en production
- [x] 6.6 Renvoi vers la récupération sous le message d'échec, affiché uniquement sur `401` : une panne réseau ou un compte interdit ne se règle pas par un nouveau mot de passe. Le message ne distingue pas l'email du mot de passe
- [x] 6.7 ~~Ajouter~~ le champ « Confirmer le mot de passe » à `Register.jsx` : **déjà présent** depuis le commit `6ca7e5f` (2026-01-17), avec comparaison côté client bloquant la soumission et corps de requête inchangé, conforme à D8 ; couvert désormais par la spec `auth-recovery-ui` comme garde de non-régression
- [x] 6.8 Étendre `site/src/pages/Auth.css` pour le lien de récupération, l'indicateur de robustesse et les états de message ; vérifier l'absence de défilement horizontal sur desktop, iPhone et iPad
- [x] 6.9 Exécuter `npm run lint` et `npm run build` dans `essensys-support-site/site` et vérifier l'absence d'erreur

## 7. Tests de bout en bout et matrice UX

- [ ] 7.1 Ajouter un test Playwright du parcours complet en desktop, iPhone et iPad : lien depuis la connexion, demande, page de réinitialisation avec jeton injecté, connexion réussie ; vérifier que les trois profils passent
- [ ] 7.2 Ajouter un test Playwright des liens invalides (absent, expiré, déjà consommé) et vérifier que les champs de mot de passe ne s'affichent pas
- [ ] 7.3 Ajouter un test Playwright de la divergence des mots de passe à l'inscription et à la réinitialisation
- [ ] 7.4 Vérifier par test d'intégration backend qu'une demande produit une ligne `sent` dans `email_send_log` pour le slug `password_reset` — constaté manuellement en production (cf. 8.4), reste à automatiser

## 8. Déploiement et clôture de l'incident

- [x] 8.1 Vérifier dans `essensys-ansible` que la configuration de l'URL publique du portail et les variables SMTP sont bien renseignées ; vérifier que le lien produit pointe sur le bon hôte — `FRONTEND_URL=https://www.essensys.fr/` et SMTP Infomaniak (hôte, port 465, utilisateur, mot de passe, expéditeur) présents dans `/opt/essensys/cloud-backend/.env`. **Correction de l'hypothèse initiale** : la page `/reset-password` est servie par `www.essensys.fr` (build `essensys-support-site`), pas par `mon.essensys.fr` qui sert le portail — le repli de `pwreset.PortalBaseURL()` visait le mauvais hôte et a été corrigé (`36ef04a`)
- [x] 8.2 Appliquer la migration `013` sur `essensys_db` en production et vérifier la présence de la table et l'activation du modèle — table `password_reset_tokens` présente, modèle `password_reset` à `enabled=true` avec `{{reset_url}}` et sans `temporary_password`
- [x] 8.3 Déployer `essensys-cloud-backend` et vérifier que les nouvelles routes répondent, le lien frontend n'étant pas encore publié — `deploy-portal-stack.yml --tags cloud_backend`, commit `36ef04a`, service actif. `validate` et `reset` renvoient `400 invalid_token` sur jeton bidon ; `POST /api/admin/users/{id}/password-reset` renvoie `401` sans JWT admin (route montée et gardée)
- [x] 8.4 Jalon atteint par le **parcours libre-service** plutôt que par l'action admin, qui exige un JWT `admin_global` indisponible depuis la ligne de commande : `email_send_log` porte deux lignes `sent` pour le slug `password_reset` vers `emilienbieber67260@gmail.com` (18:38 et 18:44 UTC le 2026-08-24), sans échec. L'action admin reste couverte par ses tests unitaires mais non exercée en production
- [x] 8.5 Frontend déployé (`support-site.yml --tags frontend -e support_site_version=b96409f`, branche `feat/essensys-support-nav-responsive-2026-06-032`) ; parcours vérifié en production : lien présent sur `/login`, `/forgot-password` rend son captcha réel et renvoie la confirmation neutre, `/reset-password` sans jeton propose « Demander un nouveau lien »
- [ ] 8.6 Réinitialisation déclenchée deux fois pour `emilienbieber67260@gmail.com` (`users.id=12`) : jeton `id=2` valide une heure, courriel `sent`. **Reste à vérifier** la connexion effective, qui dépend de l'utilisation du lien par le titulaire du compte. Le premier courriel (18:38) portait un lien vers le mauvais hôte et son jeton a été invalidé ; seul le second est exploitable
- [ ] 8.7 Documenter le parcours utilisateur et le runbook support dans `essensys-doc`, en incluant le diagnostic par `email_send_log` et par les actions d'audit ; vérifier la construction du site de documentation
- [x] 8.8 Mettre à jour la mémoire OKF (`essensys-memory`) : pages portail et journal, puis exécuter les scripts de synchronisation et `python3 scripts/okf/validate_okf.py okf` — validation `PASS` (117 concepts), couverture dans `output/okf-discovery-coverage-2026-08-24.md`
