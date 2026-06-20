## ADDED Requirements

### Requirement: Scenario definition entity

The system SHALL model each scenario slot (1–8) as exactly **41** byte parameters matching `Scenario_NB_VALEURS`, keyed by absolute exchange index or by offset 0–40 within the slot.

#### Scenario: Slot 3 definition size

- **WHEN** a definition is stored for slot 3
- **THEN** it contains 41 parameter entries covering indices 674–714 inclusive

### Requirement: Bitmask validation

For parameters documented as bitmasks in `enumScenario` (lighting and shutter fields), the system SHALL accept values 0–255 and reject values > 255.

#### Scenario: Invalid bitmask rejected

- **WHEN** a client submits value `"300"` for index 613
- **THEN** the API returns HTTP 400 with a validation error

### Requirement: Restore firmware preset

The system SHALL support restoring a predefined firmware preset for slots 2–8 by writing `Scenario_Efface` (offset 40, absolute index base+40) with values 2–6 as defined in firmware for Je sors, vacances, Je rentre, coucher, lever respectively.

#### Scenario: Restore Je sors defaults

- **WHEN** an admin triggers restore preset for slot 2
- **THEN** the system writes index 673 (Scenario2 base + 40) with value `"2"` per firmware convention
- **AND** the firmware re-initializes Scenario2 default masks on next processing cycle

### Requirement: Slot 1 server reservation

Slot 1 (Scenario1, indices 592–632) SHALL be treated as server/inject reserved in the UI editor MVP: read-only definition in user-facing editor, writable only via Mode B inject paths.

#### Scenario: User cannot edit slot 1 via editor API

- **WHEN** a non-admin user calls PUT on slot 1 definition
- **THEN** the API returns HTTP 403 or 409 with message that slot 1 is server-reserved
