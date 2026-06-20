## ADDED Requirements

### Requirement: Multi-tab scenario editor

The frontend SHALL provide an editor for slots 2–8 with tabs: Alarm, Lights, Shutters, Heating, Cumulus, Reveil — mapping to the corresponding `enumScenario` parameter groups.

#### Scenario: Edit lights tab

- **WHEN** the user toggles "Petite chambre 3" on in Allumer CHB for slot 7
- **THEN** the client sets bit 6 (value 64) on the appropriate absolute index before save

### Requirement: Save and launch from editor

The editor SHALL provide **Save**, **Restore preset**, and **Launch now** actions.

#### Scenario: Save then launch

- **WHEN** the user clicks Save then Launch now on slot 7
- **THEN** PUT /scenarios/7 is called followed by POST /scenarios/7/launch

#### Scenario: Restore preset confirmation

- **WHEN** the user clicks Restore preset
- **THEN** a confirmation dialog appears before calling the restore API

### Requirement: Slot 1 not editable in MVP editor

The editor SHALL NOT allow editing slot 1 in the user-facing UI; slot 1 parameters remain managed by server inject (Mode B).

#### Scenario: Slot 1 opens read-only or hidden

- **WHEN** the user navigates to scenario slot 1 in the editor
- **THEN** fields are read-only or the slot is not listed in the editable slot picker

### Requirement: Twin editor parity

Both frontends SHALL implement the same editor tabs and field layout for slots 2–8.

#### Scenario: Heating tab present on portal

- **WHEN** the portal editor opens for slot 3
- **THEN** a Heating tab with zones zj, zn, zsb1, zsb2 is visible
