## Purpose

Garantit qu'un service qui ne démarre pas fait échouer le déploiement qui l'a redémarré, avec le diagnostic dans la sortie du play.

## ADDED Requirements

### Requirement: Vérification de santé après redémarrage

Le rôle de déploiement du backend SHALL vérifier, après tout redémarrage du service, que celui-ci est actif et répond à sa route de santé.

#### Scenario: Service sain

- **WHEN** le service est actif et `GET /api/portal/health` répond `200` dans le délai
- **THEN** le play continue

#### Scenario: Service en boucle de redémarrage

- **WHEN** le service n'est pas actif après le délai
- **THEN** le play échoue
- **AND** les 30 dernières lignes du journal du service figurent dans le message d'échec

#### Scenario: Service actif mais ne répondant pas

- **WHEN** le service est actif mais la route de santé ne répond pas `200` dans le délai
- **THEN** le play échoue avec le même diagnostic

#### Scenario: Position dans le play

- **WHEN** le rôle redémarre le service, directement ou par handler
- **THEN** la vérification s'exécute après le dernier redémarrage et avant toute tâche qui dépend du service

#### Scenario: Délai borné

- **WHEN** la vérification s'exécute
- **THEN** elle attend au plus 30 secondes
