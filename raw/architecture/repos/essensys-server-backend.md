# essensys-server-backend

> Passerelle HTTP en Go qui fait le pont entre les boîtiers domotiques embarqués legacy (BP_MQX_ETH) et l'écosystème web/MQTT moderne, tout en conservant 100 % de compatibilité avec le protocole de l'ancien serveur ASP.NET.

**Catégorie :** Service backend (gateway domotique on-premise / Raspberry)
**Stack :** Go 1.23, Redis, PostgreSQL (sqlx + lib/pq), MQTT (paho), Prometheus, MCP (mark3labs/mcp-go), API HTTP `net/http`
**Statut :** actif (cœur de la migration depuis le legacy .NET)

## Rôle dans l'architecture Essensys

Ce service est le **serveur central** qui tourne typiquement sur la gateway Raspberry (image `essensyshub/essensys-base:raspberry.2026.02`). Il remplit deux fonctions simultanées (architecture **dual-protocol**, documentée dans `docs/ARCHITECTURE_DUAL_PROTOCOL.md`) :

1. **Protocole Legacy IoT** : il parle aux boîtiers embarqués `BP_MQX_ETH` (firmware C des cartes `essensys-board-SCxxx`). Ces clients pollent le serveur ~toutes les 500 ms en HTTP non-standard sur le **port 80 (obligatoire, codé en dur dans le firmware)**. Le serveur normalise leur JSON malformé (clés non-quotées), tolère leur HTTP non conforme (espaces parasites, absence de `Host`, `\n` au lieu de `\r\n`) et réplique exactement les particularités de l'ancien serveur ASP.NET (header `Content-Type: application/json ;charset=UTF-8` avec espace avant `;`, ordre des champs JSON, code `201 Created` sur POST).

2. **Protocole Web moderne** : il expose une API REST propre (JSON RFC 8259, sessions) consommée par `essensys-server-frontend` (React), ainsi que des intégrations MQTT (Home Assistant), UniFi Protect (caméras) et une synchronisation cloud optionnelle vers le hub `mon.essensys.fr`.

Les deux mondes partagent le même état : table d'échange (« exchange table », indices 0–999) en **Redis**, et historique/persistance en **PostgreSQL**.

## Stack technique & dépendances

Dépendances principales (`go.mod`) :
- `github.com/eclipse/paho.mqtt.golang` — client MQTT (discovery + commandes Home Assistant)
- `github.com/go-redis/redis/v8` — store principal de la table d'échange (`internal/data/redis_store.go`)
- `github.com/jmoiron/sqlx` + `github.com/lib/pq` — accès PostgreSQL (archiver, repositories web)
- `github.com/google/uuid` — GUID des actions
- `github.com/mark3labs/mcp-go` — serveur MCP (binaire séparé `cmd/mcp-server`)
- `github.com/prometheus/client_golang` — métriques exposées sur `/metrics`
- `golang.org/x/net`, `gopkg.in/yaml.v3` — HTTP/2, parsing de `config.yaml`

> Note : le `README.md` du dépôt décrit une version antérieure et minimaliste (store mémoire seul, sans MQTT/Redis/Postgres). Le code réel est sensiblement plus riche que ce README — se référer au code et à `docs/` pour l'état courant.

## Structure du dépôt

```
essensys-server-backend/
├── cmd/
│   ├── server/main.go          # Entry point du serveur HTTP principal
│   └── mcp-server/main.go      # Entry point du serveur MCP (Model Context Protocol)
├── internal/
│   ├── api/                    # Handlers HTTP + router
│   │   ├── router.go           # Câblage de toutes les routes + chaîne de middleware
│   │   ├── handlers.go         # Handlers LEGACY IoT (serverinfos, mystatus, myactions, done, admin)
│   │   ├── handlers_web.go     # Handlers WEB modernes (auth, user, web/actions, history)
│   │   ├── handlers_unifi.go   # Handlers UniFi Protect (caméras)
│   │   ├── json_normalizer.go  # Normalisation du JSON malformé des clients C
│   │   └── views.go / debug.html
│   ├── auth/                   # SessionStore (sessions web par cookie)
│   ├── cloudsync/sync.go       # Agent de sync sortante vers le hub cloud (mon.essensys.fr)
│   ├── config/config.go        # Chargement config (YAML + env), valeurs par défaut, validation
│   ├── core/                   # Logique métier : action_service, status_service, archiver
│   ├── data/                   # Stores : memory_store, redis_store, database_store
│   │   └── database/           # Repositories SQL (action, user, machine, state, data_index, cle_machine)
│   ├── metrics/prometheus.go   # Instrumentation Prometheus
│   ├── middleware/             # BasicAuth, RequestLogger, Recovery, métriques
│   ├── mqtt/                   # client, publisher, discovery, handlers (commandes HA)
│   ├── models/                 # Modèles de données
│   ├── server/                 # LegacyHTTPServer + LoggingListener (HTTP tolérant)
│   ├── services/user_service.go
│   └── unifi/                  # Client UniFi Protect
├── pkg/protocol/               # Types & constantes partagés (types.go, constants.go)
├── migrations/                 # SQL : 001_initial_schema, 002_add_tracking_table
├── docs/                       # ARCHITECTURE_DUAL_PROTOCOL, LEGACY_IOT_AUTHENTICATION, MCP_DEVICE_INDEX_REFERENCE, etc.
├── config.yaml / config.yaml.example
├── Dockerfile                  # Multi-stage, build server + mcp-server
└── go.mod / go.sum
```

## Build / Exécution / Déploiement

Build local :
```bash
go build -o server ./cmd/server
go build -o mcp-server ./cmd/mcp-server
# Port 80 privilégié sous Linux :
sudo setcap 'cap_net_bind_service=+ep' ./server
./server -config /etc/essensys/config.yaml
```

Tests :
```bash
go test ./...            # tests unitaires + intégration (handlers_test, integration_test, etc.)
go test ./... -race      # détecteur de data race (forte concurrence : ~500 ms de polling)
```

Docker (`Dockerfile`, multi-stage) :
- Stage builder `golang:1.23-alpine` → compile `server` et `mcp-server` (avec ldflags `version/commit/buildTime`).
- Stage runtime sur `essensyshub/essensys-base:raspberry.2026.02`.
- `EXPOSE 7070 8083`, `VOLUME ["/data"]`, `ENTRYPOINT ["server"]`, `CMD ["-config", "/etc/essensys/config.yaml"]`.
- Build CI : `.github/workflows/docker-build.yml`.

Configuration (`config.yaml`, surchargeable par variables d'env `SERVER_PORT`, `LOG_LEVEL`, `AUTH_ENABLED`, `CLIENT_CREDENTIALS`) :
- `server.port` : **80 par défaut (obligatoire pour les boîtiers)**
- `redis.addr` : `localhost:6379`
- `database` : driver `postgres`, `localhost:5432`
- `mqtt.broker` : `tcp://localhost:1883` (activable via `mqtt.enabled`)
- `unifi` : activable, requiert `api_key`
- `cloud.hub_url` : `https://mon.essensys.fr` (sync optionnelle, `cloud.enabled`)

Déploiement type : systemd (`AmbientCapabilities=CAP_NET_BIND_SERVICE`) ou container, orchestré via `essensys-ansible` / `essensys-raspberry-install`.

## Intégrations (composants Essensys et protocoles)

| Composant | Sens | Protocole / Port | Détails |
|-----------|------|------------------|---------|
| Boîtiers `BP_MQX_ETH` (cartes `essensys-board-SCxxx`) | entrant | HTTP non-standard, **port 80** | Polling ~500 ms. Endpoints legacy ci-dessous. JSON malformé normalisé. |
| `essensys-server-frontend` (React) | entrant | HTTP/REST (via Vite proxy ou nginx) | Endpoints `/api/admin/inject`, `/api/admin/exchange`, `/api/web/actions`, `/api/web/history/latest`, `/api/auth/*`, `/api/user/me`. |
| Broker MQTT (`essensys-mosquitto`) | bidir. | MQTT `tcp://localhost:1883` | Publication discovery + states ; souscription aux topics de commande (intégration Home Assistant). |
| Redis (`essensys-redis`) | bidir. | `localhost:6379` | Store de la table d'échange (indices 0–999). |
| PostgreSQL | bidir. | `localhost:5432` | Archiver (intervalle 10 min), repositories users/machines/actions. |
| UniFi Protect | sortant | HTTPS + API key | Récupération des caméras et snapshots (`/api/unifi/cameras*`). |
| Hub cloud `mon.essensys.fr` | sortant | HTTPS | `cloudsync` : poll/push optionnel avec `gateway_id` + `gateway_token`. |
| Prometheus (`essensys-prometheus`) | entrant | HTTP `/metrics` | Métriques applicatives. |
| `essensys-mcp` / clients MCP | — | binaire `cmd/mcp-server` | Exposition de l'état domotique via Model Context Protocol. |

**Endpoints HTTP (déclarés dans `internal/api/router.go`) :**

Legacy IoT (à ne JAMAIS modifier) :
- `GET  /api/serverinfos` — handshake/connexion du boîtier
- `POST /api/mystatus` — remontée d'état (table d'échange `ek:[{k,v}]`), réponse `201`
- `GET  /api/myactions` — récupération des actions en attente (champ `_de67f` AVANT `actions`)
- `POST /api/done/{guid}` — acquittement d'une action (FIFO)

Admin / debug :
- `POST /api/admin/inject` — injection d'actions (génère le bloc complet 605–622 pour lumières/volets, ajoute l'index 590=1, fusion bitwise OR)
- `GET  /api/admin/exchange` — relecture des valeurs de la table d'échange
- `GET  /health`, `GET /debug`, `GET /debug/logs`, `GET /table_ref`, `GET /metrics`

Web moderne (montés si la base PostgreSQL est connectée) :
- `POST /api/auth/login`, `/api/auth/logout`, `/api/auth/register`
- `GET  /api/user/me`
- `POST /api/web/actions` (ex. commandes alarme)
- `GET  /api/web/history/latest`

UniFi (montés si activé) :
- `GET /api/unifi/cameras`, `GET /api/unifi/cameras/{id}/snapshot`

## Points d'attention

- **Le protocole legacy est « sacré ».** Toute modification du format JSON, des headers (`application/json ;charset=UTF-8`), de l'ordre des champs ou des codes de retour peut casser silencieusement les boîtiers C (le firmware n'a pas de gestion d'erreur robuste). Voir la liste « À NE PAS FAIRE » dans `docs/ARCHITECTURE_DUAL_PROTOCOL.md`.
- **Port 80 obligatoire** : codé en dur dans le firmware ; nécessite `setcap` ou capability container. Un `WARNING` est loggé si un autre port est configuré.
- **Serveur HTTP custom** (`internal/server`) : `LegacyHTTPServer` + `LoggingListener` tolèrent l'HTTP non conforme des clients. Ne pas remplacer par un `http.Server` standard sans précaution.
- **Génération de bloc complet 605–622** : le firmware ignore une action lumière/volet si un seul indice du bloc manque ; le serveur complète automatiquement (+ index 590=1 comme déclencheur de scénario, jamais fusionné).
- **Désaccord README vs code** : le `README.md` décrit une ancienne version store-mémoire ; les dépendances réelles (Redis, Postgres, MQTT, MCP, UniFi, cloudsync) ne s'y trouvent pas. Documentation à jour côté `docs/` et code.
- **Dégradation gracieuse** : si PostgreSQL est injoignable, l'archiver et tous les handlers web/auth sont désactivés (le legacy IoT continue de fonctionner sur Redis seul). Idem MQTT/UniFi désactivés si non configurés.
- **Sécurité** : Basic Auth seulement (Base64, pas de chiffrement) pour les boîtiers ; sessions cookie pour le web. HTTPS à terminer en amont (nginx/traefik). Les credentials clients sont en clair dans `config.yaml`.
- **Binaire commité** : `server` et `essensys-mcp` (~5 Mo) sont présents dans le dépôt — artefacts qui ne devraient probablement pas être versionnés.
