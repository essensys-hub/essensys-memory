---
type: Repository
title: Essensys Traefik
description: Reverse-proxy de bordure de la gateway Essensys, terminaison TLS (Let's Encrypt + CA locale) et filtrage des routes exposees sur le WAN.
resource: file:///Users/nrineau/ESSENSYS/essensys-traefik
tags: [essensys, repository, infra, modern]
timestamp: 2026-06-28T19:07:32Z
repo: essensys-traefik
layer: infra
era: modern
source_wiki: ../../wiki/entities/essensys-traefik.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Reverse-proxy de bordure de la gateway Essensys, terminaison TLS (Let's Encrypt + CA locale) et filtrage des routes exposees sur le WAN.

# Interfaces

* Couche : Infrastructure.
* Era : modern.
* Dépôt local : `essensys-traefik`.
* Interfaces détaillées à compléter lors d’un approfondissement ciblé.

# Dépendances

* TBD

# Code pointers

* `essensys-traefik/Dockerfile`

# Risques

* Ne pas inférer de changement fonctionnel depuis cette fiche : elle décrit l'état et les contrats connus.
* Toute zone legacy ou protocolaire doit être vérifiée contre firmware + backend avant modification.

# Citations

[1] [Inventory](../../output/okf-repository-inventory.json)
[2] [Wiki source](../../wiki/entities/essensys-traefik.md)
<!-- END GENERATED CONTENT -->
