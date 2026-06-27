# device-matrix

Matrice Playwright **cible × device** pour les frontends Essensys.

## ADDED Requirements

### Requirement: Cinq profils device standard

La configuration Playwright MUST définir cinq profils device réutilisables :

| ID | Source Playwright | Navigateur |
|----|-------------------|------------|
| `desktop` | `Desktop Chrome` | Chromium |
| `iphone` | `iPhone 14` | WebKit |
| `android` | `Pixel 7` | Chromium |
| `ipad` | `iPad (gen 7)` landscape | WebKit |
| `ecran-domo` | device custom (voir `ecran-domotique-viewport`) | Chromium |

#### Scenario: Projet iphone utilise WebKit

- **WHEN** un test s'exécute sous le project `demo-iphone`
- **THEN** le navigateur lancé est WebKit avec le user-agent iPhone 14
- **AND** le viewport correspond au preset Playwright `iPhone 14`

#### Scenario: Projet desktop utilise viewport 1280×720 minimum

- **WHEN** un test s'exécute sous un project `*-desktop`
- **THEN** le viewport est au minimum 1280×720
- **AND** `isMobile` est false

### Requirement: Quatre cibles de déploiement

La matrice MUST couvrir quatre cibles :

| Cible | baseURL type | Mode anti-armoire |
|-------|--------------|-------------------|
| `support` | mon.essensys.fr (site support) | mock réseau Playwright |
| `local` | mon.essensys.local ou demo local | `VITE_DEMO_MODE` ou header dry-run |
| `remote` | mon.essensys.fr/portal/ | `?test_mode=dry_run` + header |
| _(cm5/rpi)_ | identique `local` | documenté — même build, hardware différent |

#### Scenario: Project remote pointe vers le portail

- **WHEN** le project `remote-desktop` est configuré sans override env
- **THEN** `baseURL` se termine par `/portal/` ou équivalent documenté
- **AND** les headers incluent `X-Essensys-Test-Mode: dry-run`

#### Scenario: Project support mock les API

- **WHEN** le project `support-desktop` exécute un test
- **THEN** les appels `/api/**` sont interceptés par mock ou stub réseau
- **AND** aucune requête n'atteint un backend non contrôlé sans opt-in explicite

### Requirement: Nommage projects `{cible}-{device}`

Chaque combinaison utile MUST être un project Playwright nommé `{cible}-{device}` (ex. `demo-iphone`, `support-ecran-domo`).

#### Scenario: Liste projects générée

- **WHEN** `npx playwright test --list` est exécuté depuis `e2e/`
- **THEN** au minimum 15 projects sont listés (3 cibles MVP × 5 devices)
- **AND** chaque nom respecte le pattern `{cible}-{device}`

### Requirement: Scripts npm documentés

Le package e2e MUST exposer :

- `test:matrix` — matrice demo complète
- `test:support`, `test:local`, `test:remote` — filtre par cible
- `test:device <name>` — filtre par device
- `test:update-snapshots` — mise à jour baseline visuelle

#### Scenario: Commande matrix demo sans backend armoire

- **WHEN** un développeur exécute `npm run test:matrix` sans variables secrets
- **THEN** seuls les projects demo/support mockés s'exécutent par défaut
- **AND** la commande se termine sans credential gateway client
