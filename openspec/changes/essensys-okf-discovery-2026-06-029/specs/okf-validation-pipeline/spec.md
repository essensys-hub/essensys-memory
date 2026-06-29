# okf-validation-pipeline

## ADDED Requirements

### Requirement: OKF validation

The discovery implementation MUST include a validation step for OKF conformance and local link health.

#### Scenario: OKF conformance passes

- **GIVEN** generated files exist under `okf/`
- **WHEN** the OKF validator runs
- **THEN** every non-reserved markdown file has parseable YAML frontmatter
- **AND** every concept has a non-empty `type` field
- **AND** reserved `index.md` and `log.md` files follow the OKF conventions used by the bundle

#### Scenario: Local link validation runs

- **GIVEN** generated OKF concepts include markdown links
- **WHEN** local link validation runs
- **THEN** bundle-relative OKF links resolve
- **AND** repository-relative wiki citations resolve when they point to local files
- **AND** unresolved links are reported rather than silently ignored

### Requirement: Coverage report

The discovery implementation MUST produce a human-readable coverage report.

#### Scenario: Coverage report is written

- **GIVEN** discovery and validation have run
- **WHEN** the job completes
- **THEN** it writes `output/okf-discovery-coverage-YYYY-MM-DD.md`
- **AND** the report includes repository coverage, mandatory legacy concept coverage, roadmap/portal coverage, validation results, gaps, contradictions, and recommended follow-up tasks

### Requirement: Regeneration safety

The discovery implementation MUST be safe to rerun without destroying manual curation.

#### Scenario: Regeneration preserves curated unknown fields

- **GIVEN** an OKF concept already exists and contains producer-defined fields or curated notes
- **WHEN** discovery reruns
- **THEN** it updates source-backed generated sections deterministically
- **AND** it preserves unknown frontmatter fields and explicitly marked curated sections where possible
- **AND** it reports any overwrite risk before replacing non-generated content

### Requirement: Brain bookkeeping

The discovery implementation MUST keep ESSENSYS brain indexes and logs consistent.

#### Scenario: Indexes and logs are updated

- **GIVEN** new OKF or wiki concepts are created
- **WHEN** the discovery implementation completes
- **THEN** `okf/index.md` and relevant subdirectory `index.md` files are updated
- **AND** `okf/log.md` receives a dated entry
- **AND** `wiki/index.md` and `wiki/log.md` are updated when wiki pages are created or changed
