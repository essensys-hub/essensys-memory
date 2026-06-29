---
type: Repository
title: Essensys Base
description: Image Docker de base commune (Alpine 3.19) partagée par tous les services Essensys déployés sur Raspberry Pi.
resource: file:///Users/nrineau/ESSENSYS/essensys-base
tags: [essensys, repository, infra, modern]
timestamp: 2026-06-28T19:07:32Z
repo: essensys-base
layer: infra
era: modern
source_wiki: ../../wiki/entities/essensys-base.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Image Docker de base commune (Alpine 3.19) partagée par tous les services Essensys déployés sur Raspberry Pi.

# Interfaces

* Couche : Infrastructure.
* Era : modern.
* Dépôt local : `essensys-base`.
* Interfaces détaillées à compléter lors d’un approfondissement ciblé.

# Dépendances

* TBD

# Code pointers

* `essensys-base/Dockerfile`
* `essensys-base/README.md`

# Risques

* Ne pas inférer de changement fonctionnel depuis cette fiche : elle décrit l'état et les contrats connus.
* Toute zone legacy ou protocolaire doit être vérifiée contre firmware + backend avant modification.

# Citations

[1] [Inventory](../../output/okf-repository-inventory.json)
[2] [Wiki source](../../wiki/entities/essensys-base.md)
<!-- END GENERATED CONTENT -->
