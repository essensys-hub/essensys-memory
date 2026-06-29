## Why

La page admin **Gestion des Utilisateurs** (`mon.essensys.fr/admin`, `UserManager.jsx`) permet de créer des comptes et de modifier rôles/liaisons, mais **aucune action de modération** n'existe : impossible d'interdire un accès (tout en conservant l'email pour traçabilité) ni de supprimer définitivement un compte. Les admins doivent pouvoir couper l'accès d'un utilisateur abusif ou obsolète sans perdre l'historique email, avec redirection vers la page « en construction » existante.

> **Roadmap ID:** 2026-06.027  
> **Horizon:** Now (modération admin mon.essensys.fr)  
> **Contexte sécurité:** revue préalable — JWT stale et IDOR links à traiter dans le même change (voir design)

## What Changes

- Colonne **`forbidden_at`** (soft-ban) sur la table utilisateurs : l'email reste en base, le compte ne peut plus se connecter ni accéder au portail.
- Endpoints admin **`POST /api/admin/users/{id}/forbid`** et **`DELETE /api/admin/users/{id}`** (plus **`POST …/unforbid`** optionnel) avec scope `admin_global` / `admin_local` aligné sur `UpdateUserRole`.
- **Login / OAuth** : refus des comptes interdits ; réponse ou redirect frontend vers **`/maintenance/`** (page « Site En Construction »).
- **Middleware JWT** : revalidation statut utilisateur en DB (forbidden / supprimé) — corrige la faille JWT stale identifiée en revue sécurité.
- **UI** : boutons **Interdire** / **Supprimer** (avec confirmation) dans la colonne Actions de `UserManager.jsx` ; badge « Interdit » sur la ligne.
- **Jumeau cloud** : même logique dans `essensys-user-portal-backend` (`internal/admin/`) — backend prod du hub mon.essensys.fr.
- Migration SQL + audit log (`FORBID_USER`, `DELETE_USER`, `UNFORBID_USER`).

## Capabilities

### New Capabilities

- `admin-user-lifecycle` : interdiction (soft-ban), levée d'interdiction, suppression admin, enforcement auth et UI admin.

### Modified Capabilities

_(aucune spec existante dans `openspec/specs/` — nouveau capability uniquement)_

## Impact

- `essensys-support-site/site/src/pages/UserManager.jsx` — actions Interdire / Supprimer
- `essensys-support-site/site/src/pages/Login.jsx` — redirect maintenance si compte interdit
- `essensys-support-site/backend/internal/models/user.go`, `data/user_store.go`, `api/handlers_admin.go`, `handlers_auth.go`, `handlers_oauth.go`, `middleware/auth.go`
- `essensys-user-portal-backend/internal/domain/`, `data/user_store.go`, `internal/admin/handlers.go`, `internal/identity/` (login OAuth)
- PostgreSQL : migration `forbidden_at TIMESTAMPTZ NULL` sur `users`
- `essensys-support-site/maintenance/index.html` — page cible (déjà déployée via nginx)
- [[Platform Overview]] — modération comptes hub ; pas d'impact protocole legacy IoT / table d'échange
