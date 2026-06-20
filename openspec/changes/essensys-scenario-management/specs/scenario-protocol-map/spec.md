## ADDED Requirements

### Requirement: Firmware-validated scenario index map

The system SHALL maintain an authoritative mapping of scenario-related exchange indices for firmware reference **SC944D 099-37**, including at minimum:

| Indice | Mnemonique | Description |
|--------|------------|-------------|
| 590 | Scenario | Scenario number to launch (0=none, 1=server, 2–8=slots) |
| 591 | Scenario_DernierLance | Last launched scenario |
| 592–632 | Scenario1 | Server scenario (41 parameters) |
| 633–673 | Scenario2 | Je sors |
| 674–714 | Scenario3 | Je pars en vacances |
| 715–755 | Scenario4 | Je rentre |
| 756–796 | Scenario5 | Je vais me coucher |
| 797–837 | Scenario6 | Je me lève |
| 838–878 | Scenario7 | Personnalisé 1 |
| 879–919 | Scenario8 | Personnalisé 2 |

Absolute index for parameter offset `O` in slot `N` (1–8) SHALL equal `592 + (N-1)*41 + O`.

#### Scenario: Allumer CHB LSB index for Scenario1

- **WHEN** offset of `Scenario_Allumer_CHB_LSB` is 21 in `enumScenario`
- **THEN** the absolute index for Scenario1 is **613** (592 + 21)

#### Scenario: Scenario2 base index

- **WHEN** slot number is 2
- **THEN** the base index is **633**

### Requirement: Protocol audit artifact

Before implementation phases, the change SHALL produce an audit document listing every discrepancy between `essensys-memory/raw/protocol/exchange-table.md`, `essensys-doc/archi/exchange-table.md`, and firmware `TableEchange.h` / `Scenario.c`.

#### Scenario: Audit completed

- **WHEN** Phase 0 ends
- **THEN** a markdown audit table exists in the change directory or wiki with zero unexplained gaps

### Requirement: Errata raw exchange-table documentation

The system SHALL update `essensys-memory/raw/protocol/exchange-table.md` to replace base-600 offsets with base-592 absolute indices and document index 590 values 1–8.

#### Scenario: Index 590 documentation corrected

- **WHEN** a developer reads the raw exchange-table after Phase 0
- **THEN** index 590 is documented as supporting values 0–8, not only `"1"`
