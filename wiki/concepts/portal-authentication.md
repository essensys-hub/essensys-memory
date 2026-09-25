---
tags: [concept, auth, security]
sources: [essensys-password-reset-2026-08-039, essensys-temporary-password-2026-09-040]
created: 2026-09-25
updated: 2026-09-25
---

# Portal Authentication

Authentification par email/mot de passe des comptes `users` (portail cloud, distinct du protocole IoT legacy) : connexion, récupération et dépannage.

## Connexion

`POST /api/auth/login` — bcrypt, rôle porté dans le JWT (`GenerateJWT`). Refuse un compte `forbidden_at` non nul ([[Modération comptes utilisateurs (admin)]]) avant même la comparaison du mot de passe.

## Récupération — lien à usage unique (voie par défaut)

`essensys-password-reset-2026-08-039`. Jeton opaque 256 bits (`internal/pwreset`), SHA-256 seul stocké, 60 min, usage unique. Endpoints publics `POST /auth/password/forgot`, `GET /auth/password/reset/validate`, `POST /auth/password/reset`. Action admin d'assistance : `POST /api/admin/users/{id}/password-reset` (déclenche l'envoi, l'admin ne voit jamais le jeton).

Piège déjà rencontré une fois : le lien doit être construit contre `PASSWORD_RESET_BASE_URL` (le support-site, où vit `/reset-password`), jamais contre `FRONTEND_URL` (le portail `mon.essensys.fr`, qui n'a pas cette route et avale l'URL via son fallback SPA).

## Dépannage — mot de passe temporaire (voie manuelle)

`essensys-temporary-password-2026-09-040`. Pour le cas où le lien ci-dessus est inutilisable (email erroné, boîte inaccessible). `POST /api/admin/users/{id}/temporary-password` (rôle `admin_global` uniquement) génère 12 caractères (`internal/temppass`, alphabet sans `O0Il1`, ~70 bits), affichés **une seule fois** à l'admin pour transmission orale — jamais par email par défaut. Écrase `password_hash` et pose `password_change_required_at` + `temp_password_expires_at` (+72h) en un seul `UPDATE`. Invalide au passage tout jeton de réinitialisation encore actif pour ce compte : les deux voies ne coexistent jamais.

**Verrou serveur** (pas côté client) : `enforceActiveUser` (`internal/middleware/user_status.go`) refuse `409 password_change_required` sur toute route authentifiée tant que ce drapeau est posé — sauf `POST /auth/password/change`, seule exemption, seule sortie. Le compte étant rechargé depuis la base à chaque requête, le verrou s'applique **immédiatement** à une session déjà ouverte, sans attendre l'expiration du JWT ni sa réémission. `forbidden_at` prime toujours sur `password_change_required_at` quand les deux sont posés.

Le SPA (`essensys-support-site`) patche `window.fetch` une fois au démarrage (`lib/passwordChangeGuard.js`) pour rediriger vers `/change-password` sur tout `409` portant cet `error`, depuis n'importe quelle page — seul moyen de couvrir ça sans instrumenter chaque appel `fetch()` individuellement, ce dépôt n'ayant pas de wrapper fetch partagé.

## Implémentation

`essensys-user-portal-backend` (API, prod) ; UI + jumeau dev dans `essensys-support-site` (`/login`, `/change-password`, console admin `UserManager.jsx`). Aucun impact sur le protocole IoT legacy — `middleware.BasicAuth` authentifie des machines via `hashed_pkey` contre la table `machines`, jamais `users.password_hash`.

## Bug transverse trouvé en vérifiant cette feature

`.page-content` (Admin.jsx) porte `backdrop-filter`, qui — comme `transform`/`filter`/`perspective` — crée un nouveau contexte de positionnement pour les descendants `position:fixed`. Toute modale de `UserManager.jsx` ouverte après un scroll de page se retrouvait positionnée hors-écran. Contourné pour la nouvelle modale via un portail React (`createPortal` dans `document.body`) ; les modales préexistantes (`resendUser`, `editingUser`) n'ont pas été retouchées — même bug, à corriger si une prochaine feature les touche.
