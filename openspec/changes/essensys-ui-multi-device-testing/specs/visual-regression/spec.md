# visual-regression

Régression visuelle Playwright par device — détection troncature et débordement.

## ADDED Requirements

### Requirement: Snapshots par project device

Les specs critiques MUST utiliser `toHaveScreenshot()` avec baseline versionnée par combinaison project + OS (suffix Playwright natif).

#### Scenario: Baseline shutters desktop

- **WHEN** la spec volets capture un snapshot sur `demo-desktop`
- **THEN** un fichier baseline existe sous `*-snapshots/` avec le suffix device
- **AND** un changement CSS provoquant débordement horizontal fait échouer le test

#### Scenario: Détection troncature 800×480

- **WHEN** un composant déborde sur `demo-ecran-domo-compact` (800×480)
- **THEN** le snapshot diff ou assertion layout échoue en CI
- **AND** le rapport HTML Playwright affiche le diff visuel

### Requirement: Seuils de comparaison documentés

La configuration MUST définir `maxDiffPixelRatio` (défaut ≤ 0.01) et `threshold` par type de page ; animations désactivées ou stabilisées en mode test.

#### Scenario: Animation Aurora stabilisée

- **WHEN** un snapshot capture la page login Aurora
- **THEN** les éléments animés n'introduisent pas de flaky diff (reduced-motion ou délai `waitForLoadState`)
- **AND** deux exécutions consécutives produisent un diff nul

### Requirement: Mise à jour baseline contrôlée

La commande `npm run test:update-snapshots` MUST exister ; toute mise à jour baseline MUST être revue en PR avec diff visuel attaché.

#### Scenario: Update snapshots local

- **WHEN** un développeur exécute `npm run test:update-snapshots -- --project=demo-iphone`
- **THEN** seuls les snapshots du project ciblé sont régénérés
- **AND** les fichiers modifiés sont listés pour revue git

### Requirement: Option Lost Pixel non bloquante

Lost Pixel (MIT) MAY être proposé en documentation comme outil complémentaire de revue ; il MUST NOT être une dépendance obligatoire de la CI MVP.

#### Scenario: CI sans Lost Pixel

- **WHEN** la CI ui-matrix s'exécute
- **THEN** seul Playwright natif est requis pour les snapshots
- **AND** l'absence de Lost Pixel n'empêche pas le vert

### Requirement: Autocritique visuelle support avant baseline

Les captures générées pour `support-desktop`, `support-iphone`, `support-ipad` et `support-ecran-domo` MUST être revues avant clôture visuelle. Les défauts visibles suivants MUST être corrigés avant de figer les baselines : navigation basse qui masque le contenu, focus/ring appliqué à plusieurs cartes, état caméra démo ambigu, débordement horizontal ou dernier contrôle inaccessible.

#### Scenario: Bottom navigation ne masque pas le dashboard mobile

- **WHEN** `ui-smoke.spec.ts` capture `/dashboard` sur `support-iphone`
- **THEN** le dernier contenu du dashboard reste atteignable par scroll
- **AND** la `BottomTabs` ne recouvre pas une carte ou un bouton interactif en fin de page

#### Scenario: Focus ring tablette limité à l'élément focus

- **WHEN** `ui-smoke.spec.ts` capture `/dashboard` sur `support-ipad`
- **THEN** les cartes dashboard n'affichent pas toutes un contour focus bleu simultané
- **AND** un élément navigué au clavier conserve un focus visible discret

#### Scenario: État caméra démo explicite

- **WHEN** une caméra mock/support n'a pas de flux image disponible
- **THEN** le placeholder indique que le flux est indisponible ou désactivé en mode démo
- **AND** le libellé ne laisse pas croire à une panne armoire réelle
