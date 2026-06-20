# essensys-ansible

> Référentiel Ansible qui automatise l'intégralité du déploiement Essensys : passerelles Raspberry Pi / CM5 sur site (backend, frontend, MQTT, Redis, AdGuard, Traefik, monitoring, assistant IA) et infrastructure cloud OVH (portail, site support, HTTPS, New Relic).

**Catégorie :** Déploiement / Automatisation
**Stack :** Ansible (playbooks YAML, rôles), collections `community.docker` et `ansible.posix`, Docker Compose, systemd, Go 1.23 / Node 20, Traefik v2.11, Nginx, Certbot/Let's Encrypt, MkDocs (documentation du dépôt)
**Statut :** Actif — versionne `essensys_version V.1.3.0` et `control_plane_version V.1.3.7`, ~40 rôles, doc MkDocs publiée via GitHub Pages

## Rôle dans l'architecture Essensys

Ce dépôt est le **point d'entrée du déploiement** de toute la plateforme Essensys. Il remplace les anciens scripts shell (`install.sh` / `update.sh` / `uninstall.sh` du dépôt `essensys-raspberry-install`) par des playbooks Ansible idempotents.

Il couvre deux familles de cibles :

1. **Les passerelles domotiques sur site** (groupe d'inventaire `raspberrypi`) — Raspberry Pi et modules Compute Module 5 (CM5) installés dans les armoires électriques des bâtiments. Elles font tourner le backend Go, le frontend, le broker MQTT, Redis, le DNS/ad-blocking, le reverse-proxy et le monitoring local.
2. **L'infrastructure cloud OVH** (groupe d'inventaire `essensys`, hôte `test.essensys.fr` / `mon.essensys.fr`) — héberge le portail utilisateur consolidé, le site support, PostgreSQL et la terminaison HTTPS publique.

Il s'appuie sur les autres dépôts comme **sources** (clone Git de `essensys-server-backend`, `essensys-server-frontend`, `essensys-user-portal-backend`, `essensys-control-plane`) qu'il compile et installe sur les hôtes cibles.

## Structure du dépôt

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
├── uninstall.cm5.yml            # Désinstallation passerelle CM5 (confirmation requise)
├── prepare.nixos-cm5.yml        # Préparation NixOS sur CM5 (confirmation requise)
├── quick-deploy.yml             # Redéploiement rapide backend+frontend (cloud)
├── support-site.yml             # Déploiement complet du site support / portail cloud
├── cloud-nginx-only.yml         # Ré-application du snippet nginx consolidé seul
├── deploy_openclaw.yml          # Déploiement de l'assistant IA OpenClaw seul
├── enable-https-prod.yml        # Certificats Let's Encrypt (mon/www/gateway.essensys.fr)
├── enable-https-test.yml        # Certificat Let's Encrypt (test.essensys.fr)
├── setup-newrelic-alerts.yml    # Configuration alertes + déploiements New Relic
├── promote-admin.yml            # Promotion d'un utilisateur en admin (SQL PostgreSQL)
├── group_vars/essensys/         # main.yml (New Relic, cloud hub), database.yml, vault.yml
├── config/                      # database.example.yml, newrelic.vars.example.yml, .env
├── roles/                       # ~40 rôles (voir détail ci-dessous)
├── docs/ + mkdocs.yml + site/   # Documentation MkDocs (publiée GitHub Pages)
└── .github/workflows/           # deploy-docs.yml (publication de la doc)
```

## Ce qui est déployé / automatisé

### Inventaires (hôtes cibles)

| Inventaire | Groupe | Hôtes |
|---|---|---|
| `inventory` | `essensys` | `test.essensys.fr` (cloud OVH, user `ubuntu`) |
| `inventory` | `raspberrypi` | `localhost` (exécution locale sur la passerelle) |
| `inventory.gateway` | `raspberrypi` | `gateway-essensys` @ `192.168.0.14`, profil double NIC (eth0 LAN / eth1 armoire `10.0.1.1/24`) + DHCP serveur (`10.0.1.100-200`) + NVMe (`/dev/nvme0n1` → `/mnt/nvme`) |

### Playbooks → ce qu'ils installent

| Playbook | Hôtes | Installe / configure |
|---|---|---|
| `install.raspberrypi.yml` | `raspberrypi` | Stack complète passerelle : système de base + Docker, Mosquitto (MQTT), Redis, backend Go, serveur MCP, frontend, Nginx (port 80, client legacy), Traefik (port 443 + auth, WAN), Control Plane, AdGuard (DNS/ad-block), Prometheus/Alertmanager/Node Exporter, OpenClaw (assistant IA + WhatsApp), lancement de tous les conteneurs via Docker Compose, puis monitor, logrotate, push status |
| `install.gateway.yml` | `raspberrypi` (CM5) | Idem ci-dessus **plus** en pré-requis : stockage NVMe, réseau double NIC (systemd-networkd), DHCP+DNS split sur eth1, Avahi. Compile le backend/frontend depuis les sources Git (Go 1.23, Node 20). UniFi désactivé par défaut |
| `update.raspberrypi.yml` | `raspberrypi` | Mise à jour applicative seule : backend, MCP, frontend, Nginx (port 80), Traefik (port 443 + auth), push status |
| `support-site.yml` | `essensys` (cloud) | Site support / portail cloud : common, New Relic Infra, PostgreSQL, backend (consolidé `cloud_backend` ou legacy selon flag), frontend, portal backend/frontend, nginx (consolidé ou legacy), puis import de `enable-https-prod.yml` |
| `quick-deploy.yml` | `essensys` | Redéploiement rapide backend + frontend |
| `cloud-nginx-only.yml` | `essensys` | Ré-applique uniquement le snippet nginx consolidé |
| `enable-https-prod.yml` | `essensys` | Certbot + certificats Let's Encrypt pour `mon.essensys.fr`, `www.essensys.fr`, `gateway.essensys.fr` (webroot `/var/www/certbot`), réapplication nginx |
| `enable-https-test.yml` | `essensys` | Certbot --nginx pour `test.essensys.fr` (avec redirect) |
| `setup-newrelic-alerts.yml` | `essensys` | Rôles `newrelic_alerts` + `newrelic_deployment` |
| `promote-admin.yml` | `essensys` | `UPDATE users SET role='admin'` sur PostgreSQL `essensys_db` |
| `deploy_openclaw.yml` | `raspberrypi` | Déploiement isolé de l'assistant IA OpenClaw |
| `install.github_runner.yml` | `raspberrypi` | Runner GitHub Actions self-hosted (prompt URL repo + token) |
| `prepare.nixos-cm5.yml` | `raspberrypi` | Préparation NixOS sur CM5 (garde `confirm_cm5_nixos_prep=true`) |
| `uninstall.raspberrypi.yml` / `uninstall.cm5.yml` | `raspberrypi` | Désinstallation complète (gardes `confirm_uninstall=true` / `confirm_cm5_uninstall=true`) |

### Rôles (roles/)

**Cloud OVH** (groupe `essensys`) :
- `common` — préparation système de base de l'hôte cloud
- `database` — PostgreSQL (host `127.0.0.1:5432`, base `essensys_db`, user `essensys`)
- `backend` / `cloud_backend` — backend legacy vs backend consolidé (clone `essensys-user-portal-backend`, service systemd `essensys-cloud-backend` sur port 8080, import des machines depuis `machines.json`)
- `frontend` / `portal_frontend` — frontend support et frontend portail utilisateur
- `portal_backend` — backend portail (mode legacy)
- `cloud_nginx` / `portal_nginx` — config Nginx consolidée vs legacy
- `newrelic_infra` — agent New Relic Infrastructure + intégration `nri-postgresql`
- `newrelic_alerts` / `newrelic_deployment` — politiques d'alerte et marqueurs de déploiement New Relic

**Passerelles Raspberry Pi / CM5** (groupe `raspberrypi`) :
- `raspberry_common`, `raspberry_docker`, `raspberry_avahi` — base système, Docker, mDNS
- `raspberry_mosquitto` — broker MQTT
- `raspberry_redis` — Redis
- `raspberry_backend` — clone + compilation Go du backend (service `essensys-backend`)
- `raspberry_mcp` — serveur MCP (Model Context Protocol)
- `raspberry_frontend` — frontend local
- `raspberry_nginx` — reverse-proxy port 80 (tolérant client legacy)
- `raspberry_traefik` / `raspberry_caddy` — reverse-proxy port 443 + auth (Traefik v2.11 ; Caddy alternatif)
- `raspberry_control_plane` — control plane local (V.1.3.7)
- `raspberry_adguard` — AdGuard Home (DNS + ad-blocking)
- `raspberry_prometheus` — Prometheus + Alertmanager + Node Exporter
- `raspberry_openclaw` — assistant IA OpenClaw + intégration WhatsApp
- `raspberry_compose` — génère et lance le `docker-compose.yml` global (orchestre tous les conteneurs)
- `raspberry_monitor`, `raspberry_logrotate`, `raspberry_push_status` — supervision locale, rotation des logs, remontée d'état vers le cloud hub
- `raspberry_homeassistant` — intégration Home Assistant
- **Profil Gateway CM5 :** `raspberry_gateway_nvme` (stockage NVMe + bind mounts), `raspberry_gateway_network` (double NIC systemd-networkd, eth0 LAN / eth1 armoire), `raspberry_gateway_dhcp` (serveur DHCP + DNS split sur eth1)
- **NixOS / cycle de vie :** `raspberry_cm5_nixos`, `raspberry_cm5_uninstall`, `raspberry_uninstall`
- `raspberry_github_runner` — runner GitHub Actions self-hosted

## Build / Exécution

```bash
# Pré-requis : installer les collections
ansible-galaxy collection install -r requirements.yml

# --- Passerelle Raspberry Pi standard ---
ansible-playbook -i inventory install.raspberrypi.yml
ansible-playbook -i inventory update.raspberrypi.yml
ansible-playbook -i inventory uninstall.raspberrypi.yml -e "confirm_uninstall=true"

# --- Passerelle Gateway CM5 (double NIC + NVMe) ---
ansible-playbook -i inventory.gateway install.gateway.yml
ansible-playbook -i inventory.gateway uninstall.cm5.yml -e confirm_cm5_uninstall=true
ansible-playbook -i inventory.gateway prepare.nixos-cm5.yml -e confirm_cm5_nixos_prep=true

# --- Cloud OVH (site support / portail) ---
ansible-playbook -i inventory support-site.yml
ansible-playbook -i inventory quick-deploy.yml          # redéploiement rapide back+front
ansible-playbook -i inventory enable-https-prod.yml
ansible-playbook -i inventory setup-newrelic-alerts.yml

# --- Options courantes ---
# Let's Encrypt staging : -e "use_staging=true"
# Email ACME            : -e "acme_email=ton@email"
```

Le domaine WAN est lu sur l'hôte dans `/home/essensys/domain.txt` (défaut `essensys.acme.com`). Le script de génération htpasswd est installé en `/usr/local/bin/generate-htpasswd-essensys.sh`.

La documentation du dépôt est gérée par **MkDocs** (`mkdocs serve` / `mkdocs build`) et publiée automatiquement via GitHub Pages (`.github/workflows/deploy-docs.yml`).

## Intégrations

- **Dépôts sources clonés/compilés :** `essensys-server-backend`, `essensys-server-frontend`, `essensys-user-portal-backend`, `essensys-control-plane` (org GitHub `essensys-hub`).
- **New Relic** (compte `8176900`, région EU) : APM backend (`essensys-cloud-backend`), Browser (portail + site support), Infrastructure (`ovh-mon-essensys`) avec intégration PostgreSQL (`nri-postgresql`).
- **Let's Encrypt / Certbot** pour la terminaison HTTPS publique (`mon.essensys.fr`, `www`, `gateway`, `test.essensys.fr`).
- **Cloud hub** `https://mon.essensys.fr` : les passerelles remontent leur état via le rôle `raspberry_push_status` (TTL d'obsolescence d'échange : 120 s).
- **MQTT (Mosquitto)**, **Redis**, **AdGuard Home**, **Traefik/Caddy**, **Prometheus/Alertmanager**, **Home Assistant**, **OpenClaw + WhatsApp** déployés sur les passerelles.
- **GitHub Actions** : rôle `raspberry_github_runner` pour CI/CD sur les passerelles.
- **UniFi** : intégration optionnelle (désactivée par défaut, `unifi_enabled: false`).

## Points d'attention

- **Cutover backend cloud :** deux modes coexistent, pilotés par `cloud_backend_consolidated` et `cloud_backend_legacy_mode` (group_vars `main.yml`). `support-site.yml` choisit dynamiquement entre les rôles consolidés (`cloud_backend` / `cloud_nginx`) et legacy (`backend` / `portal_backend` / `portal_nginx`). Vérifier ces flags avant tout déploiement cloud.
- **Secrets :** `group_vars/essensys/vault.yml` (Ansible Vault) et `config/.env` contiennent des secrets — non détaillés ici. Présence d'exemples (`database.example.yml`, `newrelic.vars.example.yml`, `.env.example`).
- **Étapes manuelles CM5 non automatisables** (cf. `roles/raspberry_gateway_network/README.md`) : flash eMMC via `rpiboot`, activation PCIe/NVMe dans `/boot/firmware/config.txt`, relevé des adresses MAC eth0/eth1 à renseigner dans l'inventaire **avant** le premier run.
- **Versions hétérogènes :** `install.*.yml` utilisent Go 1.23.4 et `essensys_version V.1.3.0`, mais `update.raspberrypi.yml` référence encore `backend_version V.1.2.2` et Go 1.21.5 — désalignement à surveiller.
- **Playbooks destructifs** protégés par des gardes (`confirm_uninstall`, `confirm_cm5_uninstall`, `confirm_cm5_nixos_prep`) à passer explicitement en `-e`.
- **`promote-admin.yml`** contient une adresse e-mail en dur (`nicolas@rineau.eu`) — à paramétrer avant réutilisation.
- L'inventaire par défaut pointe sur `test.essensys.fr` (environnement de test) ; bien choisir l'inventaire/hôte avant un déploiement de production.
