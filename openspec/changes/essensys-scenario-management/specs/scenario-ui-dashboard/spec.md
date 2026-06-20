## ADDED Requirements

### Requirement: Scenario button grid

The frontend SHALL provide a Scenarios page with one-click buttons for slots 2–8 labeled: Je sors, Je pars en vacances, Je rentre, Je vais me coucher, Je me lève, Personnalisé 1, Personnalisé 2.

#### Scenario: Launch Je sors from dashboard

- **WHEN** the user clicks the Je sors button
- **THEN** the client calls POST /scenarios/2/launch
- **AND** displays success or error feedback within 3 seconds

#### Scenario: Custom label for Perso slots

- **WHEN** slot 7 has user-defined label "Mode nuit"
- **THEN** the button displays "Mode nuit" instead of default "Personnalisé 1"

### Requirement: Last launched indicator

The dashboard SHALL display the last launched scenario using index 591 when available from exchange cache.

#### Scenario: Show last scenario

- **WHEN** exchange cache reports index 591 with value 2
- **THEN** the UI shows "Dernier scénario : Je sors"

### Requirement: Gateway offline state

On the cloud portal frontend, scenario launch buttons SHALL be disabled when the linked gateway is reported offline.

#### Scenario: Offline gateway disables buttons

- **WHEN** gateway heartbeat is stale beyond configured threshold
- **THEN** launch buttons are disabled with explanatory tooltip

### Requirement: Twin frontend parity

`essensys-server-frontend` and `essensys-user-portal-frontend` SHALL share equivalent Scenario dashboard components and behavior, differing only in API base path and auth.

#### Scenario: Same button count on both UIs

- **WHEN** both frontends render the Scenarios page
- **THEN** each displays 7 launch buttons for slots 2–8
