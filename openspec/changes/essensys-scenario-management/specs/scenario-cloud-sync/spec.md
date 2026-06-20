## ADDED Requirements

### Requirement: Default scenarios sync profile

The system SHALL seed a default sync profile named **Scénarios** with `index_ranges: [[592, 919]]`, `interval_hours: 3`, `pull_from_armoire: true`, `push_to_cloud: true`, `enabled: true`.

#### Scenario: Seed on migration

- **WHEN** the scenarios migration runs
- **THEN** the Scénarios profile template exists alongside existing heating/shutter profiles

### Requirement: Pull scenario definitions from armoire

The gateway scheduler SHALL pull indices 592–919 in chunks of at most 30 indices per firmware cycle using `ExchangePullScheduler`.

#### Scenario: Full scenario range pull

- **WHEN** a scheduled Scénarios profile run completes successfully
- **THEN** Redis contains keys for all 328 indices in range 592–919

### Requirement: Exclude trigger index 590 from continuous push

The gateway SHALL NOT include index 590 in routine `pushExchange` payloads because firmware resets it to 0 after execution.

#### Scenario: Push after scenario launch

- **WHEN** a user launches Je sors and push runs immediately after
- **THEN** index 590 is omitted from the pushed keys

#### Scenario: Index 591 included

- **WHEN** push runs after a scenario launch and index 591 is present in Redis
- **THEN** index 591 (last launched) SHALL be included in the pushed keys

### Requirement: Settings UI toggle for scenario sync

The existing Sync Settings panel SHALL include a toggle **Synchroniser les scénarios** bound to the Scénarios profile `enabled` flag.

#### Scenario: Disable scenario sync

- **WHEN** the user disables scenario sync in Settings
- **THEN** the Scénarios profile is set to `enabled: false` and no scheduled pulls run for that profile

### Requirement: Cloud definition merge after pull

After a successful pull, the portal backend SHALL merge pulled values into `scenario_definitions.params` when no newer local edit exists (`updated_at` comparison).

#### Scenario: Pull updates cloud definition

- **WHEN** armoire slot 7 params change on-site and pull completes
- **THEN** cloud GET /api/portal/scenarios/7 reflects the pulled values
