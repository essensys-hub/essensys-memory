## ADDED Requirements

### Requirement: Install doc Cursor rule

The ESSENSYS monorepo SHALL include `.cursor/rules/essensys-install-doc.mdc` with globs for ansible, raspberry-install, and raspberry-gateway; triggers on playbook, env template, or install script changes.

#### Scenario: Ansible gateway playbook edit

- **WHEN** `install.gateway.yml` or `roles/raspberry_backend/tasks/cloud_sync.yml` changes
- **THEN** the agent updates `wiki/concepts/install-documentation.md` or ingests relevant excerpt
- **AND** appends `wiki/log.md`

### Requirement: Install documentation index

The vault SHALL maintain `wiki/concepts/install-documentation.md` indexing install paths: CM5 gateway, cloud register, TLS local, WAN tests.

#### Scenario: Support looks up recovery

- **WHEN** a user reads install-documentation concept
- **THEN** they find wikilinks to [[Essensys Ansible]] install-gateway source and gateway register API

### Requirement: Dependency on centralized doc rule

Install doc updates SHALL follow the same traceability rules as `essensys-centralized-doc.mdc` (sources cited, no invention).

#### Scenario: Conflicting instructions

- **WHEN** install doc and architecture entity disagree
- **THEN** agent flags conflict in log rather than silently merging
