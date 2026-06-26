---
tags: [entity, repo, migration, infra]
sources: [essensys-ansible.md]
created: 2026-06-20
updated: 2026-06-26
era: migration
repo: essensys-ansible
---

# Essensys Ansible

> Référentiel Ansible qui automatise l'intégralité du déploiement Essensys : passerelles Raspberry Pi / CM5 sur site (backend, frontend, MQTT, Redis, AdGuard, Traefik, monitoring, assistant IA) et infrastructure cloud OVH (portail, site support, HTTPS, New Relic).

| | |
|---|---|
| **Catégorie** | Déploiement / Automatisation |
| **Stack** | Ansible (playbooks YAML, rôles), collections `community.docker` et `ansible.posix`, Docker Compose, systemd, Go 1.23 / Node 20, Traefik v2.11, Nginx, Certbot/Let's Encrypt, MkDocs (documentation du dépôt) |
| **Statut** | Actif — `essensys_version V.1.3.0`, `control_plane_version V.1.3.7`, playbook `deploy-portal-stack.yml` (2026-06-26) |
| **Era** | migration |

## Rôle

Ce dépôt est le **point d'entrée du déploiement** de toute la plateforme Essensys. Il remplace les anciens scripts shell (`install.sh` / `update.sh` / `uninstall.sh` du dépôt `essensys-raspberry-install`) par des playbooks Ansible idempotents.

Il couvre deux familles de cibles :

1. **Les passerelles domotiques sur site** (groupe d'inventaire `raspberrypi`) — Raspberry Pi et modules Compute Module 5 (CM5) installés dans les armoires électriques des bâtiments. Elles font tourner le backend Go, le frontend, le broker MQTT, Redis, le DNS/ad-blocking, le reverse-proxy et le monitoring local.
2. **L'infrastructure cloud OVH** (groupe d'inventaire `essensys`, hôte `test.essensys.fr` / `mon.essensys.fr`) — héberge le portail utilisateur consolidé, le site support, PostgreSQL et la terminaison HTTPS publique.

Il s'appuie sur les autres dépôts comme **sources** (clone Git de `essensys-server-backend`, `essensys-server-frontend`, `essensys-user-portal-backend`, `essensys-control-plane`) qu'il compile et installe sur les hôtes cibles.

## Intégrations

- **Dépôts sources clonés/compilés :** `essensys-server-backend`, `essensys-server-frontend`, `essensys-user-portal-backend`, `essensys-control-plane` (org GitHub `essensys-hub`).
- **New Relic** (compte `8176900`, région EU) : APM backend (`essensys-cloud-backend`), Browser (portail + site support), Infrastructure (`ovh-mon-essensys`) avec intégration PostgreSQL (`nri-postgresql`).
- **Let's Encrypt / Certbot** pour la terminaison HTTPS publique (`mon.essensys.fr`, `www`, `gateway`, `test.essensys.fr`).
- **Cloud hub** `https://mon.essensys.fr` : les passerelles remontent leur état via le rôle `raspberry_push_status` (TTL d'obsolescence d'échange : 120 s).
- **MQTT (Mosquitto)**, **Redis**, **AdGuard Home**, **Traefik/Caddy**, **Prometheus/Alertmanager**, **Home Assistant**, **OpenClaw + WhatsApp** déployés sur les passerelles.
- **GitHub Actions** : rôle `raspberry_github_runner` pour CI/CD sur les passerelles.
- **UniFi** : intégration optionnelle (désactivée par défaut, `unifi_enabled: false`).

## Structure

```
essensys-ansible/
├── inventory                    # Inventaire par défaut (essensys cloud + raspberrypi local)
├── inventory.gateway            # Inventaire dédié au profil Gateway CM5 (double NIC + NVMe)
├── requirements.yml             # Collections Ansible Galaxy (community.docker, ansible.posix)
├── install.raspberrypi.yml      # Installation complète d'une passerelle RPi
├── install.gateway.yml          # Installation passerelle CM5 (double NIC + NVMe)
├── install.github_runner.yml    # Déploiement d'un runner GitHub Actions self-hosted
├── update.raspberrypi.yml       # Mise à jour applicative d'une passerelle
├── uninstall.raspberrypi.yml    # Désinstallation passerelle (confirmation requise)
├── uninstall.cm5.yml            # Désinstallation passerelle CM5 (confirmation requis

_… voir source complète dans raw/_

## Points d'attention

- **Cutover backend cloud :** deux modes coexistent, pilotés par `cloud_backend_consolidated` et `cloud_backend_legacy_mode` (group_vars `main.yml`). `support-site.yml` choisit dynamiquement entre les rôles consolidés (`cloud_backend` / `cloud_nginx`) et legacy (`backend` / `portal_backend` / `portal_nginx`). Vérifier ces flags avant tout déploiement cloud.
- **Secrets :** `secrets/cloud/essensys.sops.yaml` (SOPS + age, versionné chiffré) ; rôle `sops_load`. Legacy : `group_vars/essensys/vault.yml` (Ansible Vault, gitignored — rollback). Gateway phase 2 : `host_vars/*/secrets.sops.yaml`. Doc : `docs/secrets.md`, [[Secrets Management]].
- **Étapes manuelles CM5 non automatisables** (cf. `roles/raspberry_gateway_network/README.md`) : flash eMMC via `rpiboot`, activation PCIe/NVMe dans `/boot/firmware/config.txt`, relevé des adresses MAC eth0/eth1 à renseigner dans l'inventaire **avant** le premier run.
- **Versions hétérogènes (résolu 2026-06-26) :** `update.raspberrypi.yml` aligné sur `V.1.3.0` et Go **1.26** ; pre_task upgrade Go si < 1.25 (requis par `essensys-server-backend` go.mod).
- **Cloudsync gateway CM5 :** le service systemd doit lancer le binaire avec `-config /opt/data/config/backend/config.yaml` (pas le `config.yaml` par défaut sous `/opt/essensys/backend/` où `cloud.enabled: false`). Corrigé dans le rôle `raspberry_backend` (2026-06-26). Symptôme : commandes portail distant en `pending` sur OVH, éclairage inopérant.
- **Playbooks déploiement ciblés :** `deploy-portal-stack.yml` (hub + SPA portail, sans certbot), `deploy-security-fix.yml` (backend cloud + SPA support).
- **Image Docker backend `essensyshub/essensys-backend:V.1.3.0` :** régression arm64 au restart (`exec /usr/local/bin/server: no such file or directory`) — ticket Jira SCRUM-15 ; workaround systemd + binaire git.
- **Playbooks destructifs** protégés par des gardes (`confirm_uninstall`, `confirm_cm5_uninstall`, `confirm_cm5_nixos_prep`) à passer explici

_… voir source complète dans raw/_

## Liens

- [[Platform Overview]]
- [[Feature Lifecycle]]
- [[Security Gate]]

## Source

`raw/architecture/repos/essensys-ansible.md`
