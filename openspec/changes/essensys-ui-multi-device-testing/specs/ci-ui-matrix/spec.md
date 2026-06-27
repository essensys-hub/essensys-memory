# ci-ui-matrix

Intégration continue GitHub Actions pour la matrice UI multi-device.

## ADDED Requirements

### Requirement: Workflow ui-matrix sur PR

Un workflow `.github/workflows/ui-matrix.yml` MUST s'exécuter sur PR touchant `src/` ou `e2e/` et lancer au minimum **demo + support × 5 devices**.

#### Scenario: PR frontend déclenche la matrice

- **WHEN** une PR modifie `essensys-server-frontend/src/`
- **THEN** le workflow ui-matrix démarre automatiquement
- **AND** les projects demo/support sur 5 devices sont exécutés

#### Scenario: PR sans changement UI

- **WHEN** une PR ne touche que la documentation backend
- **THEN** le workflow MAY être ignoré via path filter
- **AND** aucun faux négatif n'est imposé

### Requirement: Local et remote en jobs manuels ou nightly

Les cibles `local-*` et `remote-*` MUST NOT bloquer chaque push ; elles MUST être disponibles via `workflow_dispatch` et/ou cron nightly, avec secrets staging.

#### Scenario: Dispatch local avec secrets

- **WHEN** un opérateur lance `workflow_dispatch` avec secrets `ESSENSYS_BASIC_*` configurés
- **THEN** les projects local-* s'exécutent contre l'URL staging documentée
- **AND** la couche no-armoire reste active

### Requirement: Artefacts CI

Le workflow MUST publier en artefact :

- Rapport HTML Playwright
- Traces et screenshots on failure
- Diff snapshots en cas d'échec visuel

#### Scenario: Artefact sur échec

- **WHEN** un test échoue en CI
- **THEN** le job upload un artefact `playwright-report`
- **AND** les traces zip sont disponibles au téléchargement

### Requirement: Échec CI si garde réseau déclenchée

Si la fixture no-armoire bloque un appel, la CI MUST échouer — ce comportement est attendu et MUST NOT être contourné.

#### Scenario: Blocage inject compte comme échec test

- **WHEN** un test déclenche la fixture couche 2
- **THEN** le job CI est rouge
- **AND** le log contient le message `BLOQUÉ`

### Requirement: Aucune dépendance SaaS propriétaire obligatoire

La CI MUST tourner avec Playwright headless open-source uniquement ; BrowserStack/Sauce Labs/Percy MUST NOT être requis.

#### Scenario: Runner GitHub standard

- **WHEN** ui-matrix s'exécute sur `ubuntu-latest`
- **THEN** `npx playwright install --with-deps` suffit
- **AND** aucune clé API SaaS n'est nécessaire pour le vert PR
