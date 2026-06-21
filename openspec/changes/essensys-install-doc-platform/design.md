## Context

Install gateway = cross-cutting : Ansible playbooks, CM5 image, cloud register, TLS `.local`, tests WAN.

## Décisions

1. **Index unique brain** : `wiki/concepts/install-documentation.md` pointe vers sources, ne duplique pas les playbooks.
2. **Règle** `essensys-install-doc.mdc` : globs `essensys-ansible/**`, `essensys-raspberry-install/**`, `essensys-raspberry-gateway/**`.
3. **Ingest** : après modif install, sync excerpt vers brain (manuel ou ingest) + log.
4. **Wizard futur** = change OpenSpec séparé (`essensys-install-wizard` — planned), dépend de ce change.

## Sources canoniques (vérifiées)

- `essensys-ansible/docs/install-gateway.md`
- `essensys-ansible/docs/tls-local-domain.md`
- `essensys-ansible/docs/cloud-backend-migration.md`
- `essensys-raspberry-install/` (bootstrap)
- `essensys-raspberry-gateway/docs/` (accès, maintenance)

## Non-goals

- UI wizard particulier (change futur).
- Automatisation Ansible du brain sync (option Later).
