## ADDED Requirements

### Requirement: Product roadmap rubric page

The vault SHALL maintain `wiki/roadmap/product-roadmap-rubric.md` defining Phase 0 gate, change sizing rules, and link to living priorities doc.

#### Scenario: New developer onboarding

- **WHEN** a developer reads [[Roadmap OpenSpec]]
- **THEN** they find a wikilink to [[Product Roadmap Rubric]]
- **AND** understand Phase 0 must complete before feature epics

### Requirement: Living product roadmap

The vault SHALL maintain `wiki/synthesis/product-roadmap.md` with gap matrix and Now / Next / Later horizons, each item linked to an OpenSpec change or `> [!todo]`.

#### Scenario: Epic prioritized

- **WHEN** an item moves from Next to Now in product-roadmap.md
- **THEN** a corresponding OpenSpec change exists or is created in the appropriate host repo

### Requirement: Phase 0 gate

No new feature epic SHALL be marked **Now** in product-roadmap.md until changes `essensys-centralized-doc-maintenance` and `essensys-install-doc-platform` are **completed**.

#### Scenario: Agent plans trusted devices epic

- **WHEN** Phase 0 changes have unchecked tasks
- **THEN** trusted devices remains in Next or Later, not Now
