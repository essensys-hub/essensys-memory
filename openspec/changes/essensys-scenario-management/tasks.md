# Tasks — essensys-scenario-management

## Phase 0 — Audit protocole

- [x] 0.1 Croiser `TableEchange.h`, `Scenario.c`, `global.h` (099-37) vs doc raw et essensys-doc
- [x] 0.2 Produire tableau d'écarts dans `openspec/changes/essensys-scenario-management/audit-protocol.md`
- [x] 0.3 Corriger `essensys-memory/raw/protocol/exchange-table.md` (base 592, 590=1..8, slots 633+)
- [x] 0.4 Valider map bitmasks via `table_reference.json` (HA) — indices 605–622 confirmés

## Phase 1 — Domain backend

- [x] 1.1 Package `internal/scenario/` dans `essensys-server-backend` (LaunchParams, SlotBaseIndex, ValidateDefinition)
- [x] 1.2 `ExpandModeB` (592–632 option full) + tests table-driven
- [x] 1.3 Batch inject writer (2 actions × 30 params max) pour écriture slot
- [x] 1.4 Miroir domain dans `essensys-user-portal-backend/internal/domain/scenario/`
- [x] 1.5 Tests non-régression `test_chb3.py` et Mode A launch 590=2

## Phase 2 — API

- [x] 2.1 Handlers LAN `GET/PUT/POST /api/scenarios/*` (`essensys-server-backend`)
- [x] 2.2 Handlers portail `GET/PUT/POST /api/portal/scenarios/*` (`essensys-user-portal-backend`)
- [x] 2.3 `GET /api/scenarios/meta/bitmasks` (+ portail)
- [x] 2.4 Auth : basic auth LAN (clientID) ; portail link approuvé
- [ ] 2.5 Migration PG `scenario_definitions` (optionnel — cache exchange pour MVP)

## Phase 3 — UI dashboard

- [x] 3.1 Page `/scenarios` dans `essensys-server-frontend`
- [x] 3.2 Parité `essensys-user-portal-frontend` (route `/portal/scenarios`)
- [x] 3.3 Composants partagés : `ScenarioButtonGrid`, `ScenarioEditorDrawer`, hook `useScenarios`
- [x] 3.4 Indicateur dernier lancé (591) ; offline gateway portail

## Phase 4 — UI éditeur

- [x] 4.1 `ScenarioEditorDrawer` onglets Lumières/volets + Avancé
- [x] 4.2 Save, Restore preset, Launch now
- [x] 4.3 Slot 1 non éditable (API) ; édition slots 2–8
- [x] 4.4 Parité jumeaux frontends

## Phase 5 — Sync cloud

- [x] 5.1 Migration seed profil **Scénarios** [[591,919]] + `exclude_indices: [590]`
- [x] 5.2 Extension `pushExchange` / pull scheduler pour plage scénarios
- [x] 5.3 Toggle Settings « Synchroniser les scénarios » (`SyncSettingsPanel`)
- [x] 5.4 Merge pull → cache exchange portail (MVP ; `scenario_definitions` PG différé)

## Phase 6 — E2E & déploiement

- [x] 6.1 Pilote CM5 : script `test_scenarios_e2e.sh` (Je sors, Perso 1, sync admin)
- [x] 6.2 Déploiement OVH : migration 009 + `test_scenarios_cloud_parity.sh` + doc `maintenance/scenarios.md`
- [x] 6.3 Ansible : `scenarios_sync_enabled` (defaults cloud_sync + cloud_backend)

## Phase 7 — Documentation

- [x] 7.1 `wiki/concepts/scenarios-domotique.md`
- [x] 7.2 `wiki/roadmap/changes/essensys-scenario-management.md` (via update-roadmap.sh)
- [x] 7.3 `essensys-raspberry-gateway/docs/versions.md` (V.1.4.0)
- [x] 7.4 `scripts/sync-sources.sh` + update roadmap index

## Verification

```bash
# Audit / backend
cd essensys-server-backend && go test ./internal/scenario/... ./internal/core/...

# Mode A — Je sors
curl -sS -X POST http://localhost/api/scenarios/2/launch

# Mode B — lumière (non régression)
./test/test_chb3.py

# API liste
curl -sS http://localhost/api/scenarios | jq .

# OpenSpec
cd essensys-memory && openspec validate essensys-scenario-management
openspec status --change essensys-scenario-management
```
