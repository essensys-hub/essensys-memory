## Why

Finaliser la publication doc : enregistrement DNS, cert Let's Encrypt, vhost dedie (migration depuis /docs/ sur mon.essensys.fr).

> **Roadmap ID:** 2026-06.008  
> **Horizon:** voir [[OpenSpec Queue 2026 06]]  
> **Depend de:** 007

## What Changes

- Epic **DNS docs.essensys.fr et certificat dedie** — voir [[Product Roadmap]].
- Dépôt hôte principal : `essensys-memory`.

## Capabilities

### New Capabilities

- `doc-site-dns` : spec dans `specs/doc-site-dns/spec.md`.

## Impact

Composants : essensys-ansible, essensys-doc.

## Gate

Ne pas demarrer implementation tant que les dependances 007 ne sont pas **completed** (sauf N/A).
