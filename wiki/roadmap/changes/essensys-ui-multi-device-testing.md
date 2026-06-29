---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-27
updated: 2026-06-28
status: active
host_repo: essensys-memory
---

# Essensys Ui Multi Device Testing

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-ui-multi-device-testing`
**Status:** active
**OpenSpec created:** 2026-06-27

## Why

Les frontends Essensys (support, local CM5/Raspberry, remote portail) sont des **jumeaux React** déployés sur des surfaces très différentes — iPhone, Android, iPad, écran domotique tactile, desktop. Aujourd'hui, Playwright ne couvre que **Desktop Chrome** sur 3 cibles (`demo` / `local` / `remote`) dans `essensys-server-frontend/e2e/`, sans matrice device ni couverture du support-site.

Les régressions d'affichage (menu tronqué à 800×480, `BottomTabs` cassé, hero illisible) ne sont pas détectées …

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 6

## Source files

- `essensys-memory/openspec/changes/essensys-ui-multi-device-testing/proposal.md`
- `essensys-memory/openspec/changes/essensys-ui-multi-device-testing/design.md`
- `essensys-memory/openspec/changes/essensys-ui-multi-device-testing/tasks.md`
