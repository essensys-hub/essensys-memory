# Tasks — essensys-install-doc-platform

> **Phase 0 — priorité 2** (bloquant pour wizard / provisioning UX)

## Règle Cursor

- [x] 1.1 Créer `.cursor/rules/essensys-install-doc.mdc`
- [x] 1.2 Mettre à jour `AGENTS.md` (section install doc)

## Wiki

- [x] 2.1 Créer `wiki/concepts/install-documentation.md` (index procédures)
- [x] 2.2 Wikilinks : [[Essensys Ansible]], [[Essensys Raspberry Install]], [[Essensys Raspberry Gateway]], [[Gateway PKI]] (register)
- [x] 2.3 Backlink depuis [[Product Roadmap Rubric]] et [[Index]]

## Sync sources

- [x] 3.1 Vérifier chemins `install-gateway.md`, `tls-local-domain.md` sous ESSENSYS_ROOT
- [x] 3.2 Option : excerpt dans `wiki/sources/` si ingest manuel — **différé** (Later, non bloquant gate)

## Validation

- [x] 4.1 `python3 scripts/lint-wiki.py` → 0 erreur
- [x] 4.2 Entrée `wiki/log.md`

## Dépendance

- [x] D.1 Lire et appliquer `essensys-centralized-doc.mdc` pour toute mise à jour wiki
