## Purpose

Définit la remise à l'utilisateur du lien de réinitialisation par courriel, en réutilisant le modèle transactionnel `password_reset` déjà présent dans `email_templates`, et le comportement attendu lorsque le service d'envoi est indisponible ou désactivé.

## ADDED Requirements

### Requirement: Courriel de réinitialisation basé sur un modèle

Le système SHALL envoyer le lien de réinitialisation en utilisant le modèle transactionnel de slug `password_reset`, dont le sujet et le corps restent modifiables par un administrateur.

#### Scenario: Modèle activé et service d'envoi configuré

- **WHEN** un jeton de réinitialisation est émis, que le modèle `password_reset` est activé et que le service d'envoi est configuré
- **THEN** le système rend le sujet et le corps du modèle avec les variables disponibles
- **AND** envoie le courriel à l'adresse du compte concerné
- **AND** enregistre une entrée `sent` dans le journal d'envoi pour le destinataire et le slug `password_reset`

#### Scenario: Variable de lien de réinitialisation

- **WHEN** le corps ou le sujet du modèle contient le marqueur `{{reset_url}}`
- **THEN** le système le remplace par une URL absolue de la forme `<url_portail>/reset-password?token=<token>`
- **AND** `<url_portail>` provient de la configuration de l'URL publique du portail, avec repli sur `https://mon.essensys.fr`

#### Scenario: Variable de durée de validité

- **WHEN** le modèle contient le marqueur `{{expires_in}}`
- **THEN** le système le remplace par la durée de validité restante exprimée en minutes

#### Scenario: Aucun secret réutilisable dans le courriel

- **WHEN** un courriel de réinitialisation est composé
- **THEN** il ne contient **jamais** de mot de passe en clair ni de mot de passe temporaire
- **AND** le marqueur `{{temporary_password}}`, s'il subsiste dans un modèle hérité, est rendu comme chaîne vide

#### Scenario: Modèle désactivé

- **WHEN** le modèle `password_reset` est désactivé
- **THEN** aucun courriel n'est envoyé
- **AND** une entrée `failed` est enregistrée dans le journal d'envoi avec le motif « template disabled »
- **AND** la réponse de l'endpoint de demande reste `202 Accepted` et inchangée

### Requirement: Résilience de l'envoi

Le système SHALL traiter l'échec d'envoi comme une condition observable côté exploitation, sans jamais la révéler à l'appelant anonyme.

#### Scenario: Service d'envoi non configuré

- **WHEN** aucune configuration d'envoi de courriel n'est présente
- **THEN** aucun courriel n'est tenté
- **AND** une entrée `failed` est enregistrée dans le journal d'envoi avec le motif « SMTP configuration missing »
- **AND** une entrée d'audit `EMAIL_SEND_FAILED` est créée pour le slug `password_reset`

#### Scenario: Échec transitoire de l'envoi

- **WHEN** le serveur de courriel refuse ou interrompt la remise
- **THEN** le système enregistre l'échec dans le journal d'envoi avec le message d'erreur
- **AND** le jeton émis reste valide jusqu'à son expiration, permettant une nouvelle demande

#### Scenario: Aucune fuite d'information vers l'appelant

- **WHEN** l'envoi échoue pour quelque raison que ce soit
- **THEN** l'endpoint de demande répond `202 Accepted` avec le corps uniforme
- **AND** le corps de la réponse ne mentionne ni l'état du modèle, ni l'état du service d'envoi, ni l'existence du compte

### Requirement: Consultation de l'historique d'envoi

Le système SHALL rendre les envois de réinitialisation consultables par un administrateur pour permettre au support de diagnostiquer un utilisateur bloqué.

#### Scenario: Support vérifiant un envoi

- **WHEN** un administrateur consulte le journal d'envoi de courriels filtré sur une adresse destinataire
- **THEN** il voit les tentatives de slug `password_reset` avec leur statut, leur horodatage et l'éventuel message d'erreur
- **AND** il ne voit ni le jeton, ni son empreinte, ni aucun lien de réinitialisation exploitable
