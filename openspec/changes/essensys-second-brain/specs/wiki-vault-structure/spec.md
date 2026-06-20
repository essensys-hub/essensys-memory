## ADDED Requirements

### Requirement: Vault directory layout

The ESSENSYS-BRAIN vault SHALL maintain the following top-level directories: `raw/`, `raw/assets/`, `raw/architecture/`, `raw/openspec-index/`, `wiki/` (with subdirs `sources/`, `entities/`, `concepts/`, `synthesis/`, `roadmap/`, `timeline/`), `output/`, `scripts/`, and `openspec/`.

#### Scenario: Fresh clone bootstrap

- **WHEN** a contributor clones `essensys-memory` and runs `scripts/sync-sources.sh`
- **THEN** `raw/architecture/` contains a copy of the monorepo `docs/architecture/` tree
- **AND** `wiki/index.md` and `wiki/log.md` exist at vault root under `wiki/`

### Requirement: Page frontmatter schema

Every wiki page under `wiki/` (except `index.md` and `log.md`) MUST include YAML frontmatter with fields: `tags`, `sources`, `created`, `updated`, and SHOULD include `era` (`legacy`, `modern`, or `migration`) for entity pages.

#### Scenario: New entity page creation

- **WHEN** an agent creates `wiki/entities/essensys-server-backend.md`
- **THEN** the file includes `era: modern` in frontmatter
- **AND** uses `[[wikilink]]` syntax for cross-references

### Requirement: Immutability of raw sources

Files under `raw/` MUST NOT be modified by ingest or query operations. Only sync scripts MAY overwrite `raw/architecture/` and `raw/openspec-index/` during explicit sync runs.

#### Scenario: Ingest of architecture doc

- **WHEN** `/second-brain-ingest` processes a file in `raw/architecture/`
- **THEN** the source file in `raw/` remains unchanged
- **AND** new or updated content is written only under `wiki/`
