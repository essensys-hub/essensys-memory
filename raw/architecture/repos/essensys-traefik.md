# essensys-traefik

> Reverse-proxy de bordure de la gateway Essensys, terminaison TLS (Let's Encrypt + CA locale) et filtrage des routes exposees sur le WAN.

**Catégorie :** Infrastructure
**Stack :** Traefik v2.11.3, Docker (multi-arch arm64/amd64), image de base `essensyshub/essensys-base`
**Statut :** Actif

## Rôle dans l'architecture Essensys

Traefik est le point d'entree HTTPS de la gateway (Raspberry Pi). Il assure la terminaison TLS et controle finement ce qui est accessible depuis l'exterieur (WAN), par opposition a Nginx qui sert le trafic LAN interne. Dans la stack Docker il tourne en `network_mode: host` aux cotes de Nginx, du backend, de Redis et de Mosquitto.

Sa fonction principale cote securite est de n'exposer sur Internet qu'un sous-ensemble strictement controle de l'application :
- le frontend (protege par BasicAuth) ;
- une unique route d'API autorisee (`/api/admin/inject`, egalement protegee par BasicAuth) ;
- toutes les autres routes `/api/` sont volontairement bloquees (renvoyees vers un service de blocage).

## Configuration & fichiers clés

- `traefik.yml` — configuration statique : dashboard/API (insecure), metriques Prometheus activees (labels entrypoints/services/routers), entryPoints, resolveur ACME, provider `file` en watch sur `/etc/traefik/dynamic`, logs JSON.
- `dynamic/wan-routes.yml` — configuration dynamique des routes WAN : middlewares (`redirect-to-https`, `auth-wan` via `users.htpasswd`), routers avec priorites, et services de load-balancing vers les backends locaux. Le `DOMAIN_PLACEHOLDER` est substitue au deploiement (cf. Ansible, domaine `mon.essensys.local`).
- `Dockerfile` — telecharge le binaire Traefik selon l'architecture detectee, copie les configs, prepare `acme.json` (chmod 600) et `users.htpasswd`.
- `.github/workflows/docker-build.yml` — CI de build/push.

### EntryPoints declares

| EntryPoint | Port | Usage |
|------------|------|-------|
| `websecure` | 443 | Trafic HTTPS applicatif (TLS via resolveur `letsencrypt`) |
| `dashboard` | 8080 | Dashboard Traefik |
| `traefik` | 8081 | API/admin Traefik |

### Routers WAN (par priorite)

| Router | Regle | Priorite | Cible |
|--------|-------|----------|-------|
| `api-inject-wan` | `Host && PathPrefix(/api/admin/inject)` | 25 | backend `127.0.0.1:7070` (auth) |
| `block-api-wan` | `Host && /api/ sauf /api/admin/inject` | 15 | service de blocage `127.0.0.1:8082` |
| `frontend-wan` | `Host && !PathPrefix(/api/)` | 10 | frontend `127.0.0.1:80` (auth) |

## Build / Déploiement (Docker, ports exposés)

- Image : `essensyshub/essensys-traefik`, taguee par version Essensys + `latest`.
- Build CI multi-arch (`linux/arm64`, `linux/amd64`) declenche sur tags `V.*` ou manuellement, push vers Docker Hub (`essensyshub`).
- `EXPOSE 443 8080 8081` ; volumes `/etc/traefik` et `/var/log/traefik`.
- ENTRYPOINT `traefik`, lance avec `--configFile=/etc/traefik/traefik.yml`.
- En production (template Ansible `raufebpr_compose`) : `network_mode: host`, `restart: unless-stopped`, montage de `{{ config_dir }}/traefik` vers `/etc/traefik` et des logs.
- Cote Ansible (role `raspberry_traefik`), une CA locale est generee pour signer un certificat du domaine mDNS `mon.essensys.local` (Let's Encrypt ne pouvant signer un `.local`) ; la CA est publiee en telechargement et installee dans les trust stores.

## Intégrations (quels services route/proxy/surveille-t-il)

- **frontend** (`127.0.0.1:80`, servi par Nginx) — expose au WAN sous BasicAuth.
- **backend** (`127.0.0.1:7070`) — uniquement la route `/api/admin/inject`.
- **service de blocage** (`127.0.0.1:8082`) — capte et rejette toutes les autres routes `/api/`.
- **Prometheus** — Traefik expose ses metriques (scrapees par la stack monitoring).

## Points d'attention

- `api.insecure: true` et `dashboard.insecure: true` : le dashboard est servi sans TLS sur l'entryPoint dashboard/traefik — a n'exposer que sur le LAN.
- `certificatesResolvers.letsencrypt.acme.email: admin@acme.com` est une valeur placeholder a personnaliser.
- `DOMAIN_PLACEHOLDER` dans `wan-routes.yml` doit imperativement etre substitue au deploiement (gere par Ansible), sinon les routers ne matchent rien.
- La securite du WAN repose sur `users.htpasswd` (BasicAuth) : ce fichier doit etre provisionne, sinon `auth-wan` echoue.
- Le `tlsChallenge` ACME requiert que le port 443 soit accessible publiquement pour l'emission Let's Encrypt ; en local on s'appuie plutot sur la CA locale.
