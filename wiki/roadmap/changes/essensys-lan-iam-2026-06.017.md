---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-06-21
updated: 2026-06-28
status: active
host_repo: essensys-memory
---

# Essensys Lan Iam 2026 06.017

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-lan-iam-2026-06.017`
**Status:** active
**OpenSpec created:** 2026-06-21

## Why

Aujourd'hui, l'accès au dashboard sur **`https://mon.essensys.local`** repose sur une **Basic Auth optionnelle en mode passif** (capture seulement, pas de 401) ou sur des identifiants statiques en bordure Traefik. Il n'existe **pas** de gestion multi-utilisateur LAN : pas de création de comptes, pas de reset mot de passe, pas de rôles locaux, pas d'UI d'administration.

Le backend Go embarque déjà une **ébauche legacy** (`UserService`, `/api/auth/login`, hash SHA1) héritée de la migration ASP.NE…

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 1

## Source files

- `essensys-memory/openspec/changes/essensys-lan-iam-2026-06.017/proposal.md`
- `essensys-memory/openspec/changes/essensys-lan-iam-2026-06.017/design.md`
- `essensys-memory/openspec/changes/essensys-lan-iam-2026-06.017/tasks.md`
