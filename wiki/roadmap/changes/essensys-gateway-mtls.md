---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-21
updated: 2026-06-25
status: active
host_repo: essensys-memory
---

# Essensys Gateway Mtls

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-gateway-mtls`
**Status:** active
**OpenSpec created:** 2026-06-21

## Why

L’authentification gateway cloud repose sur un **secret partagé** (`gateway_token`) et des **MAC Ethernet** en headers — suffisant pour le NAT traversal initial, insuffisant pour une identité matérielle forte et une révocation fine. Voir [[Gateway PKI]].

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 0

## Source files

- `essensys-memory/openspec/changes/essensys-gateway-mtls/proposal.md`
- `essensys-memory/openspec/changes/essensys-gateway-mtls/design.md`
- `essensys-memory/openspec/changes/essensys-gateway-mtls/tasks.md`
