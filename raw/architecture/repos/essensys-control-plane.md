# essensys-control-plane

> Plan de contrôle de la passerelle Essensys : service Go (UI React embarquée) qui orchestre la **flotte de conteneurs Docker** locaux (état, restart, update, rollback, versions), expose le **registre d'échange Redis** des cartes (clients, table d'échange, actions, audit) et proxifie la supervision **Prometheus/Alertmanager** — le tout derrière un seul binaire packagé en image ARM64.

**Catégorie :** Passerelle / Plan de contrôle
**Stack :** Go 1.24 (API HTTP + WebSocket) · React 19 + TypeScript + Vite + Tailwind v4 (UI admin embarquée via `go:embed`) · Docker SDK · Redis (go-redis) · SQLite (mattn/go-sqlite3, CGO) · Prometheus client · Docker multi-stage → image `essensyshub/essensys-control-plane`
**Statut :** Actif, bien structuré, déployé en conteneur. Release par tags `V.*` (CI build/push ARM64). Quelques TODO (ex. « apply all updates » route encore branchée sur `CheckUpdates`).

## Rôle dans l'architecture Essensys

`essensys-control-plane` est le **chef d'orchestre local** de la passerelle. Il tourne **sur le Raspberry/CM5**, à côté des autres conteneurs Essensys, et fournit l'**interface d'administration et de gestion de flotte** de l'appareil :

- **Gestion des services** : lister/inspecter les conteneurs, redémarrer, **mettre à jour** (pull d'un nouveau tag depuis le registre Docker), **rollback**, suivre les versions installées vs disponibles, historique des mises à jour. C'est le « fleet management » d'**un** appareil (et le socle d'une gestion multi-appareils).
- **Pont vers les cartes via Redis** : il lit/écrit le **registre d'échange Redis** qui matérialise l'état et les commandes des cartes domotiques (`exchange/{clientID}`, clients, `authinfo`, file d'**actions**, audit). C'est l'interface d'admin du « bus » applicatif entre cartes locales et backend.
- **Supervision** : proxy vers Prometheus (`/api/prometheus/*`) et Alertmanager (`/api/alertmanager/*`) pour exposer métriques, alertes, règles et cibles dans l'UI.
- **UI admin** : SPA React servie par le même binaire (montée par défaut sous le base path `/controle_plane`), avec santé `/health` et métriques `/metrics` (scrape Prometheus).

Il est conçu pour vivre **derrière le reverse-proxy** de la passerelle (base path configurable) et n'expose pas de logique domotique propre : il **observe et pilote** la pile (Docker) et le registre d'échange (Redis).

## Stack technique & dépendances

- **Backend Go 1.24** (`module github.com/essensys-hub/essensys-control-plane`) :
  - `github.com/docker/docker` v27 (SDK Docker, socket unix), `github.com/go-redis/redis/v8`, `github.com/mattn/go-sqlite3` (CGO), `github.com/gorilla/websocket` (streams logs/exchange), `github.com/prometheus/client_golang`, `gopkg.in/yaml.v3`.
  - Routeur via `net/http` `ServeMux` (méthodes + path values Go 1.22+). Middlewares : BasePath → Recovery → CORS → Logger → **BearerAuth**.
  - Build info injectée par ldflags (`version`/`commit`/`buildTime`), exposée par `/health`.
- **UI** (`ui/`) : React 19, React Router 7, Recharts, Heroicons, Tailwind CSS v4, Vite 7, TypeScript ~5.9. Build embarqué dans le binaire via `ui/embed.go` (`go:embed dist`) → servie par `spaHandler` (fallback `index.html`).
- **Persistance** : SQLite (`/data/controlplane.db`) pour l'historique (versions, mises à jour, audit) + Redis pour l'état temps réel des cartes.
- **Conteneurisation** : `Dockerfile` multi-stage (Stage 1 build UI Node 20 → Stage 2 build Go alpine CGO_ENABLED=1 → Stage 3 runtime `essensyshub/essensys-base:raspberry.2026.02`). Expose `9100`, volume `/data`, config `/etc/controlplane/config.yaml`.

## Structure du dépôt

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
│   ├── docker/client.go            # SDK Docker : ServiceInfo, VersionInfo, pull/restart…
│   ├── redis/client.go             # client Redis
│   ├── store/sqlite.go             # store SQLite (historique/audit)
│   └── metrics/prometheus.go       # métriques exposées sur /metrics
├── ui/                             # SPA React/TS/Vite/Tailwind (embed.go → go:embed dist)
├── config.yaml.example             # gabarit de config
├── Dockerfile                      # build multi-stage ARM64
└── .github/workflows/docker-build.yml   # build & push sur tags V.* (self-hosted arm64)
```

## Build / Installation / Déploiement (sur Raspberry, services, scripts)

- **Configuration** (`config.yaml.example`, surchargeable par ENV) :
  - `server.port` 9100, `server.token` (Bearer pour l'API), `server.base_path` (`/controle_plane` par défaut).
  - `redis.addr` (`redis:6379` en Docker), `docker.socket_path` (`/var/run/docker.sock`), `sqlite.path` (`/data/controlplane.db`), `registry.org` (`nrineau` — org Docker Hub pour les pulls/updates).
  - Overrides ENV : `CP_PORT`, `CP_TOKEN`, `CP_BASE_PATH`, `REDIS_ADDR/PASSWORD/DB`, `DOCKER_SOCKET`, `SQLITE_PATH`, `REGISTRY_ORG`.
- **Exécution locale** : `go run ./cmd/controlplane -config config.yaml` (nécessite CGO/sqlite, accès socket Docker + Redis).
- **Déploiement réel** : **image Docker** `essensyshub/essensys-control-plane:<tag>` (et `:latest`), runtime basé sur `essensys-base`. Lancée dans la pile de la passerelle (cf. `essensys-raspberry-install`/`essensys-ansible`, conteneur `essensys-control-plane`), avec :
  - montage du socket Docker (`/var/run/docker.sock`) — pour piloter la flotte ;
  - volume `/data` (SQLite) ; accès au Redis et aux endpoints Prometheus/Alertmanager (`127.0.0.1:9092/9093` codés côté handler).
- **CI/CD** (`docker-build.yml`) : sur tag `V.*`, runner **self-hosted linux/arm64**, login Docker Hub, build `linux/arm64` avec args `VERSION/COMMIT/BUILD_TIME`, push `:<tag>` + `:latest`, cache GHA.
- **Santé/observabilité** : `/health` (hors base path, hors auth) et `/metrics` (Prometheus) restent accessibles même avec base path configuré.

## Intégrations (pont entre cartes locales, MQTT, cloud backend)

- **Docker (flotte locale)** : via le socket, il liste/inspecte/restart les conteneurs, fait `docker pull` du tag cible (org `registry.org`) pour update/rollback, lit les logs (+ stream WebSocket). C'est le mécanisme de **mise à jour de la passerelle** appareil par appareil.
- **Redis (registre d'échange des cartes)** : API riche sur `/api/redis/exchange/{clientID}` (lecture/écriture de la table d'échange, recherche, stream), `/api/redis/clients` (+ `authinfo`), `/api/redis/actions` (file de commandes : push/list/delete/purge), `/api/audit`, `backup`/`restore`. C'est l'**interface d'administration du pont applicatif** entre cartes locales et backend — Redis y joue le rôle de bus d'état/commandes.
- **Prometheus/Alertmanager** : proxy de requêtes (`query`, `query_range`, `alerts`, `rules`, `targets`, silences) pour la supervision dans l'UI.
- **MQTT** : pas d'intégration directe ici ; la messagerie MQTT (Mosquitto) est gérée au niveau de la passerelle (`essensys-raspberry-gateway`/`-install`). Le control-plane agit sur l'**état persisté en Redis**, pas sur le flux MQTT.
- **Cloud backend** : le control-plane est local à l'appareil ; le lien cloud (hub) passe par les autres composants (backend conteneurisé, `push_status.py`, agents WAN décrits dans les OpenSpec de `raspberry-gateway`).

## Points d'attention

- **Accès au socket Docker** = privilèges élevés (équivalent root sur l'hôte). À combiner impérativement avec le **Bearer token** (`server.token`) et l'isolement réseau (base path derrière reverse-proxy). Un token vide désactive de fait l'auth.
- **Endpoints Prometheus/Alertmanager codés en dur** (`http://127.0.0.1:9092` / `:9093`) dans `router.go` — non configurables ; suppose une topologie réseau précise (host/loopback partagé).
- **Org de registre `nrineau`** par défaut (compte personnel Docker Hub) — à vérifier/paramétrer pour la prod (`REGISTRY_ORG`).
- **TODO connus** : `POST /api/update/apply` est branché sur `CheckUpdates` (pas encore d'« apply all » réel) ; rollback/update reposent sur la disponibilité des tags d'images.
- **CGO/SQLite** : build nécessite gcc/musl (géré dans le Dockerfile) ; complexifie une compilation hors conteneur.
- **Fleet management mono-appareil** : l'orchestration porte sur les conteneurs de **la passerelle locale**. Une gestion centralisée multi-passerelles (flotte cloud) n'est pas implémentée ici et relèverait du hub/portail.
