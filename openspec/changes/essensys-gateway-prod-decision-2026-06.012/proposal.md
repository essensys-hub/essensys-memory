## Why

Documenter criteres, choix prod, gate deploiement ; lier essensys-gateway-dual-nic et essensys-gateway-nixos.

> **Roadmap ID:** 2026-06.012  
> **Horizon:** voir [[OpenSpec Queue 2026 06]]  
> **Depend de:** 010,011

## What Changes

- Epic **Decision prod CM5 Ansible vs NixOS** — voir [[Product Roadmap]].
- Dépôt hôte principal : `essensys-memory`.

## Capabilities

### New Capabilities

- `gateway-prod-decision` : spec dans `specs/gateway-prod-decision/spec.md`.

## Impact

Composants : essensys-raspberry-gateway, essensys-ansible.

## Gate

Ne pas demarrer implementation tant que les dependances 010,011 ne sont pas **completed** (sauf N/A).
