## ADDED Requirements

### Requirement: Sync Cloud admin menu

The support-site admin interface SHALL include a **Sync Cloud** tab visible to users with role `admin_global`.

#### Scenario: Admin navigates to Sync Cloud

- **WHEN** an authenticated `admin_global` user opens `/admin` and selects **Sync Cloud**
- **THEN** the sync profiles list is displayed with gateway filter

### Requirement: Profile editor

The Sync Cloud UI SHALL allow creating and editing a profile with fields:

- Name (label)
- Gateway (select from registered gateways)
- Index ranges (repeatable rows: start index, end index)
- Interval in hours (number input, default 3)
- Toggles: Pull from armoire, Push to cloud, Enabled

#### Scenario: Add SDB1 profile

- **WHEN** admin adds range 181–264, interval 3 h, pull and push enabled
- **THEN** `POST /api/admin/sync-profiles` is called and the profile appears in the list

### Requirement: Manual sync trigger

The UI SHALL provide a **Sync now** action per profile calling `POST /api/admin/sync-profiles/{id}/run`.

#### Scenario: Manual run from admin

- **WHEN** admin clicks **Sync now** on profile « Planning SDB1 »
- **THEN** the gateway receives a run command via cloud
- **AND** the UI shows run status transitioning `pending → running → success|partial|failed`

### Requirement: Sync console panel

The Sync Cloud page SHALL display a console/log panel for the selected profile showing the last run entries (timestamp, phase, message, level).

Minimum log lines per run:

- Run started (profile name, ranges, expected indices count)
- Pull progress (`received/total`, chunk `n/N`)
- Push result (keys merged count)
- Run finished (duration, status)

#### Scenario: Operator monitors scheduled run

- **WHEN** a 3-hour scheduled run executes
- **THEN** the admin can refresh or poll logs and see chunk progress similar to the LAN heating sync console

### Requirement: Next run and last run display

Each profile row SHALL show `last_run_at`, `last_run_status`, and computed `next_run_at` based on `interval_hours`.

#### Scenario: Next run calculation

- **GIVEN** last successful run at 09:00 with interval 3 h
- **WHEN** the list is rendered at 10:00
- **THEN** next run displays 12:00
