# Tasks — essensys-lan-iam-2026-06.017

> **Roadmap ID:** 2026-06.017 — **active** (implémentation 2026-06-26)

## Phase 0 — Validation (gate)

- [x] 0.1 Revue autocritique D1–D8 avec produit / ops
- [x] 0.2 Confirmer PostgreSQL actif sur CM5 prod (prérequis auth) — PG 17 installé 2026-06-27, rôle `raspberry_postgresql`
- [x] 0.3 **Décision : table `lan_users` dédiée** (pas legacy `users`)
- [x] 0.4 **Décision : `lan_guest` = pilotage LAN identique à `lan_user`**, sans admin users
- [x] 0.5 **Décision : session TTL 7 jours** (168 h, sliding)
- [x] 0.6 Spec + design validés (openspec validate manuel si CLI indispo)

## Phase 1 — Backend auth (`essensys-server-backend`)

- [x] 1.1 Migration SQL : créer table **`lan_users`** (D1)
- [x] 1.2 Middleware `RequireSession` + `RequireRole`
- [x] 1.3 Appliquer middleware sur routes UI ; allowlist legacy IoT
- [x] 1.4 CRUD `/api/admin/lan-users/*` + bootstrap token
- [x] 1.5 `PUT /api/user/me/password` ; invalidation sessions
- [x] 1.6 Session store TTL **168 h** sliding ; config `lan_session_ttl_hours`
- [x] 1.7 Désactiver capture Basic Auth passive si `LAN_IAM_ENABLED`
- [x] 1.8 Hash bcrypt/argon2 pour tout compte natif `lan_users`
- [x] 1.9 Tests unitaires laniam + build router/middleware
- [x] 1.10 `/health` expose `auth_ready`, `lan_iam_enabled`

## Phase 2 — Frontend (`essensys-server-frontend`)

- [x] 2.1 Page `/login` + hook session (`VITE_LAN_IAM=true`)
- [x] 2.2 Garde routes : redirect `/login` si non authentifié
- [x] 2.3 Page `/settings/account` (changement mot de passe)
- [x] 2.4 Page `/settings/users` (admin LAN)
- [x] 2.5 Retirer reload Basic Auth navigateur sur 401 (mode LAN IAM)

## Phase 3 — Deploy & bootstrap (`essensys-ansible`)

- [x] 3.1 Tâche génération token bootstrap + block config `lan_iam` (`lan_iam.yml`)
- [x] 3.2 Doc install : premier login `lan_admin`, rotation mot de passe
- [x] 3.3 Vérifier profil Traefik : pas de double basicauth dashboard
- [x] 3.4 Rôle `raspberry_postgresql` + migrations auto + dedupe config YAML
- [x] 3.5 Vars monitoring/nginx/traefik dans `update.raspberrypi.yml` ; build frontend `VITE_LAN_IAM` si LAN IAM

## Phase 4 — Intégration changes liés

- [x] 4.1 Aligner spec avec **016** install-wizard (UX bootstrap)
- [x] 4.2 Préparer hook **013** trusted-devices (TTL session 7j documenté)

## Phase 5 — Brain & doc

- [x] 5.1 Wiki concept `lan-iam.md` + MAJ [[Essensys Server Backend]]
- [x] 5.2 Entrée `wiki/log.md`

## Verification

```bash
cd essensys-memory && openspec validate essensys-lan-iam-2026-06.017
cd essensys-server-backend && go test ./internal/laniam/... && go build ./cmd/server
cd essensys-server-frontend && VITE_LAN_IAM=true npm run build
# Gateway CM5 (LAN IAM) :
ansible-playbook -i inventory.gateway update.raspberrypi.yml -e lan_iam_enabled=true
# Migration 003 incluse dans le rôle backend si PG actif
```

## Definition of Done

- [x] Bootstrap `lan_admin` via Ansible sur CM5 vierge (2026-06-27 — admin@essensys.local)
- [x] Login/logout UI sur `mon.essensys.local` (build `VITE_LAN_IAM=true` sur CM5)
- [ ] CRUD users admin fonctionnel (API OK ; UI admin 2.4 livrée — validation prod pending)
- [x] Legacy `/api/mystatus` vert sans session (router allowlist)
- [ ] Security gate vert sur backend + frontend après merge
- [x] Autocritique + décisions produit archivées dans le change
