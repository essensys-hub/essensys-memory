## ADDED Requirements

### Requirement: Roadmap index page

The vault SHALL maintain `wiki/roadmap/index.md` as the canonical index of all OpenSpec changes known to the brain, organized by status: `active`, `planned`, `completed`.

#### Scenario: After sync and roadmap update

- **WHEN** `scripts/update-roadmap.sh` runs after `sync-sources.sh`
- **THEN** `wiki/roadmap/index.md` lists each change from `raw/openspec-index/manifest.json`
- **AND** includes wikilinks to per-change pages under `wiki/roadmap/changes/`

### Requirement: Per-change roadmap pages

For each OpenSpec change in the manifest, the system SHALL maintain or create `wiki/roadmap/changes/<change-name>.md` summarizing: host repo, proposal excerpt, status (derived from presence of `tasks.md` completion markers or manual flag), and links to source files.

#### Scenario: Gateway nixos change indexed

- **WHEN** roadmap update processes `essensys-gateway-nixos`
- **THEN** `wiki/roadmap/changes/essensys-gateway-nixos.md` exists
- **AND** references `[[essensys-raspberry-gateway]]` entity page

### Requirement: Local brain changes tracked

OpenSpec changes within `essensys-memory/openspec/changes/` MUST appear in the roadmap index with `host: essensys-memory`.

#### Scenario: Second brain change visible

- **WHEN** roadmap update runs
- **THEN** `essensys-second-brain` appears under `active` changes
