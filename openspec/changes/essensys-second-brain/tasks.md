# Tasks — essensys-second-brain

## Phase 1 — Foundation (this PR)

- [x] 1.1 Create OpenSpec change `essensys-second-brain` with proposal, design, specs, tasks
- [x] 1.2 Add `openspec/config.yaml` with ESSENSYS project context
- [x] 1.3 Extend vault directories (`wiki/roadmap/`, `wiki/timeline/`, `raw/architecture/`, `raw/openspec-index/`, `scripts/`)
- [x] 1.4 Implement `scripts/sync-sources.sh` (architecture copy + OpenSpec manifest)
- [x] 1.5 Implement `scripts/extract-git-history.sh` (timeline per repo)
- [x] 1.6 Implement `scripts/update-roadmap.sh` (roadmap index + change pages)
- [x] 1.7 Run sync + history + roadmap bootstrap
- [x] 1.8 Create core wiki pages: platform overview, migration synthesis, roadmap index
- [x] 1.9 Add `.cursor/rules/essensys-brain.mdc` in ESSENSYS monorepo root
- [x] 1.10 Update `essensys-memory` agent configs with ESSENSYS-specific rules
- [x] 1.11 Update `README.md` with usage guide

## Phase 2 — Full repo ingest

- [x] 2.1 Ingest all 40 fiches from `raw/architecture/repos/` → `wiki/entities/`
- [x] 2.2 Create concept pages: [[Dual Protocol]], [[Table D Echange]], [[Cloud Relay]], [[Gateway Exchange]]
- [x] 2.3 Ingest `MIGRATION_PLAN.md` → update `wiki/synthesis/migration-legacy-to-modern.md`
- [x] 2.4 Ingest OpenSpec changes gateway (dual-nic, nixos) → roadmap detail pages (via update-roadmap.sh)
- [x] 2.5 Ingest legacy repos summaries (`client-essensys-legacy`, `essensys-web-legacy`)
- [x] 2.6 Run `/second-brain-lint` and fix gaps

## Phase 3 — Automation & MCP

- [x] 3.1 GitHub Action + git post-merge hook (`brain-sync.yml`, `install-git-hook.sh`)
- [x] 3.2 Index vault with `qmd` (`scripts/index-qmd.sh`, collection `wiki`)
- [x] 3.3 Wire `essensys-mcp` brain server (`brain_server.py`, 6 MCP tools)
- [x] 3.4 Document OpenSpec workflow (`docs/WORKFLOW.md`)
- [x] 3.5 Protocol deep ingest (`raw/protocol/`, TableEchange, exchange-table, MCP indices)

## Verification

```bash
cd essensys-memory
ESSENSYS_ROOT=/Users/nrineau/ESSENSYS ./scripts/sync-sources.sh
ESSENSYS_ROOT=/Users/nrineau/ESSENSYS ./scripts/extract-git-history.sh
./scripts/update-roadmap.sh
openspec status --change essensys-second-brain
```

Expected: `raw/architecture/` populated, `wiki/timeline/*.md` for each git repo, `wiki/roadmap/index.md` lists gateway + memory changes.
