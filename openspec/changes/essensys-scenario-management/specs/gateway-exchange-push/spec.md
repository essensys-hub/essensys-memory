## ADDED Requirements

### Requirement: Scenario indices in profile-aware push

When sync profiles are configured, `pushExchange` SHALL include keys from the Scénarios profile range 592–919 (excluding index 590 per sync-profile-config) in addition to keys from other active profiles executed in the same run or present in Redis from scheduled sync.

#### Scenario: Push includes Scenario2 block after sync

- **GIVEN** a successful Scénarios profile pull populated Redis with indices 633–673
- **WHEN** pushExchange runs
- **THEN** cloud gateway_exchange_cache receives keys 633–673 merged

### Requirement: Fallback includes scenario block extension

When no sync profiles are configured, the fallback `exchangePushIndices()` SHALL continue to push 590 and 605–622 for backward compatibility unchanged from pre-scenario deployments.

#### Scenario: Legacy gateway without profiles unchanged

- **WHEN** sync-config returns empty profiles
- **THEN** push behavior matches pre-scenario-change deployments (590 + 605–622 minimum)

### Requirement: Profile-driven push supersedes hardcoded subset

When the Scénarios profile is enabled, routine push SHALL prefer profile-collected keys over the minimal hardcoded 605–622 subset for indices in range 592–919.

#### Scenario: Enabled scenarios profile replaces partial hardcode

- **GIVEN** Scénarios profile enabled and Redis contains 592–919 keys
- **WHEN** scheduled push executes
- **THEN** at least all non-excluded keys in 592–919 present in Redis are pushed to cloud
