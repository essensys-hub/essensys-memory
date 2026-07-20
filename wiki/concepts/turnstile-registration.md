---
title: Turnstile Registration
tags: [auth, security, support-site, cloud]
updated: 2026-07-20
---

# Turnstile Registration

Public email/password registration on Essensys (`POST /api/auth/register`) is protected by **Cloudflare Turnstile** with fail-closed server `siteverify`, plus IP rate-limit and a honeypot field.

## OpenSpec

- Change: `essensys-turnstile-registration-2026-07-036`
- Spec: `openspec/changes/essensys-turnstile-registration-2026-07-036/specs/turnstile-registration/spec.md`

## Surfaces

| Role | Repo |
|------|------|
| Register UI | `essensys-support-site` (`Register.jsx`, `VITE_TURNSTILE_SITE_KEY`) |
| Production API | `essensys-user-portal-backend` identity `Register` |
| Secrets / deploy | `essensys-ansible` SOPS + `cloud-backend.env.j2` + frontend Vite env |
| Ops doc | `essensys-support-site/docs/turnstile-registration.md` |

Legacy IoT endpoints and the exchange table are **unchanged**. Admin create user bypasses Turnstile.

## Related

- [[Secrets Management]]
- [[Modération comptes utilisateurs (admin)]]
- Support-site privacy / cookie consent (Turnstile third-party script disclosure)
