---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-20
updated: 2026-06-22
status: completed
host_repo: essensys-memory
---

# Essensys Cloud Sync Scheduler

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-cloud-sync-scheduler`
**Status:** completed
**OpenSpec created:** 2026-06-20

## Why

La table d'échange domotique (indices **13–348** planning chauffage, **566–589** volets, **349–352** modes immédiats, etc.) n'est **pas remontée automatiquement** par le cycle firmware `serverinfos → mystatus` : le BP_MQX_ETH limite à **30 indices** par requête. Aujourd'hui :

- le cache Redis gateway et le cache cloud `gateway_exchange_cache` ne contiennent que les indices déjà injectés ou listés dans `serverinfos` ;
- la **sync manuelle** (bouton « Sync armoire » chauffage) fonctionne mais n'e…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 4

## Source files

- `essensys-memory/openspec/changes/essensys-cloud-sync-scheduler/proposal.md`
- `essensys-memory/openspec/changes/essensys-cloud-sync-scheduler/design.md`
- `essensys-memory/openspec/changes/essensys-cloud-sync-scheduler/tasks.md`
