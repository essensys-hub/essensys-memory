---
tags: [concept, security, gateway, lan]
sources: [essensys-lan-iam-2026-06.017]
created: 2026-06-26
updated: 2026-06-26
---

# LAN IAM

> Comptes email/mot de passe locaux sur `mon.essensys.local` — table **`lan_users`**, sessions cookie **7 jours**, rôles `lan_admin` / `lan_user` / `lan_guest`.

## Périmètre

| In | Out |
|----|-----|
| CRUD users LAN, login/logout, bootstrap installateur | IAM cloud `mon.essensys.fr` (JWT/OAuth) |
| Protection routes dashboard UI | Protocole legacy IoT (`/api/mystatus`, …) |
| Config `lan_iam.enabled` dans backend gateway | Sync comptes LAN ↔ OVH |

## Rôles

| Rôle | Pilotage domotique | Admin users |
|------|-------------------|-------------|
| `lan_admin` | Oui | Oui |
| `lan_user` | Oui | Non |
| `lan_guest` | Oui (identique user) | Non |

## OpenSpec

- Change : `essensys-memory/openspec/changes/essensys-lan-iam-2026-06.017/`
- Roadmap ID : **2026-06.017**
- Dépendances recommandées : [[Essensys Trusted Devices 2026 06.013]], install-wizard 016

## Intégration install-wizard (016)

Le bootstrap token Ansible (`lan_bootstrap.token`) et l'appel `POST /api/admin/lan-users/bootstrap` restent le mécanisme v1. Le change **016** pourra remplacer l'appel curl par une étape wizard post-install (création mot de passe installateur dans l'UI) sans modifier le schéma `lan_users`.

## Liens

- [[Essensys Server Backend]]
- [[Essensys Server Frontend]]
- [[Dual Protocol]]
- [[Product Roadmap]]
