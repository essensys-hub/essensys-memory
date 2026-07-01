## ADDED Requirements

### Requirement: Dashboard pull rotation for armoire exchange indices

The gateway backend SHALL rotate dedicated exchange-table index groups through `GET /api/serverinfos` responses so the SC944D firmware reports dashboard-relevant values via `POST /api/mystatus`, without exceeding the firmware limit of 30 indices per cycle.

The rotation SHALL cycle at least these index groups:

| Group | Indices (k) | Purpose |
|-------|-------------|---------|
| Identity & link | 0, 1, 5–9, 945, 947–952 | Firmware version, RTC clock, Ethernet health, MAC |
| Health | 10, 11, 12, 408, 413, 414, 415, 920 | Status, alerts, comm faults, alarm state |
| Comfort & energy | 349–353, 363, 459, 591, 460–464, 940 | Heating, cumulus, sprinkler, scenario, Linky, wind |

The rotation MUST NOT remove indices required for existing command flows (590, 605–622 block for inject) when no manual heating sync is active.

#### Scenario: Firmware receives rotatable dashboard group

- **WHEN** the armoire polls `GET /api/serverinfos` during normal operation
- **THEN** the response `infos` array contains at most 30 indices from the active dashboard rotation group or the default legacy list

#### Scenario: Manual heating sync takes priority

- **WHEN** an admin starts `POST /api/admin/heating/sync`
- **THEN** `serverinfos` returns heating planning chunks until sync completes
- **AND** dashboard rotation resumes after sync ends or times out

---

### Requirement: Armoire snapshot admin API

The gateway backend SHALL expose `GET /api/admin/armoire/snapshot` (authenticated admin or LAN session) returning a structured JSON document derived from the last `mystatus` values stored for the legacy armoire client.

The response MUST include at minimum:

- `connected` (boolean) and `last_poll_at` (RFC3339 timestamp)
- `client_id` (legacy matricule)
- `identity` (firmware embedded version, MAC address when available)
- `system` (decoded `Status` k=10: heures creuses, délestage, secouru)
- `alarm` (decoded from k=408, 413, 414, 415, 920)
- `comfort` (decoded heating modes k=349–352, cumulus k=353, sprinkler k=363, last scenario k=591)
- `raw_missing` (list of expected keys not yet received)

The endpoint MUST NOT expose alarm user codes (k=417–418).

#### Scenario: Armoire connected and snapshot fresh

- **WHEN** the armoire posted `mystatus` within the last 6 seconds
- **THEN** `connected` is `true`
- **AND** decoded fields reflect the latest stored exchange values

#### Scenario: Armoire offline

- **WHEN** no `mystatus` was received for more than 6 seconds
- **THEN** `connected` is `false`
- **AND** the response still returns the last known values with `stale_seconds` > 6

#### Scenario: Unauthorized request

- **WHEN** an unauthenticated client calls `GET /api/admin/armoire/snapshot`
- **THEN** the server responds with HTTP 401

---

### Requirement: Exchange index decoding for armoire semantics

The backend SHALL decode exchange-table octets into human-readable French labels using mappings documented in `essensys-doc/archi/exchange-table.md` and `TableEchange.h` (099-37).

Decoding MUST include:

- `Status` (k=10) bit flags: heures creuses, délestage, secouru
- `Information` (k=12) bit flags: Linky, IHM, BA PDV/CHB/PDE faults
- `Alerte` (k=11) bit flags: alarm triggered, water leak detectors
- `Chauf_*_Mode` (k=349–352): consigne (OFF/CONFORT/ECO/…) and mode (auto/forcé/anticipé)
- `Alarme_Mode` (k=408) and `Alarme_SuiviAlarme` (k=413) enumerated states
- `EtatEthernet` (k=945) link/DHCP/DNS/server bits
- `Scenario_DernierLance` (k=591) scenario name mapping (1–8)

Decoding MUST NOT present scenario lighting bitmask indices (605–616, 607, 613, 615) as live equipment state.

#### Scenario: Secouru mode active

- **WHEN** k=10 has bit 2 set (secouru)
- **THEN** `system.secouru` is `true` in the snapshot

#### Scenario: Heating zone decoded

- **WHEN** k=349 value is `0x11` (confort, forcé)
- **THEN** `comfort.heating.zone_jour` shows consigne CONFORT and mode forcé

---

### Requirement: Dashboard armoire status panel

The gateway frontend (`essensys-server-frontend`) SHALL display an `ArmoireStatusPanel` on `/dashboard` when `VITE_LAN_IAM` or gateway profile is active.

The panel MUST show:

- Connection badge (connected / offline / partial data)
- Identity line (MAC, firmware version when available)
- Health section: secouru, alarm state, comm faults
- Comfort section: heating zones summary, cumulus, sprinkler, last scenario
- Energy section (if Linky data present): tariff period and apparent power

The panel MUST poll `GET /api/admin/armoire/snapshot` every 5 seconds.

The panel MUST display a disclaimer that values are the last armoire-reported exchange data, not verified sensor feedback for individual lights or shutters.

#### Scenario: User opens dashboard with connected armoire

- **WHEN** the user navigates to `/dashboard` and the snapshot reports `connected: true`
- **THEN** a green status badge and decoded sections are visible

#### Scenario: Armoire offline

- **WHEN** the snapshot reports `connected: false`
- **THEN** the panel shows an offline badge and last known values greyed out

#### Scenario: Mock / E2E test mode

- **WHEN** the frontend runs in test mode (`mockFetch` / dry-run)
- **THEN** the panel renders from mock snapshot data without calling the real armoire

---

### Requirement: Brain documentation for gateway armoire dashboard

The essensys-memory wiki SHALL document the gateway armoire dashboard feature: index groups pulled, snapshot API shape, and UI limitations (no live per-lamp state).

#### Scenario: Wiki page exists after implementation

- **WHEN** the change is marked complete
- **THEN** `wiki/concepts/gateway-armoire-dashboard.md` exists and links to [[Table D Echange]] and [[Essensys Board SC944D]]
