# Tasks — essensys-doc-site

## Phase 1 — Contenu & build

- [x] 1.1 Ajouter `mkdocs.yml` + nav dans `essensys-doc` (subset archi + index)
- [x] 1.2 Inclure ou lier extraits install (`install-gateway`, `guide-utilisateur-https-local`, raspberry-install)
- [x] 1.3 GitHub Action : `mkdocs build` (+ mike si versioning requis)

## Phase 2 — OVH deploy

- [x] 2.1 Rôle Ansible `docs_site` : `/opt/essensys/docs-site/`, reload Nginx
- [x] 2.2 DNS `docs.essensys.fr` + cert Let's Encrypt (playbook support-site)
- [x] 2.3 Snippet Nginx vhost statique (pas de conflit `/api/`)

## Phase 3 — Intégration produit

- [x] 3.1 Lien « Documentation » dans `essensys-support-site` SPA
- [x] 3.2 Concept wiki `user-documentation-site.md` + backlinks [[Centralized Documentation]]
- [x] 3.3 MAJ `raw/architecture/repos/essensys-doc.md` (publication OVH)

## Verification

```bash
cd essensys-doc && bash scripts/prepare-docs.sh && mkdocs build --strict
curl -sS -o /dev/null -w '%{http_code}\n' https://docs.essensys.fr/
cd essensys-memory && openspec validate essensys-doc-site
python3 scripts/lint-wiki.py
```

> **Note deploy** : DNS `docs.essensys.fr` → IP VPS requis avant premier `certbot` sur le serveur.
