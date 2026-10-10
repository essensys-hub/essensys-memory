---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-10-09
updated: 2026-10-10
status: active
host_repo: essensys-ios-phone-apps
---

# Ios Portal Refresh 2026 10 003

**Host repo:** [[Essensys Ios Phone Apps]]
**Path:** `essensys-ios-phone-apps/openspec/changes/ios-portal-refresh-2026-10-003`
**Status:** active
**OpenSpec created:** 2026-10-09

## Why

L'app iPhone (janvier 2026) a les mêmes défauts que l'Android v1 :
- Basic Auth, `/api/admin/inject` en cloud ;
- mot de passe en clair dans `UserDefaults`, HTTP en clair ;
- écrans en partie factices, aucun test.

Surtout, **ses sources n'existent que sur le poste du mainteneur** : un sous-module sans `.gitmodules` ni remote, que GitHub ne connaît que comme un pointeur.

Après la livraison de l'Android v2.0.0, les testeurs iPhone doivent avoir la même app.

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 5

## Source files

- `essensys-ios-phone-apps/openspec/changes/ios-portal-refresh-2026-10-003/proposal.md`
- `essensys-ios-phone-apps/openspec/changes/ios-portal-refresh-2026-10-003/design.md`
- `essensys-ios-phone-apps/openspec/changes/ios-portal-refresh-2026-10-003/tasks.md`
