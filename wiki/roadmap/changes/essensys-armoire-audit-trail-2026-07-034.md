---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-07-01
updated: 2026-08-24
status: active
host_repo: essensys-memory
---

# Essensys Armoire Audit Trail 2026 07 034

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-armoire-audit-trail-2026-07-034`
**Status:** active
**OpenSpec created:** 2026-07-01

## Why

Les utilisateurs et administrateurs Essensys n'ont pas aujourd'hui de **journal d'audit par armoire** couvrant les actions domotiques, les changements de configuration et les transitions d'état — seulement un audit **plateforme** (login, rôles) dans `audit_logs` / `portal_audit_log`. Sans trace append-only par `machine_id`, il est impossible de répondre de façon fiable à une demande utilisateur (« qui a fait quoi ? »), de corréler une anomalie ou de détecter une intrusion sur une installation.

…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 1

## Source files

- `essensys-memory/openspec/changes/essensys-armoire-audit-trail-2026-07-034/proposal.md`
- `essensys-memory/openspec/changes/essensys-armoire-audit-trail-2026-07-034/design.md`
- `essensys-memory/openspec/changes/essensys-armoire-audit-trail-2026-07-034/tasks.md`
