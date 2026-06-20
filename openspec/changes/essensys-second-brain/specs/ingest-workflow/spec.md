## ADDED Requirements

### Requirement: ESSENSYS-specific ingest scope

When ingesting ESSENSYS sources, agents SHALL create or update: (1) a source summary in `wiki/sources/`, (2) entity pages for each repo/service/board mentioned, (3) concept pages for cross-cutting topics (dual-protocol, table d'échange, cloud relay), and (4) update `wiki/index.md` and `wiki/log.md`.

#### Scenario: Architecture README ingest

- **WHEN** `docs/architecture/README.md` is ingested from `raw/architecture/README.md`
- **THEN** at least one synthesis page `wiki/synthesis/platform-overview.md` is created or updated
- **AND** entity stub pages are created for repos not yet present in `wiki/entities/`

### Requirement: Code ingestion depth limit

Agents MUST NOT copy full source trees into `wiki/`. Code references SHALL use repo-relative paths in a `## Code pointers` section, limited to entry points (main, cmd/, critical headers like `TableEchange.h`).

#### Scenario: Firmware repo ingest

- **WHEN** ingesting `essensys-board-SC944D`
- **THEN** the entity page summarizes role, MCU, and bus
- **AND** lists pointers such as `TableEchange.h` without duplicating file contents

### Requirement: Legacy tagging

Sources and entities originating from legacy stacks (`client-essensys-legacy`, `essensys-web-legacy`, ColdFire/MQX firmware) MUST be tagged with `era: legacy` and linked from `wiki/synthesis/migration-legacy-to-modern.md`.

#### Scenario: Legacy client ingest

- **WHEN** `client-essensys-legacy` entity page is created
- **THEN** frontmatter includes `era: legacy` and tags include `mqx` and `legacy-iot`
