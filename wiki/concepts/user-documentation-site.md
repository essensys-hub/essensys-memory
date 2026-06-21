---
tags: [concept, documentation, user-facing, ovh]
sources: [essensys-doc-site/proposal.md, essensys-doc, essensys-ansible]
created: 2026-06-21
updated: 2026-06-21
era: modern
---

# User Documentation Site

Facade **publique** de la documentation Essensys, hébergée sur le **VPS OVH** — distincte du brain (`essensys-memory`) et de la doc admin support-site.

## Rôle

| Couche | Public | Hébergement |
|--------|--------|-------------|
| **Brain** | Non (agents) | Vault Obsidian |
| **Dépôts** | Sources canoniques | GitHub |
| **Ce site** | Oui (users, installateurs) | `docs.essensys.fr` (cible) |
| **Support SPA** | Admin + portail | `mon.essensys.fr` |

## Stack cible (MVP)

- **MkDocs Material** + build CI (aligné `essensys-raspberry-install`)
- Static **Nginx** sur OVH — `/opt/essensys/docs-site/`
- Contenu : subset `essensys-doc/archi`, guides install vendus depuis `essensys-ansible`
- Deploy : role Ansible `docs_site` dans `support-site.yml`
- Lien SPA : `VITE_DOCS_URL` / navbar « Documentation »

## OpenSpec

[[Essensys Doc Site]] — change **completed** (2026-06-21). Deploy prod : DNS `docs.essensys.fr` → VPS puis `ansible-playbook support-site.yml`.

## Voir aussi

- [[Centralized Documentation]] — gouvernance sources
- [[Install Documentation]] — index procédures install
- [[Essensys Doc]] — dépôt architecture
