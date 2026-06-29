---
type: Repository
title: Essensys Control Plane
description: "Plan de contrôle de la passerelle Essensys : service Go (UI React embarquée) qui orchestre la **flotte de conteneurs Docker** locaux (état, restart, update, rollback, versions), expose le **registre d'échange Redis** des"
resource: file:///Users/nrineau/ESSENSYS/essensys-control-plane
tags: [essensys, repository, gateway-lan, modern]
timestamp: 2026-06-28T19:07:32Z
repo: essensys-control-plane
layer: gateway-lan
era: modern
source_wiki: ../../wiki/entities/essensys-control-plane.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Plan de contrôle de la passerelle Essensys : service Go (UI React embarquée) qui orchestre la **flotte de conteneurs Docker** locaux (état, restart, update, rollback, versions), expose le **registre d'échange Redis** des

# Interfaces

* Couche : Gateway / LAN.
* Era : modern.
* Dépôt local : `essensys-control-plane`.
* Interfaces détaillées à compléter lors d’un approfondissement ciblé.

# Dépendances

* TBD

# Code pointers

* `essensys-control-plane/Dockerfile`
* `essensys-control-plane/README.md`
* `essensys-control-plane/go.mod`

# Risques

* Ne pas inférer de changement fonctionnel depuis cette fiche : elle décrit l'état et les contrats connus.
* Toute zone legacy ou protocolaire doit être vérifiée contre firmware + backend avant modification.

# Citations

[1] [Inventory](../../output/okf-repository-inventory.json)
[2] [Wiki source](../../wiki/entities/essensys-control-plane.md)
<!-- END GENERATED CONTENT -->
