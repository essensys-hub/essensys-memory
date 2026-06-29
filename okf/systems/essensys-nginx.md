---
type: Repository
title: Essensys Nginx
description: "Serveur web et reverse-proxy interne de la gateway Essensys : sert le frontend React (SPA) et proxifie l'API, le MCP et le control-plane sur le LAN."
resource: file:///Users/nrineau/ESSENSYS/essensys-nginx
tags: [essensys, repository, infra, modern]
timestamp: 2026-06-28T19:07:32Z
repo: essensys-nginx
layer: infra
era: modern
source_wiki: ../../wiki/entities/essensys-nginx.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Serveur web et reverse-proxy interne de la gateway Essensys : sert le frontend React (SPA) et proxifie l'API, le MCP et le control-plane sur le LAN.

# Interfaces

* Couche : Infrastructure.
* Era : modern.
* Dépôt local : `essensys-nginx`.
* Interfaces détaillées à compléter lors d’un approfondissement ciblé.

# Dépendances

* TBD

# Code pointers

* `essensys-nginx/Dockerfile`

# Risques

* Ne pas inférer de changement fonctionnel depuis cette fiche : elle décrit l'état et les contrats connus.
* Toute zone legacy ou protocolaire doit être vérifiée contre firmware + backend avant modification.

# Citations

[1] [Inventory](../../output/okf-repository-inventory.json)
[2] [Wiki source](../../wiki/entities/essensys-nginx.md)
<!-- END GENERATED CONTENT -->
