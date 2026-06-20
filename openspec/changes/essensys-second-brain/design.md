## Context

- **État actuel** : `essensys-memory` contient un vault Obsidian scaffoldé (second-brain wizard) avec `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/second-brain.mdc`. Le monorepo parent `/Users/nrineau/ESSENSYS` regroupe ~40 dépôts Git. La doc d'architecture existe dans `docs/architecture/` (générée 2026-06-16). OpenSpec n'est actif que dans `essensys-raspberry-gateway` (2 changes : dual-nic, nixos).
- **Contraintes** : `raw/` est immuable ; le brain ne remplace pas le code source ; les LLM doivent pouvoir naviguer sans ingérer 3 Go d'artefacts Android.
- **Stakeholders** : développeurs firmware/backend/frontend, agents IA (Cursor, Claude Code, Codex), futur `essensys-mcp`.

## Goals / Non-Goals

**Goals:**

- Mémoire centralisée legacy + modern stack, navigable par wikilinks.
- Roadmap pilotée par OpenSpec (changes = unités de travail traçables).
- Timeline Git datée par dépôt pour comprendre l'évolution.
- Règles claires : quand et comment mettre à jour le brain.
- Bootstrap initial : architecture + timeline + index roadmap.

**Non-Goals:**

- RAG vectoriel ou base Redis (Phase ultérieure, couplage `essensys-mcp`).
- Ingestion ligne-par-ligne de tout le code source (résumés par dépôt/module seulement).
- Déplacer les OpenSpec existants hors de leurs dépôts d'origine.
- CI automatique complète (Phase 2).

## Decisions

### D1 — Vault Obsidian comme source de vérité sémantique

**Choix** : `essensys-memory/wiki/` héberge la connaissance structurée ; `raw/` contient des copies/snapshots immuables.

**Alternatives** : Redis seul (rejeté — illisible humain) ; tout dans `docs/` du monorepo (rejeté — mélange code et mémoire agent).

### D2 — OpenSpec dans essensys-memory pour le brain lui-même

**Choix** : le change `essensys-second-brain` vit dans `essensys-memory/openspec/`. Les changes métier restent dans leurs dépôts (ex. gateway).

**Alternatives** : OpenSpec centralisé à la racine ESSENSYS (rejeté pour l'instant — chaque dépôt garde son autonomie).

### D3 — Synchronisation par scripts shell, pas par symlinks Git

**Choix** : `scripts/sync-sources.sh` copie `docs/architecture/` et indexe les OpenSpec distants dans `raw/openspec-index/`.

**Alternatives** : symlinks (fragiles cross-OS) ; submodule (complexité).

### D4 — Timeline Git = markdown généré, pas base de données

**Choix** : `scripts/extract-git-history.sh` produit `wiki/timeline/<repo>.md` avec commits (date ISO, hash court, auteur, sujet). Régénérable à la demande.

**Alternatives** : JSONL (moins lisible Obsidian) ; intégration GitHub API (nécessite réseau/token).

### D5 — Profondeur d'ingestion code : résumé architectural, pas AST

**Choix** : une page `wiki/entities/<repo>.md` par dépôt (synthèse depuis fiche architecture + README + points clés). Les fichiers source volumineux restent dans leurs dépôts ; le brain pointe vers eux.

**Alternatives** : indexation complète (trop lourd, bruit pour LLM).

### D6 — Sous-dossiers wiki ESSENSYS

```
wiki/
├── sources/      # résumés de docs/articles ingérés
├── entities/     # dépôts, cartes, services, personnes
├── concepts/     # dual-protocol, table-échange, migration…
├── synthesis/    # analyses transverses
├── roadmap/      # index OpenSpec + statuts
└── timeline/     # historique Git par repo (généré)
```

## Risks / Trade-offs

| Risque | Mitigation |
|--------|------------|
| Brain obsolète si devs ne mettent pas à jour | Règles obligatoires + checklist PR + lint mensuel |
| Duplication doc architecture / wiki | `raw/architecture/` = snapshot ; wiki = synthèse enrichie avec wikilinks |
| Timeline énorme sur gros dépôts | Limiter à N commits récents (défaut 100) + `--full` optionnel |
| OpenSpec dispersés | `raw/openspec-index/manifest.json` liste tous les changes connus |
| Confusion legacy vs modern | Tag frontmatter `era: legacy \| modern \| migration` sur chaque page entity |

## Migration Plan

1. **Phase 1 (ce change)** : scaffold, scripts, bootstrap architecture + timeline + roadmap index, règles dev.
2. **Phase 2** : ingest systématique des 40 fiches repos + concepts clés + changes OpenSpec gateway.
3. **Phase 3** : hook CI post-merge, couplage `essensys-mcp`, recherche `qmd` indexée.

Rollback : le vault est additif ; suppression de `essensys-memory/wiki/` ne touche pas le code produit.

## Open Questions

- Faut-il un change OpenSpec par dépôt ou seulement pour les évolutions cross-cutting ? → **Décision provisoire** : changes dans le dépôt concerné ; le brain agrège via manifest.
- Seuil de commit « significatif » déclenchant mise à jour manuelle ? → **Provisoire** : tout change OpenSpec + tout merge touchant protocole/table d'échange/firmware maître.
