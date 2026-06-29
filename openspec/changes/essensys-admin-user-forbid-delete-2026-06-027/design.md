## Context

- **Surface** : admin utilisateurs sur `mon.essensys.fr` — frontend React dans `essensys-support-site/site/`, API servie en prod par **`essensys-user-portal-backend`** (mode `CONSOLIDATED_MODE`), avec code miroir dans `essensys-support-site/backend/`.
- **État actuel** : CRUD partiel (liste, création, rôle, liens, renvoi email). `DeleteUser` existe dans le store mais n'est exposé que via `DELETE /api/profile` (auto-suppression). Aucun champ `forbidden_at`.
- **Page construction** : `essensys-support-site/maintenance/index.html`, déployée sur nginx (`/maintenance/` ou équivalent prod).
- **Revue sécurité** (pré-change) : JWT 24h sans revalidation DB, IDOR sur `PUT …/links`, scope inventaire machines — findings #1–#2 bloquants pour un forbid fiable.

## Goals / Non-Goals

**Goals:**

- Permettre à un admin (`admin_global`, `admin_local` dans son scope) d'**interdire** un utilisateur (conserver email + historique audit).
- Permettre la **suppression définitive** d'un utilisateur (hors auto-suppression profil).
- Rediriger tout utilisateur interdit vers la page « en construction » à la connexion (email, Google, Apple).
- Invalider l'accès des JWT existants pour comptes interdits/supprimés (lookup DB middleware).
- UI admin claire : boutons, confirmations, état visible.

**Non-Goals:**

- RGPD export/anonymisation automatique (hors scope — delete hard suffit pour l'instant).
- Rate limiting inscription (finding séparé).
- Refonte complète RBAC ou whitelist rôles (amélioration opportuniste seulement).
- Modification protocole legacy IoT.

## Decisions

### 1. Soft-ban via `forbidden_at` (pas de rôle dédié)

**Choix** : colonne nullable `forbidden_at TIMESTAMPTZ` sur `users`.

**Alternatives** :
- Rôle `forbidden` → pollue l'enum rôles et complique les dropdowns admin.
- Flag `is_active` → ambigu avec machines IoT (`es_machine.is_active`).

**Rationale** : timestamp audit-friendly ; email intact ; réversible via `unforbid`.

### 2. Endpoints REST admin

| Méthode | Route | Effet |
|---------|-------|-------|
| `POST` | `/api/admin/users/{id}/forbid` | Set `forbidden_at = now()` |
| `POST` | `/api/admin/users/{id}/unforbid` | Set `forbidden_at = NULL` |
| `DELETE` | `/api/admin/users/{id}` | Hard delete row |

Réponses : `204 No Content` ou `200` avec user mis à jour pour forbid/unforbid.

**Autorisation** (helper partagé `authorizeAdminTargetUser(caller, targetID, action)`):

- `admin_global` : toute cible sauf **auto-action sur soi-même** pour delete ; interdit de supprimer le **dernier** `admin_global`.
- `admin_local` : uniquement users de `linked_machine_id` ; **pas** de forbid/delete sur `admin_global`, `admin_local`, `support`.
- Audit obligatoire sur chaque action.

### 3. Enforcement auth — login + middleware

**Login (`HandleLogin`, OAuth callbacks)** :

- Si `user.ForbiddenAt != nil` → `403 Forbidden` avec body JSON :
  ```json
  { "error": "account_forbidden", "redirect": "/maintenance/" }
  ```
- Frontend (`Login.jsx`, callback OAuth admin) : si `account_forbidden`, `window.location.href = '/maintenance/'` **sans** persister le token.

**Middleware `UserTokenMiddleware` / `AdminTokenMiddleware`** :

- Après validation JWT, **lookup DB** par email (`GetUserByEmail`).
- Si user nil ou `forbidden_at` set → `403` + même payload redirect (API) ; routes protégées inaccessibles même avec JWT valide émis avant le ban.

**Alternative rejetée** : denylist JWT par `jti` — complexité migration ; lookup DB suffit à volume actuel.

### 4. Redirect page construction

**Choix** : URL canonique **`/maintenance/`** (fichier statique existant).

**Frontend** : pas de route React — redirect HTTP full page vers le static nginx.

**OAuth Google/Apple** : même check avant émission token ; redirect navigateur vers `/maintenance/` si interdit.

### 5. UI `UserManager.jsx`

- Colonne Actions (visible `admin_global` ; `admin_local` pour users de son scope) :
  - **Interdire** (si `!forbidden_at`) — confirm dialog
  - **Réautoriser** (si `forbidden_at`) — confirm
  - **Supprimer** — confirm avec saisie email
- Badge visuel « Interdit » sur la ligne (`forbidden_at` dans JSON liste users).
- Désactiver édition rôle/liens pour comptes interdits (optionnel v1 : read-only).

### 6. Jumeau `essensys-user-portal-backend`

Implémenter en **priorité prod** dans `internal/admin/handlers.go` + migration PG partagée. Reporter dans `essensys-support-site/backend` pour parité dev/local.

Helper autorisation extrait pour réutilisation role/links/forbid/delete (corrige partiellement IDOR links — finding #1).

## Risks / Trade-offs

| Risque | Mitigation |
|--------|------------|
| JWT stale 24h après forbid | Lookup DB middleware + refus login |
| Admin local bannit un autre admin | Guard : interdit sur rôles privilégiés |
| Delete irréversible | Confirm UI + audit ; pas de delete dernier admin_global |
| OAuth crée compte puis forbid immédiat | Check à chaque token refresh/login |
| Performance lookup DB | Acceptable ; index sur `email` existant |

## Migration Plan

1. Migration SQL : `ALTER TABLE users ADD COLUMN forbidden_at TIMESTAMPTZ NULL;`
2. Déployer backend user-portal (API + middleware).
3. Déployer frontend support-site (UserManager + Login).
4. Vérifier nginx sert `/maintenance/`.
5. Rollback : drop column ou set all NULL ; retirer checks middleware (feature flag env `ESSENSYS_FORBID_CHECK=0` optionnel dev).

## Open Questions

- Exposer **unforbid** dans l'UI dès v1 ? → **Oui** (symétrie admin).
- `admin_local` peut-il interdire un `user`/`guest_local` de sa machine ? → **Oui**.
- Notification email à l'utilisateur interdit ? → **Non** v1 (silencieux, redirect construction).
