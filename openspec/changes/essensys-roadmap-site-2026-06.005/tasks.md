# Tasks — essensys-roadmap-site-2026-06.005

> **Roadmap ID:** 2026-06.005 — **planned** (scaffold juin 2026)

## Phase 0 — Spec & gouvernance

- [x] 0.1 Proposal + design + spec
- [x] 0.2 Prompt `prompts/roadmap-site.md`
- [x] 0.3 Rule `.cursor/rules/essensys-roadmap-site.mdc` (sync queue → sites publics) + MAJ AGENTS/CLAUDE
- [x] 0.4 Scripts `publish-roadmap-public.sh`, `build-roadmap-site.sh`, `prepare-blog.sh`
- [x] 0.5 Spec Ansible `specs/roadmap-site-ansible/spec.md` + section design deploy
- [x] 0.6 Valider dependance 004 (queue + product-roadmap a jour — 2026-06-22)

## Phase 1 — Contenu & générateur

- [x] 1.1 Creer `content/roadmap/` + `content/blog/` + README schema frontmatter
- [x] 1.2 Script `scripts/build-roadmap-site.sh` + `build-roadmap-site.py`
- [x] 1.3 Script `scripts/prepare-blog.sh` (blog → support-site public/)
- [x] 1.4 Article pilote blog 2026-06.007 doc-site

## Phase 2 — Site roadmap.essensys.fr

- [x] 2.1 Generateur HTML statique (`build-roadmap-site.py`)
- [x] 2.2 Pages : index (en cours / passé / futur), fiche change detaillee
- [ ] 2.3 CI GitHub Action `roadmap-site.yml` (build artifact)

## Phase 3 — Deploy Ansible OVH

- [x] 3.1 Creer `essensys-ansible/roles/roadmap_site/defaults/main.yml`
- [x] 3.2 `roles/roadmap_site/tasks/main.yml`
- [x] 3.3 `roles/roadmap_site/templates/essensys-roadmap.conf.j2`
- [x] 3.4 `roles/roadmap_site/handlers/main.yml`
- [x] 3.5 Playbook `deploy-roadmap-site.yml`
- [x] 3.6 Documenter dans `essensys-ansible/docs/playbooks.md`
- [ ] 3.7 DNS `roadmap.essensys.fr` → VPS OVH
- [ ] 3.8 DoD : `ansible-playbook deploy-roadmap-site.yml` + `curl -sI https://roadmap.essensys.fr` → 200

## Phase 4 — Blog mon.essensys.fr

- [x] 4.1 Routes `/blog`, `/blog/:slug` support-site
- [x] 4.2 Composants Blog + BlogPost + navbar
- [x] 4.3 Integrer prepare-blog au deploy Ansible (role frontend)
- [ ] 4.4 DoD : `curl -sI https://mon.essensys.fr/blog` → 200

## Phase 5 — Sync continue

- [ ] 5.1 Hook doc : checklist PR resync roadmap + blog si epic significatif
- [ ] 5.2 Post blog pour prochain epic active (006 ou 009)
- [ ] 5.3 Option : activer `roadmap_site` dans `support-site.yml` apres validation

## Verification

```bash
cd essensys-memory && openspec validate essensys-roadmap-site-2026-06.005
python3 scripts/lint-wiki.py
cd essensys-ansible && ansible-playbook deploy-roadmap-site.yml -i inventory/ovh --check
curl -sI https://roadmap.essensys.fr | head -1
curl -sI https://mon.essensys.fr/blog | head -1
```
