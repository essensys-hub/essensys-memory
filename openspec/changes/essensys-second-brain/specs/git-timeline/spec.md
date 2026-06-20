## ADDED Requirements

### Requirement: Git history extraction script

The system SHALL provide `scripts/extract-git-history.sh` that iterates Git repositories under `ESSENSYS_ROOT` and generates one markdown file per repo at `wiki/timeline/<repo-name>.md`.

#### Scenario: Extract recent commits

- **WHEN** `scripts/extract-git-history.sh` runs with default `COMMIT_LIMIT=100`
- **THEN** each timeline file lists up to 100 most recent commits
- **AND** each entry includes ISO date, short hash, author, and subject line

### Requirement: Timeline page format

Each timeline file MUST begin with YAML frontmatter (`tags: [timeline, git]`, `repo`, `updated`) and a heading `# Timeline — <repo-name>`. Commits MUST be listed newest-first under `## Commits`.

#### Scenario: Timeline readability

- **WHEN** a developer opens `wiki/timeline/essensys-server-backend.md` in Obsidian
- **THEN** commits are sorted with the latest at the top
- **AND** each line is `- **YYYY-MM-DD** `abc1234` — subject (author)`

### Requirement: Skip non-git and empty repos

The extraction script SHALL skip directories without a `.git` folder and SHALL log skipped paths to stderr without failing the overall run.

#### Scenario: Mixed monorepo layout

- **WHEN** `docs/` (no `.git`) and `essensys-server-backend/` (with `.git`) both exist under `ESSENSYS_ROOT`
- **THEN** only `essensys-server-backend` receives a timeline file
