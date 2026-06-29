---
type: Process
title: ESSENSYS UX Matrix Gate
description: Gate lifecycle bloquante imposant tests Playwright desktop, iPhone et iPad pour toute feature UI ESSENSYS.
tags: [essensys, ux, playwright, regression, gate, no-armoire]
timestamp: 2026-06-28T07:25:59Z
resource: file:///Users/nrineau/ESSENSYS/essensys-feature-lifecycle/openspec/changes/essensys-ux-matrix-gate-2026-06-030
---

# Rôle

ESSENSYS UX Matrix Gate force la preuve de non-régression UX pour chaque feature UI. Une feature UI ne peut plus se contenter d'un manifest valide : elle doit déclarer et prouver une matrice desktop + iPhone + iPad.

# Contrat manifest

Le manifest `features/<id>.json` accepte maintenant :

* `tests.ux_matrix.required: true`
* `tests.ux_matrix.devices` contenant au minimum `desktop`, `iphone`, `ipad`
* `tests.ux_matrix.required_projects` couvrant ces devices
* `tests.ux_matrix.screenshots_required: true`
* `tests.ux_matrix.visual_regression_required: true`
* `tests.ux_matrix.no_armoire_required: true` pour UI domotique
* `tests.ux_evidence` pour rapport Playwright, captures, devices validés et statut

# Gate bloquante

`scripts/feature_lifecycle/check_feature_gate.py --strict` détecte une feature UI depuis `primary_surface`, les chemins frontend (`src/pages`, `src/components`, `.tsx`, e2e/Playwright) ou les surfaces release. Si la matrice UX est absente ou incomplète, la gate échoue.

# Artefacts

* OpenSpec : `essensys-feature-lifecycle/openspec/changes/essensys-ux-matrix-gate-2026-06-030`
* Checker : `scripts/feature_lifecycle/check_feature_gate.py`
* Schema : `features/schema/feature.schema.json`
* Rule : `.cursor/rules/essensys-ux-matrix-gate.mdc`
* Skill : `.cursor/skills/essensys-ux-regression-gate/SKILL.md`
* Template CI : `.cursor/skills/feature-lifecycle-bootstrap/templates/.github/workflows/ux-matrix-gate.yml.tpl`

# No-armoire

Pour les UIs domotiques, la gate impose `no_armoire_required=true` et les tests doivent bloquer ou mocker les mutations vers `/api/admin/inject`, `/api/portal/inject`, `/api/web/actions` et `/scenarios/*/launch` sauf dry-run explicite.

# Citations

[1] OpenSpec: `file:///Users/nrineau/ESSENSYS/essensys-feature-lifecycle/openspec/changes/essensys-ux-matrix-gate-2026-06-030`
[2] Rule: `file:///Users/nrineau/ESSENSYS/essensys-feature-lifecycle/.cursor/rules/essensys-ux-matrix-gate.mdc`
[3] Skill: `file:///Users/nrineau/ESSENSYS/essensys-feature-lifecycle/.cursor/skills/essensys-ux-regression-gate/SKILL.md`
