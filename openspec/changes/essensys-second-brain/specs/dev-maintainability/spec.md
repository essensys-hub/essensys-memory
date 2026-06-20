## ADDED Requirements

### Requirement: Developer update triggers

Developers and AI agents MUST update the brain when any of the following occur: (1) a new OpenSpec change is created, (2) an OpenSpec change reaches `tasks` completion, (3) a merge affects legacy IoT protocol, table d'échange indices, or master firmware (SC944D), (4) a new repository is added to the monorepo.

#### Scenario: New OpenSpec change in gateway

- **WHEN** a developer runs `openspec new change "my-feature"` in `essensys-raspberry-gateway`
- **THEN** they run `scripts/sync-sources.sh && scripts/update-roadmap.sh` in `essensys-memory`
- **AND** append a log entry to `wiki/log.md`

### Requirement: Cursor rule in monorepo root

The ESSENSYS monorepo SHALL include `.cursor/rules/essensys-brain.mdc` pointing agents to `essensys-memory/` and listing the update triggers above.

#### Scenario: Agent working in server-backend

- **WHEN** a Cursor agent modifies dual-protocol handling in `essensys-server-backend`
- **THEN** the rule reminds the agent to update relevant concept pages in the brain

### Requirement: PR checklist item

Contributors SHOULD include in PR descriptions: `[ ] Brain updated (essensys-memory)` when the change meets any update trigger.

#### Scenario: PR without brain impact

- **WHEN** a PR only fixes a typo in comments with no architectural impact
- **THEN** the checkbox may be marked N/A

### Requirement: Monthly lint

Maintainers SHALL run `/second-brain-lint` on the vault at least monthly and after every 10 ingests.

#### Scenario: Stale roadmap detected

- **WHEN** lint finds an OpenSpec change in manifest but missing from `wiki/roadmap/`
- **THEN** lint report lists the gap and suggests running `scripts/update-roadmap.sh`
