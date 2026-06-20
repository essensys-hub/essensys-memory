## ADDED Requirements

### Requirement: Mode A — Launch memorized scenario

When launching scenario slots 2–8, the backend SHALL enqueue exactly one parameter `{k: 590, v: "<slot_number>"}` where `slot_number` is 2 through 8, and SHALL NOT append the 605–622 block.

#### Scenario: Launch Je sors

- **WHEN** the client calls launch for slot 2 (Je sors)
- **THEN** the action params contain only `{k: 590, v: "2"}` plus required `_de67f` handling at inject layer

#### Scenario: Launch Personnalisé 1

- **WHEN** the client calls launch for slot 7
- **THEN** the action params contain `{k: 590, v: "7"}` without indices 605–622

### Requirement: Mode B — Server immediate action with expansion

When any parameter targets indices 605–622 (or 592–632 when full expansion enabled), the backend SHALL set `{k: 590, v: "1"}` and fill missing indices in the active range with `"0"`.

#### Scenario: Single light toggle uses expansion

- **WHEN** inject receives `{k: 613, v: "64"}`
- **THEN** the expanded action includes 590=1 and all indices 605–622 with 613=64 and others 0

#### Scenario: Index 590 never fused

- **WHEN** two actions both specify index 590 with different values
- **THEN** the later action value is used without bitwise OR fusion

### Requirement: Full Scenario1 expansion when requested

When the client sets header or flag `X-Scenario-Full-Block: true`, the backend SHALL use `ExpandFullScenario1Block` filling indices 592–632 (alarm, security, heating, cumulus, reveil fields) with `"0"` for unspecified values and `{k: 590, v: "1"}` as trigger.

#### Scenario: Full block for alarm scenario field

- **WHEN** a write targets index 593 (Scenario_Alarme_ON) with full expansion enabled
- **THEN** the action includes 590=1 and all indices 592–632 with unspecified values set to `"0"`
