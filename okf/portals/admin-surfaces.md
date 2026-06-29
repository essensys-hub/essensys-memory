---
type: Portal
title: Admin Surfaces
description: Surfaces d'administration utilisateurs, sécurité et installation.
tags: [essensys, portal, 2025, 2026]
timestamp: 2026-06-28T19:07:32Z
deployment: LAN + Cloud
horizon_year: 2025/2026
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Surfaces d'administration utilisateurs, sécurité et installation.

# Audience et déploiement

| Champ | Valeur |
|---|---|
| Audience | Administrateurs ESSENSYS et installateurs |
| Déploiement | LAN + Cloud |
| Horizon | 2025/2026 lorsque sourcé par roadmap, sinon TBD par item |

# Dépôts

* [Essensys Server Frontend](/systems/essensys-server-frontend.md)
* [Essensys User Portal Frontend](/systems/essensys-user-portal-frontend.md)
* [Essensys Server Backend](/systems/essensys-server-backend.md)
* [Essensys User Portal Backend](/systems/essensys-user-portal-backend.md)

# Roadmap liée

* [Essensys Admin User Forbid Delete 2026 06 027](/roadmap/essensys-admin-user-forbid-delete-2026-06-027.md)
* [Essensys Trusted Devices 2026 06 013](/roadmap/essensys-trusted-devices-2026-06.013.md)

* [Essensys Trusted Devices 2026 06 013](/roadmap/essensys-trusted-devices-2026-06.013.md)

# Trusted devices — surface admin

Route **`/settings/users`** (menu **Comptes .local**) :

* CRUD comptes `lan_users`
* Tableau **connexions récentes** (user + MAC + IP) → **Appairer (permanent)**
* Gestion appareils actifs : révoquer, promouvoir temporaire → permanent

Règle : seul **`admin@essensys.local`** est exclu de l'auto-login ; les autres `lan_admin` (ex. installateur) peuvent être appairés.

Référence : [Trusted Devices LAN](/concepts/trusted-devices-lan.md).

# APIs et sécurité

* Les portails LAN/cloud doivent respecter [Dual Protocol](/protocols/dual-protocol.md) quand ils touchent les chemins backend.
* Les surfaces admin/utilisateur doivent rester alignées avec [Feature Lifecycle](/processes/feature-lifecycle.md) et les gates sécurité.
* Les états de déploiement doivent rester source-backed ; tout état non sourcé est un gap à remonter.

# Citations

[1] [Roadmap index](../../wiki/roadmap/index.md)
[2] [Platform overview](../../wiki/synthesis/platform-overview.md)
<!-- END GENERATED CONTENT -->
