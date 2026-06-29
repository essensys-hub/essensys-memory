# okf-roadmap-portals

## ADDED Requirements

### Requirement: Roadmap integration

The OKF base MUST integrate the ESSENSYS roadmap and OpenSpec changes relevant to 2025 and 2026.

#### Scenario: Roadmap concepts are generated

- **GIVEN** `wiki/roadmap/index.md`, `openspec/changes/**`, and `content/roadmap/site/**` exist
- **WHEN** roadmap OKF generation runs
- **THEN** OKF contains roadmap concepts for active, completed, and planned changes
- **AND** each concept records status, host repository, scope, dependencies when known, and citations to source roadmap/OpenSpec files

#### Scenario: 2025/2026 horizon is explicit

- **GIVEN** a roadmap item or portal deployment source includes 2025 or 2026 timing
- **WHEN** the OKF concept is generated
- **THEN** the concept records the year/horizon explicitly
- **AND** unknown timing is recorded as `TBD` rather than invented

### Requirement: Portal catalog

The OKF base MUST include a catalog of ESSENSYS portals and user/admin surfaces.

#### Scenario: Local and cloud portals are represented

- **GIVEN** the discovery covers server frontend/backend, user portal frontend/backend, support site, doc site, roadmap site, gateway, and install docs
- **WHEN** portal OKF generation completes
- **THEN** concepts exist for LAN local portal, cloud user portal, support site, documentation site, roadmap site, admin surfaces, and gateway install/control surfaces where sources exist
- **AND** each concept identifies user audience, deployment target, backing repositories, APIs, and known authentication/security gates

#### Scenario: Portal deployment state is source-backed

- **GIVEN** a portal is described as deployed, planned, active, or completed
- **WHEN** its OKF concept is generated
- **THEN** the state is backed by roadmap/OpenSpec/wiki/source citation
- **AND** unsupported claims are marked as gaps in the coverage report

### Requirement: Roadmap to architecture traceability

The OKF base MUST connect roadmap items to affected architecture and protocol concepts.

#### Scenario: Architecture-impacting roadmap items are linked

- **GIVEN** a roadmap item touches gateway, LAN IAM, scenarios, MCU panels, cloud sync, security, docs, install, or portals
- **WHEN** its OKF concept is generated
- **THEN** it links to affected system, portal, process, and protocol concepts
- **AND** it identifies local gateway vs OVH/cloud impact where applicable
