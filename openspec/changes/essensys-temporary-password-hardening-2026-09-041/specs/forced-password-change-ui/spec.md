## Purpose

Renforce le parcours de changement imposé de `essensys-temporary-password-2026-09-040` : le verrou devient structurel (appliqué avant tout rendu d'une page protégée) et non plus seulement réactif (déclenché par un `409` reçu), et la destination d'origine est préservée quel que soit le chemin d'entrée.

## ADDED Requirements

### Requirement: Indicateur de changement requis persisté côté client

L'interface SHALL conserver localement l'information qu'un changement de mot de passe est requis, indépendamment du jeton d'authentification.

#### Scenario: Pose à la connexion

- **WHEN** la réponse de connexion porte `password_change_required: true`
- **THEN** l'indicateur est posé avant toute navigation

#### Scenario: Pose sur refus serveur

- **WHEN** une requête reçoit `409 password_change_required`
- **THEN** l'indicateur est posé avant la redirection

#### Scenario: Levée au changement réussi

- **WHEN** le changement de mot de passe réussit
- **THEN** l'indicateur est effacé avant la redirection vers la destination d'origine

#### Scenario: Levée à la déconnexion

- **WHEN** l'utilisateur se déconnecte
- **THEN** l'indicateur est effacé avec le jeton

#### Scenario: Survie au rechargement

- **WHEN** l'indicateur est posé et la page est rechargée
- **THEN** l'indicateur est toujours posé

### Requirement: Garde structurel des routes de l'espace connecté

L'interface SHALL empêcher le rendu de toute page de l'espace connecté tant que l'indicateur est posé, sans dépendre d'une requête réseau émise par cette page.

#### Scenario: Accès direct par URL

- **WHEN** l'indicateur est posé et l'utilisateur saisit directement l'adresse d'une page de l'espace connecté
- **THEN** la page de changement s'affiche
- **AND** aucune requête vers l'API n'a été émise par la page visée

#### Scenario: Navigation par l'historique

- **WHEN** l'indicateur est posé et l'utilisateur revient en arrière vers une page de l'espace connecté
- **THEN** la page de changement s'affiche

#### Scenario: Pages publiques non affectées

- **WHEN** l'indicateur est posé et l'utilisateur visite une page hors de l'espace connecté
- **THEN** la page s'affiche normalement

#### Scenario: Complémentarité avec le garde réactif

- **WHEN** un verrou est posé côté serveur pendant une session déjà ouverte, sans indicateur local
- **THEN** la première requête refusée (`409`) pose l'indicateur
- **AND** toute navigation ultérieure vers l'espace connecté est bloquée structurellement, avant toute requête

### Requirement: Préservation de la destination sur le chemin 409

L'interface SHALL ramener l'utilisateur à la page où il se trouvait, une fois le changement effectué, y compris lorsque le verrou a été détecté par un refus serveur.

#### Scenario: Refus serveur sur une page de l'espace connecté

- **WHEN** une requête émise depuis une page de l'espace connecté reçoit `409 password_change_required`
- **THEN** la page de changement est ouverte avec la page d'origine (chemin et paramètres) comme destination de retour

#### Scenario: Refus serveur sur la page de changement elle-même

- **WHEN** une requête émise depuis la page de changement reçoit `409`
- **THEN** aucune redirection n'est déclenchée

### Requirement: Indicateur local orphelin

L'interface SHALL tolérer un indicateur posé alors que le serveur ne verrouille plus le compte.

#### Scenario: Changement réussi non enregistré côté client

- **WHEN** la page de changement s'ouvre avec l'indicateur posé et que le serveur répond `200` à une requête de profil
- **THEN** l'indicateur est effacé
- **AND** l'utilisateur est renvoyé vers sa destination sans avoir à ressaisir de mot de passe

### Requirement: Affichage des mots de passe

Le formulaire de changement SHALL offrir une bascule d'affichage en clair des trois champs de mot de passe, alignée sur le formulaire de réinitialisation.

#### Scenario: Bascule

- **WHEN** l'utilisateur active la bascule
- **THEN** les trois champs affichent leur contenu en clair
- **AND** la bascule est désactivée par défaut
