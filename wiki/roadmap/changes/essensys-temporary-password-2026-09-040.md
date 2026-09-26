---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-09-25
updated: 2026-09-26
status: completed
host_repo: essensys-memory
---

# Essensys Temporary Password 2026 09 040

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-temporary-password-2026-09-040`
**Status:** completed
**OpenSpec created:** 2026-09-25

## Why

Depuis la change `essensys-password-reset-2026-08-039`, le support dispose d'un seul moyen de débloquer un compte : `POST /api/admin/users/{id}/password-reset`, qui émet un lien à usage unique et **l'envoie par courriel**. Tout ce chemin repose sur une hypothèse : l'utilisateur accède à sa boîte mail.

Quand cette hypothèse tombe — adresse saisie avec une faute à l'inscription, boîte saturée, domaine qui rejette le relais, personne qui n'a plus l'usage de sa messagerie — il n'existe **aucune** i…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 4

## Source files

- `essensys-memory/openspec/changes/essensys-temporary-password-2026-09-040/proposal.md`
- `essensys-memory/openspec/changes/essensys-temporary-password-2026-09-040/design.md`
- `essensys-memory/openspec/changes/essensys-temporary-password-2026-09-040/tasks.md`
