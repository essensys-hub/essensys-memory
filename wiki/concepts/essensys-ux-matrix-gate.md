---
tags: [concept, ux, playwright, regression, gate, no-armoire]
sources: [essensys-ux-matrix-gate-2026-06-030]
created: 2026-06-28
updated: 2026-06-28
era: modern
---

# ESSENSYS UX Matrix Gate

ESSENSYS UX Matrix Gate est une gate lifecycle bloquante pour les features UI. Elle impose des tests Playwright et preuves de non-régression sur desktop, iPhone et iPad.

## Ce qui est maintenant obligatoire

- `features/<id>.json` doit déclarer `tests.ux_matrix` pour toute feature UI.
- La matrice minimale est `desktop`, `iphone`, `ipad`.
- Les projects Playwright requis doivent couvrir ces formats.
- Les specs doivent porter des annotations du type `@devices: desktop,iphone,ipad`.
- Les UIs domotiques doivent déclarer `no_armoire_required=true`.
- `check_feature_gate.py --strict` bloque si la déclaration UX est absente ou incomplète.

## Artefacts

- OpenSpec : `essensys-feature-lifecycle/openspec/changes/essensys-ux-matrix-gate-2026-06-030`.
- Schema : `features/schema/feature.schema.json`.
- Gate : `scripts/feature_lifecycle/check_feature_gate.py`.
- Rule : `.cursor/rules/essensys-ux-matrix-gate.mdc`.
- Skill : `.cursor/skills/essensys-ux-regression-gate/SKILL.md`.
- Template CI : `ux-matrix-gate.yml.tpl`.

## Liens

- [[Feature Lifecycle]]
- [[UI Multi Device Testing]]
- [[ESSENSYS OKF Memory Sync]]
