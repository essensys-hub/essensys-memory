## Why

La [[Product Roadmap]] liste des epics **Now/Next/Later** sans ordre d'exécution explicite ni identifiant stable. Les agents et devs ont besoin d'une **file OpenSpec numérotée** (`2026-06.NNN`) pour enchaîner les changes sans conflit.

## What Changes

- Registre **`wiki/roadmap/openspec-queue-2026-06.md`** — ordre canonique 001–023.
- Champ **`roadmap_id`** dans chaque `.openspec.yaml` (changes existants + nouveaux scaffolds).
- Scaffolds **planned** pour epics roadmap sans change OpenSpec dédié.
- Mise à jour [[Product Roadmap]] avec colonne ID.

## Capabilities

- `roadmap-queue-registry` : index ordonné, dépendances, statuts.

## Non-goals

- Renommer les dossiers changes existants (ex. `essensys-scenario-management`).
- Exécuter l'implémentation des epics planned.

## Liens

- [[Product Roadmap Rubric]]
- [[OpenSpec Queue 2026 06]] — `wiki/roadmap/openspec-queue-2026-06.md`
