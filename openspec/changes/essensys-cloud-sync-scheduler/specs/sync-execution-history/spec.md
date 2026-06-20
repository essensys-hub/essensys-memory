## ADDED Requirements

### Requirement: Sync run persistence

The cloud backend SHALL record each sync execution in `sync_runs` with: `id`, `profile_id`, `gateway_id`, `started_at`, `finished_at`, `status` (`pending|running|success|partial|failed`), `expected_count`, `received_count`, `pushed_count`, `error_message`, `log_lines` (JSON array).

#### Scenario: Successful run recorded

- **WHEN** a profile sync completes with 84/84 indices received and push OK
- **THEN** a row exists with `status: success`, `received_count: 84`

### Requirement: Run history API

Admins SHALL access `GET /api/admin/sync-profiles/{id}/runs?limit=20` and `GET /api/admin/sync-runs/{runId}/logs`.

#### Scenario: View last 5 runs

- **WHEN** admin requests run history for a profile
- **THEN** up to 20 most recent runs are returned with status and counts

### Requirement: Gateway reports run progress

During execution, the gateway SHALL POST progress to `POST /api/gateway/sync-runs/{runId}/progress` (or batch in completion payload).

Payload fields: `received_count`, `chunk_index`, `chunk_total`, `phase` (`pull|push|done`), `message`.

#### Scenario: Cloud UI polls progress

- **WHEN** gateway sends progress updates during pull
- **THEN** admin UI console updates without requiring LAN access

### Requirement: Retention policy

Sync run logs SHALL be retained for at least 30 days; older rows MAY be purged by a nightly cleanup job.

#### Scenario: Old runs purged

- **WHEN** a run is older than 30 days
- **THEN** it is eligible for deletion by cleanup job without affecting active profiles
