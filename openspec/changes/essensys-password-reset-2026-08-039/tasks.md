## 1. Socle base de données et stockage des jetons

- [ ] 1.1 Créer `essensys-user-portal-backend/migrations/013_password_reset_tokens.sql` avec la table décrite dans `design.md` (D2) et les index sur `token_hash` et `user_id` ; vérifier en appliquant la migration sur une base locale et en contrôlant `\d password_reset_tokens`
- [ ] 1.2 Dans la même migration, réécrire le modèle `password_reset` de `email_templates` autour de `{{reset_url}}` et `{{expires_in}}`, retirer `{{temporary_password}}`, et passer `enabled = true` ; vérifier par `SELECT slug, enabled, body_html FROM email_templates WHERE slug='password_reset'`
- [ ] 1.3 Créer `internal/data/password_reset_store.go` avec `EnsureTableExists`, `Create(userID, tokenHash, expiresAt, requestIP)`, `ConsumeByHash(tokenHash, ip)` en `UPDATE` conditionnel retournant le `user_id`, `GetByHash`, `InvalidateForUser(userID)` et `PurgeOlderThan(d)` ; vérifier par tests unitaires du paquet `data`
- [ ] 1.4 Écrire un test de concurrence sur `ConsumeByHash` (deux goroutines, même jeton) et vérifier qu'exactement une consommation réussit
- [ ] 1.5 Ajouter `UserStore.UpdatePasswordHash(userID, hash)` (D6) et vérifier par un test que prénom et nom ne sont pas modifiés

## 2. Extraction du service de courriel transactionnel

- [ ] 2.1 Créer `internal/mailtpl` en déplaçant `sendTemplateEmail`, `buildTemplateVars`, `enrichDeviceVars` et `recordEmailFailure` depuis `internal/admin/transactional.go`, avec le paramètre `extra notify.TemplateVars` (D4) ; vérifier par `go build ./...`
- [ ] 2.2 Remplacer le corps des appels de `internal/admin` par une délégation vers `mailtpl` en conservant les signatures publiques, et vérifier que `go test ./internal/admin/...` passe **sans modification des tests existants**
- [ ] 2.3 Ajouter à `mailtpl` un test vérifiant qu'un modèle désactivé n'envoie rien mais produit une ligne `failed` dans le journal d'envoi

## 3. Endpoint de demande de réinitialisation

- [ ] 3.1 Créer `internal/identity/password_reset.go` avec le handler `ForgotPassword` : validation de l'email, vérification Turnstile, résolution du compte, émission du jeton, réponse `202` à corps constant ; vérifier par tests de handler couvrant compte existant, compte inconnu, compte interdit et email invalide
- [ ] 3.2 Implémenter la génération du jeton (32 octets `crypto/rand`, `base64.RawURLEncoding`, stockage `sha256` uniquement) et vérifier par un test que le clair n'apparaît ni en base ni dans les logs
- [ ] 3.3 Implémenter l'invalidation des jetons antérieurs du compte à chaque nouvelle émission et vérifier par test qu'un jeton précédent devient inutilisable
- [ ] 3.4 Rendre l'envoi du courriel asynchrone via goroutine détachée avec timeout (D3) et vérifier par test que le handler répond sans attendre l'envoi
- [ ] 3.5 Ajouter le travail cryptographique factice dans la branche « compte inconnu » et vérifier par un test de latence que l'écart des médianes sur 20 appels reste sous 50 ms
- [ ] 3.6 Monter la route `POST /auth/password/forgot` dans `internal/identity/routes.go` avec un `RateLimiter(5, time.Hour)` par IP, sur le motif de `registerRateLimitMiddleware` ; vérifier par test que la 6ᵉ requête renvoie `429`
- [ ] 3.7 Implémenter la limite de 3 jetons par heure et par compte **sans** modifier le corps ni le code de réponse ; vérifier par test que la 4ᵉ demande renvoie `202` avec le corps uniforme et n'émet aucun jeton
- [ ] 3.8 Journaliser `PASSWORD_RESET_REQUESTED` et `PASSWORD_RESET_BLOCKED_RATELIMIT` sans jeton ni empreinte ; vérifier par test d'audit

## 4. Endpoints de validation et de consommation

- [ ] 4.1 Implémenter `GET /auth/password/reset/validate` renvoyant `valid` et l'email masqué, avec les codes `200` / `410 expired` / `410 used` / `400 invalid` ; vérifier par tests de handler pour chaque état
- [ ] 4.2 Vérifier par test que la pré-validation répétée d'un jeton valide ne le consomme pas et ne compte pas comme tentative
- [ ] 4.3 Implémenter `POST /auth/password/reset` en transaction unique (consommation conditionnelle, contrôle du nombre de lignes, réécriture bcrypt, invalidation des jetons frères) ; vérifier par test que la connexion avec le nouveau mot de passe réussit ensuite
- [ ] 4.4 Implémenter les règles de robustesse (minimum 8 caractères, refus d'un mot de passe identique à l'actuel) **sans consommer le jeton** en cas de rejet ; vérifier par test que le même lien reste utilisable après un rejet
- [ ] 4.5 Traiter le cas du compte interdit entre l'émission et la consommation (`403 account_forbidden`, jeton invalidé, mot de passe inchangé) et vérifier par test
- [ ] 4.6 Vérifier par test que la seconde soumission du même jeton renvoie `400 invalid_token` et que le mot de passe issu de la première consommation reste en vigueur
- [ ] 4.7 Monter les deux routes avec `RateLimiter(10, time.Hour)` sur la consommation, journaliser `PASSWORD_RESET_COMPLETED` et `PASSWORD_RESET_TOKEN_INVALID` ; vérifier par test d'audit
- [ ] 4.8 Brancher l'envoi du courriel sur `mailtpl` avec les variables `reset_url` (construite depuis l'URL publique du portail, repli `https://mon.essensys.fr`) et `expires_in` ; vérifier par test que `{{temporary_password}}` est rendu vide et que le corps ne contient aucun mot de passe
- [ ] 4.9 Ajouter la purge paresseuse des jetons de plus de 30 jours à l'émission et vérifier par test que les lignes anciennes disparaissent

## 5. Action administrateur d'assistance

- [ ] 5.1 Implémenter `POST /api/admin/users/{id}/password-reset` dans `internal/admin`, réservé au rôle administrateur, réutilisant l'émission de jeton du paquet `identity` ou un service partagé ; vérifier par tests couvrant `200`, `401`, `403`, `404` et `409 account_forbidden`
- [ ] 5.2 Vérifier par test que la réponse ne contient ni jeton, ni empreinte, ni lien exploitable, et qu'elle porte `email_sent` avec le motif en cas d'échec
- [ ] 5.3 Journaliser `PASSWORD_RESET_REQUESTED_BY_ADMIN` avec l'administrateur appelant et le compte visé ; vérifier par test d'audit
- [ ] 5.4 Ajouter l'action « Envoyer un lien de réinitialisation » avec confirmation dans `essensys-support-site/site/src/pages/UserManager.jsx`, désactivée pour les comptes interdits ; vérifier manuellement sur la console d'administration
- [ ] 5.5 Exécuter `go test ./...` dans `essensys-user-portal-backend` et vérifier que la suite complète passe

## 6. Parcours frontend de récupération

- [ ] 6.1 Extraire la logique de widget Turnstile de `Register.jsx` vers un composant ou hook réutilisable et vérifier par une exécution `npm run dev` que l'inscription fonctionne toujours
- [ ] 6.2 Créer `site/src/pages/ForgotPassword.jsx` (saisie email, Turnstile, message de confirmation neutre, gestion du `429`, lien de retour vers la connexion) ; vérifier manuellement les quatre états d'affichage
- [ ] 6.3 Créer `site/src/pages/ResetPassword.jsx` avec pré-validation du jeton avant affichage des champs, double saisie, indicateur de longueur, bascule d'affichage en clair, succès puis redirection vers la connexion sous 3 secondes sans connexion automatique ; vérifier manuellement chaque état
- [ ] 6.4 Déclarer les routes `/forgot-password` et `/reset-password` dans `site/src/App.jsx` hors du `Layout`, comme `/login` ; vérifier que les URL directes se chargent
- [ ] 6.5 Ajouter le lien « Mot de passe oublié ? » sous le champ mot de passe de `Login.jsx`, transmettant l'email déjà saisi en paramètre d'URL ; vérifier le pré-remplissage manuellement
- [ ] 6.6 Enrichir le message d'échec de connexion d'un renvoi vers le parcours de récupération, sans indiquer si l'email ou le mot de passe est en cause ; vérifier manuellement
- [ ] 6.7 Ajouter le champ « Confirmer le mot de passe » à `Register.jsx` avec comparaison côté client bloquant la soumission (D8), corps de requête inchangé ; vérifier par l'onglet réseau qu'aucune requête n'est émise en cas de divergence
- [ ] 6.8 Étendre `site/src/pages/Auth.css` pour le lien de récupération, l'indicateur de robustesse et les états de message ; vérifier l'absence de défilement horizontal sur desktop, iPhone et iPad
- [ ] 6.9 Exécuter `npm run lint` et `npm run build` dans `essensys-support-site/site` et vérifier l'absence d'erreur

## 7. Tests de bout en bout et matrice UX

- [ ] 7.1 Ajouter un test Playwright du parcours complet en desktop, iPhone et iPad : lien depuis la connexion, demande, page de réinitialisation avec jeton injecté, connexion réussie ; vérifier que les trois profils passent
- [ ] 7.2 Ajouter un test Playwright des liens invalides (absent, expiré, déjà consommé) et vérifier que les champs de mot de passe ne s'affichent pas
- [ ] 7.3 Ajouter un test Playwright de la divergence des mots de passe à l'inscription et à la réinitialisation
- [ ] 7.4 Vérifier par test d'intégration backend qu'une demande produit une ligne `sent` dans `email_send_log` pour le slug `password_reset`

## 8. Déploiement et clôture de l'incident

- [ ] 8.1 Vérifier dans `essensys-ansible` que la configuration de l'URL publique du portail et les variables SMTP sont bien renseignées pour `mon.essensys.fr` ; vérifier par un rendu à blanc du modèle que le lien produit pointe sur le bon hôte
- [ ] 8.2 Appliquer la migration `013` sur `essensys_db` en production et vérifier la présence de la table et l'activation du modèle
- [ ] 8.3 Déployer `essensys-cloud-backend` et vérifier que les nouvelles routes répondent, le lien frontend n'étant pas encore publié
- [ ] 8.4 Déclencher depuis l'admin une réinitialisation sur un compte de test et vérifier la réception effective du courriel ainsi que la ligne `sent` dans `email_send_log` — **jalon bloquant** avant publication du parcours en libre-service
- [ ] 8.5 Déployer le frontend `essensys-support-site` et vérifier le parcours complet en production sur un compte de test
- [ ] 8.6 Déclencher la réinitialisation pour `emilienbieber67260@gmail.com` (`users.id=12`) et vérifier une connexion réussie dans les journaux du service
- [ ] 8.7 Documenter le parcours utilisateur et le runbook support dans `essensys-doc`, en incluant le diagnostic par `email_send_log` et par les actions d'audit ; vérifier la construction du site de documentation
- [ ] 8.8 Mettre à jour la mémoire OKF (`essensys-memory`) : pages portail et journal, puis exécuter les scripts de synchronisation et `python3 scripts/okf/validate_okf.py okf`
