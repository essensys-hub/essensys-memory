# ESSENSYS-BRAIN

> Mémoire persistante Essensys — legacy + modern stack, roadmaps OpenSpec, timeline Git, contexte LLM.

Vault Obsidian + OpenSpec pour centraliser la connaissance des ~40 dépôts ESSENSYS.

## Quick start

```bash
# 1. Synchroniser docs + manifest OpenSpec
ESSENSYS_ROOT=/Users/nrineau/ESSENSYS ./scripts/sync-sources.sh

# 2. Extraire historique Git (100 derniers commits/repo)
ESSENSYS_ROOT=/Users/nrineau/ESSENSYS ./scripts/extract-git-history.sh

# 3. Mettre à jour la roadmap OpenSpec
./scripts/update-roadmap.sh
```

Ouvrir ce dossier dans **Obsidian**. Clipper des articles vers `raw/` avec [Obsidian Web Clipper](https://chromewebstore.google.com/detail/obsidian-web-clipper/cnjifjpddelmedmihgijeibhnjfabmlf).

## Structure

```
raw/              Sources immuables (architecture, plans, index OpenSpec)
wiki/             Connaissance structurée (entities, concepts, roadmap, timeline)
openspec/         Changes OpenSpec du brain lui-même
scripts/          sync-sources, extract-git-history, update-roadmap, ingest-architecture-repos, lint-wiki
output/           Rapports générés
```

## Workflows agent

| Commande | Action |
|----------|--------|
| `/second-brain-ingest` | Doc/code → pages wiki |
| `/second-brain-query` | Interroger le wiki |
| `/second-brain-lint` | Contrôle santé (mensuel / 10 ingests) |
| `/openspec-propose` | Nouveau change OpenSpec |

## OpenSpec actifs

Voir [[Roadmap OpenSpec]] — changes dans `essensys-raspberry-gateway` + `essensys-memory`.

Change en cours : **essensys-second-brain** (foundation du brain).

## Règles dev

Documentées dans `.cursor/rules/essensys-brain.mdc` (monorepo ESSENSYS) et `openspec/changes/essensys-second-brain/specs/dev-maintainability/spec.md`.

## Phase 2 — ✅ complete

- **40 entités** dans `wiki/entities/` (legacy + modern + firmware + HAL)
- **4 concepts** : Dual Protocol, Table d'échange, Cloud Relay, Gateway Exchange
- **2 sources** ingérées + synthèse migration enrichie
- **5 changes roadmap** (3 actifs + 2 planifiés)
- Lint : 0 erreurs

```bash
python3 scripts/ingest-architecture-repos.py   # regénérer entités
python3 scripts/lint-wiki.py                     # contrôle santé
```

## Phase 3 — ✅ complete

- **GitHub Action** `.github/workflows/brain-sync.yml` (push + hebdo)
- **Hook git** : `./scripts/install-git-hook.sh` (post-merge timeline)
- **Refresh complet** : `./scripts/refresh-all.sh`
- **qmd** : 96 docs indexés, collection `wiki` — `qmd query -c wiki "…"`
- **Protocol ingest** : `raw/protocol/` (TableEchange.h, exchange-table, dual-protocol…)
- **essensys-mcp** : `./run-brain-mcp.sh` (6 tools MCP)
- **Workflow** : `docs/WORKFLOW.md`

```bash
./scripts/refresh-all.sh              # tout regénérer
./scripts/index-qmd.sh                # réindexer recherche
../essensys-mcp/run-brain-mcp.sh      # MCP pour Cursor
```
