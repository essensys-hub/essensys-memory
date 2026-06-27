# ecran-domotique-viewport

Devices Playwright custom pour écrans tactiles muraux domotique.

## ADDED Requirements

### Requirement: Device custom avec touch et mobile

Le fichier `e2e/devices/ecran-domotique.ts` MUST exporter au moins un device Playwright avec :

- `hasTouch: true`
- `isMobile: true`
- `defaultBrowserType: 'chromium'`

#### Scenario: Device enregistré dans config

- **WHEN** `playwright.config.ts` importe `ecranDomotiqueLandscape`
- **THEN** le project `demo-ecran-domo` utilise ce preset
- **AND** les événements touch sont disponibles via Playwright

### Requirement: Plusieurs résolutions paramétrables

La matrice MUST supporter une **liste** de profils, pas une résolution unique :

| Profil | Viewport | Orientation |
|--------|----------|-------------|
| landscape | 1024×600 | paysage |
| portrait | 600×1024 | portrait |
| compact | 800×480 | paysage |

#### Scenario: Compact 800×480

- **WHEN** un test s'exécute sur `demo-ecran-domo-compact`
- **THEN** le viewport est 800×480
- **AND** les specs layout vérifient l'absence de scroll horizontal sur la page volets

#### Scenario: Landscape par défaut

- **WHEN** le project s'appelle `*-ecran-domo` sans suffix
- **THEN** le profil landscape 1024×600 est utilisé par défaut

### Requirement: Confirmation résolutions réelles Phase 0

Avant baseline snapshots, les résolutions MUST être validées contre le parc installé (CM5 / Raspberry / dalles client) et documentées dans le wiki brain.

#### Scenario: Mise à jour liste viewports

- **WHEN** une résolution client 1280×800 est confirmée en Phase 0
- **THEN** un profil `ecran-domo-wide` MAY être ajouté à la liste
- **AND** tasks.md Phase 0 est cochée avec la référence wiki

### Requirement: Safe-area et viewport dynamique

Les devices domotique MUST utiliser `100dvh` friendly tests — les specs MUST vérifier que les contrôles bas de page ne sont pas masqués sur viewport bas (600px height).

#### Scenario: Bottom tabs visibles écran domo

- **WHEN** la navigation mobile est active sur écran domo portrait
- **THEN** les `BottomTabs` restent visibles sans être coupés
- **AND** le dernier contrôle de page est atteignable par scroll ou tap
