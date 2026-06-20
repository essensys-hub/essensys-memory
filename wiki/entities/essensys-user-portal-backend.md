---
tags: [entity, repo, legacy, backend]
sources: [essensys-user-portal-backend.md]
created: 2026-06-20
updated: 2026-06-20
era: legacy
repo: essensys-user-portal-backend
---

# Essensys User Portal Backend

> Backend Go du hub cloud Essensys (OVH) : portail domotique distant + relais d'actions vers les gateways, qui consolide aussi l'identité, l'admin et le protocole IoT legacy du support-site en un seul service.

| | |
|---|---|
| **Catégorie** | Backend / Service cloud (API HTTP) |
| **Stack** | Go 1.25, go-chi v5, PostgreSQL (sqlx + lib/pq), JWT, New Relic APM |
| **Statut** | Actif — déployé en production sous le nom `essensys-cloud-backend` (`:8080`), `CONSOLIDATED_MODE=true` depuis le cutover de juin 2026 |
| **Era** | legacy |

## Rôle

Ce service est le **hub cloud** hébergé sur le VPS OVH, derrière `https://mon.essensys.fr`. Il remplit deux fonctions distinctes des serveurs locaux Essensys :

- **Portail domotique distant** : il permet à un utilisateur final de piloter son armoire domotique Essensys depuis Internet (hors réseau local), sans être sur le même LAN que sa box/armoire. C'est la différence majeure avec `essensys-server-backend`, qui est le serveur **local** d'une installation (sur site, réseau privé) et parle directement au firmware via la table d'échange.
- **Hub de consolidation** : en `CONSOLIDATED_MODE=true`, il absorbe le backend de l'ancien `essensys-support-site` (authentification email/OAuth, profils, admin, newsletter) et le protocole IoT WAN legacy (mystatus/serverinfos/infos), pour faire tourner un **seul binaire** au lieu de deux backends séparés.

Le pont avec l'armoire distante n'est pas direct : le portail dépose des **actions cloud** en base, et la **gateway Raspberry/CM5** (`essensys-raspberry-gateway`) installée chez le client effectue du polling sortant (`GET /api/gateway/pending-actions`), exécute les ordres localement, puis remonte l'état (`POST /api/gateway/exchange`). C'est un modèle pull/push pensé pour traverser un NAT résidentiel sans port ouvert.

Distinction des utilisateurs :
- **Utilisateur final** (propriétaire d'une armoire) → routes `/api/portal/*` avec JWT utilisateur.
- **Gateway** (agent embarqué chez le client) → routes `/api/gateway/*` authentifiées par head

_… voir source complète dans raw/_

## Intégrations

- **essensys-user-portal-frontend** : SPA React servie sur `/portal/`, consomme `/api/portal/*` et `/api/auth/*` sur le même host.
- **essensys-raspberry-gateway** (CM5) : agent client qui poll `/api/gateway/pending-actions`, acquitte via `/api/gateway/actions/{guid}/done`, envoie `/api/gateway/heartbeat` et pousse l'état via `/api/gateway/exchange`.
- **essensys-support-site** : code d'origine consolidé ici (auth, admin, newsletter, IoT legacy) ; PostgreSQL et `JWT_SECRET` partagés. La matrice de migration handler→package est dans le README.
- **OAuth Google / Apple** : login social via `internal/identity`.
- **New Relic APM** : app `essensys-cloud-backend`.
- **Nginx** (sur le VPS) : route `/api/` → backend `:8080` ; sert le frontend statique sous `/portal/`.

## Structure

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
  legacyiot/               # /api/mystatus, /myactions, /done,

_… voir source complète dans raw/_

## Points d'attention

- **Mode dual selon `CONSOLIDATED_MODE`** : à `false`, seuls portail + gateway sont montés (mode staging historique `:8081`) ; à `true`, c'est le hub complet de production. Un mauvais flag fait silencieusement disparaître les routes auth/admin/legacy.
- **Couplage fort avec le support-site** : même base PostgreSQL et même `JWT_SECRET`. Toute rotation de secret ou migration de schéma doit être coordonnée entre les deux.
- **Éligibilité gateway** : `domain.IsRemoteEligibleGateway()` exclut explicitement la gateway `essensys-server` (VPS legacy) du portail distant — le frontend affiche un message « portail indisponible » dans ce cas.
- **Authentification gateway par headers** (MAC eth0/eth1 + token), pas par JWT : surface différente du reste de l'API, à traiter avec soin (les MAC sont des identifiants).
- **Migrations auto au démarrage** : pratique mais les erreurs ne sont que logguées en WARNING (pas fatales), ce qui peut masquer une base non migrée.
- **`ADMIN_TOKEN` a un défaut faible** (`essensys-admin-secret`) : doit impérativement être surchargé en prod (vault).
- **Modèle pull/push gateway** : la latence de pilotage dépend de l'intervalle de polling de la gateway et du TTL `EXC

_… voir source complète dans raw/_

## Liens

- [[Cloud Relay]]
- [[Essensys User Portal Frontend]]
- [[Essensys Server Backend]]

## Source

`raw/architecture/repos/essensys-user-portal-backend.md`
