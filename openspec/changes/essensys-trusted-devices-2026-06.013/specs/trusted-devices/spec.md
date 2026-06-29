# trusted-devices

Connexions automatiques LAN sur `mon.essensys.local` pour clients de confiance identifies par adresse MAC, au-dessus de l'IAM locale (`lan_users`).

## ADDED Requirements

### Requirement: Selection d'un client LAN par adresse MAC

Le systeme MUST exposer a l'utilisateur authentifie une liste de clients LAN detectes et eligibles a partir de l'**adresse MAC observee cote gateway/backend**, sans exiger une saisie manuelle de la MAC dans le navigateur.

#### Scenario: L'utilisateur voit les clients detectes

- **WHEN** un `lan_user` ou `lan_guest` authentifie ouvre l'ecran **Appareils de confiance**
- **THEN** le backend renvoie la liste des clients observes recemment sur le LAN avec au minimum `mac_address`, `device_label` si disponible, et `last_seen_at`
- **AND** le frontend permet de choisir un client a partir de cette liste

#### Scenario: Aucun client detecte

- **WHEN** aucun client LAN eligible n'a ete observe pour la session en cours
- **THEN** l'interface n'autorise pas la creation d'un trusted device
- **AND** elle invite l'utilisateur a poursuivre en login classique

### Requirement: Activation self-service temporaire

Le systeme MUST permettre a un `lan_user` ou `lan_guest` actif d'associer son compte a un client LAN choisi par adresse MAC pour une **connexion automatique temporaire de 60 jours**.

#### Scenario: Activation reussie par un utilisateur standard

- **WHEN** un `lan_user` actif selectionne un client detecte et demande la connexion automatique
- **THEN** le backend cree une entree `trusted_devices` liee au compte et a la `mac_address`
- **AND** `trust_mode` vaut `temporary`
- **AND** `expires_at` est fixe a `now + 60 jours`

#### Scenario: Activation reussie par un guest

- **WHEN** un `lan_guest` actif selectionne un client detecte et demande la connexion automatique
- **THEN** le trusted device est cree avec les memes regles qu'un `lan_user`

#### Scenario: Tentative depuis un compte admin

- **WHEN** un `lan_admin` tente d'activer la connexion automatique sur un appareil
- **THEN** la requete est refusee
- **AND** aucun trusted device n'est cree

### Requirement: Re-authentification obligatoire tous les deux mois

Le systeme MUST exiger une re-authentification complete par login + mot de passe lorsque la confiance temporaire d'un appareil a depasse **60 jours**.

#### Scenario: Trusted device encore valide

- **WHEN** une requete arrive depuis une `mac_address` ayant un trusted device temporaire actif non expire
- **THEN** le compte associe peut beneficier de la connexion automatique

#### Scenario: Trusted device expire

- **WHEN** une requete arrive depuis une `mac_address` ayant un trusted device temporaire dont `expires_at` est depasse
- **THEN** la connexion automatique est refusee
- **AND** l'utilisateur MUST repasser par le login/mot de passe

#### Scenario: Nouvelle confiance apres re-login

- **WHEN** l'utilisateur s'est reconnecte avec login + mot de passe apres expiration
- **THEN** il peut recreer ou renouveler un trusted device temporaire pour 60 jours supplementaires

### Requirement: Appairage permanent admin pour comptes non-admin

Le systeme MUST permettre a un `lan_admin` de creer et gerer un appairage **permanent** entre une **adresse MAC** et un compte `lan_user` ou `lan_guest`.

#### Scenario: Admin cree un appairage permanent

- **WHEN** un `lan_admin` envoie une creation pour une `mac_address` detectee et un compte `lan_user`
- **THEN** le backend cree une entree `trusted_devices`
- **AND** `trust_mode` vaut `permanent`
- **AND** `expires_at` vaut `NULL`

#### Scenario: Admin convertit un temporaire en permanent

- **WHEN** un `lan_admin` promeut un trusted device temporaire existant pour un compte non-admin
- **THEN** l'entree passe en mode `permanent`
- **AND** l'expiration est retiree

#### Scenario: Admin revoque un appairage

- **WHEN** un `lan_admin` revoque un trusted device actif
- **THEN** `revoked_at` est renseigne
- **AND** la connexion automatique ne doit plus fonctionner pour cette MAC

### Requirement: Interdiction pour le compte administrateur usine

Le systeme MUST NOT autoriser de connexion automatique pour le compte usine `admin@essensys.local`, y compris via l'API d'administration.

#### Scenario: Auto-login refuse pour compte usine

- **WHEN** une requete arrive depuis une `mac_address` associee au compte `admin@essensys.local`
- **THEN** le backend refuse l'auto-login
- **AND** la page de login standard est affichee

#### Scenario: Creation permanente vers compte usine refusee

- **WHEN** un `lan_admin` tente de creer un appairage permanent pour `admin@essensys.local`
- **THEN** la requete est refusee avec une erreur metier
- **AND** aucune entree active n'est creee

#### Scenario: Administrateur local eligible

- **WHEN** un `lan_admin` dont l'email n'est pas `admin@essensys.local` active un trusted device
- **THEN** les memes regles s'appliquent qu'un `lan_user` (temporaire 60 jours ou permanent via admin)

### Requirement: Comportement en cas d'ambiguite MAC

Le systeme MUST refuser l'auto-login silencieux lorsqu'une meme `mac_address` correspond a plusieurs appairages actifs eligibles.

#### Scenario: Deux comptes actifs sur la meme MAC

- **WHEN** deux trusted devices actifs non revoques existent pour la meme `mac_address`
- **THEN** le backend n'etablit aucune session automatiquement
- **AND** le client revient au login explicite ou a un ecran de choix confirme
