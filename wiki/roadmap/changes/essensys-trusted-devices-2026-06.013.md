---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-21
updated: 2026-06-29
status: active
implementation: partial-deployed-cm5
host_repo: essensys-memory
---

# Essensys Trusted Devices 2026 06.013

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-trusted-devices-2026-06.013`
**Status:** active — **phases 1–3 implémentées**, phase 4 doc brain (2026-06-29)
**OpenSpec created:** 2026-06-21

## Why

Sur `mon.essensys.local`, les utilisateurs ont besoin d'un **login automatique par appareil** pour les iPad muraux, tablettes cuisine et postes fixes du LAN, sans redemander le mot de passe a chaque ouverture. En meme temps, l'authentification locale ne doit pas devenir permanente sans controle : un utilisateur standard doit **reconfirmer son login/mot de passe tous les 2 mois**, et l'administrateur local peut rendre un couple **adresse MAC + login** permanent.

> **Roadmap ID:** 2026-06.013

## Implémentation (2026-06-29)

| Composant | État |
|-----------|------|
| Backend `internal/laniam` | ✓ trusted_devices, lan_login_clients, auto-login |
| Frontend `LanUsersAdminPage`, `AccountSettingsPage` | ✓ |
| Migrations `004`, `005` + Ansible | ✓ |
| Déploiement CM5 test | ✓ rsync + Docker |
| Wiki / OKF | ✓ [[Trusted Devices LAN]] |

**Règle admin usine** : seul `admin@essensys.local` exclu (`BootstrapLanAdminEmail`) ; les `lan_admin` locaux peuvent utiliser l'auto-login.

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 1

## Source files

- `essensys-memory/openspec/changes/essensys-trusted-devices-2026-06.013/proposal.md`
- `essensys-memory/openspec/changes/essensys-trusted-devices-2026-06.013/design.md`
- `essensys-memory/openspec/changes/essensys-trusted-devices-2026-06.013/tasks.md`
