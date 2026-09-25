## 1. Socle base de données — essensys-user-portal-backend

- [x] 1.1 Créer `migrations/014_temporary_password.sql` ajoutant `password_change_required_at`, `temp_password_expires_at`, `temp_password_issued_by` à `users` (D1), avec le commentaire justifiant le revirement vis-à-vis de la migration 013 ; vérifier en appliquant la migration sur une base locale et en contrôlant `\d users`
- [x] 1.2 Dans la même migration, insérer le modèle `temporary_password` dans `email_templates` (`enabled = true`, variables `{{temporary_password}}`, `{{expires_in}}`, `{{login_url}}`) ; vérifier par `SELECT slug, enabled, body_html FROM email_templates WHERE slug='temporary_password'`
- [x] 1.3 Répliquer les trois `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` dans `UserStore.EnsureTableExists` (convention déjà suivie pour `forbidden_at`) ; vérifier que `go build ./...` passe et que la table créée par un test à vide porte les trois colonnes
- [x] 1.4 Ajouter les trois champs à `domain.User` (tags `db`/`json`, `json:"-"` sur `temp_password_issued_by` sauf besoin d'affichage admin) et deux helpers `domain.PasswordChangeRequired(u *User) bool` / `domain.TempPasswordExpired(u *User, now time.Time) bool` ; vérifier par des tests unitaires courts sur les deux helpers (nil, non posé, posé non expiré, posé expiré)
- [x] 1.5 Ajouter `domain.WritePasswordChangeRequired(w http.ResponseWriter)` dans `internal/domain/auth.go`, calqué sur `WriteAccountForbidden` (`409`, `{"error":"password_change_required","redirect":"/change-password"}`) ; vérifier par un test de handler HTTP

## 2. Génération du mot de passe temporaire — essensys-user-portal-backend

- [x] 2.1 Créer `internal/temppass/temppass.go` : `Generate() (string, error)` sur `crypto/rand`, alphabet de 57 caractères excluant `O`, `0`, `I`, `l`, `1`, longueur 12 (D4) ; vérifier par un test statistique (1000 générations, aucun caractère exclu présent, aucune collision) et par un test d'entropie minimale
- [x] 2.2 Ajouter `internal/data/user_store.go` : `SetTemporaryPassword(userID int, hash string, expiresAt time.Time, issuedBy int) error` (un seul `UPDATE` posant `password_hash`, `password_change_required_at = NOW()`, `temp_password_expires_at`, `temp_password_issued_by`) et `ClearPasswordChangeRequired(userID int, hash string) error` (un seul `UPDATE` posant le nouveau `password_hash` et remettant les trois colonnes à `NULL`) ; vérifier par tests utilisant `sqlmock`, sur le patron de `password_reset_store_test.go`

## 3. Verrou serveur — essensys-user-portal-backend

- [x] 3.1 Dans `internal/middleware/user_status.go`, ajouter le test `domain.PasswordChangeRequired(user)` → `domain.WritePasswordChangeRequired(w)` dans `enforceActiveUser`, juste après le test `IsUserForbidden` (D2) ; vérifier par un test unitaire de `enforceActiveUser` couvrant les quatre combinaisons (aucun état, interdit seul, changement requis seul, les deux → priorité à interdit)
- [x] 3.2 Ajouter `middleware.UserJWTAllowPasswordChange(users ActiveUserStore) func(http.Handler) http.Handler`, copie de `UserJWTWithStore` sans le test 3.1 (D3) ; vérifier par un test qu'un compte marqué passe au travers de cette fonction mais pas de `UserJWTWithStore`
- [x] 3.3 Vérifier par test d'intégration que `GET /api/profile` (identity), une route `portal` et une route `admin` répondent toutes `409 password_change_required` pour un compte marqué, y compris quand ce compte porte un rôle administrateur
- [x] 3.4 Vérifier par test qu'une session dont le jeton a été émis avant la pose du drapeau reçoit `409` à sa requête suivante (pas d'effet différé)

## 4. Émission — essensys-user-portal-backend

- [ ] 4.1 Créer `internal/admin/temporary_password.go` : `IssueTemporaryPassword` — `requireAdminGlobal`, résolution du compte (`404`), test `IsUserForbidden` (`409 account_forbidden`), génération (2.1), hachage bcrypt, `SetTemporaryPassword` (2.2, échéance +72h), `PasswordResetStore.InvalidateForUser` (D6), audit `TEMPORARY_PASSWORD_ISSUED` sans le clair ; vérifier par tests couvrant `403`, `404`, `409`, succès
- [ ] 4.2 Ajouter l'envoi optionnel : corps `{"send_email": bool}`, si vrai composer et envoyer le modèle `temporary_password` via le service transactionnel existant (`sendTemplateEmailWithVars`), échec d'envoi → `200 {"email_sent": false, "reason": ...}` sans annuler l'émission (D7) ; vérifier par test simulant un envoi en échec
- [ ] 4.3 Monter `POST /admin/users/{id}/temporary-password` dans `internal/admin/routes.go`, sous le groupe `AdminAuthWithStore` déjà existant ; vérifier par un test de routage que l'endpoint répond
- [ ] 4.4 Exposer `password_change_required_at` et `temp_password_expires_at` dans la réponse JSON de `internal/admin/handlers.go:GetUsers` (consommé par le badge de la tâche 6.3) ; vérifier par un test que ces deux champs apparaissent pour un compte marqué et sont absents/nuls sinon
- [ ] 4.5 Vérifier par test qu'aucune ligne de journal applicatif ne contient le mot de passe en clair (grep sur la sortie capturée du logger pendant le test)
- [ ] 4.6 Vérifier par test qu'émettre un second mot de passe temporaire invalide immédiatement le premier (connexion avec l'ancien échoue)

## 5. Connexion et changement — essensys-user-portal-backend

- [ ] 5.1 Dans `internal/identity/handlers.go`, après le succès de `bcrypt.CompareHashAndPassword` dans `Login` : si `TempPasswordExpired` → `401 {"error":"temporary_password_expired"}` sans émettre de jeton (D5) ; sinon poursuivre normalement et ajouter `"password_change_required": domain.PasswordChangeRequired(user)` à la réponse de succès ; vérifier par tests couvrant expiré, valide non expiré, compte ordinaire, et l'absence de divulgation d'état sur mot de passe erroné
- [ ] 5.2 Créer `internal/identity/password_change.go` : `ChangePassword` — email depuis le contexte JWT, décode `{current_password, new_password}`, revérifie `current_password` par bcrypt (`401` sinon), applique `pwreset.MinPasswordLength` (`400` sinon), refuse `new_password == current_password` (`400`), hache et appelle `ClearPasswordChangeRequired` (2.2) dans une transaction unique, audit `PASSWORD_CHANGED_AFTER_TEMPORARY` ; vérifier par tests couvrant chaque rejet et le succès
- [ ] 5.3 Monter `POST /auth/password/change` dans `internal/identity/routes.go` sous `UserJWTAllowPasswordChange` (3.2), avec un `RateLimiter(10, time.Hour)` sur le patron de `resetLimiter` ; vérifier par test que la route répond `429` au-delà de la limite
- [ ] 5.4 Vérifier par test d'intégration qu'après un changement réussi, le même jeton JWT (sans réémission) obtient désormais `200` sur une route qui répondait `409` avant le changement

## 6. Modale d'émission — essensys-support-site

- [ ] 6.1 Créer `site/src/components/TemporaryPasswordModal.jsx` : état de confirmation (email affiché, avertissement de remplacement définitif, case « Envoyer aussi par email » décochée par défaut) puis état de résultat (mot de passe en monospace, bouton copier, date d'expiration formatée, statut d'envoi et motif d'échec le cas échéant, mention explicite que le mot de passe ne sera plus affiché après fermeture) ; vérifier par un rendu manuel dans le navigateur de dev (`npm run dev`)
- [ ] 6.2 Dans `site/src/pages/UserManager.jsx`, ajouter l'entrée « Définir un mot de passe temporaire… » au menu d'actions (sous « Envoyer un lien de réinitialisation », état `[tempPassUser, setTempPassUser]` sur le patron de `resendUser`), brancher l'appel à `POST /api/admin/users/{id}/temporary-password` et le rendu de la modale (6.1) ; vérifier manuellement le parcours complet dans le navigateur
- [ ] 6.3 Ajouter un badge « MDP TEMPORAIRE » dans la liste des utilisateurs pour tout compte dont la réponse admin renvoie `password_change_required_at` non nul (nécessite d'exposer ce champ dans la réponse JSON de `internal/admin/handlers.go:GetUsers`, côté `essensys-user-portal-backend`, non couvert par les tâches 1–5 — l'ajouter avant d'écrire ce badge) ; vérifier visuellement à côté du badge « Interdit » existant

## 7. Écran de changement imposé — essensys-support-site

- [ ] 7.1 Créer `site/src/pages/ChangePassword.jsx` (formulaire mot de passe actuel / nouveau / confirmation, appel à `POST /api/auth/password/change`, distinction des erreurs 401/400, redirection vers l'espace connecté au succès sans reconnexion) et son style dans `Auth.css`, sur le patron de `ResetPassword.jsx` ; vérifier manuellement les trois cas d'erreur et le succès
- [ ] 7.2 Déclarer la route `/change-password` dans `site/src/App.jsx`
- [ ] 7.3 Dans `Login.jsx`, rediriger vers `/change-password` quand la réponse de connexion porte `password_change_required: true`, et afficher un message dédié (pas « identifiants invalides ») quand la connexion échoue avec `temporary_password_expired` ; vérifier manuellement les deux cas
- [ ] 7.4 Ajouter un traitement global du `409 password_change_required` (intercepteur fetch ou équivalent déjà en place dans le SPA) qui redirige vers `/change-password` depuis n'importe quelle page ; vérifier manuellement en simulant la réponse
- [ ] 7.5 Empêcher toute navigation hors de `/change-password` tant que le changement n'est pas fait (retirer les liens de nav sur cette page, rediriger toute route protégée vers `/change-password` si le contexte utilisateur porte l'indicateur) tout en gardant la déconnexion disponible ; vérifier manuellement qu'une saisie directe d'URL vers une autre page protégée ramène ici

## 8. Vérification transverse et matrice UX

- [ ] 8.1 Écrire `site/e2e/temporary-password.spec.js` (Playwright) couvrant : émission depuis l'admin, affichage unique, connexion avec mot de passe temporaire, redirection, changement réussi, retour à `/change-password` sur un `409` simulé ; exécuter et vérifier que la suite passe
- [ ] 8.2 Exécuter la matrice UX (`desktop`, `iphone`, `ipad`) sur la modale d'émission et sur `/change-password`, capturer les captures d'écran requises par `tests.ux_matrix` du manifeste `essensys-support-site`, et vérifier l'absence de défilement horizontal sur iPhone
- [ ] 8.3 Exécuter `go test ./...` dans `essensys-user-portal-backend` et vérifier qu'aucun test existant ne régresse, en particulier `internal/middleware`, `internal/identity`, `internal/admin`
- [ ] 8.4 Relire le journal d'audit produit pendant les tests 8.1–8.3 et vérifier qu'aucune entrée `TEMPORARY_PASSWORD_ISSUED` ne contient de mot de passe en clair ni d'empreinte

## 9. Documentation et mémoire

- [ ] 9.1 Rédiger `docs/features/temporary-password.md` (guide support : comment émettre, comment transmettre par téléphone, que faire à expiration) dans `essensys-user-portal-backend` ou `essensys-doc` selon l'emplacement retenu par le dépôt pour les guides transverses
- [ ] 9.2 Mettre à jour `essensys-memory` : nouvelle entité liée [[Portal Authentication]] mentionnant le mot de passe temporaire, et mise à jour de la mémoire `prod-deploy-topology` si le parcours de déploiement de cette change diffère de celui déjà documenté
- [ ] 9.3 Faire passer `essensys-feature-lifecycle/scripts/feature_lifecycle/check_feature_gate.py --strict` sur les deux manifestes (`essensys-user-portal-backend`, `essensys-support-site`) une fois tous les fichiers déclarés créés, et corriger tout écart entre chemins déclarés et chemins réels
