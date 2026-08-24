## Why

Le formulaire de connexion `mon.essensys.fr` (`essensys-support-site/site/src/pages/Login.jsx`) n'offre **aucun lien « Mot de passe oublié »**. Côté backend, `essensys-user-portal-backend/internal/identity/routes.go` ne monte aucune route de réinitialisation, et aucun outil admin ne permet de forcer un nouveau mot de passe : un utilisateur qui perd son mot de passe est **définitivement bloqué**.

Le cas est déjà survenu en production : le compte `emilienbieber67260@gmail.com` (`users.id=12`, créé le 2026-08-14, `last_login = created_at`) a généré 25 tentatives `POST /api/auth/login` → `401` depuis l'IP de sa machine liée le 2026-08-24 entre 15:32 et 15:48 UTC. Les temps de réponse (78–139 ms, coût du `bcrypt.CompareHashAndPassword`) prouvent que l'email est bien résolu en base et que seul le mot de passe est faux.

La cause exacte reste indéterminée : `Register.jsx` possède un champ « Confirmer le mot de passe » depuis le commit `6ca7e5f` (2026-01-17), soit sept mois avant cette inscription. Une simple faute de frappe est donc peu probable — l'utilisateur a saisi deux fois la même valeur. Restent l'oubli du mot de passe choisi, un gestionnaire de mots de passe qui n'a pas enregistré la valeur, ou une confusion avec un autre compte. Quelle que soit l'hypothèse, l'absence de tout mécanisme de récupération transforme un incident bénin en compte définitivement perdu, et c'est ce manque que cette change corrige.

Le modèle d'email `password_reset` existe déjà dans `email_templates` (migration `006_email_templates.sql`) mais n'est **jamais envoyé** : aucun code Go ne référence `domain.EmailSlugPasswordReset`. L'infrastructure est à moitié posée, il manque la boucle complète.

## What Changes

- **Frontend `essensys-support-site`** : ajout d'un lien « Mot de passe oublié ? » sous le champ mot de passe de `Login.jsx`, d'une page `ForgotPassword.jsx` (saisie email + widget Turnstile) et d'une page `ResetPassword.jsx` (lecture du token en query string, nouveau mot de passe + confirmation, indicateur de robustesse). Routes `/forgot-password` et `/reset-password` déclarées dans `site/src/App.jsx`.
- **Frontend `essensys-support-site`** : le champ « Confirmer le mot de passe » de `Register.jsx` existe déjà ; la change se limite à le figer dans une spécification pour empêcher toute régression.
- **Backend `essensys-user-portal-backend`** : nouvelle table `password_reset_tokens` (migration `013`), nouveau store `data.PasswordResetStore`, et trois endpoints publics montés dans `identity` :
  - `POST /api/auth/password/forgot` — demande de réinitialisation, protégé par Turnstile + rate limit, **réponse toujours 202** (pas d'énumération de comptes).
  - `POST /api/auth/password/reset` — consommation du token à usage unique, réécriture du `password_hash` en bcrypt.
  - `GET /api/auth/password/reset/validate` — pré-vérification du token pour afficher un message clair avant la saisie.
- **Backend** : le token est transmis par email via le modèle `password_reset` existant, en remplaçant `{{temporary_password}}` par un **lien signé** `{{reset_url}}` — aucun mot de passe en clair ne transite par email. Le rendu réutilise `notify.Render` / `notify.Send` et journalise dans `email_send_log`.
- **Backend** : nouvelle action admin `POST /api/admin/users/{id}/password-reset` permettant au support de déclencher l'envoi pour un utilisateur bloqué, tracée dans `audit_logs`.
- **Observabilité** : nouvelles actions d'audit `PASSWORD_RESET_REQUESTED`, `PASSWORD_RESET_COMPLETED`, `PASSWORD_RESET_TOKEN_INVALID`, `PASSWORD_RESET_BLOCKED_RATELIMIT`, exploitables depuis l'écran `AuditLogs` de l'admin.

Aucun impact sur le protocole legacy IoT : les endpoints `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}` et la table d'échange ne sont pas touchés. La réinitialisation ne concerne que les comptes portail (`users`), pas les identifiants machine legacy.

## Capabilities

### New Capabilities
- `password-reset-request`: demande de réinitialisation résistante à l'énumération de comptes (Turnstile, rate limit, réponse uniforme) et émission du token à usage unique
- `password-reset-consume`: validation et consommation du token, règles de robustesse du nouveau mot de passe, invalidation des tokens restants
- `password-reset-notification`: envoi du lien de réinitialisation via le modèle `password_reset` et journalisation dans `email_send_log`
- `auth-recovery-ui`: parcours UI « mot de passe oublié / réinitialisation » sur `mon.essensys.fr`, et garde de non-régression sur la confirmation de mot de passe à l'inscription
- `admin-password-reset-assist`: action admin de déclenchement d'une réinitialisation pour un compte bloqué, avec traçabilité

### Modified Capabilities
<!-- Aucune capacité existante sous openspec/specs/ ne voit ses exigences modifiées :
     le parcours de login actuel reste inchangé, on ajoute un parcours parallèle. -->

## Impact

- **Repos** : `essensys-support-site` (frontend `site/`), `essensys-user-portal-backend` (Go), `essensys-ansible` (variables SMTP / `FRONTEND_URL` / activation du modèle d'email), `essensys-doc` (guide utilisateur + runbook support).
- **Fichiers backend** : `internal/identity/routes.go`, `internal/identity/handlers.go` (nouveau `password_reset.go`), `internal/data/` (nouveau `password_reset_store.go`), `internal/admin/routes.go` + `handlers.go`, `internal/domain/email.go`, `migrations/013_password_reset_tokens.sql`.
- **Fichiers frontend** : `site/src/pages/Login.jsx`, `Register.jsx`, `ForgotPassword.jsx` (nouveau), `ResetPassword.jsx` (nouveau), `Auth.css`, `App.jsx`.
- **Base de données** : nouvelle table `password_reset_tokens` ; le modèle `password_reset` de `email_templates` doit passer à `enabled = true`.
- **Configuration** : dépend d'un SMTP fonctionnel (`notify.Configured()`), de `FRONTEND_URL` pour construire le lien, et réutilise `TURNSTILE_SECRET_KEY` / `VITE_TURNSTILE_SITE_KEY` déjà déployés par la change `essensys-turnstile-registration-2026-07-036`.
- **Entités wiki liées** : [[Essensys User Portal Backend]], [[Essensys Support Site]], [[Portal Authentication]], [[Email Templates]].
- **Non impacté** : firmware SC944D, table d'échange, indices k/v, `essensys-server-backend` (le login local gateway ne partage pas la table `users` cloud).
