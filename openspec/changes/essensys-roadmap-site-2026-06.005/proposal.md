## Why

La [[Product Roadmap]] et la [[OpenSpec Queue 2026 06]] vivent dans `essensys-memory` — lisibles par les devs et agents, **invisibles** pour la communauté et les parties prenantes externes. Il manque une **facade publique** listant les changes (en cours, passés, futur) avec descriptions détaillées, plus un canal **blog** sur [mon.essensys.fr](https://mon.essensys.fr) pour documenter les avancées avec captures d'écran.

> **Roadmap ID:** 2026-06.005  
> **Horizon:** voir [[OpenSpec Queue 2026 06]]  
> **Depend de:** 004

## What Changes

- Site statique **`https://roadmap.essensys.fr`** généré depuis manifest OpenSpec + proposals/tasks.
- Rubrique **`https://mon.essensys.fr/blog`** dans la SPA support-site.
- Contenu blog : `content/blog/` + assets `raw/assets/roadmap-blog/`.
- Rule agent **`.cursor/rules/essensys-roadmap-site.mdc`** : resync obligatoire à chaque avancement significatif.
- Prompt opérationnel : `prompts/roadmap-site.md`.
- Deploy Ansible OVH (pattern `docs_site`).

## Capabilities

### New Capabilities

- `roadmap-site-publish` : générateur, nav en cours/passé/futur, CI, Nginx, DoD prod.
- `roadmap-site-ansible` : rôle `roadmap_site`, playbook `deploy-roadmap-site.yml`, DNS/TLS OVH.
- `roadmap-blog-sync` : posts Markdown, build Vite, lien navbar, captures MCP Chrome.

## Impact

- `essensys-memory` (scripts, content/, OpenSpec)
- `essensys-support-site` (routes `/blog`, navbar)
- `essensys-ansible` (rôle `roadmap_site`, playbook `deploy-roadmap-site.yml`, DNS, cert, doc `docs/playbooks.md`)
- `essensys-doc` (optionnel : lien croisé doc ↔ roadmap)

## Non-goals

- Remplacer le brain Obsidian ou éditer la queue à la main sur le site public.
- CMS dynamique avec base de données.
- Blog commentaires / auth rédacteur (Markdown git-only MVP).

## Gate

Ne pas demarrer implementation tant que la dependance **004** (living roadmap + queue) n'est pas **active** avec queue a jour.
