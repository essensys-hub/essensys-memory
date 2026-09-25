## Purpose

Garantit qu'un compte portant un mot de passe temporaire ne peut rien faire d'autre que remplacer ce mot de passe, et que ce mot de passe cesse d'autoriser la connexion au terme de sa durée de vie. Le contrôle est exercé par le serveur, de sorte qu'aucun client ne puisse s'en affranchir.

## ADDED Requirements

### Requirement: Verrou serveur sur les routes authentifiées

Le système SHALL refuser toute requête authentifiée émanant d'un compte marqué comme devant changer de mot de passe, à l'exception de la route de changement de mot de passe.

#### Scenario: Accès au profil

- **WHEN** un compte marqué comme devant changer de mot de passe appelle une route de profil avec un jeton valide
- **THEN** le système répond `409 Conflict` avec `{ "error": "password_change_required" }`
- **AND** n'exécute aucun effet de bord

#### Scenario: Accès aux routes du portail

- **WHEN** ce même compte appelle une route du portail avec un jeton valide
- **THEN** le système répond `409 Conflict` avec `{ "error": "password_change_required" }`

#### Scenario: Accès aux routes d'administration

- **WHEN** ce même compte dispose d'un rôle administrateur et appelle une route d'administration avec un jeton valide
- **THEN** le système répond `409 Conflict` avec `{ "error": "password_change_required" }`
- **AND** le rôle administrateur ne confère aucune exemption

#### Scenario: Route de changement accessible

- **WHEN** ce même compte appelle la route de changement de mot de passe avec un jeton valide
- **THEN** le système traite la requête normalement

#### Scenario: Gel des sessions ouvertes avant l'émission

- **WHEN** un mot de passe temporaire est émis pour un compte dont une session était déjà ouverte
- **THEN** le jeton de cette session reçoit `409 Conflict` à sa requête suivante
- **AND** cela sans attendre son expiration

#### Scenario: Compte non concerné

- **WHEN** un compte ne porte aucune marque de changement requis
- **THEN** aucune de ses requêtes authentifiées n'est affectée

#### Scenario: Priorité de l'interdiction de compte

- **WHEN** un compte est à la fois interdit et marqué comme devant changer de mot de passe
- **THEN** le système répond `403 Forbidden` avec `{ "error": "account_forbidden" }`

### Requirement: Connexion avec un mot de passe temporaire

Le système SHALL accepter la connexion avec un mot de passe temporaire valide et signaler au client que le changement est requis.

#### Scenario: Connexion réussie

- **WHEN** un utilisateur se connecte avec un mot de passe temporaire non expiré
- **THEN** le système répond `200 OK` avec un jeton d'authentification
- **AND** la réponse porte `"password_change_required": true`

#### Scenario: Connexion d'un compte ordinaire

- **WHEN** un utilisateur se connecte avec un mot de passe ordinaire
- **THEN** la réponse ne demande aucun changement de mot de passe

### Requirement: Expiration du mot de passe temporaire

Le système SHALL refuser la connexion avec un mot de passe temporaire dont l'échéance est dépassée.

#### Scenario: Mot de passe temporaire expiré

- **WHEN** un utilisateur se connecte avec un mot de passe temporaire dont l'échéance est dépassée
- **THEN** le système répond `401 Unauthorized` avec `{ "error": "temporary_password_expired" }`
- **AND** n'émet aucun jeton d'authentification

#### Scenario: Absence de divulgation d'état

- **WHEN** quelqu'un tente de se connecter avec un mot de passe erroné sur un compte portant un mot de passe temporaire expiré
- **THEN** le système répond comme pour toute tentative infructueuse, sans révéler l'existence ni l'expiration d'un mot de passe temporaire

#### Scenario: Ancien mot de passe non restauré

- **WHEN** un mot de passe temporaire expire
- **THEN** le mot de passe qui précédait son émission ne redevient pas valide

### Requirement: Changement du mot de passe

Le système SHALL exposer `POST /api/auth/password/change`, accessible à un compte authentifié, qui remplace le mot de passe et lève la marque de changement requis.

#### Scenario: Changement réussi

- **WHEN** un utilisateur authentifié fournit son mot de passe actuel et un nouveau mot de passe conforme
- **THEN** le système remplace l'empreinte du mot de passe
- **AND** efface la marque de changement requis et l'échéance du mot de passe temporaire
- **AND** répond `200 OK`

#### Scenario: Reprise d'accès immédiate

- **WHEN** le changement a réussi
- **THEN** le jeton d'authentification déjà détenu par l'utilisateur redonne accès aux routes qui répondaient `409 Conflict`
- **AND** aucune reconnexion n'est nécessaire

#### Scenario: Mot de passe actuel erroné

- **WHEN** le mot de passe actuel fourni ne correspond pas
- **THEN** le système répond `401 Unauthorized`
- **AND** le mot de passe et la marque de changement requis restent inchangés

#### Scenario: Nouveau mot de passe trop court

- **WHEN** le nouveau mot de passe compte moins de 8 caractères
- **THEN** le système répond `400 Bad Request`
- **AND** le mot de passe reste inchangé

#### Scenario: Nouveau mot de passe identique à l'actuel

- **WHEN** le nouveau mot de passe est identique au mot de passe actuel
- **THEN** le système répond `400 Bad Request`
- **AND** la marque de changement requis n'est pas levée

#### Scenario: Atomicité

- **WHEN** l'écriture du nouveau mot de passe échoue
- **THEN** la marque de changement requis n'est pas levée

#### Scenario: Limitation du débit

- **WHEN** un même appelant soumet un nombre excessif de tentatives de changement en une heure
- **THEN** le système répond `429 Too Many Requests`

### Requirement: Traçabilité du changement

Le système SHALL journaliser le changement de mot de passe consécutif à un mot de passe temporaire.

#### Scenario: Journalisation du changement

- **WHEN** un utilisateur remplace un mot de passe temporaire
- **THEN** une entrée d'audit `PASSWORD_CHANGED_AFTER_TEMPORARY` est créée, portant le compte concerné et l'adresse IP appelante
- **AND** ne contenant ni l'ancien ni le nouveau mot de passe
