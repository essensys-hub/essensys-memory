---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-20
updated: 2026-06-21
status: active
host_repo: essensys-memory
---

# Essensys Scenario Management

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-scenario-management`
**Status:** active
**OpenSpec created:** 2026-06-20

## Why

Les scénarios domotiques (Je sors, vacances, Personnalisé 1/2, etc.) sont **implémentés dans le firmware** BP_MQX_ETH (8 slots × 41 paramètres, indices **590–919**) et éditables depuis l'écran IHM legacy, mais **absents des UIs modernes** Go/React. Aujourd'hui :

- seul le **bloc partiel 605–622 + trigger 590=1** est géré par `ActionService` / `ExpandLegacyScenarioBlock` (actions lumières/volets immédiates) ;
- le **lancement par bouton** (`590=2..8`) existe dans le MCP mais pas dans les fronten…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 10

## Source files

- `essensys-memory/openspec/changes/essensys-scenario-management/proposal.md`
- `essensys-memory/openspec/changes/essensys-scenario-management/design.md`
- `essensys-memory/openspec/changes/essensys-scenario-management/tasks.md`
