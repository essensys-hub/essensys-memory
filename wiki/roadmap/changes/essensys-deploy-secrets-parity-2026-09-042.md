---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-09-26
updated: 2026-09-26
status: active
host_repo: essensys-memory
---

# Essensys Deploy Secrets Parity 2026 09 042

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-deploy-secrets-parity-2026-09-042`
**Status:** active
**OpenSpec created:** 2026-09-26

## Why

Le 25/09/2026, le premier redéploiement du backend cloud depuis plusieurs mois a mis la production hors service pendant environ une heure (`mon.essensys.fr` et `www.essensys.fr` : `502` sur toute l'API, protocole IoT legacy compris — un seul binaire). Aucun des trois défauts en cause n'était dans le code déployé. Tous étaient dans le pipeline, dormants, et se sont réveillés ensemble :

1. **`deploy-security-fix.yml` n'invoquait pas le rôle `sops_load`.** Ce playbook « allégé » (backend + SPA, sa…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 2

## Source files

- `essensys-memory/openspec/changes/essensys-deploy-secrets-parity-2026-09-042/proposal.md`
- `essensys-memory/openspec/changes/essensys-deploy-secrets-parity-2026-09-042/design.md`
- `essensys-memory/openspec/changes/essensys-deploy-secrets-parity-2026-09-042/tasks.md`
