---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-08-24
updated: 2026-08-24
status: active
host_repo: essensys-memory
---

# Essensys Password Reset 2026 08 039

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-password-reset-2026-08-039`
**Status:** active
**OpenSpec created:** 2026-08-24

## Why

Le formulaire de connexion `mon.essensys.fr` (`essensys-support-site/site/src/pages/Login.jsx`) n'offre **aucun lien « Mot de passe oublié »**. Côté backend, `essensys-user-portal-backend/internal/identity/routes.go` ne monte aucune route de réinitialisation, et aucun outil admin ne permet de forcer un nouveau mot de passe : un utilisateur qui perd son mot de passe est **définitivement bloqué**.

Le cas est déjà survenu en production : le compte `emilienbieber67260@gmail.com` (`users.id=12`, cré…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 5

## Source files

- `essensys-memory/openspec/changes/essensys-password-reset-2026-08-039/proposal.md`
- `essensys-memory/openspec/changes/essensys-password-reset-2026-08-039/design.md`
- `essensys-memory/openspec/changes/essensys-password-reset-2026-08-039/tasks.md`
