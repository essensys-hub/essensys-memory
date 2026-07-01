---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-29
updated: 2026-06-29
status: in-progress
host_repo: essensys-memory
---

# Essensys Gateway Armoire Dashboard 2026 06 033

**Host repo:** [[Essensys Server Backend]], [[Essensys Server Frontend]]
**Path:** `essensys-memory/openspec/changes/essensys-gateway-armoire-dashboard-2026-06-033`
**Status:** in-progress
**Roadmap ID:** 2026-06.033

## Why

Visibilité installateur sur l'état armoire SC944D depuis `https://mon.essensys.local/dashboard` sans modifier le firmware ni les endpoints legacy.

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: gateway-armoire-dashboard

## Implémentation

- Backend : rotation `serverinfos`, package `internal/armoire/`, `GET /api/admin/armoire/snapshot`
- Frontend : `ArmoireStatusPanel`, poll 5 s, mock E2E
- Doc : [[Gateway Armoire Dashboard]]

## Source files

- `essensys-memory/openspec/changes/essensys-gateway-armoire-dashboard-2026-06-033/`
