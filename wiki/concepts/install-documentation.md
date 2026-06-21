---
tags: [concept, documentation, install, gateway]
sources: [install-gateway.md, essensys-ansible, essensys-raspberry-install]
created: 2026-06-21
updated: 2026-06-21
era: modern
---

# Install Documentation

Index **centralisé** des procédures d’installation — sources opérationnelles dans les dépôts, synthèse et liens dans le brain.

## Règle agent

Fichier monorepo : `.cursor/rules/essensys-install-doc.mdc`  
Globs : `essensys-ansible/**`, `essensys-raspberry-install/**`, `essensys-raspberry-gateway/**`

Toute modification playbook, template env, script bootstrap ou doc install **doit** mettre à jour cette page ou ingérer l’extrait pertinent (+ `wiki/log.md`).

## Parcours install gateway CM5

| Étape | Source canonique | Brain |
|-------|------------------|-------|
| Prérequis HW (CM5 dual-NIC) | [[Essensys Raspberry Gateway]] | entité wiki |
| Playbook Ansible | `essensys-ansible/docs/install-gateway.md` | [[Essensys Ansible]] |
| Bootstrap image | [[Essensys Raspberry Install]] | entité wiki |
| TLS local `.local` | `essensys-ansible/docs/tls-local-domain.md` | [[Essensys Traefik]] |
| Enregistrement cloud | `POST /api/portal/admin/gateways/register` | [[Gateway PKI]], [[Gateway Exchange]] |
| Variables cloud sync | `config.yaml` / vault Ansible | [[Essensys Server Backend]] cloudsync |
| Tests WAN HTTPS | `essensys-raspberry-gateway/scripts/test-wan-https-ovh.sh` | — |
| NixOS (alternatif) | [[Essensys Gateway Nixos]] | change OpenSpec |

## Réseau (rappel)

- **eth0** : WAN / LAN utilisateur — HTTPS sortant vers `mon.essensys.fr`
- **eth1** : segment armoire `10.0.1.0/24` — HTTP firmware port 80

## Futur

Wizard particulier = change OpenSpec **`essensys-install-wizard`** (planned) — **après** [[Essensys Install Doc Platform]] completed.

## Voir aussi

- [[Product Roadmap Rubric]] — Phase 0b
- [[Essensys Install Doc Platform]]
