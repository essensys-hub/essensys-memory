---
type: Portal
title: LAN Local Portal
description: Portail local gateway pour pilotage domotique sur le LAN.
tags: [essensys, portal, 2025, 2026]
timestamp: 2026-06-28T19:07:32Z
deployment: Gateway locale Raspberry/CM5
horizon_year: 2025/2026
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Portail local gateway pour pilotage domotique sur le LAN.

# Audience et déploiement

| Champ | Valeur |
|---|---|
| Audience | Utilisateur local, installateur, admin LAN |
| Déploiement | Gateway locale Raspberry/CM5 |
| Horizon | 2025/2026 lorsque sourcé par roadmap, sinon TBD par item |

# Dépôts

* [Essensys Server Frontend](/systems/essensys-server-frontend.md)
* [Essensys Server Backend](/systems/essensys-server-backend.md)
* [Essensys Control Plane](/systems/essensys-control-plane.md)

# Roadmap liée

* [Essensys Lan Iam 2026 06 017](/roadmap/essensys-lan-iam-2026-06.017.md)
* [Essensys Trusted Devices 2026 06 013](/roadmap/essensys-trusted-devices-2026-06.013.md)
* [Essensys Lan Mcu Panels 2026 06 025](/roadmap/essensys-lan-mcu-panels-2026-06.025.md)
* [Essensys Install Wizard 2026 06 016](/roadmap/essensys-install-wizard-2026-06.016.md)

* [Essensys Trusted Devices 2026 06 013](/roadmap/essensys-trusted-devices-2026-06.013.md)

# Trusted devices (auto-login MAC)

Implémenté sur le périmètre LAN (change **2026-06.013**) :

* **Utilisateur** : `/settings/account` — confiance 60 jours, re-login mot de passe ensuite.
* **Admin local** : `/settings/users` — appairage **permanent** pour un compte qui s'est connecté depuis l'appareil.
* **Exclusion** : seul `admin@essensys.local` (compte usine) ne peut pas utiliser l'auto-login.

Voir [Trusted Devices LAN](/concepts/trusted-devices-lan.md).

# APIs et sécurité

* Les portails LAN/cloud doivent respecter [Dual Protocol](/protocols/dual-protocol.md) quand ils touchent les chemins backend.
* Les surfaces admin/utilisateur doivent rester alignées avec [Feature Lifecycle](/processes/feature-lifecycle.md) et les gates sécurité.
* Les états de déploiement doivent rester source-backed ; tout état non sourcé est un gap à remonter.

# Citations

[1] [Roadmap index](../../wiki/roadmap/index.md)
[2] [Platform overview](../../wiki/synthesis/platform-overview.md)
<!-- END GENERATED CONTENT -->
