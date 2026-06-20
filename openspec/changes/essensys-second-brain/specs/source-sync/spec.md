## ADDED Requirements

### Requirement: Architecture documentation sync

The system SHALL provide `scripts/sync-sources.sh` that copies the monorepo path `docs/architecture/` into `raw/architecture/` relative to the ESSENSYS workspace root (`../docs/architecture/` from vault).

#### Scenario: Sync from monorepo

- **WHEN** `scripts/sync-sources.sh` is executed with `ESSENSYS_ROOT=/Users/nrineau/ESSENSYS`
- **THEN** all files under `docs/architecture/` are copied to `raw/architecture/`
- **AND** a sync timestamp is appended to `wiki/log.md`

### Requirement: OpenSpec manifest generation

The system SHALL provide logic in `scripts/sync-sources.sh` that scans `ESSENSYS_ROOT/*/openspec/changes/*/` and writes `raw/openspec-index/manifest.json` listing each change name, host repo, paths, and `.openspec.yaml` creation date if present.

#### Scenario: Gateway changes discovered

- **WHEN** sync runs and `essensys-raspberry-gateway/openspec/changes/essensys-gateway-nixos/` exists
- **THEN** `manifest.json` includes an entry with `change: essensys-gateway-nixos`, `repo: essensys-raspberry-gateway`

### Requirement: Configurable workspace root

Sync scripts MUST accept `ESSENSYS_ROOT` environment variable defaulting to the parent directory of the vault (`dirname vault)/..` resolved absolutely).

#### Scenario: Custom monorepo path

- **WHEN** `ESSENSYS_ROOT=/custom/path scripts/sync-sources.sh` is run
- **THEN** sync reads architecture docs from `/custom/path/docs/architecture/`
