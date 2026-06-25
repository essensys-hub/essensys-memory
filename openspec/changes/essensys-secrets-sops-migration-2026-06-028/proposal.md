## Why

Les secrets Essensys cloud (JWT, OAuth, SMTP, PostgreSQL, New Relic) sont aujourd'hui dans `essensys-ansible/group_vars/essensys/vault.yml`, **gitignored** et chiffrés avec **Ansible Vault** et un mot de passe partagé. Ce modèle empêche la review en PR, complique l'onboarding des opérateurs et diverge de la trajectoire **sops-nix** documentée pour les gateways NixOS. Il faut migrer vers **SOPS + age**, secrets versionnés chiffrés dans Git, tout en conservant le runtime actuel (`.env` systemd sur le VPS OVH).

> **Roadmap ID:** 2026-06.028  
> **Horizon:** Next (infra cloud OVH MVP, puis gateways CM5)  
> **Source:** `prompts/vault.md`

## What Changes

- Introduction de fichiers **SOPS chiffrés avec age** dans `essensys-ansible/secrets/cloud/essensys.sops.yaml` (MVP cloud OVH).
- Nouveau rôle Ansible **`sops_load`** : déchiffrement au déploiement, injection des variables `vault_*` / `portal_*` existantes (templates Jinja2 inchangés en MVP).
- Fichier racine **`.sops.yaml`** avec `creation_rules` par chemin (cloud vs gateway).
- Doc opérateur **`essensys-ansible/docs/secrets.md`** + page brain **`wiki/concepts/secrets-management.md`**.
- Collection Galaxy **`community.sops`** dans `requirements.yml`.
- **BREAKING (opérateur)** : fin de dépendance à `ansible-vault edit group_vars/essensys/vault.yml` pour le cloud — remplacé par `sops secrets/cloud/essensys.sops.yaml`.
- Phase 2 (hors MVP) : secrets gateway par `host_vars/<hostname>/secrets.sops.yaml`.
- Suppression des **defaults dangereux** dans les templates (fail explicite si secret absent).
- Ajustement **`.gitignore`** : retirer `vault.yml` post-migration ; ignorer clés age privées.

## Capabilities

### New Capabilities

- `sops-cloud-secrets` : stockage chiffré versionné, chargement Ansible et déploiement des secrets cloud OVH (`support-site.yml`, playbooks NR).
- `sops-gateway-secrets` : convention SOPS par gateway CM5 (tokens cloudsync, identité) — phase 2, alignée sops-nix.

### Modified Capabilities

_(aucune spec existante dans `openspec/specs/` — nouvelles capabilities uniquement)_

## Impact

- **`essensys-ansible`** : `.sops.yaml`, `secrets/`, rôle `sops_load`, `support-site.yml`, `setup-newrelic-alerts.yml`, `.gitignore`, `config/.env.example`, `requirements.yml`, `docs/secrets.md`, `docs/newrelic.md`.
- **`essensys-memory`** : `wiki/concepts/secrets-management.md`, MAJ [[Essensys Ansible]], `wiki/log.md`.
- **Runtime cloud** : inchangé en MVP — `/opt/essensys/cloud-backend/.env` via `cloud-backend.env.j2`, systemd `EnvironmentFile`.
- **Pas d'impact** protocole legacy IoT, table d'échange, endpoints `/api/serverinfos|mystatus|myactions|done`.
- **Pas d'impact** jumeaux UI/backends domotique (server ↔ portal) — périmètre infra Ansible cloud/gateway uniquement.
- **Alignement** change `essensys-gateway-nixos` (même format SOPS + age pour edge NixOS).
