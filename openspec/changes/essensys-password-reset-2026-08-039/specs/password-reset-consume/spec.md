## Purpose

Définit la validation et la consommation à usage unique d'un jeton de réinitialisation, ainsi que les règles de robustesse appliquées au nouveau mot de passe avant réécriture de l'empreinte bcrypt du compte portail.

## ADDED Requirements

### Requirement: Pré-validation du jeton

Le système SHALL exposer `GET /api/auth/password/reset/validate?token=<token>` afin que l'interface puisse informer l'utilisateur de l'état du jeton avant qu'il ne saisisse un mot de passe.

#### Scenario: Jeton valide

- **WHEN** le jeton fourni existe, n'est ni expiré, ni consommé, ni invalidé
- **THEN** le système répond `200 OK` avec `{ "valid": true, "email_masked": "e***@gmail.com" }`
- **AND** l'adresse est masquée de sorte que seuls le premier caractère de la partie locale et le domaine restent lisibles

#### Scenario: Jeton expiré

- **WHEN** l'expiration du jeton est antérieure à l'instant courant
- **THEN** le système répond `410 Gone` avec `{ "valid": false, "reason": "expired" }`

#### Scenario: Jeton déjà consommé ou invalidé

- **WHEN** le jeton a déjà servi à une réinitialisation, ou a été invalidé par l'émission d'un jeton plus récent
- **THEN** le système répond `410 Gone` avec `{ "valid": false, "reason": "used" }`

#### Scenario: Jeton inconnu ou paramètre absent

- **WHEN** le jeton est absent de la base, ou le paramètre `token` n'est pas fourni
- **THEN** le système répond `400 Bad Request` avec `{ "valid": false, "reason": "invalid" }`

#### Scenario: Pré-validation sans effet de bord

- **WHEN** un jeton valide est pré-validé, y compris plusieurs fois de suite
- **THEN** le jeton reste utilisable et n'est ni consommé ni compté comme tentative

### Requirement: Endpoint de réinitialisation

Le système SHALL exposer `POST /api/auth/password/reset` en accès public, acceptant `{ "token": string, "password": string }`.

#### Scenario: Réinitialisation réussie

- **WHEN** un jeton valide est soumis avec un mot de passe conforme aux règles de robustesse
- **THEN** le système remplace `users.password_hash` par une empreinte bcrypt du nouveau mot de passe
- **AND** marque le jeton comme consommé avec son horodatage et l'adresse IP appelante
- **AND** répond `200 OK` avec `{ "message": "Mot de passe mis à jour." }`
- **AND** l'utilisateur peut immédiatement se connecter via `POST /api/auth/login` avec le nouveau mot de passe

#### Scenario: Jeton invalide, expiré ou déjà consommé

- **WHEN** le jeton soumis est inconnu, expiré, invalidé ou déjà consommé
- **THEN** le système répond `400 Bad Request` avec `{ "error": "invalid_token" }`
- **AND** le mot de passe du compte reste inchangé
- **AND** une entrée d'audit `PASSWORD_RESET_TOKEN_INVALID` est journalisée

#### Scenario: Usage unique strictement appliqué

- **WHEN** la même valeur de jeton est soumise une seconde fois après une réinitialisation réussie
- **THEN** le système répond `400 Bad Request` avec `{ "error": "invalid_token" }`
- **AND** le mot de passe défini lors de la première consommation reste en vigueur

#### Scenario: Compte devenu interdit entre l'émission et la consommation

- **WHEN** le compte associé au jeton a été interdit après l'émission du jeton
- **THEN** le système répond `403 Forbidden` avec `{ "error": "account_forbidden" }`
- **AND** le mot de passe n'est pas modifié
- **AND** le jeton est invalidé

#### Scenario: Limitation des tentatives de consommation

- **WHEN** une même adresse IP soumet plus de 10 tentatives de réinitialisation en 1 heure
- **THEN** le système répond `429 Too Many Requests`

### Requirement: Robustesse du nouveau mot de passe

Le système SHALL rejeter tout nouveau mot de passe ne respectant pas les règles minimales, en appliquant les mêmes règles que l'inscription.

#### Scenario: Mot de passe trop court

- **WHEN** le mot de passe soumis compte moins de 8 caractères
- **THEN** le système répond `400 Bad Request` avec `{ "error": "weak_password", "message": "Le mot de passe doit contenir au moins 8 caractères." }`
- **AND** le jeton n'est **pas** consommé, permettant une nouvelle tentative

#### Scenario: Mot de passe identique à l'ancien

- **WHEN** le mot de passe soumis correspond à l'empreinte bcrypt actuellement enregistrée
- **THEN** le système répond `400 Bad Request` avec `{ "error": "password_reused" }`
- **AND** le jeton reste utilisable

#### Scenario: Mot de passe conforme

- **WHEN** le mot de passe compte au moins 8 caractères et diffère de l'ancien
- **THEN** le système l'accepte et poursuit la réinitialisation

### Requirement: Effets de la réinitialisation sur les sessions

Le système SHALL garantir qu'une réinitialisation réussie ne laisse aucun autre jeton de réinitialisation exploitable pour le compte concerné.

#### Scenario: Invalidation des autres jetons de réinitialisation

- **WHEN** une réinitialisation aboutit pour un compte
- **THEN** tous les autres jetons de réinitialisation non consommés de ce compte sont marqués invalidés

#### Scenario: Journalisation de la réinitialisation

- **WHEN** une réinitialisation aboutit
- **THEN** une entrée d'audit `PASSWORD_RESET_COMPLETED` est créée avec l'identifiant du compte, l'adresse email, l'adresse IP et l'horodatage
- **AND** ni le mot de passe ni le jeton en clair n'apparaissent dans le journal ni dans les logs applicatifs
