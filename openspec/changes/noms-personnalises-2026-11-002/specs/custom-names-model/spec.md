## Purpose

Définir ce qu'est un nom personnalisé : quels objets on peut nommer, quel nom s'affiche, quelle saisie est valide et qui peut la modifier. Ces règles sont les mêmes sur le cloud, la gateway, les portails et les apps.

## ADDED Requirements

### Requirement: Catalogue des objets nommables
Le système SHALL connaître un catalogue fixe d'objets nommables, identiques sur tous les clients et les serveurs. Chaque objet MUST avoir un type, une clé stable, un nom d'origine, et éventuellement une pièce et un patron de nom. Les types SHALL être : pièce, lumière, volet, zone de chauffage, prises de sécurité, chauffe-eau, arrosage, scénario. L'utilisateur MUST NOT pouvoir ajouter ni supprimer d'objet du catalogue.

#### Scenario: Objets d'une pièce
- **WHEN** un client affiche la pièce « Petite Chambre 3 »
- **THEN** le catalogue lui associe la lumière principale, la lumière de chevet et le volet de cette pièce

#### Scenario: Objet inconnu
- **WHEN** un client reçoit d'un serveur le nom d'un objet absent de son catalogue
- **THEN** il l'ignore sans erreur

### Requirement: Nom affiché
Le nom affiché d'un objet SHALL être, par ordre de priorité : le nom forcé de l'objet ; sinon le patron de l'objet rempli avec le nom de sa pièce, quand l'objet a une pièce ; sinon son nom d'origine. Le nom d'une pièce SHALL être son nom personnalisé, ou son nom d'origine. Les noms d'origine et les patrons MUST reproduire les libellés actuels des clients.

#### Scenario: Aucun nom personnalisé
- **WHEN** aucun nom n'a été saisi
- **THEN** chaque objet s'affiche avec son libellé actuel, par exemple « Volet Petite Chambre 3 »

#### Scenario: Nom de pièce
- **GIVEN** la pièce « Petite Chambre 3 » renommée « Chambre de Nico »
- **WHEN** un client affiche ses objets sans nom forcé
- **THEN** il montre « Chambre de Nico », « Chambre de Nico (chevet) » et « Volet Chambre de Nico »

#### Scenario: Nom forcé
- **GIVEN** la pièce renommée « Chambre de Nico » et le volet de cette pièce forcé en « Volet lit »
- **WHEN** un client affiche ces objets
- **THEN** le volet s'affiche « Volet lit » et les autres objets gardent le nom de la pièce

### Requirement: Rétablissement
Vider le nom d'un objet ou d'une pièce SHALL supprimer son nom personnalisé : l'objet retrouve alors le nom hérité de sa pièce, puis son nom d'origine.

#### Scenario: Rétablir un volet
- **GIVEN** le volet forcé en « Volet lit » dans la pièce « Chambre de Nico »
- **WHEN** l'administrateur rétablit son nom
- **THEN** il s'affiche « Volet Chambre de Nico »

#### Scenario: Rétablir une pièce
- **WHEN** l'administrateur rétablit le nom de la pièce
- **THEN** la pièce et ses objets sans nom forcé retrouvent leurs noms d'origine

### Requirement: Validité d'un nom
Un nom SHALL être du texte brut de 1 à 40 caractères après suppression des espaces en début et en fin et réduction des espaces répétés. Les caractères de contrôle et les caractères de direction du texte MUST être refusés. Le nom MUST être normalisé en Unicode (NFC) avant enregistrement. Un client ne MUST PAS interpréter un nom comme du HTML ni comme du balisage.

#### Scenario: Nom valide
- **WHEN** l'administrateur saisit « Chambre de Nico »
- **THEN** le nom est accepté

#### Scenario: Nom trop long
- **WHEN** l'administrateur saisit un nom de 41 caractères
- **THEN** le nom est refusé avec un message qui indique la limite de 40 caractères

#### Scenario: Balises
- **WHEN** un nom contient « <b>Nico</b> »
- **THEN** il s'affiche tel quel, sans mise en forme et sans exécuter de code

#### Scenario: Caractère de direction
- **WHEN** un nom contient un caractère qui inverse le sens du texte
- **THEN** le nom est refusé

### Requirement: Droits
Seul l'administrateur de l'armoire SHALL pouvoir créer, modifier ou rétablir un nom. Tous les autres utilisateurs liés à l'installation MUST pouvoir lire les noms. Côté cloud, l'administrateur de l'armoire est un utilisateur lié à cette armoire avec le rôle administrateur local ou administrateur global. Côté gateway, c'est un utilisateur du rôle administrateur du réseau local. Le serveur MUST refuser toute écriture d'un autre utilisateur, même si le client ne l'a pas empêchée.

#### Scenario: Utilisateur ordinaire
- **WHEN** un utilisateur sans rôle d'administrateur tente de renommer un objet
- **THEN** le serveur refuse l'écriture et le nom ne change pas

#### Scenario: Lecture
- **WHEN** un utilisateur ordinaire ouvre un écran
- **THEN** il voit les noms choisis par l'administrateur
