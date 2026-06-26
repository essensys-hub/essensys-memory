---
tags: [entity, repo, legacy, backend]
sources: [essensys-server-backend.md]
created: 2026-06-20
updated: 2026-06-26
era: legacy
repo: essensys-server-backend
---

# Essensys Server Backend

> Passerelle HTTP en Go qui fait le pont entre les boîtiers domotiques embarqués legacy (BP_MQX_ETH) et l'écosystème web/MQTT moderne, tout en conservant 100 % de compatibilité avec le protocole de l'ancien serveur ASP.NET.

| | |
|---|---|
| **Catégorie** | Service backend (gateway domotique on-premise / Raspberry) |
| **Stack** | Go **1.25+**, Redis, PostgreSQL (sqlx + lib/pq), MQTT (paho), Prometheus, MCP (mark3labs/mcp-go), API HTTP `net/http` |
| **Statut** | actif (cœur de la migration depuis le legacy .NET) |
| **Era** | legacy |

## Rôle

Ce service est le **serveur central** qui tourne typiquement sur la gateway Raspberry (image `essensyshub/essensys-base:raspberry.2026.02`). Il remplit deux fonctions simultanées (architecture **dual-protocol**, documentée dans `docs/ARCHITECTURE_DUAL_PROTOCOL.md`) :

1. **Protocole Legacy IoT** : il parle aux boîtiers embarqués `BP_MQX_ETH` (firmware C des cartes `essensys-board-SCxxx`). Ces clients pollent le serveur ~toutes les 500 ms en HTTP non-standard sur le **port 80 (obligatoire, codé en dur dans le firmware)**. Le serveur normalise leur JSON malformé (clés non-quotées), tolère leur HTTP non conforme (espaces parasites, absence de `Host`, `\n` au lieu de `\r\n`) et réplique exactement les particularités de l'ancien serveur ASP.NET (header `Content-Type: application/json ;charset=UTF-8` avec espace avant `;`, ordre des champs JSON, code `201 Created` sur POST).

2. **Protocole Web moderne** : il expose une API REST propre (JSON RFC 8259, sessions) consommée par `essensys-server-frontend` (React), ainsi que des intégrations MQTT (Home Assistant), UniFi Protect (caméras) et une synchronisation cloud optionnelle vers le hub `mon.essensys.fr`.

Les deux mondes partagent le même état : table d'échange (« exchange table », indices 0–999) en **Redis**, et historique/persistance en **PostgreSQL**.

## Intégrations

_Non documenté._

## Structure

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
│

_… voir source complète dans raw/_

## Points d'attention

- **Le protocole legacy est « sacré ».** Toute modification du format JSON, des headers (`application/json ;charset=UTF-8`), de l'ordre des champs ou des codes de retour peut casser silencieusement les boîtiers C (le firmware n'a pas de gestion d'erreur robuste). Voir la liste « À NE PAS FAIRE » dans `docs/ARCHITECTURE_DUAL_PROTOCOL.md`.
- **Port 80 obligatoire** : codé en dur dans le firmware ; nécessite `setcap` ou capability container. Un `WARNING` est loggé si un autre port est configuré.
- **Serveur HTTP custom** (`internal/server`) : `LegacyHTTPServer` + `LoggingListener` tolèrent l'HTTP non conforme des clients. Ne pas remplacer par un `http.Server` standard sans précaution.
- **Génération de bloc complet 605–622** : le firmware ignore une action lumière/volet si un seul indice du bloc manque ; le serveur complète automatiquement (+ index 590=1 comme déclencheur de scénario, jamais fusionné).
- **Désaccord README vs code** : le `README.md` décrit une ancienne version store-mémoire ; les dépendances réelles (Redis, Postgres, MQTT, MCP, UniFi, cloudsync) ne s'y trouvent pas. Documentation à jour côté `docs/` et code.
- **[[Security Gate]] (2026-06-26, branche `V.1.3.0`) :** bootstrap [[Essensys Feature Lifecycle]] ; CVE Go/npm corrigées (PR #2–#6), Dockerfile non-root, `.gitleaks.toml` allowlist doc, tests Go recompilés (PR #7, 11 `t.Skip` tests obsolètes auth passive / log `[GO]`).
- **[[LAN IAM]] (OpenSpec 2026-06.017, impl. 2026-06-26) :** package `internal/laniam`, table `lan_users`, sessions cookie 7j, routes `/api/admin/lan-users/*` ; activer `lan_iam.enabled` + migration SQL `003_lan_users`.
- **Cloudsync** : agent `internal/cloudsync` poll `GET /api/gateway/pending-actions` sur `mon.essensys.fr` ; requiert `cloud.enabled: true` + credentials dans le **bon** `config.yaml` (voir [[Essensys Ansible]]).
- **Dégradation gracieuse** : si PostgreSQL est injoignable,

_… voir source complète dans raw/_

## Liens

- [[Dual Protocol]]
- [[Table D Echange]]
- [[Essensys Server Frontend]]
- [[Essensys Redis]]

## Source

`raw/architecture/repos/essensys-server-backend.md`
