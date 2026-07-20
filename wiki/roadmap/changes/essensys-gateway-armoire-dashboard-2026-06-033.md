---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-29
updated: 2026-07-20
status: active
host_repo: essensys-memory
---

# Essensys Gateway Armoire Dashboard 2026 06 033

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-gateway-armoire-dashboard-2026-06-033`
**Status:** active
**OpenSpec created:** 2026-06-29

## Why

Sur la **gateway CM5** (`https://mon.essensys.local/dashboard`), l'utilisateur ne voit pas si l'armoire SC944D est connectée ni son état système (secouru, alarme, chauffage, défauts BA). Pourtant le firmware remonte déjà des valeurs via `POST /api/mystatus` et la [[Table D Echange]] — elles sont stockées côté backend mais non exposées dans l'UI locale.

> **Roadmap ID:** 2026-06.033  
> **Horizon:** voir [[Roadmap OpenSpec]]  
> **Périmètre:** gateway LAN uniquement (pas portail cloud `/portal/`…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 1

## Source files

- `essensys-memory/openspec/changes/essensys-gateway-armoire-dashboard-2026-06-033/proposal.md`
- `essensys-memory/openspec/changes/essensys-gateway-armoire-dashboard-2026-06-033/design.md`
- `essensys-memory/openspec/changes/essensys-gateway-armoire-dashboard-2026-06-033/tasks.md`
