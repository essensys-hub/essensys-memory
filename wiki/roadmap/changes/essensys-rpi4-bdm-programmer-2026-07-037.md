---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-07-28
updated: 2026-08-24
status: active
host_repo: essensys-memory
---

# Essensys Rpi4 Bdm Programmer 2026 07 037

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-rpi4-bdm-programmer-2026-07-037`
**Status:** active
**OpenSpec created:** 2026-07-28

## Why

La carte `essensys-board-SC944D` (MCF52259, ColdFire V2, flash interne 512 KB) n'a aujourd'hui qu'un
chemin de programmation historique : **P&E Micro BDM + CodeWarrior**, manuel, non reproductible, non
outillé en CI. `essensys-gcc` sait déjà produire `BP_MQX_ETH-<VERSION>.s19`, mais rien n'automatise
l'extraction d'un backup fiable de la flash existante ni la programmation vérifiée de la nouvelle image.
Le risque dominant est le **brick** : effacer/écraser le bootloader (`0x0-0x3000`), la persis…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 2

## Source files

- `essensys-memory/openspec/changes/essensys-rpi4-bdm-programmer-2026-07-037/proposal.md`
- `essensys-memory/openspec/changes/essensys-rpi4-bdm-programmer-2026-07-037/design.md`
- `essensys-memory/openspec/changes/essensys-rpi4-bdm-programmer-2026-07-037/tasks.md`
