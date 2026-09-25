## Why

Depuis la change `essensys-password-reset-2026-08-039`, le support dispose d'un seul moyen de débloquer un compte : `POST /api/admin/users/{id}/password-reset`, qui émet un lien à usage unique et **l'envoie par courriel**. Tout ce chemin repose sur une hypothèse : l'utilisateur accède à sa boîte mail.

Quand cette hypothèse tombe — adresse saisie avec une faute à l'inscription, boîte saturée, domaine qui rejette le relais, personne qui n'a plus l'usage de sa messagerie — il n'existe **aucune** issue. L'administrateur voit le compte dans `UserManager.jsx`, déclenche l'envoi, lit `email_sent: true`, et l'utilisateur reste bloqué. L'action a réussi ; le déblocage, non.

Il manque une voie **hors-bande** : un mot de passe temporaire que l'administrateur lit à l'écran et transmet de vive voix, et que l'utilisateur est contraint de remplacer dès sa première connexion.

### Le point sensible : ce que la migration 013 avait retiré

La migration `013_password_reset_tokens.sql` a délibérément réécrit le modèle `password_reset` pour en retirer `{{temporary_password}}`, avec ce motif : un secret réutilisable envoyé par courriel survit dans la boîte mail et dans les journaux du relais SMTP. Cette change réintroduit un mot de passe temporaire et doit donc répondre à cette objection plutôt que la contourner :

- la **voie par défaut n'est pas le courriel** mais l'affichage à l'écran de l'administrateur, pour une transmission orale ;
- l'envoi par courriel est **opt-in, décision par décision**, pris explicitement par l'administrateur au moment de l'émission ;
- le mot de passe temporaire **expire au bout de 72 h** et cesse alors d'autoriser la connexion ;
- il est **effacé à la première connexion réussie**, le changement étant imposé par le serveur et non par le client — sa durée de vie utile est donc d'un seul usage dans le cas nominal.

Ce sont ces quatre conditions, pas le confort de l'administrateur, qui justifient le revirement. Elles sont exigibles, donc spécifiées ci-dessous.

## What Changes

- **Backend `essensys-user-portal-backend`** : migration `014_temporary_password.sql` ajoutant trois colonnes à `users` (`password_change_required_at`, `temp_password_expires_at`, `temp_password_issued_by`) et insérant le modèle de courriel `temporary_password`.
- **Backend** : nouvel endpoint `POST /api/admin/users/{id}/temporary-password`, réservé au rôle administrateur global, qui génère un mot de passe fort, réécrit `password_hash`, pose les trois colonnes, invalide les jetons de réinitialisation en cours, journalise l'action et **renvoie le mot de passe en clair une seule fois** dans sa réponse. Envoi de courriel optionnel via `{"send_email": true}`.
- **Backend** : nouveau paquet `internal/temppass` (génération dans un alphabet sans caractères ambigus, destiné à être dicté).
- **Backend** : verrou serveur dans `middleware.enforceActiveUser` — un compte portant `password_change_required_at` reçoit `409 password_change_required` sur **toutes** les routes authentifiées, à l'exception de la route de changement.
- **Backend** : nouvel endpoint `POST /api/auth/password/change`, seule route exemptée du verrou, qui réécrit le mot de passe et efface les trois colonnes dans un `UPDATE` unique.
- **Backend** : `identity.Login` refuse un mot de passe temporaire expiré (`401 temporary_password_expired`) et signale `password_change_required` dans sa réponse de succès.
- **Frontend `essensys-support-site`** : entrée « Définir un mot de passe temporaire… » dans le menu d'actions de `UserManager.jsx`, modale dédiée en deux temps (confirmation puis affichage unique du mot de passe), badge d'état dans la liste des utilisateurs.
- **Frontend** : page `ChangePassword.jsx` et route `/change-password`, vers laquelle `Login.jsx` redirige, et vers laquelle tout `409 password_change_required` renvoie.
- **Observabilité** : actions d'audit `TEMPORARY_PASSWORD_ISSUED` et `PASSWORD_CHANGED_AFTER_TEMPORARY`, consultables depuis l'écran d'audit de l'administration.

Hors périmètre : la création de compte (`POST /api/admin/users`) conserve son comportement actuel, où l'administrateur choisit un mot de passe transmis dans le courriel de bienvenue.

Aucun impact sur le protocole legacy IoT. `middleware.BasicAuth` authentifie des **machines** par `hashedPkey` contre la table `machines` et ne lit jamais `users.password_hash` : les endpoints `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}` et la table d'échange sont insensibles à cette change.

## Capabilities

### New Capabilities
- `admin-temporary-password-issue`: émission par un administrateur d'un mot de passe temporaire à durée de vie bornée, affiché une seule fois et tracé dans le journal d'audit
- `password-change-enforcement`: verrou serveur interdisant tout usage du compte tant que le mot de passe temporaire n'est pas remplacé, et expiration du mot de passe temporaire à la connexion
- `forced-password-change-ui`: parcours utilisateur de changement imposé sur `www.essensys.fr`, sans échappatoire autre que la déconnexion
- `temporary-password-notification`: envoi optionnel du mot de passe temporaire par courriel, à la demande explicite de l'administrateur

### Modified Capabilities
<!-- Aucune exigence de `essensys-password-reset-2026-08-039` n'est modifiée. L'émission
     d'un mot de passe temporaire invalide les jetons de réinitialisation en cours, ce qui
     relève du comportement déjà spécifié par `InvalidateForUser` et non d'une exigence
     nouvelle sur le parcours de réinitialisation. -->

## Impact

- **Repos** : `essensys-user-portal-backend` (Go, API + migration), `essensys-support-site` (frontend `site/`), `essensys-doc` (guide support et guide utilisateur).
- **Fichiers backend** : `migrations/014_temporary_password.sql`, `internal/data/user_store.go`, `internal/domain/user.go`, `internal/domain/auth.go`, `internal/domain/email.go`, `internal/middleware/user_status.go`, `internal/admin/routes.go` + `temporary_password.go` (nouveau), `internal/identity/routes.go` + `handlers.go` + `password_change.go` (nouveau), `internal/temppass/` (nouveau).
- **Fichiers frontend** : `site/src/pages/UserManager.jsx`, `site/src/components/TemporaryPasswordModal.jsx` (nouveau), `site/src/pages/ChangePassword.jsx` (nouveau), `site/src/pages/Login.jsx`, `site/src/pages/Auth.css`, `site/src/App.jsx`.
- **Base de données** : trois colonnes ajoutées à `users` ; nouveau modèle `temporary_password` dans `email_templates`.
- **Configuration** : aucune variable nouvelle. L'envoi optionnel réutilise le SMTP déjà configuré (`notify.Configured()`) ; son indisponibilité ne bloque pas l'émission.
- **Entités wiki liées** : [[Essensys User Portal Backend]], [[Essensys Support Site]], [[Portal Authentication]], [[Email Templates]].
- **Non impacté** : firmware SC944D, table d'échange, indices k/v, `essensys-server-backend` (le login local gateway ne partage pas la table `users` cloud), `essensys-user-portal-frontend` (aucune page d'authentification).
