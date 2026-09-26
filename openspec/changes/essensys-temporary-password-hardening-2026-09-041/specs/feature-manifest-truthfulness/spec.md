## Purpose

Un `features/<id>.json` est déclaré « source de vérité » par `AGENTS.md`. Cette capacité exige que ses affirmations vérifiables le soient effectivement, à commencer par celles de `essensys-temporary-password-2026-09-040`, dont le gate a validé des valeurs qui ne correspondaient à rien.

## ADDED Requirements

### Requirement: Projets requis existants

Tout manifest déclarant `tests.ux_matrix.required_projects` SHALL n'y nommer que des projets définis dans le `playwright.config.js` du dépôt.

#### Scenario: Correspondance exacte

- **WHEN** le manifest déclare un projet requis
- **THEN** un projet de ce nom exact existe dans la configuration Playwright

#### Scenario: Captures nommées par projet

- **WHEN** une capture d'écran de preuve UX est produite
- **THEN** son nom de fichier porte le nom du projet Playwright qui l'a produite

### Requirement: Couverture déclarée effective

Tout manifest déclarant `tests.coverage_must_test` SHALL n'y lister que des exigences pour lesquelles un test nommé à l'identique existe.

#### Scenario: Titre de test aligné

- **WHEN** le manifest liste une exigence de couverture
- **THEN** un test dont le titre est exactement cette chaîne existe dans les fichiers de test déclarés

#### Scenario: Gate sans avertissement

- **WHEN** `check_feature_gate.py --strict` s'exécute sur le manifest
- **THEN** aucun avertissement « Coverage requirement not matched by any test title » n'est émis

#### Scenario: Exigence non testée

- **WHEN** une exigence n'a pas encore de test
- **THEN** elle n'apparaît pas dans `coverage_must_test`
