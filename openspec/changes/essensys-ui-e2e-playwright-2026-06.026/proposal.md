## Why

Les régressions UI (chauffage, scénarios, éclairage, jumeaux local/portail/démo) ne sont pas couvertes par une suite **E2E navigateur** unique. Les scripts Python existants (`test_chb3.py`, `e2e_scenarios_portal.sh`) injectent de vraies actions vers la **file firmware** — risqué sur une installation réelle (armoire SC944D).

Il faut un **mode test** : valider les payloads et les valeurs **reçues** (table d'échange / API) **sans enqueue** vers l'armoire, puis des tests **Playwright** rejouables sur **local**, **remote** (portail) et **demo** (mock).

> **Roadmap ID:** 2026-06.026  
> **Horizon:** Now → Next (voir [[OpenSpec Queue 2026 06]])  
> **Depend de:** 006 (scénarios stables), parité jumeaux documentée (rules portal-server-frontend-sync)

## What Changes

- **Mode test backend** (`dry_run` / header dédié) sur les écritures : inject, launch scénario, actions web — validation complète, **aucune action en file** vers le firmware.
- **Mode test frontend** : bannière « Mode test », boutons actifs, réponses API interprétées comme verdict `test_ok` / `test_failed` avec détail k/v attendu vs reçu.
- **Suite Playwright** centralisée avec profils **local** | **remote** | **demo** (URLs, auth, mocks).
- **CI** : job optionnel demo (sans armoire) ; job local/remote sur runner avec secrets ou gateway de staging.
- Documentation et rule agent : quand activer le mode test ; ne jamais lancer E2E « write » sans dry-run sur prod client.

## Capabilities

### New Capabilities

- `ui-test-mode` : contrat dry-run, validation k/v, lecture exchange sans effet armoire.
- `playwright-e2e` : matrice local / remote / demo, scénarios non-régression par feature.

## Impact

- `essensys-server-backend` — dry-run inject, scenarios launch/put, web actions ; endpoint rapport test
- `essensys-user-portal-backend` — équivalent `/api/portal/*` en dry-run (hub cloud)
- `essensys-server-frontend`, `essensys-user-portal-frontend` — flag mode test, affichage verdict
- `essensys-ui-e2e/` (nouveau dossier racine monorepo ou sous `essensys-server-frontend/e2e/`) — Playwright
- `essensys-memory` — OpenSpec, wiki, prompts CI
- `demo.essensys.fr` — profil demo (mocks + assertions UI sans backend)

## Non-goals

- Remplacer les tests unitaires Go/React existants.
- Simuler le firmware SC944D en boucle (hors scope — on lit le cache exchange réel en local si armoire connectée).
- Tests charge / perf (k6, etc.).

## Gate

Peut démarrer en **Phase 1 demo + dry-run backend local** sans attendre 015.  
Le profil **remote** avec gateway réel nécessite credentials CI et gateway online (015 recommandé).
