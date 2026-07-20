## Why

Public email/password registration on `www.essensys.fr` (`POST /api/auth/register`) has no bot protection, so automated clients create large numbers of fictitious accounts and pollute user inventory / admin User Manager. We need a low-friction, EU-friendly CAPTCHA with mandatory server-side verification before any `CreateUser`, without touching the legacy IoT protocol or the exchange table.

## What Changes

- Add **Cloudflare Turnstile** (managed widget) on the public `/register` page (`essensys-support-site`).
- Require `turnstile_token` on `POST /api/auth/register` and **fail-closed** verify against Cloudflare `siteverify` **before** password hash / user insert (production handler: consolidated `essensys-user-portal-backend` / cloud-backend on OVH; keep support-site backend aligned if still deployable).
- Add **IP rate-limit** on register (reuse portal `RateLimiter` pattern).
- Add HTML **honeypot** field rejected when filled.
- Store Turnstile secret via **SOPS / Ansible** env; expose site key to Vite build (`VITE_TURNSTILE_SITE_KEY`).
- Audit log blocked registrations (`REGISTER_BLOCKED_TURNSTILE` / `REGISTER_BLOCKED_RATELIMIT`) without logging tokens.
- Document Turnstile hostnames, privacy/cookie note, and CI/test keys (or non-prod disable only).
- **Not in MVP**: Turnstile on login/OAuth, mandatory email verification, mass purge of existing fake users (optional ops note only).
- **Legacy impact**: **none** — modern auth only; no change to `/api/serverinfos`, `mystatus`, `myactions`, `done`, or the exchange table.

## Capabilities

### New Capabilities

- `turnstile-registration`: Server-verified Cloudflare Turnstile on public registration, plus rate-limit and honeypot; admin user provisioning remains exempt.

### Modified Capabilities

- _(none — no existing OpenSpec capability covers public register bot protection)_

## Impact

| Area | Impact |
|------|--------|
| `essensys-support-site` | `Register.jsx` widget + token; docs/privacy note; optional legacy `HandleRegister` sync |
| `essensys-user-portal-backend` | `identity.Register` + siteverify client + register rate-limit |
| `essensys-ansible` | SOPS/env for `TURNSTILE_SECRET_KEY` / site key; cloud-backend env template |
| OVH deploy | Rebuild/restart cloud-backend + support SPA; Cloudflare Turnstile site hostnames |
| CI / Playwright | Stub or Cloudflare test keys so e2e register does not call production siteverify |
| Wiki / OKF | New concept + roadmap entry; `publish-roadmap-public.sh` after queue |
| Related wiki | [[Authentication]], privacy/cookie consent surfaces on support-site |
