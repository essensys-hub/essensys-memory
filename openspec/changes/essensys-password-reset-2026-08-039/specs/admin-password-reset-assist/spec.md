## Purpose

Donne au support Essensys un moyen tracé de débloquer un utilisateur qui ne reçoit pas ou ne parvient pas à utiliser l'email de réinitialisation, en déclenchant depuis la console d'administration l'émission d'un lien pour un compte donné.

## ADDED Requirements

### Requirement: Déclenchement administrateur d'une réinitialisation

Le système SHALL exposer `POST /api/admin/users/{id}/password-reset`, réservé aux comptes disposant du rôle administrateur.

#### Scenario: Administrateur déclenchant une réinitialisation

- **WHEN** un administrateur authentifié appelle l'endpoint pour un compte utilisateur existant et non interdit
- **THEN** le système émet un jeton de réinitialisation pour ce compte selon les mêmes règles que la demande en libre-service
- **AND** déclenche l'envoi du courriel de réinitialisation à l'adresse du compte
- **AND** répond `200 OK` avec `{ "email_sent": true, "expires_at": "<horodatage>" }`

#### Scenario: Appelant non administrateur

- **WHEN** un utilisateur sans rôle administrateur appelle l'endpoint
- **THEN** le système répond `403 Forbidden` et n'émet aucun jeton

#### Scenario: Appelant non authentifié

- **WHEN** l'appel est effectué sans jeton d'authentification valide
- **THEN** le système répond `401 Unauthorized`

#### Scenario: Compte inexistant

- **WHEN** l'identifiant fourni ne correspond à aucun compte
- **THEN** le système répond `404 Not Found`

#### Scenario: Compte interdit

- **WHEN** le compte visé est interdit
- **THEN** le système répond `409 Conflict` avec `{ "error": "account_forbidden" }`
- **AND** n'émet aucun jeton, le déblocage exigeant d'abord la levée de l'interdiction

#### Scenario: Envoi de courriel impossible

- **WHEN** le modèle de courriel est désactivé ou le service d'envoi n'est pas configuré
- **THEN** le système répond `200 OK` avec `{ "email_sent": false, "reason": "<motif>" }`
- **AND** l'administrateur voit dans l'interface que l'envoi a échoué, avec le motif

#### Scenario: Aucun secret exposé à l'administrateur

- **WHEN** l'endpoint répond
- **THEN** la réponse ne contient ni le jeton de réinitialisation, ni son empreinte, ni un lien exploitable
- **AND** aucun mot de passe temporaire n'est renvoyé ni affiché

### Requirement: Traçabilité de l'action administrateur

Le système SHALL journaliser toute réinitialisation déclenchée par un administrateur de manière distinguable des demandes en libre-service.

#### Scenario: Journalisation de l'action

- **WHEN** un administrateur déclenche une réinitialisation
- **THEN** une entrée d'audit `PASSWORD_RESET_REQUESTED_BY_ADMIN` est créée, portant l'identifiant et l'adresse de l'administrateur, le compte visé et l'adresse IP appelante

#### Scenario: Consultation par un autre administrateur

- **WHEN** un administrateur consulte le journal d'audit filtré sur le compte concerné
- **THEN** il voit qui a déclenché la réinitialisation et quand
- **AND** il voit, le cas échéant, l'entrée `PASSWORD_RESET_COMPLETED` correspondante

### Requirement: Point d'entrée dans la console d'administration

L'interface d'administration SHALL permettre de déclencher cette action depuis la fiche d'un utilisateur.

#### Scenario: Action disponible sur la fiche utilisateur

- **WHEN** un administrateur affiche la gestion des utilisateurs
- **THEN** une action « Envoyer un lien de réinitialisation » est disponible pour chaque compte non interdit

#### Scenario: Confirmation avant déclenchement

- **WHEN** l'administrateur active cette action
- **THEN** l'interface demande une confirmation mentionnant l'adresse email destinataire avant d'émettre la requête

#### Scenario: Retour visible du résultat

- **WHEN** le serveur répond
- **THEN** l'interface affiche explicitement si le courriel a été envoyé ou non, et le motif en cas d'échec
