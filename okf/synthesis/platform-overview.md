---
type: Synthesis
title: ESSENSYS Platform Overview
description: Vue d'ensemble des quatre couches de la plateforme domotique ESSENSYS.
tags: [essensys, platform, architecture, iot, home-automation]
timestamp: 2026-06-28T06:11:17Z
source_wiki: ../../wiki/synthesis/platform-overview.md
---

# Résumé

ESSENSYS est une solution domotique résidentielle couvrant alarme, chauffage, éclairage, volets, arrosage, cumulus et détection de fuite. La plateforme combine un parc legacy embarqué avec une architecture moderne gateway/LAN/cloud.

# Couches

| Couche | Rôle | Exemples |
|---|---|---|
| Armoire | Firmware et cartes terrain | SC944D maître, SC940/SC941C/SC942C esclaves, SC945D écran, SC946D sirène |
| Passerelle | Pont local et migration modernisée | Raspberry Gateway CM5/NixOS, client legacy BP_MQX_ETH |
| LAN | Services locaux | Backend Go, frontend React, Redis, Mosquitto, Traefik, Nginx |
| Cloud | Accès distant et hub utilisateur | User Portal backend/frontend sur `mon.essensys.fr` |

# Concepts liés

* [Dual Protocol](/concepts/dual-protocol.md) — coexistence du protocole legacy IoT et de l'API REST moderne.
* [Feature Lifecycle](/processes/feature-lifecycle.md) — méthode de livraison et de traçabilité.
* [Essensys Memory](/systems/essensys-memory.md) — mémoire persistante agent-friendly.

# Citations

[1] [Wiki source: Platform Overview](../../wiki/synthesis/platform-overview.md)
