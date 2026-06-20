## ADDED Requirements

### Requirement: Wiki concept page for scenarios

The change SHALL add or update `essensys-memory/wiki/concepts/scenarios-domotique.md` documenting Mode A/B, slot mapping, and links to [[Table D Echange]] and [[Gateway Exchange]].

#### Scenario: Wiki page exists

- **WHEN** Phase 7 documentation task completes
- **THEN** `wiki/concepts/scenarios-domotique.md` is reachable from the roadmap index

### Requirement: Roadmap entry

The change SHALL add `wiki/roadmap/changes/essensys-scenario-management.md` with status, host repo, and links to proposal/design/tasks.

#### Scenario: Roadmap lists change

- **WHEN** `scripts/update-roadmap.sh` runs after manifest update
- **THEN** the roadmap index includes essensys-scenario-management

### Requirement: Gateway versions changelog

The change SHALL add an entry to `essensys-raspberry-gateway/docs/versions.md` when scenario features ship to production gateway builds.

#### Scenario: Version entry documents scenarios

- **WHEN** the feature is released
- **THEN** versions.md mentions scenario UI/API/sync in the release notes section

### Requirement: OpenSpec manifest sync

The change SHALL be registered in `raw/openspec-index/manifest.json` via `scripts/sync-sources.sh`.

#### Scenario: Manifest includes change

- **WHEN** sync-sources runs
- **THEN** manifest.json lists essensys-scenario-management under essensys-memory host
