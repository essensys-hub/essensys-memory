## Why

L’installation gateway (CM5, dual-NIC, cloud register, TLS local) est documentée dans **Ansible**, **raspberry-install**, **raspberry-gateway** — difficile pour un particulier et pour les agents. Il faut une **doc install centralisée** dans le brain + une **règle** obligeant toute modif install/deploy à la mettre à jour.

## What Changes

- Règle **`.cursor/rules/essensys-install-doc.mdc`** — triggers sur `essensys-ansible`, `essensys-raspberry-install`, `essensys-raspberry-gateway`, playbooks gateway.
- Concept wiki **`wiki/concepts/install-documentation.md`** — index des procédures, liens vers sources immuables `raw/`.
- Section dédiée dans **`wiki/synthesis/product-roadmap.md`** (Later → Now quand wizard prévu).
- Pas de wizard UI dans ce change — **documentation et gouvernance** seulement.

## Capabilities

### New Capabilities

- `install-doc-rule` : règle agent + liste fichiers à synchroniser vers brain.
- `install-doc-index` : page concept avec parcours installateur / support / particulier.

## Impact

- `.cursor/rules/`, wiki concepts/synthesis.
- Sources de vérité opérationnelles restent dans les dépôts ; brain agrège et wikilink.

## Gate Phase 0

**Completed** avec `essensys-centralized-doc-maintenance` avant changes feature install (wizard, provisioning UX).

## Liens

- `essensys-ansible/docs/install-gateway.md`
- [[Essensys Ansible]], [[Essensys Raspberry Install]], [[Essensys Raspberry Gateway]]
