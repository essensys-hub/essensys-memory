## Why

`essensys-doc` et les guides install sont aujourd'hui lus sur **GitHub** ou **GitHub Pages** (raspberry-install, ansible) — pas sur le **VPS OVH** où vivent `mon.essensys.fr`, le portail et l'API. Les utilisateurs et installateurs n'ont pas de **facade doc unifiée** HTTPS sur l'infra Essensys.

## What Changes

- Site statique **MkDocs Material** (aligné raspberry-install / ansible) hébergé sur OVH.
- URL cible : **`https://docs.essensys.fr`** (ou `/docs/` sur `mon.essensys.fr` — décision design).
- Contenu : hub public (subset `essensys-doc/archi`, guides install/utilisateur, liens support) — **pas** le brain Obsidian ni les `skills/` agents.
- CI build + déploiement Ansible (`support-site.yml`, rôle `docs_site`).
- Lien depuis la SPA support-site vers la doc publique.

## Capabilities

### New Capabilities

- `doc-site-publish` : générateur, nav, build CI, Nginx OVH, DoD URL prod.

## Impact

- `essensys-doc` (mkdocs.yml, nav, workflow)
- `essensys-ansible` (rôle deploy, snippet Nginx, cert DNS)
- `essensys-support-site` (lien navbar Documentation)
- `essensys-memory` (concept wiki, [[Product Roadmap]])

## Non-goals (ce change)

- Remplacer `essensys-memory` (brain agents).
- Doc admin support-site (`docs/` rôles audit) — reste interne ou gh-pages.
- Docusaurus / thème React custom — **Later** si besoin parité UI dashboard.

## Liens

- [[Product Roadmap]] — Next
- [[Centralized Documentation]], [[Install Documentation]]
- `essensys-doc`, `essensys-raspberry-install/mkdocs.yml`
