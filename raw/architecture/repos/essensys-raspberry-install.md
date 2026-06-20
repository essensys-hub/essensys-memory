# essensys-raspberry-install

> Provisioning / bootstrap d'installation de la passerelle Essensys sur Raspberry Pi : un script `install.sh` minimal qui pose les prérequis (git, Ansible) puis **délègue tout le déploiement au dépôt `essensys-ansible`** (pile Docker), avec scripts annexes (monitor, push status, DuckDNS, runner GitHub) et configs reverse-proxy historiques.

**Catégorie :** Passerelle / Plan de contrôle
**Stack :** Bash (scripts d'install/maintenance) · Ansible (orchestration déléguée) · Docker (cible d'exécution) · Python 3 (monitor TUI, push status) · Caddy / Traefik / Nginx (configs reverse-proxy) · AdGuard Home · MkDocs Material (doc)
**Statut :** Actif, version courante **V.1.3.0**. ⚠️ Le `README.md` décrit l'**ancienne** architecture (binaires natifs Go/React + systemd) ; le `install.sh` réel (V.1.3.0) est devenu un **bootstrap Ansible→Docker**. Plusieurs scripts/configs (Caddy, Nginx natif, fix-network) sont des vestiges de la version précédente.

## Rôle dans l'architecture Essensys

C'est le **point d'entrée de provisioning** d'une passerelle Essensys sur Raspberry Pi (Pi 4 historiquement, généralisé). Son rôle : amener une carte « nue » (Raspberry Pi OS) à une passerelle Essensys complète et opérationnelle.

Évolution clé (à comprendre absolument) :

- **Avant (README, ≤ V.1.2.x)** : `install.sh` installait Go/Node, clonait `essensys-server-backend` + `essensys-server-frontend`, compilait le backend (port 7070), buildait le frontend, configurait Nginx (80/9090) + Traefik (80/443), et créait des **services systemd natifs**.
- **Maintenant (V.1.3.0)** : `install.sh` est un **bootstrap minimal** qui (1) installe `git` + `ansible`, (2) crée l'utilisateur `essensys`, (3) gère le domaine WAN (`domain.txt`), (4) clone/maj `essensys-ansible` (`/opt/essensys-ansible`), (5) lance `ansible-playbook install.raspberrypi.yml`. Le déploiement réel — **conteneurs Docker** — est entièrement décrit dans `essensys-ansible`.

Ce dépôt n'embarque donc plus la logique d'installation : il **bootstrappe Ansible**, qui à son tour déploie la pile de conteneurs orchestrée ensuite par `essensys-control-plane`.

## Stack technique & dépendances

- **`install.sh`** (Bash, `set -e`, root requis) : prérequis `git`/`ansible`, user `essensys` (home `/home/essensys`), saisie WAN, clone `essensys-ansible` (tag = `ESSENSYS_VERSION` = `V.1.3.0`), `ansible-galaxy collection install -r requirements.yml` (community.docker…), puis `ansible-playbook`.
- **Cible d'exécution** : Docker. Les conteneurs attendus (cf. `monitor.py`) : `essensys-backend`, `essensys-mcp`, `essensys-nginx`, `essensys-traefik`, `essensys-redis`, `essensys-mosquitto`, `essensys-control-plane`, `essensys-prometheus`, `essensys-alertmanager`, `essensys-node-exporter`, `essensys-adguard`. Compose attendu en `/opt/data/docker-compose.yml`.
- **Scripts Python** :
  - `monitor.py` : moniteur TUI (curses) de l'état des conteneurs + CPU + logs Docker.
  - `push_status.py` : remonte périodiquement l'état (services, CPU…) vers le hub cloud (`https://gateway.essensys.fr/api/infos`).
- **Scripts Bash annexes** : `update.sh`, `uninstall.sh`, `requirements.sh`, `setup_duckdns.sh`, `setup_monitor.sh`, `install.github.runner.sh` (runner self-hosted ARM64 pour CI), `uninstall-adguard.sh`, `uninstall-mosquitto.sh`, `view-api-logs.sh`.
- **Configs reverse-proxy / réseau** (en partie héritées) :
  - `traefik-config/` : `traefik.yml`, `dynamic/`, génération htpasswd, blocage de service (`block-service.py`), docs NAT/DNS/Ubiquiti, compat client legacy.
  - `caddy-config/` : Caddyfiles (wan/auth/lan-noauth/noauth) — alternative/vestige.
  - `nginx-config/` : templates Nginx + format de log API.
  - `adguard-config/` : template `AdGuardHome.yaml`.
- **Doc** : MkDocs Material (`mkdocs.yml`, `docs/`), GitHub Pages.

## Structure du dépôt

```
essensys-raspberry-install/
├── install.sh                 # Bootstrap : prérequis + délégation à essensys-ansible
├── update.sh / uninstall.sh   # Maj / désinstallation
├── requirements.sh
├── install.github.runner.sh   # Runner GitHub Actions self-hosted (ARM64)
├── setup_duckdns.sh / setup_monitor.sh
├── monitor.py                 # TUI curses (état conteneurs, CPU, logs)
├── push_status.py             # Heartbeat vers gateway.essensys.fr/api/infos
├── view-api-logs.sh           # Lecture des logs API (diagnostic client legacy)
├── traefik-config/            # Traefik (dynamic, htpasswd, NAT/DNS, block-service.py)
├── caddy-config/              # Caddyfiles (vestige/alternative)
├── nginx-config/              # Templates Nginx (vestige)
├── adguard-config/            # Template AdGuard Home
├── scripts/essensys-auth
├── essensys-logrotate.conf
├── RELEASE_V.1.2.0.md         # Release notes (refonte UI, API history…)
├── docs/                      # MkDocs (installation, accès, réseau, migration…)
└── README.md                  # ⚠️ décrit l'archi native (obsolète vs install.sh actuel)
```

## Build / Installation / Déploiement (sur Raspberry, services, scripts)

**Installation nominale (V.1.3.0)** :

```bash
git clone https://github.com/essensys-hub/essensys-raspberry-install
cd essensys-raspberry-install
echo "mon.monwan.io" > /home/essensys/domain.txt   # optionnel (sinon saisie interactive)
sudo ./install.sh
```

`install.sh` (5 étapes) : prérequis git/ansible → user `essensys` → domaine WAN (`domain.txt`) → clone/checkout `essensys-ansible` au tag `V.1.3.0` dans `/opt/essensys-ansible` (inventory `localhost ansible_connection=local`) → `ansible-playbook install.raspberrypi.yml`. Tout le reste (images, conteneurs, réseau, reverse-proxy, monitoring) est géré par les rôles Ansible.

Le déploiement aboutit à une **pile Docker** ; vérification recommandée :

```bash
docker ps                                  # conteneurs actifs
docker logs essensys-control-plane         # logs du plan de contrôle
systemctl status nginx traefik redis docker
```

**Scripts d'exploitation** :

- `update.sh` : met à jour la pile (le README documente l'ancien flux git pull + recompilation ; en V.1.3.0 la maj passe par Ansible/images Docker).
- `uninstall.sh` (+ `uninstall-adguard.sh`, `uninstall-mosquitto.sh`) : arrêt/suppression services, configs, logs, optionnellement user/dépôts.
- `setup_monitor.sh` + `monitor.py` : TUI de supervision locale.
- `setup_duckdns.sh` : DNS dynamique DuckDNS pour l'accès WAN.
- `install.github.runner.sh` : enregistre un runner GitHub Actions ARM64 sur la passerelle (build/CI sur place) :
  ```bash
  export GITHUB_REPO_URL="https://github.com/essensys-hub"
  export GITHUB_RUNNER_TOKEN="…"
  curl -sL …/install.github.runner.sh | bash
  ```

**Ports historiques** (mode natif, cf. README — peut différer du mode Docker) : Nginx 80 (API locales + frontend) / 9090 (frontend interne), backend Go 7070, Traefik 80/443/8081.

## Intégrations (pont entre cartes locales, MQTT, cloud backend)

- **Cartes locales (client Essensys legacy / BP_MQX_ETH)** : Nginx en frontal des API (`/api/*` → backend), avec configuration permissive « single-packet TCP » pour le client legacy qui ne respecte pas strictement HTTP (logs API détaillés via `view-api-logs.sh`).
- **MQTT** : conteneur `essensys-mosquitto` dans la pile déployée.
- **Cloud backend / hub** : `push_status.py` envoie un heartbeat (état services, CPU, hostname) vers `gateway.essensys.fr/api/infos` ; accès WAN via Traefik/Caddy + DuckDNS/`domain.txt`, NAT/port-forwarding (docs `traefik-config/NAT-CONFIGURATION.md`, `UBIQUITI-DNS-CONFIG.md`).
- **Monitoring** : la pile inclut Prometheus, Alertmanager, node-exporter ; `monitor.py` offre une vue locale ; le plan de contrôle (`essensys-control-plane`) proxifie Prometheus/Alertmanager.
- **CI** : runner GitHub self-hosted ARM64 optionnel pour builder les images sur la passerelle.

## Points d'attention

- **README obsolète** : il décrit l'architecture native (Go/React + systemd + Nginx/Traefik), alors que `install.sh` V.1.3.0 délègue tout à **Ansible → Docker**. Risque de confusion majeur — la source de vérité du déploiement est `essensys-ansible`, pas ce README.
- **Couplage fort à `essensys-ansible`** : sans ce dépôt (et son `install.raspberrypi.yml` + `requirements.yml`), l'installation échoue (`Playbook introuvable`).
- **Vestiges multiples** : `caddy-config/`, `nginx-config/`, scripts `fix-network.sh`/`configure-network.sh` (mentionnés au README mais absents du listing), configs Traefik natives — distinguer l'actif (Docker) de l'historique.
- **Deux voies de déploiement concurrentes** avec `essensys-raspberry-gateway` (NixOS déclaratif). Clarifier la cible de prod (Ansible/Docker ici vs Nix là-bas).
- **Secrets/WAN** : `domain.txt`, htpasswd Traefik, tokens DuckDNS et runner GitHub manipulés en clair — soigner la gestion des secrets et l'exposition WAN (NAT + auth).
- **Sécurité** : recommandations README (mots de passe `config.yaml`, ufw, HTTPS) à reporter sur le déploiement Docker réel.
