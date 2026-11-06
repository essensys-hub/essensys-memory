## Purpose

Permettre à l'administrateur de renommer depuis le portail cloud et le portail local, et faire apparaître les noms choisis partout où un objet est affiché. Les deux portails se comportent de la même façon.

## ADDED Requirements

### Requirement: Écran « Noms »
Le portail SHALL proposer dans les Réglages un écran « Noms » réservé à l'administrateur de l'armoire. L'écran SHALL lister les pièces et les objets par catégorie (pièces, lumières, volets, chauffage, prises de sécurité, chauffe-eau et arrosage, scénarios). Chaque ligne SHALL montrer le nom affiché et son origine : personnalisé, hérité de la pièce ou d'origine. L'administrateur SHALL pouvoir modifier un nom et le rétablir.

#### Scenario: Administrateur
- **WHEN** l'administrateur ouvre l'écran « Noms »
- **THEN** il voit toutes les catégories, chaque ligne avec son nom affiché et son origine

#### Scenario: Renommer
- **WHEN** l'administrateur saisit « Chambre de Nico » pour la pièce « Petite Chambre 3 » et enregistre
- **THEN** le nom est enregistré et la ligne passe à « personnalisé »

#### Scenario: Rétablir
- **WHEN** l'administrateur rétablit le nom d'un objet
- **THEN** la ligne retrouve son nom hérité, ou son nom d'origine, et son origine suit

#### Scenario: Utilisateur ordinaire
- **WHEN** un utilisateur sans droit d'administrateur ouvre les Réglages
- **THEN** il ne voit pas l'écran « Noms » et aucun contrôle de renommage ailleurs

### Requirement: Aperçu avant de renommer une pièce
Avant d'enregistrer le nom d'une pièce, le portail SHALL montrer à l'administrateur la liste des objets dont le nom affiché va changer, et celle des objets au nom forcé qui ne changeront pas.

#### Scenario: Aperçu
- **WHEN** l'administrateur saisit un nouveau nom pour « Petite Chambre 3 »
- **THEN** le portail liste la lumière de chevet et le volet qui prendront ce nom, et signale un objet au nom forcé qui ne changera pas

### Requirement: Saisie contrôlée
Le portail SHALL limiter la saisie à 40 caractères, afficher le nombre de caractères restants et le motif d'un refus. Un nom refusé par le serveur MUST rester dans le champ avec le message du serveur, sans perdre ce que l'administrateur a tapé.

#### Scenario: Trop long
- **WHEN** l'administrateur dépasse 40 caractères
- **THEN** le portail empêche l'enregistrement et indique la limite

#### Scenario: Refus du serveur
- **WHEN** le serveur refuse un nom
- **THEN** le portail affiche le message et garde le texte saisi

### Requirement: Noms affichés partout
Le portail SHALL afficher le nom choisi partout où un objet apparaît : pages éclairage, volets, chauffage, prises de sécurité, chauffe-eau et arrosage, scénarios et éditeur de scénarios, messages de confirmation, état et dernière action. Aucun libellé codé en dur ne MUST rester affiché à la place d'un nom choisi.

#### Scenario: Page éclairage
- **GIVEN** la pièce « Petite Chambre 3 » renommée « Chambre de Nico »
- **WHEN** l'utilisateur ouvre la page éclairage
- **THEN** les lumières de cette pièce s'affichent avec le nom « Chambre de Nico »

#### Scenario: Éditeur de scénarios
- **WHEN** l'utilisateur choisit les lumières et volets d'un scénario
- **THEN** la liste montre les noms choisis

#### Scenario: Confirmation
- **WHEN** l'utilisateur demande à couper les prises de sécurité renommées « Prises du garage »
- **THEN** le message de confirmation emploie « Prises du garage »

### Requirement: Mise à jour sans recharger
Quand un nom change sur un autre environnement, le portail SHALL l'afficher en moins d'une minute sans que l'utilisateur recharge la page.

#### Scenario: Changement venu d'une app
- **WHEN** l'administrateur renomme une lumière depuis l'app
- **THEN** le portail ouvert montre le nouveau nom en moins d'une minute

### Requirement: Noms d'origine en secours
Quand le serveur ne fournit pas les noms (API absente, erreur, hors ligne), le portail SHALL afficher les noms d'origine, ou les derniers noms connus, sans erreur visible et sans bloquer les commandes.

#### Scenario: Serveur sans les noms
- **WHEN** le portail interroge un serveur qui ne connaît pas les noms
- **THEN** il affiche les noms d'origine et toutes les commandes restent utilisables

### Requirement: Portails jumeaux
Le portail cloud et le portail local SHALL avoir le même écran « Noms », la même règle de nom affiché et les mêmes textes. Un changement d'un portail MUST être reporté sur l'autre dans la même Feature.

#### Scenario: Parité
- **WHEN** la suite de tests des deux portails s'exécute
- **THEN** les mêmes scénarios de noms passent sur les deux
