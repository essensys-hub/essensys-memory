---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-07-20
updated: 2026-07-20
status: active
host_repo: essensys-memory
---

# Essensys Turnstile Registration 2026 07 036

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-turnstile-registration-2026-07-036`
**Status:** active
**OpenSpec created:** 2026-07-20

## Why

Public email/password registration on `www.essensys.fr` (`POST /api/auth/register`) has no bot protection, so automated clients create large numbers of fictitious accounts and pollute user inventory / admin User Manager. We need a low-friction, EU-friendly CAPTCHA with mandatory server-side verification before any `CreateUser`, without touching the legacy IoT protocol or the exchange table.

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 1

## Source files

- `essensys-memory/openspec/changes/essensys-turnstile-registration-2026-07-036/proposal.md`
- `essensys-memory/openspec/changes/essensys-turnstile-registration-2026-07-036/design.md`
- `essensys-memory/openspec/changes/essensys-turnstile-registration-2026-07-036/tasks.md`
