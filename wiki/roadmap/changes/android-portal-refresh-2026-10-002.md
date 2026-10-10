---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-10-09
updated: 2026-10-10
status: active
host_repo: essensys-android-phone-apps
---

# Android Portal Refresh 2026 10 002

**Host repo:** [[Essensys Android Phone Apps]]
**Path:** `essensys-android-phone-apps/openspec/changes/android-portal-refresh-2026-10-002`
**Status:** active
**OpenSpec created:** 2026-10-09

## Why

Un client clé veut tester Essensys sur Android, mais l'app actuelle (v1.0.0, janvier 2026) a décroché du portail sur trois plans.

- **Fonctionnel** :
  - l'app appelle `/api/admin/inject` en Basic Auth ;
  - elle ne lit aucun état ;
  - plusieurs écrans sont factices (chauffage, arrosage, scènes) ;
  - au moindre échec réseau, elle bascule silencieusement en « mode démo ».
- **Sécurité** :
  - le trafic HTTP passe en clair ;
  - le mot de passe est stocké en clair dans `SharedPreferences` ;
  -…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 5

## Source files

- `essensys-android-phone-apps/openspec/changes/android-portal-refresh-2026-10-002/proposal.md`
- `essensys-android-phone-apps/openspec/changes/android-portal-refresh-2026-10-002/design.md`
- `essensys-android-phone-apps/openspec/changes/android-portal-refresh-2026-10-002/tasks.md`
