---
tags: [concept, cloud, api, gateway, sync]
sources: [essensys-server-backend.md, essensys-user-portal-backend.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
---

# Gateway Exchange

Protocole de synchronisation **passerelle ↔ hub cloud** pour état domotique et actions distantes.

## Endpoints (hub cloud)

| Route | Sens | Rôle |
|-------|------|------|
| `GET /api/gateway/pending-actions` | Gateway → Cloud | Récupérer actions en attente |
| `POST /api/gateway/exchange` | Gateway → Cloud | Pousser état table d'échange / télémétrie |
| `GET /api/gateway/sync-config` | Gateway → Cloud | Profils sync + runs `pending` |
| `POST /api/gateway/sync-runs` | Gateway → Cloud | Créer un run planifié |
| `POST /api/gateway/sync-runs/{id}/start` | Gateway → Cloud | Marquer run `running` |
| `POST /api/gateway/sync-runs/{id}/progress` | Gateway → Cloud | Progression pull/push |

Admin OVH : `GET/POST /api/admin/sync-profiles`, `POST …/{id}/run` (UI **Sync Cloud** support-site).

## Endpoints (gateway LAN)

| Route | Rôle |
|-------|------|
| `POST /api/admin/heating/sync` | Pull manuel planning (rotation serverinfos ≤30) |
| `GET /api/admin/heating/sync/status` | Progression pull manuel |
| `GET /api/admin/cloudsync/status` | État scheduler cloud (read-only, juin 2026) |
| `GET/PUT /api/admin/scenarios/sync` | Toggle profil sync **Scénarios** (juin 2026) |
| `GET/PUT/POST /api/scenarios/*` | CRUD + lancement scénarios LAN (juin 2026) |

## Scheduler planifié (juin 2026)

Change OpenSpec **essensys-cloud-sync-scheduler** :

1. Profils PostgreSQL (`sync_profiles`, `sync_runs`) — seed 6 plages chauffage/volets + **Scénarios 591–919** (migration 009), **intervalle 3 h** par défaut.
2. Agent `internal/cloudsync/` sur CM5 : poll `sync-config`, exécute runs `pending` + profils dus.
3. Pipeline par profil : `ExchangePullScheduler` (pull armoire) → Redis → `POST /api/gateway/exchange` (merge cloud).
4. Mutex : un seul pull armoire à la fois (manuel ou planifié).
5. Config gateway : `cloud.scheduled_sync_enabled` (défaut `true`).

Option v1.1 : `cron_expression` sur profil (ex. `0 */3 * * *`) à la place de `interval_hours`.

## Données échangées

- Snapshot indices [[Table D Echange]] (k/v)
- Temps de course volets (566–589) — commit 2026-06-11 backend
- Planning chauffage 13–348 par zones (profils seed)
- **Scénarios 591–919** (profil Scénarios ; trigger 590 exclu du push)
- Identité gateway : MAC + token (poll OVH hub)

## Relation [[Cloud Relay]]

[[Cloud Relay]] décrit le **cas d'usage** utilisateur ; Gateway Exchange décrit le **contrat API** technique.

## Déploiement

- TLS terminé en amont ([[Essensys Traefik]], nginx WAN)
- Agent HTTPS sortant sur eth0 ([[Essensys Raspberry Gateway]] dual-NIC)
- Ansible : `cloud_sync_enabled`, `cloud_scheduled_sync_enabled`, vault `cloud_gateway_token`

## OpenSpec

- `essensys-memory/openspec/changes/essensys-cloud-sync-scheduler/` (actif, juin 2026)
- Changes antérieurs : `gateway-exchange-push`, `gateway-rules-unified`
