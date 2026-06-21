# Tasks — essensys-doc-site

## Phase 1 — Contenu & build

- [ ] 1.1 Ajouter `mkdocs.yml` + nav dans `essensys-doc` (subset archi + index)
- [ ] 1.2 Inclure ou lier extraits install (`install-gateway`, `guide-utilisateur-https-local`, raspberry-install)
- [ ] 1.3 GitHub Action : `mkdocs build` (+ mike si versioning requis)

## Phase 2 — OVH deploy

- [ ] 2.1 Rôle Ansible `docs_site` : `/opt/essensys/docs-site/`, reload Nginx
- [ ] 2.2 DNS `docs.essensys.fr` + cert Let's Encrypt (playbook support-site)
- [ ] 2.3 Snippet Nginx vhost statique (pas de conflit `/api/`)

## Phase 3 — Intégration produit

- [ ] 3.1 Lien « Documentation » dans `essensys-support-site` SPA
- [ ] 3.2 Concept wiki `user-documentation-site.md` + backlinks [[Centralized Documentation]]
- [ ] 3.3 MAJ `raw/architecture/repos/essensys-doc.md` (publication OVH)

## Verification

```bash
cd essensys-doc && mkdocs build --strict
curl -sS -o /dev/null -w '%{http_code}\n' https://docs.essensys.fr/
cd essensys-memory && openspec validate essensys-doc-site
python3 scripts/lint-wiki.py
```
