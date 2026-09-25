## Purpose

Permet à l'administrateur de faire parvenir le mot de passe temporaire par courriel lorsque c'est pertinent, sans jamais en faire la voie par défaut, et sans que l'indisponibilité du service d'envoi ne compromette le dépannage.

## ADDED Requirements

### Requirement: Envoi sur demande explicite

Le système SHALL n'envoyer le mot de passe temporaire par courriel que lorsque l'administrateur le demande explicitement à l'émission.

#### Scenario: Envoi demandé

- **WHEN** l'administrateur émet un mot de passe temporaire en demandant l'envoi par courriel
- **THEN** le système envoie à l'adresse du compte un courriel contenant le mot de passe temporaire et sa durée de validité
- **AND** répond `200 OK` avec `"email_sent": true`

#### Scenario: Envoi non demandé

- **WHEN** l'administrateur émet un mot de passe temporaire sans demander l'envoi
- **THEN** aucun courriel n'est envoyé
- **AND** la réponse porte `"email_sent": false`

#### Scenario: Valeur par défaut dans l'interface

- **WHEN** l'administrateur ouvre la confirmation d'émission
- **THEN** l'option d'envoi par courriel est proposée non cochée

### Requirement: Contenu du courriel

Le système SHALL faire figurer dans le courriel les éléments nécessaires à l'utilisateur pour se connecter et comprendre la suite.

#### Scenario: Éléments présents

- **WHEN** le courriel est rendu
- **THEN** il contient le mot de passe temporaire, la durée de validité restante, l'adresse de connexion et l'indication que le mot de passe devra être remplacé à la première connexion

### Requirement: Indépendance vis-à-vis du service d'envoi

Le système SHALL considérer l'émission comme réussie même lorsque l'envoi du courriel échoue.

#### Scenario: Service d'envoi indisponible

- **WHEN** l'envoi échoue parce que le service de courriel n'est pas configuré ou refuse le message
- **THEN** le système répond `200 OK` avec `"email_sent": false` et un motif
- **AND** le mot de passe temporaire reste valide et affiché à l'administrateur

#### Scenario: Restitution du motif à l'administrateur

- **WHEN** la réponse indique un échec d'envoi
- **THEN** l'interface affiche le motif et invite à transmettre le mot de passe par un autre moyen

#### Scenario: Absence de réémission implicite

- **WHEN** un envoi a échoué
- **THEN** le système ne régénère pas de mot de passe de lui-même

### Requirement: Journal des envois

Le système SHALL journaliser l'envoi selon le mécanisme commun aux courriels transactionnels.

#### Scenario: Ligne de journal

- **WHEN** un envoi est tenté, qu'il réussisse ou échoue
- **THEN** une ligne est ajoutée au journal d'envoi des courriels avec son issue
- **AND** cette ligne ne contient pas le mot de passe en clair
