# roadmap-queue-registry

## ADDED Requirements

### Requirement: Ordered OpenSpec queue

The product roadmap SHALL maintain an ordered list of OpenSpec changes each identified by a unique `2026-06.NNN` suffix.

#### Scenario: Developer picks next epic

- **WHEN** Phase 0 changes are completed
- **THEN** the developer consults `wiki/roadmap/openspec-queue-2026-06.md`
- **AND** selects the lowest-numbered epic whose dependencies are satisfied and status is planned or active

### Requirement: Roadmap ID on changes

Each OpenSpec change directory SHALL declare `roadmap_id` in `.openspec.yaml` when mapped to the queue.

#### Scenario: Agent resolves change from ID

- **WHEN** an agent receives roadmap ID `2026-06.013`
- **THEN** it resolves to change folder `essensys-trusted-devices-2026-06.013` or the legacy folder documented in the queue table
