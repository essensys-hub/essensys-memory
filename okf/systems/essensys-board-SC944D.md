---
type: Repository
title: Essensys Board Sc944d
description: "Carte contrôleur central (« client ») de la box domotique Essensys : cerveau Ethernet sous RTOS MQX qui agrège les boîtiers auxiliaires, dialogue avec le serveur Essensys et distribue les firmwares aux autres cartes."
resource: file:///Users/nrineau/ESSENSYS/essensys-board-SC944D
tags: [essensys, repository, firmware, legacy]
timestamp: 2026-06-28T19:07:32Z
repo: essensys-board-SC944D
layer: firmware
era: legacy
source_wiki: ../../wiki/entities/essensys-board-sc944d.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Carte contrôleur central (« client ») de la box domotique Essensys : cerveau Ethernet sous RTOS MQX qui agrège les boîtiers auxiliaires, dialogue avec le serveur Essensys et distribue les firmwares aux autres cartes.

# Interfaces

* Couche : Firmware / armoire.
* Era : legacy.
* Dépôt local : `essensys-board-SC944D`.
* Détaillé dans [architecture armoire](/synthesis/armoire-architecture.md).
* Lié à [Table D Echange](/protocols/table-d-echange.md).
* Contraintes legacy : compatibilité firmware et non-régression protocolaire.

# Dépendances

* Détaillé dans [architecture armoire](/synthesis/armoire-architecture.md).
* Lié à [Table D Echange](/protocols/table-d-echange.md).
* Contraintes legacy : compatibilité firmware et non-régression protocolaire.

# Code pointers

* `essensys-board-SC944D/Dockerfile`
* `essensys-board-SC944D/README.md`
* `essensys-board-SC944D/SC944D/Prog/099-37/BP_MQX_ETH/H/TableEchange.h`
* `essensys-board-SC944D/SC944D/Prog/_Archives/095-34/BP_MQX_ETH/H/TableEchange.h`
* `essensys-board-SC944D/SC944D/Prog/_Archives/096-35/BP_MQX_ETH/H/TableEchange.h`
* `essensys-board-SC944D/SC944D/Prog/_Archives/097-36/BP_MQX_ETH/H/TableEchange.h`

# Risques

* Ne pas inférer de changement fonctionnel depuis cette fiche : elle décrit l'état et les contrats connus.
* Toute zone legacy ou protocolaire doit être vérifiée contre firmware + backend avant modification.

# Citations

[1] [Inventory](../../output/okf-repository-inventory.json)
[2] [Wiki source](../../wiki/entities/essensys-board-sc944d.md)
<!-- END GENERATED CONTENT -->
