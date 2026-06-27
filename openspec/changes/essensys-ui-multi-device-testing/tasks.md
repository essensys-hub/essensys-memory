# Tasks — essensys-ui-multi-device-testing

> **Roadmap ID:** 2026-06.029
> **Source prompt:** `prompts/ui-multi-device-testing.md`
> **Depend de:** change **026** (`essensys-ui-e2e-playwright`) — dry-run, mockFetch, scaffold Playwright

## Phase 0 — Prérequis & résolutions écran domotique

- [ ] 0.1 Valider que `VITE_DEMO_MODE` + `mockFetch` neutralisent 100 % des inject (grep réseau = 0 POST live en demo)
- [ ] 0.2 Valider dry-run backend/portail (026) : `POST .../inject?test_mode=dry_run` → `{ dry_run: true }`
- [ ] 0.3 Inventorier résolutions dalles domotique parc installé (800×480, 1024×600, 1280×800…) → wiki brain
- [x] 0.4 `openspec validate essensys-ui-multi-device-testing`
- [x] 0.5 Promouvoir **planned → active** dans [[OpenSpec Queue 2026 06]]

## Phase 1 — Devices custom + matrice Playwright

- [x] 1.1 Créer `e2e/devices/ecran-domotique.ts` (landscape, portrait, compact)
- [x] 1.2 Refactor `playwright.config.ts` — génération projects `{cible}-{device}` (support, local, remote × 5 devices)
- [x] 1.3 Variables env documentées : `ESSENSYS_DEMO_URL`, `ESSENSYS_LOCAL_URL`, `ESSENSYS_PORTAL_URL`, `ESSENSYS_SUPPORT_URL`
- [x] 1.4 Scripts npm : `test:matrix`, `test:support`, `test:local`, `test:remote`, `test:device`
- [x] 1.5 README e2e — matrice, durées estimées, prérequis

## Phase 2 — Garde réseau no-armoire

- [x] 2.1 Fixture `e2e/fixtures/no-armoire.ts` — route `**/api/**`, patterns mutants
- [x] 2.2 Extension globale via `test.extend` ou setup project — appliquée à TOUS les projects
- [x] 2.3 Spec négative `no-armoire.spec.ts` — prouve qu'un inject live est bloqué
- [x] 2.4 Garde env : refus URL prod client sans `ESSENSYS_ALLOW_LIVE_READONLY=1`
- [x] 2.5 Documenter interdiction armoire client dans README + rule agent

## Phase 3 — Page Objects + spec de référence (volets)

- [x] 3.1 Scaffold `e2e/pages/` — helpers `getTargetFromProject`, `getDeviceFromProject`
- [x] 3.2 Page Object `ShuttersPage` (jumeaux local/remote)
- [x] 3.3 Spec `shutters.spec.ts` — 5 devices × demo, assertions layout + dry-run
- [x] 3.4 Vérifier responsive : sidebar ≥1024px, drawer/tabs <1024px
- [ ] 3.5 Vert local : `npm run test:matrix` (demo only) sans credential

## Phase 4 — Specs features restantes

- [ ] 4.1 Dashboard + navigation menu
- [ ] 4.2 Lighting, Heating, Scenarios, Security
- [ ] 4.3 Sprinkler, WaterHeater, Notifications, UniFiProtect, Settings
- [ ] 4.4 Parité : même spec sur projects `local-*` et `remote-*` (jumeaux)
- [ ] 4.5 Support-site : Login, Admin, Profile, UserManager, Catalog (mock réseau)

## Phase 5 — Snapshots visuels

- [x] 5.1 Config `toHaveScreenshot` — seuils, reduced-motion
- [ ] 5.2 Baseline volets + dashboard par device (demo)
- [x] 5.3 Script `test:update-snapshots` + doc revue PR diff visuel
- [x] 5.4 Détection débordement 800×480 / 1024×600 (ecran-domo)
- [x] 5.5 Autocritique captures support : corriger bottom nav iPhone, focus iPad, état caméra démo, densité écran domo

## Phase 6 — CI GitHub Actions

- [ ] 6.1 Workflow `.github/workflows/ui-matrix.yml` — PR path filter `src/`, `e2e/`
- [ ] 6.2 Job matrix : demo + support × 5 devices (parallèle)
- [ ] 6.3 Artefacts : rapport HTML, traces, snapshot diffs
- [ ] 6.4 `workflow_dispatch` + nightly : local/remote staging (secrets)
- [ ] 6.5 Mesurer durée CI ; sharding par device si >20 min

## Phase 7 — Brain, doc & clôture

- [x] 7.1 Wiki `essensys-memory` — page matrice UI multi-device
- [x] 7.2 Rule agent `.cursor/rules/ui-multi-device-testing.mdc`
- [x] 7.3 Lier change **026** et **029** dans roadmap queue
- [x] 7.4 `publish-roadmap-public.sh` si visible utilisateur
- [ ] 7.5 Critères d'acceptation §8 prompt — checklist DoD

## Verification

```bash
cd essensys-memory && openspec validate essensys-ui-multi-device-testing

cd essensys-server-frontend/e2e
npm run test:matrix          # demo × 5 devices
npm run test:device iphone   # filtre device
npx playwright test no-armoire.spec.ts  # doit prouver le blocage inject live
```

## Definition of Done (prompt §8)

- [x] Commande unique matrice demo sans backend armoire
- [x] Fixture §3.2 bloque inject live (test négatif vert)
- [x] 5 devices : iPhone WebKit, Android Chromium, iPad, écran domo, desktop
- [ ] 4 cibles câblées (support, local CM5/RPI, remote)
- [x] Specs partagées par feature (pas de duplication par device)
- [x] Snapshots par device ; débordement 800×480 détecté
- [ ] CI PR demo/support verte + artefacts
- [x] Stack 100 % open-source
- [ ] Jumeaux server-frontend + user-portal-frontend couverts
