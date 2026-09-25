## Purpose

Donne au support Essensys un moyen tracé de débloquer un utilisateur qui n'accède pas à sa boîte mail, en émettant depuis la console d'administration un mot de passe temporaire à durée de vie bornée, affiché une seule fois pour une transmission hors-bande.

## ADDED Requirements

### Requirement: Émission d'un mot de passe temporaire

Le système SHALL exposer `POST /api/admin/users/{id}/temporary-password`, réservé aux comptes disposant du rôle administrateur global.

#### Scenario: Émission pour un compte existant

- **WHEN** un administrateur global authentifié appelle l'endpoint pour un compte existant et non interdit
- **THEN** le système génère un mot de passe aléatoire, remplace l'empreinte du mot de passe du compte, et marque le compte comme devant changer de mot de passe
- **AND** fixe l'échéance du mot de passe temporaire à 72 heures après l'émission
- **AND** répond `200 OK` avec `{ "password": "<clair>", "expires_at": "<horodatage>", "email_sent": <booléen> }`

#### Scenario: Appelant sans le rôle administrateur global

- **WHEN** un utilisateur authentifié dépourvu du rôle administrateur global appelle l'endpoint
- **THEN** le système répond `403 Forbidden`
- **AND** le mot de passe du compte visé reste inchangé

#### Scenario: Appelant non authentifié

- **WHEN** l'appel est effectué sans jeton d'authentification valide
- **THEN** le système répond `401 Unauthorized`

#### Scenario: Compte inexistant

- **WHEN** l'identifiant fourni ne correspond à aucun compte
- **THEN** le système répond `404 Not Found`

#### Scenario: Compte interdit

- **WHEN** le compte visé est interdit
- **THEN** le système répond `409 Conflict` avec `{ "error": "account_forbidden" }`
- **AND** n'émet aucun mot de passe temporaire, le déblocage exigeant d'abord la levée de l'interdiction

#### Scenario: Émission successive

- **WHEN** un administrateur émet un second mot de passe temporaire pour un compte qui en porte déjà un
- **THEN** le mot de passe précédent cesse immédiatement d'autoriser la connexion
- **AND** la nouvelle échéance est calculée depuis la seconde émission

### Requirement: Robustesse et lisibilité du mot de passe généré

Le système SHALL générer le mot de passe temporaire par une source cryptographiquement sûre, dans un alphabet exempt de caractères visuellement ambigus.

#### Scenario: Caractères exclus

- **WHEN** le système génère un mot de passe temporaire
- **THEN** celui-ci ne contient aucun des caractères `O`, `0`, `I`, `l`, `1`
- **AND** comporte au moins 12 caractères

#### Scenario: Absence de répétition entre émissions

- **WHEN** deux mots de passe temporaires sont générés successivement
- **THEN** ils diffèrent

### Requirement: Invalidation des jetons de réinitialisation concurrents

Le système SHALL invalider tout jeton de réinitialisation encore valide pour le compte au moment où un mot de passe temporaire est émis.

#### Scenario: Lien de réinitialisation en cours

- **WHEN** un mot de passe temporaire est émis pour un compte disposant d'un jeton de réinitialisation non consommé et non expiré
- **THEN** ce jeton est marqué invalidé
- **AND** une tentative ultérieure de l'utiliser est rejetée comme jeton invalide

### Requirement: Confidentialité du mot de passe temporaire

Le système SHALL ne divulguer le mot de passe en clair que dans la réponse à l'émission, et nulle part ailleurs.

#### Scenario: Absence dans le journal d'audit

- **WHEN** un mot de passe temporaire est émis
- **THEN** l'entrée d'audit correspondante ne contient ni le mot de passe en clair, ni son empreinte

#### Scenario: Absence dans les journaux du service

- **WHEN** un mot de passe temporaire est émis
- **THEN** aucune ligne du journal applicatif ne contient le mot de passe en clair

#### Scenario: Non relisible après l'émission

- **WHEN** un administrateur consulte la liste des utilisateurs après une émission
- **THEN** le mot de passe en clair n'est disponible dans aucune réponse de l'API

### Requirement: Traçabilité de l'émission

Le système SHALL journaliser toute émission de mot de passe temporaire de manière distinguable des autres actions de dépannage.

#### Scenario: Journalisation de l'action

- **WHEN** un administrateur émet un mot de passe temporaire
- **THEN** une entrée d'audit `TEMPORARY_PASSWORD_ISSUED` est créée, portant l'identifiant et l'adresse de l'administrateur, le compte visé et l'adresse IP appelante

#### Scenario: Consultation par un autre administrateur

- **WHEN** un administrateur consulte le journal d'audit filtré sur le compte concerné
- **THEN** il voit qui a émis le mot de passe temporaire et quand
- **AND** il voit, le cas échéant, l'entrée `PASSWORD_CHANGED_AFTER_TEMPORARY` correspondante

### Requirement: Point d'entrée dans la console d'administration

L'interface d'administration SHALL permettre d'émettre un mot de passe temporaire depuis la fiche d'un utilisateur, et d'en afficher le résultat une seule fois.

#### Scenario: Action disponible sur la fiche utilisateur

- **WHEN** un administrateur global affiche la gestion des utilisateurs
- **THEN** une action « Définir un mot de passe temporaire » est disponible pour chaque compte non interdit

#### Scenario: Confirmation avant émission

- **WHEN** l'administrateur active cette action
- **THEN** l'interface demande une confirmation mentionnant l'adresse email du compte visé
- **AND** avertit que le mot de passe actuel de l'utilisateur sera définitivement remplacé

#### Scenario: Affichage unique du mot de passe

- **WHEN** le serveur répond à l'émission
- **THEN** l'interface affiche le mot de passe en clair, sa date d'expiration, et un moyen de le copier
- **AND** indique explicitement qu'il ne sera plus affichable après fermeture

#### Scenario: Fermeture de l'affichage

- **WHEN** l'administrateur ferme l'affichage du résultat
- **THEN** le mot de passe n'est plus consultable depuis l'interface

#### Scenario: État visible dans la liste

- **WHEN** un compte porte un mot de passe temporaire en attente de changement
- **THEN** la liste des utilisateurs signale cet état pour ce compte
