# playwright-e2e

Suite Playwright de non-régression UI domotique — profils **local**, **remote**, **demo**.

## ADDED Requirements

### Requirement: Matrice de cibles Playwright

Le dépôt `essensys-ui-e2e` (ou équivalent) MUST définir au moins trois projects Playwright.

| Project | baseURL par défaut | Auth |
|---------|-------------------|------|
| `demo` | `https://demo.essensys.fr` | aucune |
| `local` | `https://mon.essensys.local` | Basic Auth via env |
| `remote` | `https://mon.essensys.fr/portal` | JWT via env |

#### Scenario: Exécution profil demo en CI

- **WHEN** `npx playwright test --project=demo` s'exécute sur un runner sans armoire
- **THEN** tous les tests demo passent sans credential
- **AND** aucune requête réelle vers `/api/` hors mocks n'est requise pour le vert

#### Scenario: Exécution profil local avec dry-run

- **WHEN** `ESSENSYS_TEST_MODE=dry_run` et credentials Basic sont configurés
- **AND** `npx playwright test --project=local` s'exécute contre une gateway LAN
- **THEN** les tests d'écriture passent avec verdict `test_ok` sans vider la file firmware

### Requirement: Couverture non-régression MVP

La suite MUST couvrir au minimum :

1. Navigation : dashboard + chaque entrée menu principale
2. Scénarios : liste des slots, launch dry-run (local/remote) ou grille visible (demo)
3. Chauffage : interaction mode + verdict test ou UI stable
4. Éclairage : page charge et contrôle principal visible

#### Scenario: Scénarios demo sans erreur JSON

- **WHEN** le test ouvre `/scenarios` sur `demo.essensys.fr`
- **THEN** la liste des scénarios s'affiche sans erreur parse JSON
- **AND** au moins le slot « Je sors » est visible

#### Scenario: Launch dry-run local

- **WHEN** le test clique « Lancer » sur le slot 2 en mode test
- **THEN** l'UI affiche un succès de test
- **AND** une requête réseau vers `launch` contient `test_mode=dry_run` ou header dry-run

### Requirement: Assertion valeurs reçues (local / remote)

Les tests local et remote MUST pouvoir comparer des valeurs exchange **reçues** sans dépendre d'une écriture réelle.

#### Scenario: Lecture exchange après mystatus

- **WHEN** le test appelle l'API exchange pour des clés chauffage connues
- **THEN** les valeurs retournées sont comparées à un fixture `expected` ou tolérance documentée
- **AND** le test échoue avec diff lisible si mismatch

### Requirement: Mode test par défaut en E2E

Les tests Playwright qui déclenchent des écritures MUST activer `ESSENSYS_TEST_MODE=dry_run` par défaut.

#### Scenario: Pas d'écriture accidentelle

- **WHEN** un développeur lance `npx playwright test` sans variable d'environnement
- **THEN** le helper de test force `dry_run` sauf si `ESSENSYS_E2E_ALLOW_LIVE=1` est explicitement défini

### Requirement: Artifacts et rapport

CI MUST publier le rapport HTML Playwright en artifact sur échec.

#### Scenario: Trace sur failure

- **WHEN** un test échoue en CI
- **THEN** screenshot + trace zip sont attachés au job
