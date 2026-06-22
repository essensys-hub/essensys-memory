# Tasks — essensys-ui-e2e-playwright-2026-06.026

> **Roadmap ID:** 2026-06.026 — **active** (implémentation juin 2026)

## Phase 0 — Spec

- [x] 0.1 Proposal + design + specs
- [x] 0.2 `openspec validate essensys-ui-e2e-playwright-2026-06.026`
- [x] 0.3 Promouvoir **planned → active** dans [[OpenSpec Queue 2026 06]]

## Phase 1 — Mode test backend (local)

- [x] 1.1 Middleware / helper `IsDryRun(r)` — header + query
- [x] 1.2 `PostAdminInject` dry-run : validate params, skip `AddActions`, réponse `test_ok` / `test_failed`
- [x] 1.3 Scénarios `launch` / `put` / `restore` dry-run (server-backend)
- [x] 1.4 `POST /api/web/actions` dry-run
- [x] 1.5 Tests table-driven Go (`handlers_testmode_test.go`)
- [x] 1.6 Doc indices + limites firmware dans spec `ui-test-mode`

## Phase 2 — Mode test portail (jumeau)

- [x] 2.1 Endpoints `/api/portal/*` dry-run (user-portal-backend)
- [x] 2.2 Pas de forward gateway si `test_mode=dry_run`
- [ ] 2.3 Tests + rule `portal-server-backend-sync.mdc`

## Phase 3 — Mode test frontend (jumeaux UI)

- [x] 3.1 Toggle / query `?test=1` + bannière
- [x] 3.2 `legacyApi` / `portalApi` : injecter header dry-run
- [x] 3.3 Affichage verdict `test_ok` / `test_failed` (InjectionSaveConsole, toasts scénarios)
- [x] 3.4 Parité server-frontend ↔ user-portal-frontend
- [x] 3.5 `npm run build` les deux

## Phase 4 — Playwright

- [x] 4.1 Scaffold `essensys-server-frontend/e2e/` — `playwright.config.ts`, deps, README
- [x] 4.2 Profil **demo** : navigation, scénarios, chauffage (mocks)
- [x] 4.3 Profil **local** : auth Basic, dry-run launch scénario + assert `test_ok`
- [ ] 4.4 Profil **remote** : JWT fixture, dry-run portail
- [ ] 4.5 Helper `assertExchangeKeys(page, expected)` — lecture API exchange
- [x] 4.6 Rapport HTML + traces CI artifacts

## Phase 5 — CI & doc

- [x] 5.1 GHA : `playwright test --project=demo` sur PR frontend
- [ ] 5.2 Workflow dispatch local/remote (secrets documentés)
- [x] 5.3 Wiki `essensys-memory` + entrée product roadmap
- [x] 5.4 Rule agent `.cursor/rules/ui-e2e-test-mode.mdc`
- [ ] 5.5 `publish-roadmap-public.sh` si visible utilisateur

## Verification

```bash
cd essensys-memory && openspec validate essensys-ui-e2e-playwright-2026-06.026

curl -s -X POST 'http://127.0.0.1:80/api/admin/inject?test_mode=dry_run' \
  -H 'Content-Type: application/json' \
  -d '{"k":590,"v":"2"}' | jq .

cd essensys-server-frontend/e2e && npm run test:demo
```
