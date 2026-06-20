---
tags: [entity, repo, modern]
sources: [essensys-control-plane.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-control-plane
---

# Essensys Control Plane

> Plan de contrôle de la passerelle Essensys : service Go (UI React embarquée) qui orchestre la **flotte de conteneurs Docker** locaux (état, restart, update, rollback, versions), expose le **registre d'échange Redis** des cartes (clients, table d'échange, actions, audit) et proxifie la supervision **Prometheus/Alertmanager** — le tout derrière un seul binaire packagé en image ARM64.

| | |
|---|---|
| **Catégorie** | Passerelle / Plan de contrôle |
| **Stack** | Go 1.24 (API HTTP + WebSocket) · React 19 + TypeScript + Vite + Tailwind v4 (UI admin embarquée via `go:embed`) · Docker SDK · Redis (go-redis) · SQLite (mattn/go-sqlite3, CGO) · Prometheus client · Docker multi-stage → image `essensyshub/essensys-control-plane` |
| **Statut** | Actif, bien structuré, déployé en conteneur. Release par tags `V.*` (CI build/push ARM64). Quelques TODO (ex. « apply all updates » route encore branchée sur `CheckUpdates`). |
| **Era** | modern |

## Rôle

`essensys-control-plane` est le **chef d'orchestre local** de la passerelle. Il tourne **sur le Raspberry/CM5**, à côté des autres conteneurs Essensys, et fournit l'**interface d'administration et de gestion de flotte** de l'appareil :

- **Gestion des services** : lister/inspecter les conteneurs, redémarrer, **mettre à jour** (pull d'un nouveau tag depuis le registre Docker), **rollback**, suivre les versions installées vs disponibles, historique des mises à jour. C'est le « fleet management » d'**un** appareil (et le socle d'une gestion multi-appareils).
- **Pont vers les cartes via Redis** : il lit/écrit le **registre d'échange Redis** qui matérialise l'état et les commandes des cartes domotiques (`exchange/{clientID}`, clients, `authinfo`, file d'**actions**, audit). C'est l'interface d'admin du « bus » applicatif entre cartes locales et backend.
- **Supervision** : proxy vers Prometheus (`/api/prometheus/*`) et Alertmanager (`/api/alertmanager/*`) pour exposer métriques, alertes, règles et cibles dans l'UI.
- **UI admin** : SPA React servie par le même binaire (montée par défaut sous le base path `/controle_plane`), avec santé `/health` et métriques `/metrics` (scrape Prometheus).

Il est conçu pour vivre **derrière le reverse-proxy** de la passerelle (base path configurable) et n'expose pas de logique domotique propre : il **observe et pilote** la pile (Docker) et le registre d'échange (Redis).

## Intégrations

_Non documenté._

## Structure

```
essensys-control-plane/
├── cmd/controlplane/main.go        # Entrée : config, SQLite, Redis, Docker, UI embarquée, serveur HTTP
├── internal/
│   ├── config/config.go            # Config YAML + overrides ENV (CP_*, REDIS_*, DOCKER_SOCKET…)
│   ├── api/
│   │   ├── router.go               # Toutes les routes + middlewares + base path
│   │   ├── services_handler.go     # services: list/get/restart/update/rollback/versions
│   │   ├── redis_handler.go        # exchange, clients, actions, audit, backup/restore
│   │   ├── logs_handler.go         # logs Docker (+ stream)
│   │   ├── prometheus_handler.go   # proxy Prometheus/Alertmanager
│   │   ├── system_handler.go       # /health, /api/system
│   │   ├── ws.go / middleware.go / helpers.go
│   ├── docker/client.go            # SDK Docke

_… voir source complète dans raw/_

## Points d'attention

- **Accès au socket Docker** = privilèges élevés (équivalent root sur l'hôte). À combiner impérativement avec le **Bearer token** (`server.token`) et l'isolement réseau (base path derrière reverse-proxy). Un token vide désactive de fait l'auth.
- **Endpoints Prometheus/Alertmanager codés en dur** (`http://127.0.0.1:9092` / `:9093`) dans `router.go` — non configurables ; suppose une topologie réseau précise (host/loopback partagé).
- **Org de registre `nrineau`** par défaut (compte personnel Docker Hub) — à vérifier/paramétrer pour la prod (`REGISTRY_ORG`).
- **TODO connus** : `POST /api/update/apply` est branché sur `CheckUpdates` (pas encore d'« apply all » réel) ; rollback/update reposent sur la disponibilité des tags d'images.
- **CGO/SQLite** : build nécessite gcc/musl (géré dans le Dockerfile) ; complexifie une compilation hors conteneur.
- **Fleet management mono-appareil** : l'orchestration porte sur les conteneurs de **la passerelle locale**. Une gestion centralisée multi-passerelles (flotte cloud) n'est pas implémentée ici et relèverait du hub/portail.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-control-plane.md`
