# doc-site-publish

## ADDED Requirements

### Requirement: Public doc site on OVH

The system SHALL publish a static documentation site reachable over HTTPS on the Essensys OVH VPS (target hostname `docs.essensys.fr` or equivalent path documented in Ansible).

#### Scenario: User opens documentation home

- **WHEN** a user navigates to the public doc URL
- **THEN** they receive a MkDocs-generated index with install and overview sections
- **AND** the response is served by Nginx from a static directory (no application server in prod)

### Requirement: Content scope

The public site SHALL aggregate user-facing content from canonical repos without replacing the brain vault.

#### Scenario: Install guide available

- **WHEN** the site is built
- **THEN** gateway install and HTTPS local user guides are reachable from the nav
- **AND** agent skills and Obsidian vault content are excluded

### Requirement: Deploy pipeline

The system SHALL rebuild and deploy the site via CI and Ansible on change to documented sources.

#### Scenario: Doc source updated

- **WHEN** a PR merges to `essensys-doc` or linked install doc paths
- **THEN** CI produces a static `site/` artifact
- **AND** Ansible deploys it to the OVH docs path and reloads Nginx

### Requirement: Support site link

The support-site SPA SHALL link to the public documentation URL from its main navigation.

#### Scenario: Support user finds docs

- **WHEN** a user opens `mon.essensys.fr`
- **THEN** a Documentation entry points to the public doc site
