---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-23
updated: 2026-06-28
status: completed
host_repo: essensys-feature-lifecycle
---

# Migrate Security Gate To Dependabot

**Host repo:** [[Essensys Feature Lifecycle]]
**Path:** `essensys-feature-lifecycle/openspec/changes/migrate-security-gate-to-dependabot`
**Status:** completed
**OpenSpec created:** 2026-06-23

## Why

The wise feature lifecycle still wires its security gate to **CodeGuard / Checkmarx One (Cyber AST)** for Software Composition Analysis (SCA) and SAST. CodeGuard is being abandoned, and a GitHub-native model already partially exists in this repo (the `security-gate` workflow plus a `security` block in the feature manifest). The lifecycle assets (skills, rules, templates, schema, docs, scripts) are inconsistent: some still reference `codeguard`/`checkmarx`, no `dependabot.yml` exists yet, and the…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 1

## Source files

- `essensys-feature-lifecycle/openspec/changes/migrate-security-gate-to-dependabot/proposal.md`
- `essensys-feature-lifecycle/openspec/changes/migrate-security-gate-to-dependabot/design.md`
- `essensys-feature-lifecycle/openspec/changes/migrate-security-gate-to-dependabot/tasks.md`
