## ADDED Requirements

### Requirement: Public register requires a Turnstile token

The public registration API (`POST /api/auth/register`) MUST reject requests that omit a Turnstile response token. The client MUST send the token in the JSON body as `turnstile_token` (or an agreed alias such as `cf-turnstile-response`). Missing token MUST NOT create a user.

#### Scenario: Register without token is rejected

- **WHEN** a client posts email and password to `/api/auth/register` without `turnstile_token`
- **THEN** the server responds with `400` and does not create a user account

#### Scenario: Register UI collects Turnstile token

- **WHEN** a human completes the `/register` form on the support-site SPA with Turnstile configured
- **THEN** the SPA includes a non-empty `turnstile_token` from the Turnstile widget in the register request body

### Requirement: Server verifies Turnstile before CreateUser

The production register handler (consolidated cloud / `essensys-user-portal-backend` identity) MUST call Cloudflare Turnstile `siteverify` with the server secret and the client token **before** hashing the password or inserting a user. Verification MUST be fail-closed: invalid, expired, already-used, or unreachable verification MUST NOT create a user. The secret MUST never be exposed to the browser or logged.

#### Scenario: Valid token allows registration

- **WHEN** `siteverify` returns success for a fresh token and other register validations pass
- **THEN** the server creates the user as today (`201` / existing success contract)

#### Scenario: Invalid token blocks registration

- **WHEN** `siteverify` returns failure or the HTTP call to Cloudflare fails or times out
- **THEN** the server responds with `403` (or equivalent blocked status), emits audit event `REGISTER_BLOCKED_TURNSTILE` without logging the token, and does not create a user

### Requirement: Register endpoint is rate-limited by IP

The system MUST apply an IP-based rate limit to `POST /api/auth/register` (default: at most 5 attempts per IP per hour, configurable). Exceeding the limit MUST NOT create a user.

#### Scenario: Excess register attempts return 429

- **WHEN** a client exceeds the configured register rate limit for its IP
- **THEN** the server responds with `429`, emits `REGISTER_BLOCKED_RATELIMIT`, and does not create a user

### Requirement: Honeypot field rejects bot-filled forms

The register request MAY include a honeypot field (e.g. `website`). If the honeypot is present and non-empty, the server MUST reject the request without creating a user and MUST NOT reveal that a honeypot was the reason in a way that helps bots (generic client error is acceptable).

#### Scenario: Filled honeypot is rejected

- **WHEN** a client posts register with a non-empty honeypot field
- **THEN** the server responds with `400`, does not create a user, and may emit `REGISTER_BLOCKED_HONEYPOT`

### Requirement: Admin user provisioning bypasses Turnstile

Administrative user creation (User Manager / admin create routes) MUST NOT require a Turnstile token and MUST remain usable for support provisioning.

#### Scenario: Admin create user without Turnstile

- **WHEN** an authenticated admin creates a user via the admin API or User Manager
- **THEN** the create succeeds without Turnstile verification (subject to existing admin authz rules)

### Requirement: Production cannot disable Turnstile verification

In production, Turnstile verification MUST be enforced when public register is enabled. A disable flag (`TURNSTILE_DISABLED`) MUST NOT skip verification when the environment is production. Non-production environments MAY use Cloudflare test keys or an explicit disable for local/CI only.

#### Scenario: Production ignores disable flag

- **WHEN** the service runs with production environment configuration and `TURNSTILE_DISABLED=true`
- **THEN** the service still requires successful `siteverify` (or refuses to serve open register) and does not create users without verification

#### Scenario: CI uses test keys or mock

- **WHEN** automated tests exercise register
- **THEN** they use Cloudflare test keys or a mocked `siteverify` client so CI does not depend on production Turnstile secrets

### Requirement: Secrets and site key handling

The Turnstile secret key MUST be supplied via server environment / SOPS (Ansible), never committed to git. The site key MAY be public and injected at SPA build time (e.g. `VITE_TURNSTILE_SITE_KEY`).

#### Scenario: Secret absent from repository

- **WHEN** the change is reviewed in git
- **THEN** no Turnstile secret key appears in tracked files

### Requirement: Legacy IoT protocol unchanged

This capability MUST NOT modify legacy IoT endpoints `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, or `/api/done/{guid}`, nor the exchange-table protocol.

#### Scenario: Legacy endpoints unaffected

- **WHEN** firmware or gateways call legacy IoT APIs
- **THEN** request/response contracts remain unchanged by the Turnstile registration work
