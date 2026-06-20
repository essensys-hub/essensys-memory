## ADDED Requirements

### Requirement: Sync profile entity

The system SHALL persist sync profiles with at least: `id`, `gateway_id`, `name`, `index_ranges` (array of `[start,end]` inclusive pairs), `interval_hours` (integer ≥ 1), `pull_from_armoire`, `push_to_cloud`, `enabled`, `created_at`, `updated_at`.

#### Scenario: Default interval is 3 hours

- **WHEN** an admin creates a profile without specifying `interval_hours`
- **THEN** the profile is stored with `interval_hours = 3`

#### Scenario: Invalid index range rejected

- **WHEN** an admin submits `index_ranges: [[181, 100]]` (start > end)
- **THEN** the API returns HTTP 400 with a validation error

### Requirement: Index range validation for firmware limit

The system SHALL validate that each pull operation splits any range into chunks of at most 30 indices (firmware `serverinfos` limit per cycle).

#### Scenario: Range 181–264 requires 3 pull chunks

- **WHEN** a profile covers indices 181 through 264 (84 indices)
- **THEN** the scheduler plans 3 sequential pull chunks of 30, 30, and 24 indices

### Requirement: Admin CRUD for sync profiles

The cloud backend SHALL expose admin-authenticated endpoints:

- `GET /api/admin/sync-profiles?gateway_id=`
- `POST /api/admin/sync-profiles`
- `PUT /api/admin/sync-profiles/{id}`
- `DELETE /api/admin/sync-profiles/{id}`

Restricted to role `admin_global`.

#### Scenario: List profiles for a gateway

- **WHEN** an admin calls `GET /api/admin/sync-profiles?gateway_id=gw-001`
- **THEN** the response includes all profiles for that gateway ordered by name

### Requirement: Gateway receives sync configuration

The gateway agent SHALL fetch active sync profiles from the cloud hub via `GET /api/gateway/sync-config` (Bearer gateway token) at least once per cloudsync poll cycle.

#### Scenario: Gateway applies updated interval

- **WHEN** an admin changes a profile interval from 3 h to 6 h
- **THEN** the gateway uses the new interval after the next successful sync-config fetch

### Requirement: Seed default heating profiles

On first deploy (migration seed), the system SHALL create default enabled profiles for gateway templates:

| Name | Range | interval_hours |
|------|-------|----------------|
| Planning Zone Jour | 13–96 | 3 |
| Planning Zone Nuit | 97–180 | 3 |
| Planning SDB1 | 181–264 | 3 |
| Planning SDB2 | 265–348 | 3 |
| Modes immédiats chauffage | 349–352 | 3 |
| Temps volets | 566–585 | 3 |

#### Scenario: Fresh install seed

- **WHEN** migration `00N_sync_profiles.sql` runs on an empty database
- **THEN** the six default profile templates exist (gateway_id assigned on gateway registration or admin link)
