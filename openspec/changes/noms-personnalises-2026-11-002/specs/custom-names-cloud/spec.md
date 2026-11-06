## Purpose

Faire du cloud la source des noms personnalisés de chaque installation : les stocker, les servir aux portails et aux apps, et les échanger avec la gateway.

## ADDED Requirements

### Requirement: Lecture des noms
Le cloud SHALL fournir à un utilisateur connecté les noms personnalisés de son installation, avec la révision courante et l'indication de ses droits (`can_rename`). Un utilisateur MUST ne voir que les noms de l'installation à laquelle il est lié. Le cloud SHALL permettre de ne recevoir que les changements postérieurs à une révision connue, y compris les rétablissements, et répondre sans corps quand rien n'a changé.

#### Scenario: Première lecture
- **WHEN** un utilisateur lié à une armoire demande les noms
- **THEN** il reçoit tous les noms personnalisés de cette armoire, la révision courante et `can_rename`

#### Scenario: Rien de nouveau
- **WHEN** un client redemande les noms avec la révision qu'il connaît déjà
- **THEN** le cloud répond que rien n'a changé, sans renvoyer les noms

#### Scenario: Changements depuis une révision
- **GIVEN** deux noms modifiés et un nom rétabli depuis la révision 12
- **WHEN** un client demande les changements depuis la révision 12
- **THEN** il reçoit ces trois changements, le rétablissement étant signalé comme tel

#### Scenario: Autre installation
- **WHEN** un utilisateur demande les noms d'une armoire à laquelle il n'est pas lié
- **THEN** le cloud refuse la demande

### Requirement: Écriture d'un nom
Le cloud SHALL permettre à l'administrateur de l'armoire d'enregistrer le nom d'un objet ou d'une pièce du catalogue. Il MUST valider le nom selon la règle de validité, refuser une clé absente du catalogue et répondre avec le nom enregistré et la nouvelle révision. Il MUST refuser toute écriture d'un utilisateur qui n'est pas administrateur de cette armoire.

#### Scenario: Nom valide
- **WHEN** l'administrateur enregistre « Chambre de Nico » pour la pièce « Petite Chambre 3 »
- **THEN** le cloud répond avec le nom et une révision plus grande que la précédente

#### Scenario: Utilisateur ordinaire
- **WHEN** un utilisateur ordinaire enregistre un nom
- **THEN** le cloud répond « interdit » et rien n'est enregistré

#### Scenario: Objet inconnu
- **WHEN** l'administrateur enregistre un nom pour une clé absente du catalogue
- **THEN** le cloud refuse la demande

#### Scenario: Nom invalide
- **WHEN** l'administrateur enregistre un nom vide après nettoyage, ou de plus de 40 caractères
- **THEN** le cloud refuse la demande avec un code d'erreur propre au nom invalide

### Requirement: Rétablissement d'un nom
Le cloud SHALL permettre à l'administrateur de supprimer le nom personnalisé d'un objet ou d'une pièce. Le rétablissement MUST augmenter la révision et rester visible dans les changements, pour que les autres environnements le reprennent.

#### Scenario: Rétablir
- **WHEN** l'administrateur rétablit le nom d'un volet
- **THEN** la révision augmente et les clients qui demandent les changements reçoivent ce rétablissement

### Requirement: Convergence des modifications simultanées
Quand plusieurs environnements modifient le même nom, le cloud SHALL appliquer la dernière modification reçue et la diffuser à tous les environnements. Il MUST attribuer lui-même la révision de chaque modification, pour ne pas dépendre de l'horloge d'une gateway.

#### Scenario: Deux modifications du même nom
- **GIVEN** un administrateur qui renomme une pièce depuis le portail pendant qu'un autre la renomme depuis la gateway
- **WHEN** le cloud a reçu les deux modifications
- **THEN** le nom de la dernière modification reçue s'affiche partout, sur le cloud comme sur la gateway

### Requirement: Synchronisation avec la gateway
Le cloud SHALL fournir à la gateway, authentifiée par son identifiant et son jeton, les changements de noms depuis une révision, et recevoir ceux de la gateway avec la révision qu'elle connaissait. Il MUST répondre avec l'état fusionné et la révision courante. Une gateway MUST ne pouvoir lire et écrire que les noms de son installation.

#### Scenario: Gateway en retard
- **GIVEN** une gateway à la révision 10 alors que le cloud est à la 14
- **WHEN** elle demande les changements depuis la révision 10
- **THEN** elle reçoit les changements des révisions 11 à 14

#### Scenario: Changement fait sur la gateway
- **WHEN** la gateway envoie le nom d'une lumière modifié en réseau local
- **THEN** le cloud l'enregistre, augmente la révision et les portails et apps du cloud le reçoivent

#### Scenario: Gateway d'une autre installation
- **WHEN** une gateway tente de lire les noms d'une autre installation
- **THEN** le cloud refuse la demande

### Requirement: Installation sans gateway
Le cloud SHALL fonctionner sans gateway : les noms d'une installation reliée directement au cloud SHALL être stockés et servis aux portails et aux apps comme les autres.

#### Scenario: Armoire directement reliée au cloud
- **GIVEN** une installation sans gateway
- **WHEN** l'administrateur renomme une lumière depuis l'app en mode Cloud
- **THEN** le nom s'affiche sur le portail cloud et sur les autres apps de l'installation

### Requirement: Traçabilité
Chaque création, modification et rétablissement d'un nom SHALL être inscrit dans le journal d'audit, avec l'auteur, l'instant, l'objet, l'ancienne et la nouvelle valeur, et l'origine (cloud ou gateway). Un nom MUST NOT figurer dans les journaux techniques hors du journal d'audit.

#### Scenario: Modification
- **WHEN** l'administrateur renomme une pièce
- **THEN** le journal d'audit contient l'auteur, la pièce, l'ancien nom, le nouveau nom et l'origine « cloud »

### Requirement: Limitation de débit
Le cloud SHALL limiter le nombre d'écritures de noms par utilisateur et par minute, et répondre « trop de demandes » au-delà.

#### Scenario: Rafale
- **WHEN** un utilisateur envoie plus d'écritures que la limite en une minute
- **THEN** le cloud répond « trop de demandes » sans traiter l'excédent

### Requirement: Suppression de l'installation
Quand une installation est supprimée du cloud, ses noms personnalisés MUST l'être aussi.

#### Scenario: Armoire supprimée
- **WHEN** une armoire est supprimée du cloud
- **THEN** ses noms personnalisés ne sont plus stockés
