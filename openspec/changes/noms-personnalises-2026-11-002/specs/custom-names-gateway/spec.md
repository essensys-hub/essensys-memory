## Purpose

Faire vivre les noms personnalisés dans la gateway, sur CM5 comme sur Raspberry Pi 4 : les garder en local, les servir au réseau local même sans internet, et les échanger avec le cloud.

## ADDED Requirements

### Requirement: Stockage local
La gateway SHALL conserver les noms personnalisés dans un stockage qui survit à son redémarrage et à sa mise à jour. Ce stockage MUST ne dépendre ni de PostgreSQL ni d'aucun service absent du Raspberry Pi 4. Une écriture interrompue par une coupure de courant MUST ne jamais laisser un stockage illisible.

#### Scenario: Redémarrage
- **GIVEN** une pièce renommée en réseau local
- **WHEN** la gateway redémarre
- **THEN** le nom est toujours là

#### Scenario: Coupure pendant l'écriture
- **WHEN** le courant est coupé pendant l'enregistrement d'un nom
- **THEN** la gateway redémarre avec l'ancien ou le nouveau nom, jamais avec un stockage corrompu

#### Scenario: Raspberry Pi 4 sans base de données
- **WHEN** la gateway tourne sur un Raspberry Pi 4 sans PostgreSQL
- **THEN** les noms fonctionnent comme sur une CM5

### Requirement: API du réseau local
La gateway SHALL fournir aux clients du réseau local la lecture, l'écriture et le rétablissement des noms, avec la même forme que le cloud : révision, `can_rename`, changements depuis une révision. L'écriture MUST être réservée à l'administrateur du réseau local. La gateway MUST valider les noms selon la règle de validité et refuser les clés absentes du catalogue.

#### Scenario: Lecture sur le réseau local
- **WHEN** un utilisateur du réseau local demande les noms
- **THEN** il reçoit les noms de la gateway, la révision et `can_rename`

#### Scenario: Écriture par l'administrateur
- **WHEN** l'administrateur du réseau local renomme une lumière
- **THEN** la gateway enregistre le nom, augmente sa révision et le sert aux autres clients du réseau local

#### Scenario: Écriture par un utilisateur ordinaire
- **WHEN** un utilisateur du réseau local qui n'est pas administrateur tente de renommer
- **THEN** la gateway refuse l'écriture

### Requirement: Fonctionnement sans cloud
La gateway SHALL accepter et servir les noms sans connexion au cloud. Les modifications faites pendant la coupure MUST être conservées, y compris après un redémarrage, jusqu'à ce que le cloud les ait reçues. Une gateway qui n'est pas reliée au cloud SHALL fonctionner uniquement avec son stockage local.

#### Scenario: Cloud injoignable
- **GIVEN** une gateway sans accès à internet
- **WHEN** l'administrateur renomme une pièce en réseau local
- **THEN** le nom est enregistré et servi aux clients du réseau local

#### Scenario: Reprise de la connexion
- **GIVEN** trois noms modifiés pendant une coupure, puis un redémarrage de la gateway
- **WHEN** la connexion au cloud revient
- **THEN** les trois modifications partent vers le cloud

#### Scenario: Gateway sans cloud
- **WHEN** la gateway n'est reliée à aucun cloud
- **THEN** les noms fonctionnent en local sans erreur ni message

### Requirement: Synchronisation avec le cloud
Quand la gateway est reliée au cloud, elle SHALL, à chaque cycle de synchronisation, récupérer les changements du cloud et lui envoyer les siens, avec la révision qu'elle connaissait. Elle MUST reprendre l'état fusionné renvoyé par le cloud. Un nom modifié sur la gateway ou sur le cloud MUST apparaître sur l'autre en moins d'une minute quand la liaison est active.

#### Scenario: Du cloud vers la gateway
- **WHEN** l'administrateur renomme une pièce depuis le portail cloud
- **THEN** le portail local et les apps en réseau local montrent le nouveau nom en moins d'une minute

#### Scenario: De la gateway vers le cloud
- **WHEN** l'administrateur renomme une lumière depuis le portail local
- **THEN** le portail cloud et les apps en mode Cloud montrent le nouveau nom en moins d'une minute

#### Scenario: Conflit
- **GIVEN** le même nom modifié sur le cloud et sur la gateway avant une synchronisation
- **WHEN** la synchronisation a lieu
- **THEN** la gateway et le cloud montrent la même valeur, celle de la dernière modification reçue par le cloud

### Requirement: Aucune écriture dans l'armoire
La gestion des noms MUST NOT lire ni écrire d'indice de la table d'échange, ni envoyer de commande à l'armoire.

#### Scenario: Renommer
- **WHEN** l'administrateur renomme un volet
- **THEN** aucun indice n'est écrit dans la table d'échange et aucune commande n'est envoyée

### Requirement: Installation et mise à jour
L'installation et la mise à jour de la gateway SHALL créer le stockage des noms avec les bons droits, sans intervention manuelle, sur CM5 (Ansible) comme sur Raspberry Pi 4 (scripts d'installation). Une mise à jour MUST conserver les noms déjà saisis, et les sauvegardes de la configuration de la gateway SHALL les inclure.

#### Scenario: Première installation
- **WHEN** la gateway est installée sur une CM5 ou un Raspberry Pi 4
- **THEN** le stockage des noms existe, avec les droits de l'utilisateur du service, et la gateway le lit au démarrage

#### Scenario: Mise à jour
- **GIVEN** une gateway qui a des noms personnalisés
- **WHEN** elle est mise à jour par Ansible ou par les scripts du Raspberry Pi 4
- **THEN** les noms sont toujours présents après la mise à jour
