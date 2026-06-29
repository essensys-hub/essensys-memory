---
type: Repository
title: Essensys Server Backend
description: Backend Go LAN qui expose l'API moderne et maintient la compatibilité legacy IoT.
resource: file:///Users/nrineau/ESSENSYS/essensys-server-backend
tags: [essensys, repository, gateway-lan, modern]
timestamp: 2026-06-28T19:07:32Z
repo: essensys-server-backend
layer: gateway-lan
era: modern
source_wiki: ../../wiki/entities/essensys-server-backend.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Backend Go LAN qui expose l'API moderne et maintient la compatibilité legacy IoT.

# Interfaces

* Couche : Gateway / LAN.
* Era : modern.
* Dépôt local : `essensys-server-backend`.
* Backend twin de [Essensys User Portal Backend](/systems/essensys-user-portal-backend.md).
* Implémente [Legacy HTTP](/protocols/legacy-http.md) et [Table D Echange](/protocols/table-d-echange.md).

# Dépendances

* Backend twin de [Essensys User Portal Backend](/systems/essensys-user-portal-backend.md).
* Implémente [Legacy HTTP](/protocols/legacy-http.md) et [Table D Echange](/protocols/table-d-echange.md).

# Code pointers

* `essensys-server-backend/Dockerfile`
* `essensys-server-backend/README.md`
* `essensys-server-backend/go.mod`
* `essensys-server-backend/internal/core/action_service.go`
* `essensys-server-backend/pkg/protocol/constants.go`
* `essensys-server-backend/test/test_serverinfos.sh`

# Risques

* Ne pas inférer de changement fonctionnel depuis cette fiche : elle décrit l'état et les contrats connus.
* Toute zone legacy ou protocolaire doit être vérifiée contre firmware + backend avant modification.

# Citations

[1] [Inventory](../../output/okf-repository-inventory.json)
[2] [Wiki source](../../wiki/entities/essensys-server-backend.md)
<!-- END GENERATED CONTENT -->
