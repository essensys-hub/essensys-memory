# essensys-redis

> Cache et store cle-valeur en memoire de la gateway Essensys, partage par le backend et le serveur MCP.

**Catégorie :** Infrastructure
**Stack :** Redis (Alpine `apk`), Docker (multi-arch arm64/amd64), image de base `essensyshub/essensys-base`
**Statut :** Actif

## Rôle dans l'architecture Essensys

Redis fournit le stockage cle-valeur rapide en memoire de la gateway : cache, etat partage et donnees ephemeres. Dans la stack Docker il est demarre tot car plusieurs services en dependent (`depends_on: essensys-redis` pour le backend et le serveur MCP). Il tourne en `network_mode: host` sur le port 6379.

## Configuration & fichiers clés

- `redis.conf` :
  - `bind 0.0.0.0`, `port 6379`, `protected-mode no` ;
  - persistance RDB : `dir /data`, `dbfilename dump.rdb`, snapshots `save 900 1 / 300 10 / 60 10000` ;
  - memoire : `maxmemory 128mb`, `maxmemory-policy allkeys-lru` (eviction LRU sur tout le keyspace) ;
  - logs : `loglevel notice`, `logfile ""` (stdout) ;
  - reseau : `tcp-backlog 128`, `tcp-keepalive 300`, `timeout 0`.
- `Dockerfile` — installe Redis via `apk`, copie la config, prepare `/data` (proprietaire `redis`).
- `.github/workflows/docker-build.yml` — CI de build/push.

## Build / Déploiement (Docker, ports exposés)

- Image : `essensyshub/essensys-redis`, taguee par version Essensys + `latest`.
- Build CI multi-arch (`linux/arm64`, `linux/amd64`) sur tags `V.*` ou manuel, push Docker Hub.
- `EXPOSE 6379` ; volumes `/data` et `/etc/redis`.
- CMD `redis-server /etc/redis/redis.conf`.
- En production (template Ansible) : `network_mode: host`, `restart: unless-stopped`, volume data monte depuis l'hote et `redis.conf` en lecture seule (role `raspberry_redis`).

## Intégrations (quels services route/proxy/surveille-t-il)

- **backend Essensys** — consommateur principal (cache / etat), avec `depends_on` explicite.
- **serveur MCP** (`essensys-mcp`) — egalement dependant de Redis au demarrage.
- Indirectement utilise par l'assistant OpenClaw (dependant du MCP).

## Points d'attention

- `protected-mode no` + `bind 0.0.0.0` sans `requirepass` : Redis accepte les connexions sans authentification. Acceptable uniquement parce que l'acces est limite a la boucle locale de la gateway (`network_mode: host`, non expose au WAN) — a ne jamais exposer hors du LAN.
- `maxmemory 128mb` avec eviction `allkeys-lru` : dimensionnement Raspberry Pi ; les cles peuvent etre evincees sous pression memoire (ne pas l'utiliser comme stockage durable critique).
- Persistance RDB uniquement (pas d'AOF) : risque de perte des dernieres ecritures en cas d'arret brutal.
