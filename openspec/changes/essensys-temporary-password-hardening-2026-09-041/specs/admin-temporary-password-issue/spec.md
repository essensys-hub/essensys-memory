## Purpose

Précise un point laissé ambigu par `essensys-temporary-password-2026-09-040` sur la limitation de débit du changement de mot de passe, pour que le choix d'implémentation soit une exigence et non une interprétation.

## ADDED Requirements

### Requirement: Clé de limitation du débit du changement

Le système SHALL limiter le débit de `POST /api/auth/password/change` par adresse IP appelante, avec le même plafond que la consommation d'un jeton de réinitialisation.

#### Scenario: Plafond par adresse

- **WHEN** une même adresse IP soumet plus de 10 tentatives de changement en une heure
- **THEN** le système répond `429 Too Many Requests` aux suivantes

#### Scenario: Comptes distincts, même adresse

- **WHEN** deux comptes distincts derrière la même adresse IP cumulent plus de 10 tentatives en une heure
- **THEN** le plafond s'applique à l'adresse, pas à chaque compte

#### Scenario: Justification du choix

- **WHEN** un attaquant tourne les adresses pour contourner le plafond
- **THEN** il ne peut réussir qu'en connaissant déjà le mot de passe temporaire du compte visé, ce qui rend le contournement sans objet
