---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-25
updated: 2026-06-28
status: active
host_repo: essensys-memory
---

# Essensys Admin User Forbid Delete 2026 06 027

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-admin-user-forbid-delete-2026-06-027`
**Status:** active
**OpenSpec created:** 2026-06-25

## Why

La page admin **Gestion des Utilisateurs** (`mon.essensys.fr/admin`, `UserManager.jsx`) permet de créer des comptes et de modifier rôles/liaisons, mais **aucune action de modération** n'existe : impossible d'interdire un accès (tout en conservant l'email pour traçabilité) ni de supprimer définitivement un compte. Les admins doivent pouvoir couper l'accès d'un utilisateur abusif ou obsolète sans perdre l'historique email, avec redirection vers la page « en construction » existante.

> **Roadmap I…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 1

## Source files

- `essensys-memory/openspec/changes/essensys-admin-user-forbid-delete-2026-06-027/proposal.md`
- `essensys-memory/openspec/changes/essensys-admin-user-forbid-delete-2026-06-027/design.md`
- `essensys-memory/openspec/changes/essensys-admin-user-forbid-delete-2026-06-027/tasks.md`
