# essensys-user-portal-backend

> Backend Go du hub cloud Essensys (OVH) : portail domotique distant + relais d'actions vers les gateways, qui consolide aussi l'identité, l'admin et le protocole IoT legacy du support-site en un seul service.

**Catégorie :** Backend / Service cloud (API HTTP)
**Stack :** Go 1.25, go-chi v5, PostgreSQL (sqlx + lib/pq), JWT, New Relic APM
**Statut :** Actif — déployé en production sous le nom `essensys-cloud-backend` (`:8080`), `CONSOLIDATED_MODE=true` depuis le cutover de juin 2026

## Rôle dans l'architecture Essensys

Ce service est le **hub cloud** hébergé sur le VPS OVH, derrière `https://mon.essensys.fr`. Il remplit deux fonctions distinctes des serveurs locaux Essensys :

- **Portail domotique distant** : il permet à un utilisateur final de piloter son armoire domotique Essensys depuis Internet (hors réseau local), sans être sur le même LAN que sa box/armoire. C'est la différence majeure avec `essensys-server-backend`, qui est le serveur **local** d'une installation (sur site, réseau privé) et parle directement au firmware via la table d'échange.
- **Hub de consolidation** : en `CONSOLIDATED_MODE=true`, il absorbe le backend de l'ancien `essensys-support-site` (authentification email/OAuth, profils, admin, newsletter) et le protocole IoT WAN legacy (mystatus/serverinfos/infos), pour faire tourner un **seul binaire** au lieu de deux backends séparés.

Le pont avec l'armoire distante n'est pas direct : le portail dépose des **actions cloud** en base, et la **gateway Raspberry/CM5** (`essensys-raspberry-gateway`) installée chez le client effectue du polling sortant (`GET /api/gateway/pending-actions`), exécute les ordres localement, puis remonte l'état (`POST /api/gateway/exchange`). C'est un modèle pull/push pensé pour traverser un NAT résidentiel sans port ouvert.

Distinction des utilisateurs :
- **Utilisateur final** (propriétaire d'une armoire) → routes `/api/portal/*` avec JWT utilisateur.
- **Gateway** (agent embarqué chez le client) → routes `/api/gateway/*` authentifiées par headers (`X-Gateway-ID`, `Authorization: Bearer`, `X-Gateway-Eth0-MAC`, `X-Gateway-Eth1-MAC`).
- **Admin / support Essensys** → `/api/portal/admin/*` et `/api/admin/*` (validation des demandes de liaison, enregistrement gateway, stats, audit, newsletter).

## Stack technique & dépendances

- **Langage** : Go 1.25 (`module github.com/essensys-hub/essensys-user-portal-backend`).
- **Routeur HTTP** : `go-chi/chi/v5` + `go-chi/cors`.
- **Base de données** : PostgreSQL via `jmoiron/sqlx` et le driver `lib/pq`. Même instance PostgreSQL que le support-site (tables partagées : `users`, etc.).
- **Auth** : `golang-jwt/jwt/v4`, secret `JWT_SECRET` partagé avec le support-site (un JWT émis côté login support est accepté par le portail).
- **Observabilité** : `newrelic/go-agent/v3` + intégration `nrgochi` (middleware Chi). Aucune donnée sensible (JWT, tokens gateway, payloads domotiques) n'est envoyée en attributs custom.
- **Email** : `gopkg.in/gomail.v2` pour la newsletter (Phase 3, SMTP).

## Structure du dépôt

```
cmd/
  server/main.go          # point d'entrée : connexion PG, migrations, router, ListenAndServe
  import-machines/main.go  # outil d'import machines.json → PostgreSQL
internal/
  api/router.go            # assemblage des routes + middlewares ; monte les modules consolidés si activé
  config/                  # chargement des variables d'environnement (Config)
  portal/routes.go         # /api/portal/* (utilisateur + sous-groupe admin)
  gateway/routes.go        # /api/gateway/* (agent gateway)
  handlers/                # handlers HTTP portal & gateway
  identity/                # /api/auth/*, /api/profile/* (OAuth Google/Apple) — CONSOLIDATED_MODE
  admin/                   # /api/admin/*, newsletter — CONSOLIDATED_MODE
  legacyiot/               # /api/mystatus, /myactions, /done, /serverinfos, /infos — CONSOLIDATED_MODE
  middleware/              # UserJWT, AdminJWT, GatewayAuth, BasicAuth, RateLimiter
  data/                    # stores PostgreSQL (portal, user, audit, inventory, newsletter, legacy IoT, exchange, MAC)
  domain/                  # types métier + règles (éligibilité gateway, expansion d'ordres, audit)
  observability/           # init New Relic
  geo/                     # résolution IP → géoloc (ipapi)
migrations/                # 001_init → 005_newsletter (SQL appliqué automatiquement au démarrage)
docs/                      # architecture.md, deployment.md, api-routes.md, migrations.md, index.md
```

Modules et activation (depuis le README) :

| Package | Routes | Activation |
|---------|--------|------------|
| `internal/portal` | `/api/portal/*` | Toujours actif |
| `internal/gateway` | `/api/gateway/*` (+ `POST /exchange`) | Toujours actif |
| `internal/identity` | `/api/auth/*`, `/api/profile/*` | `CONSOLIDATED_MODE` |
| `internal/admin` | `/api/admin/*`, `/api/newsletter/subscribe` | `CONSOLIDATED_MODE` |
| `internal/legacyiot` | `/api/mystatus`, … | `CONSOLIDATED_MODE` |

Schéma PostgreSQL principal (`migrations/001_init.sql`) : `link_requests`, `cloud_actions`, `gateway_sessions`, `portal_audit_log` (puis identity gateway, exchange cache, legacy IoT, newsletter dans 002→005).

## Build / Exécution / Déploiement

Démarrage local :

```bash
export DB_HOST=127.0.0.1 DB_PORT=5432 DB_USER=essensys DB_PASSWORD=... DB_NAME=essensys_db
export JWT_SECRET=same-as-support-site
export PORT=8081
go run ./cmd/server
```

Tests : `go test ./...` (couverture middleware, identity OAuth, admin, legacy IoT, exchange, domain). Au démarrage, le serveur applique automatiquement les migrations SQL triées du dossier `MIGRATIONS_DIR`.

Variables d'environnement clés :

| Variable | Défaut | Rôle |
|----------|--------|------|
| `CONSOLIDATED_MODE` | `false` | Active identity/admin/legacyiot. `true` en prod. |
| `PORT` | `8081` local / `8080` prod | Port HTTP |
| `EXCHANGE_STALE_TTL_SECONDS` | `120` | TTL du cache exchange du portail |
| `JWT_SECRET` | — | Partagé avec le support-site |
| `ADMIN_TOKEN` | `essensys-admin-secret` | Token legacy admin (scripts) |
| `CORS_ORIGIN` | `https://mon.essensys.fr` | Origine CORS autorisée |
| `MIGRATIONS_DIR` | `migrations` | Migrations SQL auto au démarrage |
| `SMTP_*` | — | Newsletter |
| `NEW_RELIC_*` | désactivé local | APM Go (app prod `essensys-cloud-backend`) |

Déploiement (Ansible) :
- Rôle `essensys-ansible/roles/cloud_backend`, playbook `support-site.yml` quand `cloud_backend_consolidated: true`.
- `.env` généré depuis `roles/cloud_backend/templates/cloud-backend.env.j2`.
- Secrets dans `essensys-ansible/group_vars/essensys/vault.yml` (`portal_db_password`, `portal_jwt_secret`, `vault_admin_token`, OAuth Google/Apple, SMTP, NR).
- `cmd/import-machines` importe `machines.json` → PostgreSQL (`cloud_backend_import_machines: true`).
- Déploiement manuel possible par `rsync` vers `/opt/essensys/cloud-backend-src/` avec `cloud_backend_skip_git_clone: true`.
- CI : `.github/workflows/ci.yml`.

## Intégrations

- **essensys-user-portal-frontend** : SPA React servie sur `/portal/`, consomme `/api/portal/*` et `/api/auth/*` sur le même host.
- **essensys-raspberry-gateway** (CM5) : agent client qui poll `/api/gateway/pending-actions`, acquitte via `/api/gateway/actions/{guid}/done`, envoie `/api/gateway/heartbeat` et pousse l'état via `/api/gateway/exchange`.
- **essensys-support-site** : code d'origine consolidé ici (auth, admin, newsletter, IoT legacy) ; PostgreSQL et `JWT_SECRET` partagés. La matrice de migration handler→package est dans le README.
- **OAuth Google / Apple** : login social via `internal/identity`.
- **New Relic APM** : app `essensys-cloud-backend`.
- **Nginx** (sur le VPS) : route `/api/` → backend `:8080` ; sert le frontend statique sous `/portal/`.

## Points d'attention

- **Mode dual selon `CONSOLIDATED_MODE`** : à `false`, seuls portail + gateway sont montés (mode staging historique `:8081`) ; à `true`, c'est le hub complet de production. Un mauvais flag fait silencieusement disparaître les routes auth/admin/legacy.
- **Couplage fort avec le support-site** : même base PostgreSQL et même `JWT_SECRET`. Toute rotation de secret ou migration de schéma doit être coordonnée entre les deux.
- **Éligibilité gateway** : `domain.IsRemoteEligibleGateway()` exclut explicitement la gateway `essensys-server` (VPS legacy) du portail distant — le frontend affiche un message « portail indisponible » dans ce cas.
- **Authentification gateway par headers** (MAC eth0/eth1 + token), pas par JWT : surface différente du reste de l'API, à traiter avec soin (les MAC sont des identifiants).
- **Migrations auto au démarrage** : pratique mais les erreurs ne sont que logguées en WARNING (pas fatales), ce qui peut masquer une base non migrée.
- **`ADMIN_TOKEN` a un défaut faible** (`essensys-admin-secret`) : doit impérativement être surchargé en prod (vault).
- **Modèle pull/push gateway** : la latence de pilotage dépend de l'intervalle de polling de la gateway et du TTL `EXCHANGE_STALE_TTL_SECONDS` ; l'état affiché peut être marqué `stale`.
