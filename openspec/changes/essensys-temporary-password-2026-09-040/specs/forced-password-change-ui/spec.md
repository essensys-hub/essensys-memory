## Purpose

Donne à l'utilisateur qui se connecte avec un mot de passe temporaire un parcours clair et sans échappatoire pour choisir son propre mot de passe, sur `www.essensys.fr`.

## ADDED Requirements

### Requirement: Page de changement imposé

L'interface SHALL exposer une route `/change-password` présentant un formulaire de choix de nouveau mot de passe.

#### Scenario: Contenu du formulaire

- **WHEN** l'utilisateur atteint la page
- **THEN** le formulaire demande le mot de passe temporaire reçu, le nouveau mot de passe et sa confirmation
- **AND** explique pourquoi le changement est imposé

#### Scenario: Confirmation divergente

- **WHEN** le nouveau mot de passe et sa confirmation diffèrent
- **THEN** l'interface signale l'écart et n'envoie aucune requête

#### Scenario: Retour d'erreur du serveur

- **WHEN** le serveur rejette le changement
- **THEN** l'interface affiche un message distinguant le mot de passe actuel erroné, le mot de passe trop court et le mot de passe identique à l'actuel

#### Scenario: Changement réussi

- **WHEN** le serveur accepte le changement
- **THEN** l'utilisateur est redirigé vers son espace, connecté, sans avoir à ressaisir ses identifiants

### Requirement: Redirection après connexion

L'interface SHALL diriger vers la page de changement tout utilisateur dont la connexion signale un changement requis.

#### Scenario: Connexion avec mot de passe temporaire

- **WHEN** la réponse de connexion porte l'indication de changement requis
- **THEN** l'interface conserve le jeton et affiche la page de changement
- **AND** n'affiche pas la destination habituelle après connexion

#### Scenario: Mot de passe temporaire expiré

- **WHEN** la connexion échoue parce que le mot de passe temporaire est expiré
- **THEN** l'interface affiche un message invitant à recontacter le support ou à utiliser la réinitialisation par courriel
- **AND** ne présente pas cette erreur comme un identifiant incorrect

### Requirement: Rattrapage sur session existante

L'interface SHALL diriger vers la page de changement tout utilisateur dont une requête reçoit `409 password_change_required`.

#### Scenario: Retour ultérieur avec un jeton conservé

- **WHEN** une requête de l'application reçoit `409 password_change_required`
- **THEN** l'utilisateur est amené sur la page de changement, quelle que soit la page d'où venait la requête

### Requirement: Absence d'échappatoire

L'interface SHALL empêcher l'utilisateur de poursuivre sa navigation tant que le changement n'est pas effectué.

#### Scenario: Navigation indisponible

- **WHEN** l'utilisateur est sur la page de changement
- **THEN** aucun lien de navigation vers les autres pages de l'espace connecté n'est proposé

#### Scenario: Tentative d'accès direct à une autre page

- **WHEN** l'utilisateur saisit directement l'adresse d'une autre page de l'espace connecté
- **THEN** il est ramené sur la page de changement

#### Scenario: Sortie possible

- **WHEN** l'utilisateur souhaite abandonner
- **THEN** une action de déconnexion reste disponible

### Requirement: Couverture multi-appareils

L'interface SHALL rester utilisable sur les trois familles d'appareils de la matrice de régression UX.

#### Scenario: Page de changement sur téléphone, tablette et ordinateur

- **WHEN** la page de changement est affichée sur iPhone, iPad et desktop
- **THEN** le formulaire est entièrement accessible, sans défilement horizontal

#### Scenario: Modale d'émission sur téléphone, tablette et ordinateur

- **WHEN** la modale d'émission d'un mot de passe temporaire est affichée sur iPhone, iPad et desktop
- **THEN** le mot de passe affiché et son action de copie restent lisibles et atteignables
