## Context

Change **2026-06.017** — IAM LAN user/mot de passe sur `mon.essensys.local`.

Référence critique : [`autocritique.md`](autocritique.md).

**État code (gateway)** :

- `internal/middleware/auth.go` — Basic Auth **passif** (capture Redis, jamais 401).
- `internal/services/user_service.go` — login/register SHA1 UTF-16 (legacy C#).
- `internal/api/router.go` — routes `/api/auth/*` montées si PostgreSQL connecté.
- `essensys-server-frontend` — pas de pages auth ; reload navigateur sur 401.

**IAM cloud (séparé)** : JWT/OAuth sur `essensys-user-portal-backend`, rôles `admin_global` / `admin_local` / `guest_local` — **ne pas fusionner** avec comptes LAN v1.

## Goals / Non-Goals

**Goals**

- Créer, lister, désactiver, réinitialiser mot de passe des **utilisateurs LAN** locaux.
- Login/logout par **session cookie** (HttpOnly, Secure, SameSite=Lax).
- RBAC minimal : `lan_admin`, `lan_user`, `lan_guest`.
- Protéger routes dashboard (`/api/admin/*`, scénarios UI, profil) ; laisser legacy IoT (`/api/mystatus`, `/api/myactions`, `/api/done/`) **sans session**.
- Bootstrap idempotent du premier `lan_admin`.
- Documenter migration depuis Basic Auth passif.

**Non-Goals**

- OAuth / SSO cloud sur `.local`.
- Sync comptes LAN ↔ PostgreSQL OVH.
- Remplacement immédiat SHA1 pour comptes importés legacy.
- MFA v1.

## Decisions

### D1 — Table `lan_users` dédiée (décision produit 2026-06-26)

**Choix validé :** nouvelle table **`lan_users`** — ne pas réutiliser la table legacy `users` (migration ASP.NET / import cloud).

| | |
|---|---|
| **Rationale** | Schéma legacy (`guid`, `machine_id`, validation email WAN) inadapté ; évite collision avec imports ; IAM LAN autonome |
| **Legacy `users`** | Conservée read-only pour compat historique ; **aucune écriture** IAM v1 ; login LAN lit **uniquement** `lan_users` |
| **Migration optionnelle** | Script one-shot import email→`lan_users` si données existantes (hors scope v1 sauf demande) |

Colonnes minimales v1 : `id`, `email` (unique), `password_hash`, `password_algo`, `role`, `display_name`, `disabled_at`, `created_at`, `updated_at`, `last_login_at`.

### D2 — Politique mot de passe

| Cas | Algorithme |
|-----|------------|
| Compte importé one-shot (migration) | SHA1 UTF-16 optionnel via script import |
| **Tout compte créé v1** | bcrypt ou argon2id ; `password_algo` obligatoire |

Login tente algo enregistré ; upgrade transparent au changement de mot de passe.

### D3 — Session vs Basic Auth

- **Retirer** le mode passif de capture credentials (RGPD/sécurité).
- **Option A (recommandée)** : `auth.enabled: false` + session middleware pour UI uniquement.
- **Option B** : Basic Auth strict en plus de session — rejeté (double prompt iPad).

### D4 — Rôles LAN (enum local) — droits validés 2026-06-26

| Rôle | Droits domotique LAN | Admin / config |
|------|----------------------|----------------|
| `lan_admin` | Pilotage complet (inject, scénarios, dashboard) | CRUD `lan_users`, reset MDP, sync chauffage/admin |
| `lan_user` | Pilotage complet LAN | Profil perso (MDP) uniquement |
| `lan_guest` | **Même pilotage domotique LAN que `lan_user`** (inject, scénarios, dashboard) | Profil perso (MDP) uniquement ; **pas** CRUD users ni routes `/api/admin/lan-users` |

**Différence `lan_user` vs `lan_guest` (v1) :** sémantique provisioning uniquement — l'admin distingue invité vs membre du foyer ; droits HTTP identiques sur le pilotage LAN. Révocation / reset MDP par `lan_admin` sans changer les routes.

Ne pas mapper 1:1 sur `admin_local` / `guest_local` cloud.

### D5 — Bootstrap premier admin

Ordre :

1. **v0** : `POST /api/admin/lan-users/bootstrap` avec token one-shot fichier `/opt/data/config/lan_bootstrap.token` (Ansible).
2. **v1** : intégration wizard **016**.

Register public **désactivé** (`403`).

### D6 — Surface API (v1)

| Méthode | Route | Auth |
|---------|-------|------|
| `POST` | `/api/auth/login` | Public |
| `POST` | `/api/auth/logout` | Session |
| `GET` | `/api/user/me` | Session |
| `PUT` | `/api/user/me/password` | Session |
| `GET` | `/api/admin/lan-users` | `lan_admin` |
| `POST` | `/api/admin/lan-users` | `lan_admin` |
| `POST` | `/api/admin/lan-users/{id}/reset-password` | `lan_admin` |
| `POST` | `/api/admin/lan-users/{id}/disable` | `lan_admin` |
| `POST` | `/api/admin/lan-users/bootstrap` | Token one-shot |

### D7 — Frontend

Pages dans `essensys-server-frontend` :

- `/login` — redirect `/dashboard` si session valide.
- `/settings/account` — changement mot de passe.
- `/settings/users` — admin LAN uniquement.

Garde route React : absence session → `/login`.

### D8 — Dépendances inter-changes

- **013** trusted-devices : refresh session / certificat appareil iPad **après** login LAN stable (TTL 7 j).
- **016** install-wizard : UX création mot de passe installateur.
- **027** admin-user cloud : **aucun lien** direct (bases distinctes).

### D9 — Durée session : **7 jours** (décision produit 2026-06-26)

| Paramètre | Valeur |
|-----------|--------|
| TTL session cookie | **168 h (7 j)** |
| Sliding expiration | Oui — activité API prolonge la session (max 7 j depuis dernière activité) |
| Alignement **013** | Trusted device / iPad mural : refresh session sans re-login pendant 7 j |

Variable config : `lan_session_ttl_hours: 168` dans `config.yaml` gateway.

## Risks / Trade-offs

| Risque | Mitigation |
|--------|------------|
| PG absent → pas d'auth | Health `/health` expose `auth_ready: false` ; fail playbook install |
| SHA1 faible | Nouveaux comptes bcrypt ; migration progressive |
| Régression legacy IoT | Allowlist routes sans session ; tests `test_chb3.py` |
| Session RAM perdue au restart | v1 acceptable ; v2 Redis session store |
| Conflit Traefik basicauth | Doc : désactiver basicauth dashboard si session app |

## Migration Plan

1. Migration SQL : créer table **`lan_users`** (schéma D1) ; table legacy `users` inchangée / non utilisée par IAM v1.
2. Middleware `RequireSession` + `RequireRole(lan_admin)` ; TTL session 168 h.
3. Désactiver capture Basic Auth passif (feature flag `AUTH_PASSIVE_CAPTURE=false`).
4. Déployer backend + frontend.
5. Ansible : générer bootstrap token + mot de passe initial installateur.
6. Rollback : flag `LAN_IAM_ENABLED=false` restore passif (dev only).

## Open Questions

- Audit log local (fichier vs table) pour actions admin ? — **non tranché v1**
