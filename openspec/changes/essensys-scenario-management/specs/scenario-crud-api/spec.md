## ADDED Requirements

### Requirement: List scenario slots

Both backends SHALL expose `GET /api/scenarios` (LAN) and `GET /api/portal/scenarios` (cloud) returning slots 1–8 with: `slot_number`, `label`, `preset_type`, `last_launched` (from index 591 when available), and `updated_at`.

#### Scenario: List returns eight slots

- **WHEN** an authenticated client calls GET /api/scenarios
- **THEN** the response contains exactly 8 slot entries with default labels matching firmware presets for slots 2–8

### Requirement: Read scenario definition

The system SHALL expose `GET /api/scenarios/{slot}` and `GET /api/portal/scenarios/{slot}` returning the 41 parameters for the requested slot, sourced from exchange cache or `scenario_definitions` table merged with cache.

#### Scenario: Read slot 7 definition

- **WHEN** GET /api/scenarios/7 is called
- **THEN** the response includes params for indices 838–878

### Requirement: Write scenario definition

The system SHALL expose `PUT /api/scenarios/{slot}` and `PUT /api/portal/scenarios/{slot}` accepting a params map, validating via `scenario-definition-model`, and enqueueing ordered inject actions (max 30 params per firmware action).

#### Scenario: Write slot 7 persists to armoire

- **WHEN** PUT /api/portal/scenarios/7 with valid params is called and gateway is online
- **THEN** two ordered actions are enqueued covering all 41 indices
- **AND** subsequent GET returns the written values after armoire acknowledgment

### Requirement: Launch scenario

The system SHALL expose `POST /api/scenarios/{slot}/launch` and `POST /api/portal/scenarios/{slot}/launch`.

- Slots 2–8: Mode A (`590=slot_number`).
- Slot 1 launch: rejected with HTTP 400 (use inject for Mode B).

#### Scenario: Launch slot 4 Je rentre

- **WHEN** POST /api/scenarios/4/launch
- **THEN** one action with `{k:590, v:"4"}` is enqueued

#### Scenario: Launch slot 1 rejected

- **WHEN** POST /api/scenarios/1/launch
- **THEN** HTTP 400 is returned

### Requirement: Bitmask metadata endpoint

The system SHALL expose `GET /api/scenarios/meta/bitmasks` (and portal equivalent) returning UI labels for lighting and shutter bits derived from `table_reference.json` or generated static map.

#### Scenario: Bitmask labels available for editor

- **WHEN** the editor loads metadata
- **THEN** index 613 bit 6 is labeled for petite chambre 3 lamp

### Requirement: Twin backend parity

LAN and portal backends SHALL implement equivalent scenario semantics; portal routes require approved user-gateway link per existing portail auth rules.

#### Scenario: Portal launch requires link

- **WHEN** a user without approved link calls POST /api/portal/scenarios/2/launch
- **THEN** HTTP 403 is returned
