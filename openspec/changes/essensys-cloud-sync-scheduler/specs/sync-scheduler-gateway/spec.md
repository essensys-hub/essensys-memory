## ADDED Requirements

### Requirement: Scheduled sync execution per profile

The gateway backend SHALL run a scheduler that triggers each enabled profile when `now >= last_run_at + interval_hours`.

#### Scenario: Profile runs every 3 hours

- **GIVEN** a profile with `interval_hours: 3` and `last_run_at` at 09:00
- **WHEN** the scheduler tick occurs at 12:00 or later
- **THEN** a new sync run starts for that profile

#### Scenario: Disabled profile skipped

- **GIVEN** a profile with `enabled: false`
- **WHEN** the scheduler tick occurs
- **THEN** no run is started for that profile

### Requirement: Pull-then-push pipeline

For each sync run with `pull_from_armoire: true`, the gateway SHALL:

1. Enqueue index chunks (≤ 30) via `ExchangePullScheduler`
2. Wait until all chunks are reported via `POST /api/mystatus` or timeout (default 120 s per chunk)
3. If `push_to_cloud: true`, push collected keys via `POST /api/gateway/exchange` with merge semantics

#### Scenario: Successful SDB1 scheduled sync

- **GIVEN** profile range 181–264, pull and push enabled
- **WHEN** a scheduled run completes
- **THEN** Redis contains 84 keys in range 181–264
- **AND** cloud `gateway_exchange_cache` receives the same keys merged

#### Scenario: Partial pull logged

- **WHEN** only 60 of 84 indices are received before timeout
- **THEN** the run is recorded as `status: partial`
- **AND** push includes only keys present in Redis

### Requirement: Exclusive pull lock

The gateway SHALL allow at most one armoire pull rotation (manual or scheduled) at a time.

#### Scenario: Manual sync during scheduled run

- **WHEN** a scheduled pull is in progress
- **AND** an admin triggers manual heating sync on LAN
- **THEN** the manual request receives HTTP 409 or queues until the lock is released

### Requirement: Legacy serverinfos compatibility

During scheduled pull, `GET /api/serverinfos` SHALL return only the current pull chunk (≤ 30 indices). Outside pull windows, it SHALL return the standard default index list (≤ 30 indices, no planning ranges embedded).

#### Scenario: Normal cycle between scheduled pulls

- **WHEN** no pull is active
- **THEN** `serverinfos` matches the existing production list (volets, modes 349–352, lumières, etc.)
- **AND** the armoire cycle continues with `mystatus` and `myactions`

### Requirement: Fallback hardcoded push

If no sync profiles are configured for a gateway, `pushExchange` SHALL fall back to the existing `exchangePushIndices()` hardcoded list for backward compatibility.

#### Scenario: Legacy gateway without profiles

- **WHEN** sync-config returns an empty profile list
- **THEN** cloudsync push behavior is unchanged from pre-change deployments

### Requirement: Configurable scheduler enable flag

The gateway config SHALL support `cloudsync.scheduled_sync_enabled` (default `true` when profiles exist).

#### Scenario: Emergency disable

- **WHEN** `scheduled_sync_enabled: false` in gateway config.yaml
- **THEN** no scheduled pulls run; manual LAN sync and action poll remain active
