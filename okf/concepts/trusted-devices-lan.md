---
type: Concept
title: Trusted Devices LAN
description: Auto-login par adresse MAC sur mon.essensys.local — temporaire 60 jours (utilisateur) ou permanent (admin), hors compte usine admin@essensys.local.
tags: [essensys, lan, security, trusted-devices, gateway]
timestamp: 2026-06-29T10:30:00Z
source_wiki: ../../wiki/concepts/trusted-devices-lan.md
---

# Définition

Les **trusted devices LAN** permettent une connexion automatique sur le portail local `mon.essensys.local` lorsque la gateway reconnaît l'**adresse MAC** d'un appareil déjà associé à un compte [[LAN IAM]] après un login mot de passe.

# Règles d'éligibilité

| Compte | Auto-login | Durée |
|--------|------------|-------|
| `lan_user`, `lan_guest` | Oui | 60 jours (self-service) ou permanent (admin) |
| `lan_admin` (admin local) | Oui | Idem |
| `admin@essensys.local` (usine) | **Non** | Mot de passe obligatoire |

# Surfaces UI

| Surface | Route | Action |
|---------|-------|--------|
| Utilisateur | `/settings/account` | Faire confiance 60 jours |
| Admin LAN | `/settings/users` | Appairer (permanent), révoquer, promouvoir |

Les candidats MAC proviennent de la table `lan_login_clients` (connexions enregistrées), pas d'une liste ARP brute.

# Données et migrations

* `trusted_devices` — migration `004`
* `lan_login_clients` — migration `005`
* Ansible : `raspberry_backend/tasks/lan_iam_migrations.yml`

# Déploiement

Périmètre **LAN CM5** uniquement — voir [Deployment Perimeters](/processes/deployment-perimeters.md). Dépôts : [Essensys Server Backend](/systems/essensys-server-backend.md), [Essensys Server Frontend](/systems/essensys-server-frontend.md).

# Roadmap

* [Essensys Trusted Devices 2026 06 013](/roadmap/essensys-trusted-devices-2026-06.013.md)
* [Essensys Lan Iam 2026 06 017](/roadmap/essensys-lan-iam-2026-06.017.md)

# Citations

[1] [Wiki source: Trusted devices LAN](../../wiki/concepts/trusted-devices-lan.md)
[2] [LAN local portal](../portals/lan-local-portal.md)
[3] [Admin surfaces](../portals/admin-surfaces.md)
