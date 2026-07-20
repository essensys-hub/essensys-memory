## Context

Public registration is served from the support-site SPA (`Register.jsx` → `POST /api/auth/register`). On the OVH consolidated hub, Nginx routes `/api/*` to `essensys-cloud-backend` (`essensys-user-portal-backend` identity package). Today that path accepts email/password with no CAPTCHA, no dedicated rate-limit, and no email verification — bots create fictitious users. Cookie consent already exists on the support site; Turnstile adds a third-party script that must be disclosed.

Constraints: fail-closed verification; secrets via SOPS only; admin User Manager create MUST remain free of Turnstile; legacy IoT endpoints and exchange-table protocol MUST NOT change; library-first (reuse existing `RateLimiter`).

Stakeholders: product (spam volume), support (admin UX), ops (OVH + Cloudflare Turnstile site), privacy (cookie notice).

## Goals / Non-Goals

**Goals:**

- Stop automated fake registrations with Cloudflare Turnstile + server `siteverify`.
- Layer IP rate-limit and honeypot on the same register endpoint.
- Wire secrets and site key through Ansible/SOPS and Vite build.
- Keep CI/e2e green via Cloudflare test keys or non-prod-only disable.
- Document hostnames, privacy, and ops rotation.

**Non-Goals:**

- Turnstile on login, forgot-password, or OAuth (Phase 2 if needed).
- Mandatory email verification (Phase 2 if spam persists).
- reCAPTCHA / hCaptcha / full Cloudflare WAF.
- Bulk deletion of existing fake accounts (separate ops).
- Any change to firmware, exchange table, or legacy `/api/serverinfos|mystatus|myactions|done`.

## Decisions

### D1 — Cloudflare Turnstile (managed widget), not reCAPTCHA

- **Choice**: Turnstile managed mode on `/register`.
- **Why**: Lower friction than checkbox CAPTCHA, better privacy posture than Google reCAPTCHA for EU-facing site, free tier sufficient.
- **Alternatives**: Invisible-only Turnstile (harder to debug UX); hCaptcha; email verification only (slower to ship, different UX).

### D2 — Production verify target = portal/cloud backend

- **Choice**: Implement fail-closed `siteverify` in `essensys-user-portal-backend` `identity.Register` (the binary behind OVH `/api/auth/register`). Optionally mirror the same checks in `essensys-support-site/backend` if that binary remains deployable elsewhere.
- **Why**: Frontend-only widget is bypassable (trap E1/E2).
- **Alternatives**: Nginx auth_request sidecar (more ops surface, less reuse of Go identity logic).

### D3 — Fail-closed + non-prod bypass

- **Choice**: Missing/invalid token → `403` (or `400` for missing fields); never call `CreateUser`. `TURNSTILE_DISABLED=true` allowed only when env is not production; production MUST refuse to start or MUST ignore disable and require secret.
- **Why**: Prevent accidental open registration in prod.
- **Alternatives**: Soft-fail on Cloudflare outage (rejected — spam window). Prefer short timeout + clear error; ops can temporarily disable only via non-prod path or emergency secret rotation + maintenance.

### D4 — Rate-limit + honeypot alongside Turnstile

- **Choice**: Reuse portal `middleware.RateLimiter` (or equivalent) on register: e.g. 5 requests / IP / hour. Honeypot field `website` (or similar): if non-empty → `400` without user creation (generic message).
- **Why**: Bots can still hammer `siteverify`; honeypot catches naive scrapers that fill all inputs.
- **Alternatives**: Redis-only global counter (overkill for MVP).

### D5 — Secrets and site key distribution

- **Choice**: `TURNSTILE_SECRET_KEY` in SOPS → cloud-backend env. `VITE_TURNSTILE_SITE_KEY` at support-site build time (public). Never commit secrets.
- **Why**: Matches existing Essensys secrets pattern.
- **Alternatives**: Runtime public config endpoint for site key (nice-to-have if rebuilds are painful; not required for MVP).

### D6 — Admin create exempt

- **Choice**: Admin User Manager / admin create routes do not require Turnstile.
- **Why**: Support must provision real users without solving CAPTCHA in browser automation.

### D7 — Observability

- **Choice**: Structured audit events `REGISTER_BLOCKED_TURNSTILE`, `REGISTER_BLOCKED_RATELIMIT`, `REGISTER_BLOCKED_HONEYPOT` with IP hash / email domain only — never log raw Turnstile tokens.

### D8 — Cross-cutting split

| Layer | Owner |
|-------|--------|
| Frontend widget | support-site SPA |
| Auth verify + rate-limit | user-portal-backend (prod); support-site backend optional sync |
| Secrets / deploy | Ansible + SOPS + OVH |
| Firmware / exchange table | untouched |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Widget-only without server verify | Spec mandates fail-closed `siteverify` before `CreateUser` |
| Wrong backend patched | Tasks list portal-backend as P0; support-site backend as sync |
| Secret leaked in git | SOPS only; CI secret scan; never put secret in Vite |
| e2e / Playwright break | Cloudflare always-pass test keys or mock HTTP client in CI |
| Hostname not allowlisted in Turnstile | Ops checklist: `www.essensys.fr`, `mon.essensys.fr`, `test.essensys.fr`, local as needed |
| Cloudflare outage blocks legit users | Timeout + clear error; emergency ops runbook (non-prod disable pattern documented; prod incident = temporary maintenance or Cloudflare status) |
| Privacy / cookies | Update consent / privacy blurb for Turnstile script |

## Migration Plan

1. Create Turnstile widget in Cloudflare dashboard; add hostnames; store secret in SOPS.
2. Ship backend verify + rate-limit + honeypot (feature can reject missing token immediately).
3. Ship SPA with widget + token field; rebuild with site key.
4. Deploy OVH cloud-backend then support SPA (order: backend first so old SPA without token fails closed briefly — prefer same release window).
5. Smoke: human register succeeds; curl without token fails; admin create still works.
6. Rollback: revert SPA + backend deploys; remove or keep SOPS keys inert. Do not leave backend without verify while SPA still sends tokens (harmless) — avoid leaving verify off with public register open.

## Open Questions

1. Exact rate-limit numbers (default proposal: 5 / IP / hour) — confirm with ops after first week of metrics.
2. Whether support-site backend is still deployed anywhere that needs parity (if not, document as “sync only if redeployed”).
3. Phase 2 trigger: Turnstile on login and/or mandatory email verify if spam persists via stolen/solved tokens.
