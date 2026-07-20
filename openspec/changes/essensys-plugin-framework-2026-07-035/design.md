## Context

ESSENSYS expose quatre applications modernes jumelées (deux backends Go LAN/cloud, deux frontends React LAN/cloud) au-dessus d'un socle infra déjà déployé : Mosquitto (MQTT), Redis, Prometheus, cloudsync gateway↔OVH, auth JWT/session + trusted-devices LAN, secrets SOPS, déploiement Ansible. Le protocole legacy IoT (`/api/serverinfos`, `mystatus`, `myactions`, `done`, table d'échange) est **gelé** (contrat firmware). Trois périmètres de déploiement coexistent (CM5 LAN, hub OVH, armoire seule WAN) et ne partagent ni binaires ni accès réseau.

Ce design répond à une question transverse : comment ajouter des **options/intégrations** aux 4 apps **une seule fois**, sans forker chaque app, sans dériver entre jumeaux, et sans jamais toucher le legacy. Le cas de référence est l'intégration Sungrow (collecteur WiNet-S local déjà écrit).

## Goals / Non-Goals

**Goals:**
- Contrat de plugin **déclaratif** unique, extension du schéma feature existant.
- Une intégration se déclare une fois → rendue identiquement LAN et cloud.
- Réutiliser Mosquitto / Redis / Prometheus / SOPS / cloudsync ; zéro nouvelle base ni nouveau bus.
- Binaires des 4 apps **stables** (aucun chargement dynamique de code).
- Frontière dual-protocol garantie **en CI** (impact legacy nul).
- Respect natif des 3 périmètres de déploiement.
- Passage des gates existantes (UX Matrix, feature, security).

**Non-Goals:**
- Chargement dynamique de code (Go `plugin`, module federation) — Phase 2 seulement (gRPC out-of-process).
- Marketplace / installation par l'utilisateur final.
- Plugins écrivant vers l'armoire (contrôle domotique) — MVP en lecture/observabilité.
- Remplacer Grafana/Prometheus pour la visualisation avancée.
- Toute évolution du protocole legacy, du firmware ou de la table d'échange.

## Decisions

Les six décisions ci-dessous correspondent au §0-ter du prompt de cadrage. Chacune : choix retenu, alternatives, conséquences.

### D1 — Dépôt hôte : nouveau dépôt `essensys-plugin-framework`
**Retenu** : nouveau dépôt (SDK Go `/go`, package TS `/ts`, schéma manifest, plugin exemple). Un **change primaire** ici ; les 4 apps reçoivent des **changes-satellites** liés (intégration du registre / du renderer).
**Alternatives** : (a) rattacher à `essensys-feature-lifecycle` — mélange gate lifecycle et runtime plugin ; (b) un seul change transverse dans le brain listant les tâches par dépôt — perd la localité « change dans le dépôt hôte ».
**Conséquences** : nouveau dépôt à inventorier (fiche OKF + wiki), à câbler dans Ansible et la CI ; SDK versionné indépendamment des apps.

### D2 — Runtime backend : registre **compilé** (MVP), gRPC en Phase 2
**Retenu** : les adaptateurs de plugin sont des packages Go **compilés** dans les deux backends, activés/désactivés par le manifest à l'exécution. Interface `PluginAdapter` (routes, souscription MQTT, exposition Prometheus, health).
**Alternatives** : (a) `plugin.Open` — Linux-only, verrouillé version, non testable, rejeté ; (b) hashicorp go-plugin gRPC out-of-process — bonne isolation mais surcoût ops par plugin → **Phase 2** documentée.
**Conséquences** : ajouter un plugin backend = rebuild des backends (acceptable, CI existante) ; isolation par process assurée côté **collecteur**, pas côté adaptateur → l'adaptateur reste mince (I/O bus + REST), la logique device vit dans le collecteur.

### D3 — UI : **server-driven UI** + renderer générique partagé
**Retenu** : le backend renvoie un **descripteur** (métriques, libellés, unités, type de tuile/chart) ; un renderer générique dans le package TS partagé l'affiche. Les deux frontends importent **le même** composant.
**Alternatives** : (a) slots build-time par frontend — duplication et dérive des jumeaux ; (b) module federation runtime — incompatible UX Matrix Gate et build reproductible.
**Conséquences** : dérive jumeaux éliminée par construction ; surface UX-gate réduite (renderer testé une fois sur desktop/iphone/ipad, puis snapshot par plugin) ; les plugins ne peuvent pas livrer de JS arbitraire au navigateur (contrainte volontaire, sécurité). Composants riches non couverts par le renderer = évolution du renderer, pas code par plugin.

### D4 — Persistance : **Prometheus** (séries) + **Redis** (last-value)
**Retenu** : séries temporelles → Prometheus (déjà déployé, le collecteur Sungrow sait déjà sortir en line-protocol) ; état courant / dernière valeur → Redis ; config plugin → store existant.
**Alternatives** : nouvelle TSDB (InfluxD/Timescale) — NIH, rejeté MVP.
**Conséquences** : nommage des séries `(plugin_id, machine_id, metric)` ; qui expose l'endpoint Prometheus dépend du périmètre (gateway vs OVH) — voir D6/risques.

### D5 — Transport collecteur→backend : **Mosquitto**
**Retenu** : le collecteur publie sur Mosquitto (`essensys/plugins/<id>/<machine_id>/…` + heartbeat) ; l'adaptateur backend s'abonne, alimente Redis/Prometheus.
**Alternatives** : Redis pub/sub (moins standard pour de l'ingest device) ; HTTP push (couple le collecteur au backend, casse le découplage/offline).
**Conséquences** : collecteur langage-agnostique (Python/Go/n8n) ; résilience offline (le backend sert le dernier état Redis marqué `stale` si le collecteur tombe).

### D6 — Portée MVP : framework **livré avec** le plugin `sungrow-solar`
**Retenu** : livrer le framework **et** le plugin de référence dans le même change, pour prouver le contrat end-to-end.
**Alternatives** : framework seul puis Sungrow en second change — risque de framework non validé par un cas réel.
**Conséquences** : périmètre du change plus large mais auto-vérifiant ; le plugin Sungrow est lecture seule, zéro mutation armoire.

### Découpage cross-cutting (backend / frontend / infra)

**Backend (Go)** — `essensys-server-backend` + `essensys-user-portal-backend` :
- Interface `PluginAdapter`, registre compilé, routes `/api/plugins/<id>/*` derrière les middlewares d'auth **existants**.
- Abonnement MQTT, écriture Redis/Prometheus, endpoint descripteur UI.
- Diff-guard : interdiction de toute référence aux handlers/constantes legacy depuis le package `plugins`.

**Frontend (TS/React)** — `essensys-server-frontend` + `essensys-user-portal-frontend` :
- Package partagé : renderer générique (tuile, page détail, panneau réglages) + client `/api/plugins/*`.
- Aucun composant plugin spécifique à un seul frontend (règle jumeaux).
- Mutations armoire bloquées/mockées par défaut (no-armoire).

**Infra** :
- Mosquitto : topics + heartbeat ; ACL par plugin.
- Redis : clés last-value + `stale` flag.
- Prometheus : séries + scrape par périmètre.
- SOPS : secrets référencés par le manifest, jamais en clair.
- Ansible : déploiement du collecteur par périmètre (CM5 pour device-LAN).

## Risks / Trade-offs

- **Double comptage cloudsync** (le cloud relaie les séries LAN) → clé de série idempotente `(plugin_id, machine_id, metric)` ; le cloud **agrège** ce que la gateway pousse, ne re-scrape pas le device.
- **Rebuild backend par plugin** (registre compilé) → acceptable via CI ; go-plugin gRPC en Phase 2 si le besoin de hot-plug émerge.
- **Expressivité UI limitée** par le renderer générique → faire évoluer le renderer (composant partagé testé) plutôt qu'ouvrir du JS par plugin.
- **Collecteur down** → backend sert le dernier état Redis marqué `stale` + heartbeat manquant remonté ; pas d'échec dur de l'UI.
- **Plugin device-LAN en « armoire seule WAN »** → indisponible par conception ; le manifest le déclare, l'UI affiche un message clair (pas de contournement).
- **Secrets** → lint CI bloquant si un secret apparaît en clair dans un manifest.
- **Fuite legacy** → diff-guard CI bloquant sur les fichiers/handlers legacy.

## Migration Plan

- Additif : aucun schéma legacy modifié, pas de migration destructive. Déploiement plugin par périmètre via Ansible ; rollback = désactiver le plugin dans le manifest (les séries Prometheus sont conservées). Ordre : SDK/package publiés → registre/renderer intégrés aux 4 apps (changes-satellites) → collecteur Sungrow déployé sur CM5 → activation manifest.

## Open Questions

- Endpoint Prometheus par périmètre : scrape gateway + federation OVH, ou remote-write ? (à fixer avec l'équipe infra Prometheus).
- Schéma exact d'extension de `features/schema/feature.schema.json` (champs `surfaces`/`perimeters`) — à valider contre `check_feature_gate.py`.
- Politique de rétention Prometheus pour les séries plugin (aligner sur la rétention existante).
- ACL Mosquitto par plugin : namespace par `plugin_id` suffisant, ou par `machine_id` aussi ?
