---
tags: [entity, repo, migration]
sources: [essensys-raspberry-install.md]
created: 2026-06-20
updated: 2026-06-20
era: migration
repo: essensys-raspberry-install
---

# Essensys Raspberry Install

> Provisioning / bootstrap d'installation de la passerelle Essensys sur Raspberry Pi : un script `install.sh` minimal qui pose les prérequis (git, Ansible) puis **délègue tout le déploiement au dépôt `essensys-ansible`** (pile Docker), avec scripts annexes (monitor, push status, DuckDNS, runner GitHub) et configs reverse-proxy historiques.

| | |
|---|---|
| **Catégorie** | Passerelle / Plan de contrôle |
| **Stack** | Bash (scripts d'install/maintenance) · Ansible (orchestration déléguée) · Docker (cible d'exécution) · Python 3 (monitor TUI, push status) · Caddy / Traefik / Nginx (configs reverse-proxy) · AdGuard Home · MkDocs Material (doc) |
| **Statut** | Actif, version courante **V.1.3.0**. ⚠️ Le `README.md` décrit l'**ancienne** architecture (binaires natifs Go/React + systemd) ; le `install.sh` réel (V.1.3.0) est devenu un **bootstrap Ansible→Docker**. Plusieurs scripts/configs (Caddy, Nginx natif, fix-network) sont des vestiges de la version précédente. |
| **Era** | migration |

## Rôle

C'est le **point d'entrée de provisioning** d'une passerelle Essensys sur Raspberry Pi (Pi 4 historiquement, généralisé). Son rôle : amener une carte « nue » (Raspberry Pi OS) à une passerelle Essensys complète et opérationnelle.

Évolution clé (à comprendre absolument) :

- **Avant (README, ≤ V.1.2.x)** : `install.sh` installait Go/Node, clonait `essensys-server-backend` + `essensys-server-frontend`, compilait le backend (port 7070), buildait le frontend, configurait Nginx (80/9090) + Traefik (80/443), et créait des **services systemd natifs**.
- **Maintenant (V.1.3.0)** : `install.sh` est un **bootstrap minimal** qui (1) installe `git` + `ansible`, (2) crée l'utilisateur `essensys`, (3) gère le domaine WAN (`domain.txt`), (4) clone/maj `essensys-ansible` (`/opt/essensys-ansible`), (5) lance `ansible-playbook install.raspberrypi.yml`. Le déploiement réel — **conteneurs Docker** — est entièrement décrit dans `essensys-ansible`.

Ce dépôt n'embarque donc plus la logique d'installation : il **bootstrappe Ansible**, qui à son tour déploie la pile de conteneurs orchestrée ensuite par `essensys-control-plane`.

## Intégrations

_Non documenté._

## Structure

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
├── adguard-config/            # Template AdGu

_… voir source complète dans raw/_

## Points d'attention

- **README obsolète** : il décrit l'architecture native (Go/React + systemd + Nginx/Traefik), alors que `install.sh` V.1.3.0 délègue tout à **Ansible → Docker**. Risque de confusion majeur — la source de vérité du déploiement est `essensys-ansible`, pas ce README.
- **Couplage fort à `essensys-ansible`** : sans ce dépôt (et son `install.raspberrypi.yml` + `requirements.yml`), l'installation échoue (`Playbook introuvable`).
- **Vestiges multiples** : `caddy-config/`, `nginx-config/`, scripts `fix-network.sh`/`configure-network.sh` (mentionnés au README mais absents du listing), configs Traefik natives — distinguer l'actif (Docker) de l'historique.
- **Deux voies de déploiement concurrentes** avec `essensys-raspberry-gateway` (NixOS déclaratif). Clarifier la cible de prod (Ansible/Docker ici vs Nix là-bas).
- **Secrets/WAN** : `domain.txt`, htpasswd Traefik, tokens DuckDNS et runner GitHub manipulés en clair — soigner la gestion des secrets et l'exposition WAN (NAT + auth).
- **Sécurité** : recommandations README (mots de passe `config.yaml`, ufw, HTTPS) à reporter sur le déploiement Docker réel.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-raspberry-install.md`
