## 1. Ops — Cloudflare Turnstile site

- [x] 1.1 Create Turnstile widget (managed mode) in Cloudflare dashboard
- [x] 1.2 Allowlist hostnames: `www.essensys.fr`, `mon.essensys.fr`, `test.essensys.fr` (and local if needed)
- [x] 1.3 Record site key (public) and secret key (server-only); never commit secret to git

## 2. Secrets and Ansible

- [x] 2.1 Add `TURNSTILE_SECRET_KEY` (and related vars) to SOPS cloud secrets
- [x] 2.2 Wire secret into cloud-backend / portal-backend env template via Ansible
- [x] 2.3 Document `VITE_TURNSTILE_SITE_KEY` for support-site production builds
- [x] 2.4 Enforce: `TURNSTILE_DISABLED` ignored or refused when `ENV=production`

## 3. Backend — siteverify + register (portal)

- [x] 3.1 Add Go Turnstile `siteverify` client (timeout ~5s, fail-closed on network/error)
- [x] 3.2 Unit-test client with HTTP mock (success, failure, timeout)
- [x] 3.3 Extend register request DTO with `turnstile_token` and honeypot field
- [x] 3.4 In `identity.Register`, verify Turnstile before password hash / `CreateUser`
- [x] 3.5 Apply IP rate-limit on `POST /api/auth/register` (reuse `RateLimiter`; default 5/IP/hour)
- [x] 3.6 Reject non-empty honeypot with generic `400`; no user create
- [x] 3.7 Emit audit events `REGISTER_BLOCKED_TURNSTILE` / `REGISTER_BLOCKED_RATELIMIT` / `REGISTER_BLOCKED_HONEYPOT` (no token/secret in logs)
- [x] 3.8 Confirm admin user-create paths remain Turnstile-free; add regression test
- [x] 3.9 Run `go test ./...` in `essensys-user-portal-backend`

## 4. Backend sync — support-site (if still deployable)

- [x] 4.1 Mirror fail-closed Turnstile + honeypot + rate-limit on `HandleRegister` if that binary is still served anywhere
- [x] 4.2 If support-site backend is unused in prod, document “parity only if redeployed” and skip runtime deploy

## 5. Frontend — register UI

- [x] 5.1 Integrate Turnstile managed widget on `Register.jsx` with `VITE_TURNSTILE_SITE_KEY`
- [x] 5.2 Send `turnstile_token` (+ empty honeypot) in `POST /api/auth/register`
- [x] 5.3 Surface clear errors for missing widget, `403` Turnstile fail, and `429` rate-limit
- [x] 5.4 Update cookie/privacy note for Turnstile third-party script (`CookieConsent` / auth docs)

## 6. CI and e2e

- [x] 6.1 Configure Cloudflare always-pass test keys or mock siteverify for CI
- [x] 6.2 Update Playwright / register e2e so Turnstile does not flake
- [x] 6.3 Verify CI green without production Turnstile secrets

## 7. Deploy and smoke (OVH)

- [x] 7.1 Deploy updated cloud-backend with Turnstile secret present
- [x] 7.2 Rebuild/deploy support-site SPA with site key
- [x] 7.3 Smoke: human register succeeds; curl without token fails (no user); admin create still works
- [x] 7.4 Document rollback (backend + SPA) in short ops note

## 8. Documentation and memory

- [x] 8.1 Add ops note: Turnstile site creation, hostnames, key rotation
- [x] 8.2 Update `essensys-support-site/docs/authentication.md` (or equivalent) for register Turnstile
- [x] 8.3 Ingest wiki concept `wiki/concepts/turnstile-registration.md` + link from auth pages
- [x] 8.4 Update `essensys-memory` (OKF sync scripts, `okf/log.md`, roadmap); run `openspec validate essensys-turnstile-registration-2026-07-036 --strict`
- [x] 8.5 Publish public roadmap if queue requires (`publish-roadmap-public.sh`)
- [x] 8.6 Confirm legacy IoT endpoints and exchange table were not modified
