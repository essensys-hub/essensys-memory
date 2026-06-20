## ADDED Requirements

### Requirement: Default Scénarios sync profile seed

In addition to existing heating and shutter profile seeds, the system SHALL create a default profile template:

| name | index_ranges | interval_hours |
|------|--------------|----------------|
| Scénarios | [[592, 919]] | 3 |

#### Scenario: Fresh install includes scenarios profile

- **WHEN** scenario migration seed runs on a database with existing sync_profiles seeds
- **THEN** the Scénarios profile template is present

### Requirement: Scenario profile validation

The system SHALL allow index range 592–919 (328 indices) and plan 11 pull chunks of 30, 30, …, 8 indices.

#### Scenario: Scenarios range chunk count

- **WHEN** an admin creates or validates the Scénarios profile with range 592–919
- **THEN** the scheduler plans 11 sequential pull chunks

### Requirement: Exclude index 590 from profile push filter

Sync profile configuration SHALL support an optional `exclude_indices` list; the Scénarios profile seed SHALL set `exclude_indices: [590]`.

#### Scenario: Scenarios profile excludes trigger

- **WHEN** push runs for the Scénarios profile
- **THEN** index 590 is filtered out even if present in Redis
