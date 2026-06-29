---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-25
updated: 2026-06-28
status: active
host_repo: essensys-memory
---

# Essensys Secrets Sops Migration 2026 06 028

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-secrets-sops-migration-2026-06-028`
**Status:** active
**OpenSpec created:** 2026-06-25

## Why

Les secrets Essensys cloud (JWT, OAuth, SMTP, PostgreSQL, New Relic) sont aujourd'hui dans `essensys-ansible/group_vars/essensys/vault.yml`, **gitignored** et chiffrés avec **Ansible Vault** et un mot de passe partagé. Ce modèle empêche la review en PR, complique l'onboarding des opérateurs et diverge de la trajectoire **sops-nix** documentée pour les gateways NixOS. Il faut migrer vers **SOPS + age**, secrets versionnés chiffrés dans Git, tout en conservant le runtime actuel (`.env` systemd sur…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 2

## Source files

- `essensys-memory/openspec/changes/essensys-secrets-sops-migration-2026-06-028/proposal.md`
- `essensys-memory/openspec/changes/essensys-secrets-sops-migration-2026-06-028/design.md`
- `essensys-memory/openspec/changes/essensys-secrets-sops-migration-2026-06-028/tasks.md`
