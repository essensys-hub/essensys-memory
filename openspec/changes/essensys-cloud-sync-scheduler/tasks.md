# Tasks — essensys-cloud-sync-scheduler

## Phase 1 — Modèle & API cloud

- [x] 1.1 Migration PostgreSQL `sync_profiles`, `sync_runs` + seed profils défaut (intervalle 3 h)
- [x] 1.2 Handlers admin CRUD `/api/admin/sync-profiles` (`essensys-user-portal-backend`)
- [x] 1.3 `GET /api/gateway/sync-config` + `POST /api/gateway/sync-runs/{id}/progress` (gateway auth)
- [x] 1.4 `POST /api/admin/sync-profiles/{id}/run` — enqueue run vers gateway
- [x] 1.5 Tests unitaires validation plages et chunks ≤ 30

## Phase 2 — Scheduler gateway

- [x] 2.1 Généraliser `HeatingSyncManager` → `ExchangePullScheduler` (`internal/core/`)
- [x] 2.2 Intégrer scheduler dans `cloudsync` : ticker profils, mutex pull exclusif
- [x] 2.3 Pull planifié → push profil (remplacer / compléter `exchangePushIndices()` hardcodé)
- [x] 2.4 Feature flag `scheduled_sync_enabled` + fallback legacy
- [x] 2.5 Tests intégration pilote : SDB1 181–264, 84/84 (CM5 2026-06-20)

## Phase 3 — UI Admin Sync Cloud

- [x] 3.1 Onglet **Sync Cloud** dans `essensys-support-site/site/src/pages/Admin.jsx`
- [x] 3.2 Page `SyncCloud.jsx` : liste, filtre gateway, formulaire plages + intervalle
- [x] 3.3 Bouton **Sync now** + polling statut run
- [x] 3.4 Console logs (dernier run)
- [x] 3.5 i18n FR labels admin

## Phase 4 — Déploiement & doc

- [x] 4.1 Variables Ansible : profils seed, `scheduled_sync_enabled`
- [x] 4.2 Déployer OVH + gateway pilote (192.168.0.14)
- [x] 4.3 Vérifier portail `/portal/heating` SDB1 après run planifié (pilote)
- [x] 4.4 Mettre à jour `essensys-memory` : [[Gateway Exchange]], roadmap index, `wiki/roadmap/changes/essensys-cloud-sync-scheduler.md`
- [x] 4.5 Entrée `essensys-raspberry-gateway/docs/versions.md`

## Phase 5 — Jumeaux & polish (optionnel v1.1)

- [x] 5.1 Endpoint read-only sync status sur LAN admin (`GET /api/admin/cloudsync/status`)
- [x] 5.2 Alerting New Relic / log `[sync-alert]` si `partial|failed` 3 fois consécutives
- [x] 5.3 Expression cron optionnelle (`cron_expression` migration 008)

## Verification

```bash
# Cloud
curl -sS -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://mon.essensys.fr/api/admin/sync-profiles | jq .

# Gateway LAN status
curl -sS http://127.0.0.1:7070/api/admin/cloudsync/status | jq .

# Gateway (après deploy)
curl -sS -X POST http://127.0.0.1:7070/api/admin/heating/sync \
  -H 'Content-Type: application/json' \
  -d '{"startIndex":181,"byteCount":84}'

# Scheduler manuel (après Phase 2)
curl -sS -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://mon.essensys.fr/api/admin/sync-profiles/{id}/run

# Portail
curl -sS -H "Authorization: Bearer $USER_TOKEN" \
  "https://mon.essensys.fr/api/portal/exchange?keys=181,182,183" | jq .
```

Expected: profils visibles admin ; après run planifié ou manuel, indices 181–264 présents côté cloud ; UI portail chauffage SDB1 = OFF si armoire OFF.

## Dépendances

- Change existant (implémenté partiellement) : pull manuel chauffage `HeatingSyncManager` — **essensys-server-backend**
- Merge cloud : `UpsertGatewayExchange` — **essensys-user-portal-backend** (`39a7dff`)

## Non régression legacy

- [x] Vérifier cycle armoire : `serverinfos → mystatus → myactions → done` hors fenêtre pull
- [x] Ne pas modifier signatures `/api/mystatus`, `/api/myactions`, `/api/done`
