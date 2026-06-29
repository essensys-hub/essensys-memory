---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-22
updated: 2026-06-28
status: active
host_repo: essensys-memory
---

# Essensys Ui E2e Playwright 2026 06.026

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-ui-e2e-playwright-2026-06.026`
**Status:** active
**OpenSpec created:** 2026-06-22

## Why

Les régressions UI (chauffage, scénarios, éclairage, jumeaux local/portail/démo) ne sont pas couvertes par une suite **E2E navigateur** unique. Les scripts Python existants (`test_chb3.py`, `e2e_scenarios_portal.sh`) injectent de vraies actions vers la **file firmware** — risqué sur une installation réelle (armoire SC944D).

Il faut un **mode test** : valider les payloads et les valeurs **reçues** (table d'échange / API) **sans enqueue** vers l'armoire, puis des tests **Playwright** rejouables s…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 2

## Source files

- `essensys-memory/openspec/changes/essensys-ui-e2e-playwright-2026-06.026/proposal.md`
- `essensys-memory/openspec/changes/essensys-ui-e2e-playwright-2026-06.026/design.md`
- `essensys-memory/openspec/changes/essensys-ui-e2e-playwright-2026-06.026/tasks.md`
