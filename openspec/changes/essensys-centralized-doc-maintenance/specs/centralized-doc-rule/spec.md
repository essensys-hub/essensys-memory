## ADDED Requirements

### Requirement: Centralized doc Cursor rule

The ESSENSYS monorepo SHALL include `.cursor/rules/essensys-centralized-doc.mdc` describing doc update triggers and target wiki pages per change type.

#### Scenario: API change in server-backend

- **WHEN** an agent modifies `/api/scenarios` handlers
- **THEN** the rule directs updating brain concepts if behavior is user-visible and running lint-wiki

### Requirement: Doc source map concept page

The vault SHALL maintain `wiki/concepts/centralized-documentation.md` with a table mapping repositories to wiki/raw update obligations.

#### Scenario: New repository added

- **WHEN** a new essensys-* repo joins the monorepo
- **THEN** the doc map is extended with entity ingest + architecture doc sync

### Requirement: PR doc checklist

`AGENTS.md` SHALL reference centralized doc rule alongside brain checklist.

#### Scenario: PR template

- **WHEN** a contributor opens a PR touching protocol or API
- **THEN** they verify `[ ] Doc/brain updated per essensys-centralized-doc.mdc`
