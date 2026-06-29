---
type: Repository
title: Essensys Raspberry Install
description: "Provisioning / bootstrap d'installation de la passerelle Essensys sur Raspberry Pi : un script `install.sh` minimal qui pose les prérequis (git, Ansible) puis **délègue tout le déploiement au dépôt `essensys-ansible`** ("
resource: file:///Users/nrineau/ESSENSYS/essensys-raspberry-install
tags: [essensys, repository, gateway-lan, modern]
timestamp: 2026-06-28T19:07:32Z
repo: essensys-raspberry-install
layer: gateway-lan
era: modern
source_wiki: ../../wiki/entities/essensys-raspberry-install.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Provisioning / bootstrap d'installation de la passerelle Essensys sur Raspberry Pi : un script `install.sh` minimal qui pose les prérequis (git, Ansible) puis **délègue tout le déploiement au dépôt `essensys-ansible`** (

# Interfaces

* Couche : Gateway / LAN.
* Era : modern.
* Dépôt local : `essensys-raspberry-install`.
* Interfaces détaillées à compléter lors d’un approfondissement ciblé.

# Dépendances

* TBD

# Code pointers

* `essensys-raspberry-install/README.md`

# Risques

* Ne pas inférer de changement fonctionnel depuis cette fiche : elle décrit l'état et les contrats connus.
* Toute zone legacy ou protocolaire doit être vérifiée contre firmware + backend avant modification.

# Citations

[1] [Inventory](../../output/okf-repository-inventory.json)
[2] [Wiki source](../../wiki/entities/essensys-raspberry-install.md)
<!-- END GENERATED CONTENT -->
