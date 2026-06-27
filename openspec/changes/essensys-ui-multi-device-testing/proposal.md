## Why

Les frontends Essensys (support, local CM5/Raspberry, remote portail) sont des **jumeaux React** déployés sur des surfaces très différentes — iPhone, Android, iPad, écran domotique tactile, desktop. Aujourd'hui, Playwright ne couvre que **Desktop Chrome** sur 3 cibles (`demo` / `local` / `remote`) dans `essensys-server-frontend/e2e/`, sans matrice device ni couverture du support-site.

Les régressions d'affichage (menu tronqué à 800×480, `BottomTabs` cassé, hero illisible) ne sont pas détectées avant prod. Pire : un test mal conçu pourrait **envoyer une action réelle à l'armoire SC944D** — inacceptable.

Ce change étend le socle **2026-06.026** (`essensys-ui-e2e-playwright`) avec une **matrice open-source device × cible × feature**, garantie **zéro action armoire** en trois couches, et CI GitHub Actions.

> **Roadmap ID:** 2026-06.029
> **Horizon:** Now → Next
> **Depend de:** [[OpenSpec Queue 2026 06]] **026** (dry-run, mockFetch, Playwright scaffold), parité jumeaux (`portal-server-frontend-sync`)

## What Changes

- **Matrice Playwright** : 5 devices (`desktop`, `iphone`, `android`, `ipad`, `ecran-domo`) × 4 cibles (`support`, `local-cm5`, `local-rpi`, `remote`) — CM5 et Raspberry partagent le même build local.
- **Garde réseau `no-armoire`** : fixture globale qui **échoue** tout appel mutant non `dry-run` / non mocké (inject, web/actions, launch scénario).
- **Specs partagées par feature** + Page Objects communs jumeaux `server-frontend` / `user-portal-frontend`.
- **Snapshots visuels** Playwright par device (détection troncature / débordement).
- **CI `ui-matrix.yml`** : demo/support × 5 devices sur PR ; local/remote read-only en `workflow_dispatch` / nightly.
- **Support-site** : premiers e2e back-office (`Login`, `Admin`, …) avec mock réseau.
- **Device custom « écran domotique »** : viewports tactiles paramétrables (1024×600, 800×480, portrait).

**Contrainte absolue :** aucun test ne MUST piloter l'armoire réelle. Un inject live est un **échec de conception**.

## Capabilities

### New Capabilities

- `device-matrix` : configuration Playwright cible × device, scripts npm, variables d'environnement.
- `no-armoire-guard` : trois couches anti-armoire (mode neutralisé, route Playwright, interdiction env prod client).
- `shared-feature-specs` : specs paramétrées par feature + Page Objects jumeaux.
- `visual-regression` : snapshots par device, seuils, workflow de mise à jour baseline.
- `ci-ui-matrix` : workflow GitHub Actions, artefacts HTML, secrets staging.
- `ecran-domotique-viewport` : devices custom tactiles, résolutions multiples portrait/paysage.

### Modified Capabilities

- _(aucune spec archivée dans `openspec/specs/` — extension documentée par référence au change **026** `playwright-e2e` et `ui-test-mode`)_

## Impact

| Composant | Changement |
|-----------|------------|
| `essensys-server-frontend/e2e/` | Matrice étendue, fixtures, specs, snapshots (source unique) |
| `essensys-user-portal-frontend` | Consommé via projects `remote-*` (même UI, baseURL `/portal/`) |
| `essensys-support-site/site` | Projects `support-*`, mock réseau API |
| `.github/workflows/` | `ui-matrix.yml` (server-frontend + éventuellement repo brain) |
| `essensys-memory` | OpenSpec, wiki, prompt `ui-multi-device-testing.md` |
| Backends | **Aucune modification protocole** — réutilisation dry-run (026) et demo mocks |

## Non-goals

- SaaS propriétaire obligatoire (BrowserStack, Sauce Labs, Percy).
- Tests charge / perf (k6).
- Simulation firmware SC944D en boucle.
- Remplacement des tests unitaires Go/React ou scripts Python legacy.

## Gate

Peut démarrer **Phase 0–3** (demo + garde réseau) sans gateway client.
Profils `local-*` / `remote-*` contre staging nécessitent secrets CI et **026** dry-run validé.
