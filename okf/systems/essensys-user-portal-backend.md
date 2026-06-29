---
type: Repository
title: Essensys User Portal Backend
description: Backend Go cloud/OVH pour portail distant, relais gateway et expansion d'ordres.
resource: file:///Users/nrineau/ESSENSYS/essensys-user-portal-backend
tags: [essensys, repository, cloud, modern]
timestamp: 2026-06-28T19:07:32Z
repo: essensys-user-portal-backend
layer: cloud
era: modern
source_wiki: ../../wiki/entities/essensys-user-portal-backend.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Backend Go cloud/OVH pour portail distant, relais gateway et expansion d'ordres.

# Interfaces

* Couche : Cloud / portails.
* Era : modern.
* Dépôt local : `essensys-user-portal-backend`.
* Backend twin de [Essensys Server Backend](/systems/essensys-server-backend.md).
* Relais cloud connecté au portail distant.

# Dépendances

* Backend twin de [Essensys Server Backend](/systems/essensys-server-backend.md).
* Relais cloud connecté au portail distant.

# Code pointers

* `essensys-user-portal-backend/README.md`
* `essensys-user-portal-backend/go.mod`
* `essensys-user-portal-backend/internal/domain/order_expansion.go`

# Risques

* Ne pas inférer de changement fonctionnel depuis cette fiche : elle décrit l'état et les contrats connus.
* Toute zone legacy ou protocolaire doit être vérifiée contre firmware + backend avant modification.

# Citations

[1] [Inventory](../../output/okf-repository-inventory.json)
[2] [Wiki source](../../wiki/entities/essensys-user-portal-backend.md)
<!-- END GENERATED CONTENT -->
