## Purpose

Décrit le parcours utilisateur de récupération de compte sur `mon.essensys.fr` : découverte du lien « Mot de passe oublié » depuis le formulaire de connexion, demande par email, définition d'un nouveau mot de passe, et confirmation de mot de passe à l'inscription pour éviter la faute de frappe initiale.

## ADDED Requirements

### Requirement: Point d'entrée depuis le formulaire de connexion

Le formulaire de connexion SHALL exposer un lien de récupération visible sans interaction préalable.

#### Scenario: Lien visible au chargement

- **WHEN** un visiteur ouvre la page de connexion
- **THEN** un lien libellé « Mot de passe oublié ? » est visible dans la zone du formulaire, sous le champ mot de passe
- **AND** il pointe vers la page de demande de réinitialisation

#### Scenario: Report de l'email déjà saisi

- **WHEN** le visiteur a saisi une adresse dans le champ email puis active le lien de récupération
- **THEN** la page de demande s'ouvre avec le champ email pré-rempli avec cette adresse

#### Scenario: Suggestion après échec de connexion

- **WHEN** une tentative de connexion échoue pour identifiants invalides
- **THEN** le message d'erreur affiché inclut un renvoi vers le parcours « Mot de passe oublié ? »
- **AND** le message ne précise pas si c'est l'adresse ou le mot de passe qui est en cause

#### Scenario: Accessibilité au clavier

- **WHEN** un utilisateur navigue au clavier depuis le champ mot de passe
- **THEN** le lien de récupération est atteignable, reçoit un indicateur de focus visible, et est activable par la touche Entrée

#### Scenario: Rendu sur les formats cibles

- **WHEN** la page de connexion est affichée sur desktop, iPhone et iPad
- **THEN** le lien de récupération reste visible sans défilement horizontal et sans chevaucher les autres contrôles du formulaire

### Requirement: Page de demande de réinitialisation

Le site SHALL fournir une page accessible sans authentification permettant de demander un lien de réinitialisation.

#### Scenario: Soumission d'une demande

- **WHEN** l'utilisateur saisit une adresse email, résout le captcha lorsqu'il est activé, et soumet le formulaire
- **THEN** l'interface appelle l'endpoint de demande de réinitialisation
- **AND** affiche un message de confirmation neutre indiquant qu'un email a été envoyé si un compte existe pour cette adresse
- **AND** ce message est identique quelle que soit l'existence du compte

#### Scenario: Captcha exigé mais non résolu

- **WHEN** le captcha est configuré pour ce build et que l'utilisateur soumet sans l'avoir résolu
- **THEN** le bouton de soumission reste désactivé ou l'interface affiche « Veuillez valider le captcha »
- **AND** aucune requête réseau n'est émise

#### Scenario: Retour vers la connexion

- **WHEN** la page de demande est affichée
- **THEN** un lien de retour vers le formulaire de connexion est disponible

#### Scenario: Limite de débit atteinte

- **WHEN** le serveur répond que la limite de débit est atteinte
- **THEN** l'interface affiche « Trop de demandes. Merci de réessayer dans une heure. »
- **AND** le formulaire reste utilisable après ce délai

### Requirement: Page de définition du nouveau mot de passe

Le site SHALL fournir une page consommant le jeton présent dans l'URL pour définir un nouveau mot de passe.

#### Scenario: Jeton valide

- **WHEN** l'utilisateur ouvre le lien reçu par email avec un jeton valide
- **THEN** l'interface pré-valide le jeton auprès du serveur avant d'afficher le formulaire
- **AND** affiche l'adresse email masquée du compte concerné
- **AND** propose un champ « Nouveau mot de passe » et un champ « Confirmer le mot de passe »

#### Scenario: Jeton expiré ou déjà utilisé

- **WHEN** la pré-validation indique que le jeton est expiré ou déjà consommé
- **THEN** l'interface n'affiche pas les champs de mot de passe
- **AND** affiche « Ce lien n'est plus valide » avec un lien vers une nouvelle demande

#### Scenario: Jeton absent de l'URL

- **WHEN** la page est ouverte sans paramètre de jeton
- **THEN** l'interface affiche « Lien de réinitialisation invalide » et propose une nouvelle demande

#### Scenario: Confirmation divergente

- **WHEN** les deux champs de mot de passe diffèrent
- **THEN** l'interface affiche « Les mots de passe ne correspondent pas » et bloque la soumission côté client

#### Scenario: Indicateur de robustesse

- **WHEN** l'utilisateur saisit un mot de passe
- **THEN** l'interface indique en direct si la longueur minimale de 8 caractères est atteinte
- **AND** conserve une option d'affichage en clair du mot de passe saisi

#### Scenario: Réinitialisation réussie

- **WHEN** le serveur confirme la mise à jour du mot de passe
- **THEN** l'interface affiche un message de succès
- **AND** redirige l'utilisateur vers le formulaire de connexion dans les 3 secondes, sans le connecter automatiquement

#### Scenario: Rejet serveur du mot de passe

- **WHEN** le serveur rejette le mot de passe comme trop faible ou identique au précédent
- **THEN** l'interface affiche le message renvoyé par le serveur
- **AND** conserve le formulaire actif pour une nouvelle tentative avec le même lien

### Requirement: Confirmation du mot de passe à l'inscription

Le formulaire d'inscription SHALL exiger une double saisie du mot de passe afin d'empêcher la création d'un compte avec un mot de passe saisi par erreur.

#### Scenario: Champ de confirmation présent

- **WHEN** un visiteur ouvre le formulaire d'inscription
- **THEN** un champ « Confirmer le mot de passe » est affiché sous le champ mot de passe

#### Scenario: Saisies divergentes

- **WHEN** les deux champs diffèrent au moment de la soumission
- **THEN** l'interface affiche « Les mots de passe ne correspondent pas » et n'émet aucune requête d'inscription

#### Scenario: Saisies identiques

- **WHEN** les deux champs sont identiques et conformes aux règles de robustesse
- **THEN** l'inscription se poursuit selon le comportement existant, captcha inclus
