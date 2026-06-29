# okf-repository-discovery

## ADDED Requirements

### Requirement: Repository inventory coverage

The OKF discovery MUST inventory every local ESSENSYS Git repository under `/Users/nrineau/ESSENSYS` and map each repository to at least one OKF concept or an explicit non-coverage reason.

#### Scenario: All local repositories are enumerated

- **GIVEN** the local workspace contains ESSENSYS Git repositories
- **WHEN** the discovery inventory runs
- **THEN** it records every repository name found under `/Users/nrineau/ESSENSYS`
- **AND** it classifies each repository by layer: firmware, armoire, gateway/LAN, cloud, infra, documentation, tooling, MCP, memory, or legacy
- **AND** it writes the inventory result to the OKF coverage report

#### Scenario: Every repository has an OKF representation

- **GIVEN** a repository is included in the discovery inventory
- **WHEN** OKF generation completes
- **THEN** the repository has a concept document in `okf/systems/` or a more specific OKF subdirectory
- **OR** the coverage report explains why the repository was not converted

### Requirement: Repository concept structure

Each generated repository concept MUST be source-backed and structured for both humans and agents.

#### Scenario: Repository concept contains required sections

- **GIVEN** a repository concept is generated
- **WHEN** the concept file is read
- **THEN** its frontmatter contains non-empty `type`, `title`, `description`, `tags`, and `timestamp`
- **AND** its body includes `# Rôle`, `# Interfaces`, `# Dépendances`, `# Code pointers`, `# Risques`, and `# Citations` sections when applicable
- **AND** it avoids copying full source code

#### Scenario: Existing wiki knowledge is reused before raw repository inference

- **GIVEN** a matching wiki entity page exists for a repository
- **WHEN** the repository OKF concept is generated
- **THEN** the concept cites the wiki page
- **AND** it only falls back to repository files for missing details or verification

### Requirement: Cross-repository relationships

The OKF discovery MUST capture relationships between repositories that matter for architecture, protocol compatibility, deployment, and UI/backend synchronization.

#### Scenario: Twin repositories are linked

- **GIVEN** the discovery covers `essensys-server-frontend`, `essensys-user-portal-frontend`, `essensys-server-backend`, and `essensys-user-portal-backend`
- **WHEN** the OKF concepts are generated
- **THEN** UI twin and backend twin relationships are represented with markdown links and prose explaining synchronization obligations
