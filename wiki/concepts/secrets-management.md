---
tags: [concept, security, infra, ansible, sops]
sources: [secrets.md, prompts/vault.md, essensys-secrets-sops-migration-2026-06-028]
created: 2026-06-25
updated: 2026-06-25
era: modern
---

# Secrets Management

Gestion des **secrets de déploiement** Essensys (JWT, OAuth, SMTP, PostgreSQL, New Relic, tokens gateway) via **SOPS + age + Ansible**.

> Distinct du vault Obsidian [[Essensys Memory]] (brain projet).

## Décision (2026-06.028)

| Avant | Après (MVP cloud) |
|-------|-------------------|
| `group_vars/essensys/vault.yml` gitignored + Ansible Vault | `essensys-ansible/secrets/cloud/essensys.sops.yaml` chiffré **dans Git** |
| Mot de passe vault partagé | Clés **age** par opérateur |
| Review PR impossible | Diff SOPS chiffré reviewable |

Runtime cloud **inchangé en MVP** : templates Jinja2 → `.env` systemd (`EnvironmentFile`).

## Périmètres

| Cible | Fichier | Playbook |
|-------|---------|----------|
| Cloud OVH | `secrets/cloud/essensys.sops.yaml` | `support-site.yml`, `setup-newrelic-alerts.yml` |
| Gateway CM5 | `host_vars/<hostname>/secrets.sops.yaml` | `install.gateway.yml` (phase 2) |

Rôle Ansible : **`sops_load`** (`community.sops` lookup).

## Doc canonique

- `essensys-ansible/docs/secrets.md` — bootstrap, rotation, rollback, inventaire
- `essensys-ansible/secrets/README.md` — quick start opérateur
- OpenSpec : [[Roadmap OpenSpec]] change **2026-06.028**

## Alignement NixOS

Même format SOPS + age que la voie **sops-nix** ([[Essensys Gateway Nixos]]) — matrice parité dans `docs/secrets.md`.

## Liens

- [[Essensys Ansible]]
- [[Gateway PKI]] — tokens `cloud_gateway_token`, mTLS futur
- [[Install Documentation]] — variables env / vault gateway

## Règles agent

- `.cursor/rules/essensys-install-doc.mdc` — MAJ si templates env changent
- `.cursor/rules/essensys-centralized-doc.mdc` — index brain
- PR : `[ ] Brain updated` si touché
