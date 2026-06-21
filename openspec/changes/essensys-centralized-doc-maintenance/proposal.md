## Why

La doc est éclatée (`docs/architecture/`, README par dépôt, `essensys-ansible/docs/`, brain `wiki/`). Les devs et agents oublient de synchroniser après un merge. Sans **règle Cursor explicite** et carte des sources, le brain devient stale.

## What Changes

- Règle monorepo **`.cursor/rules/essensys-centralized-doc.mdc`** — quand et quoi mettre à jour.
- Concept wiki **`wiki/concepts/centralized-documentation.md`** — cartographie source canonique → brain.
- Renforcement **`AGENTS.md`** + **`essensys-brain.mdc`** (triggers doc).
- Table de correspondance dépôt → pages wiki / `raw/` / entités.

## Capabilities

### New Capabilities

- `centralized-doc-rule` : règle agent + checklist PR doc.
- `doc-source-map` : quelle doc vit où ; brain = synthèse, pas copie brute des README.

## Impact

- `.cursor/rules/`, `AGENTS.md`, `essensys-memory/wiki/concepts/`.
- Tous les futurs changes OpenSpec **doivent** inclure une tâche doc si API/protocole/déploiement touché.

## Gate Phase 0

Ce change doit être **completed** avant tout nouveau change feature planifié dans `product-roadmap.md` (sauf hotfix prod).

## Liens

- Change parent cadre : `essensys-product-roadmap`
- Existant : `essensys-second-brain` / `dev-maintainability`
