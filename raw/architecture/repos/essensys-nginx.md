# essensys-nginx

> Serveur web et reverse-proxy interne de la gateway Essensys : sert le frontend React (SPA) et proxifie l'API, le MCP et le control-plane sur le LAN.

**Catégorie :** Infrastructure
**Stack :** Nginx (Alpine `apk`), Docker (multi-arch arm64/amd64), image de base `essensyshub/essensys-base`
**Statut :** Actif

## Rôle dans l'architecture Essensys

Nginx est le serveur HTTP local (port 80) de la gateway. Il remplit deux fonctions :
1. servir les fichiers statiques du frontend React avec routage SPA (`try_files ... /index.html`) ;
2. agir comme reverse-proxy vers les services backend internes (API, MCP, control-plane).

Dans la chaine de bordure, Nginx ecoute le trafic LAN sur `:80` tandis que Traefik gere la terminaison TLS et le filtrage WAN sur `:443`. Traefik route d'ailleurs le frontend vers ce Nginx (`http://127.0.0.1:80`).

## Configuration & fichiers clés

- `nginx.conf` — config globale : `worker_processes auto`, 256 connexions/worker, gzip actif (text/css/json/js/xml), inclusion de `/etc/nginx/http.d/*.conf`.
- `conf.d/default.conf` — server block `:80` :
  - `/` → SPA (`try_files $uri $uri/ /index.html`) servie depuis `/var/www/html` ;
  - `/api/` → proxy vers le backend `http://127.0.0.1:7070` (headers `X-Real-IP`, `X-Forwarded-*`) ;
  - `/mcp/` → proxy vers le serveur MCP `http://127.0.0.1:8083` (HTTP/1.1, support SSE) ;
  - `/admin/` → proxy vers le control-plane `http://127.0.0.1:9100/` (upgrade WebSocket) ;
  - cache 30j (`Cache-Control: public, immutable`) sur les assets statiques (js/css/images/fonts).
- `Dockerfile` — installe Nginx via `apk`, copie les configs, cree `/run/nginx` et `/var/www/html`.
- `.github/workflows/docker-build.yml` — CI de build/push.

## Build / Déploiement (Docker, ports exposés)

- Image : `essensyshub/essensys-nginx`, taguee par version Essensys + `latest`.
- Build CI multi-arch (`linux/arm64`, `linux/amd64`) sur tags `V.*` ou manuel, push Docker Hub.
- `EXPOSE 80` ; volumes `/etc/nginx/http.d` et `/var/www/html`.
- CMD `nginx -g 'daemon off;'`.
- En production (template Ansible) : `network_mode: host`, `depends_on: essensys-backend`, montage de `default.conf` en lecture seule et de la racine frontend (`{{ data_dir }}/frontend` → `/var/www/html:ro`).

## Intégrations (quels services route/proxy/surveille-t-il)

- **frontend React** — sert les fichiers statiques (build monte depuis l'hote).
- **backend** (`127.0.0.1:7070`) via `/api/`.
- **serveur MCP** (`127.0.0.1:8083`) via `/mcp/` (avec support SSE).
- **control-plane** (`127.0.0.1:9100`) via `/admin/` (avec upgrade WebSocket).
- En amont, **Traefik** consomme ce Nginx comme `frontend-service`.

## Points d'attention

- `server_name _;` (catch-all) : tout host est accepte ; le filtrage par domaine est delegue a Traefik en amont.
- Pas de TLS au niveau Nginx : il ne doit ecouter que sur le LAN ; l'exposition WAN passe obligatoirement par Traefik. En profil gateway, le LAN n'expose que HTTPS (le `:80` direct sur eth0 renvoie 444 selon la doc Ansible).
- Les cibles de proxy sont en `127.0.0.1` : cela suppose `network_mode: host` (tous les conteneurs partagent la pile reseau de l'hote) — coherent avec la compose Ansible.
- `worker_connections 256` : volontairement modeste (cible Raspberry Pi).
