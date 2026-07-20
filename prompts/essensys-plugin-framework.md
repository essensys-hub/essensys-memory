# Prompt : `essensys-plugin-framework` — extensions/options transverses aux 4 apps modernes

Tu es un ingénieur **full-stack (Go + React/TypeScript) + plateforme/infra (MQTT, Redis, Prometheus, Ansible) + sécurité**. Ta mission est de **concevoir et spécifier** (puis implémenter via **OpenSpec**, schema `spec-driven`) un **framework de plugins** `essensys-plugin-framework` permettant d'ajouter des **options/intégrations** aux quatre applications modernes ESSENSYS **sans forker chaque app pour chaque nouvelle capacité** :

- `essensys-server-backend` (Go, LAN/CM5, `:7070`) — jumeau backend LAN.
- `essensys-user-portal-backend` (Go, cloud/OVH, `:8080`) — jumeau backend cloud.
- `essensys-server-frontend` (React/TS, LAN) — jumeau UI LAN.
- `essensys-user-portal-frontend` (React/TS, cloud `mon.essensys.fr/portal`) — jumeau UI cloud.

**Cas d'usage de référence (validation end-to-end)** : intégration d'une **centrale solaire Sungrow SH6.0RS + batterie SBR064** (collecteur local WebSocket WiNet-S déjà écrit : `~/ESSENSYS/sungrow_winet_collector.py`), qui doit faire apparaître, dans les 4 apps, des **métriques de production/consommation/batterie** (tuile dashboard + page détail), **sans une seule ligne modifiée dans le protocole legacy IoT ni le firmware**.

Respecte **Clean Architecture / DDD** (bounded context `plugins` isolé), **library-first** (étendre les patterns existants — bus Mosquitto, cache Redis, métriques Prometheus, cloudsync gateway↔OVH, auth JWT/LAN trusted-devices — **avant tout NIH**), et la règle absolue des **jumeaux** : une option se déclare **une fois** et se rend **identiquement** LAN et cloud.

> ⚠️ Ce fichier est un **prompt de cadrage** destiné à `/openspec-propose`. Il ne remplace pas la proposition : il fournit le contexte, les contraintes vérifiées contre `essensys-memory/okf`, `essensys-memory/raw`, `essensys-memory/docs`, et les décisions à trancher. L'agent OpenSpec produit `proposal.md` → `design.md` → `specs/**` → `tasks.md`.

---

## 0. Autocritique — ce qu'un « plugin » **n'est PAS** ici

| Piège | Pourquoi c'est faux dans ESSENSYS | Cadrage retenu |
|-------|-----------------------------------|----------------|
| Charger dynamiquement du code Go dans les 2 backends (`plugin.Open`) | Le package Go `plugin` est **Linux-only, verrouillé à la version exacte du compilateur et de chaque dépendance**, non testable, incompatible avec un parc **multi-cible** (CM5 ARM + OVH x86) et des builds reproductibles | **Aucun chargement dynamique de code** dans les 4 binaires. Les binaires restent stables. |
| Runtime de plugins React chargé au navigateur (module federation) | Frontends buildés/bundlés, UX Matrix Gate bloquante, jumeaux à synchroniser à la main | **UI dirigée par le serveur** (server-driven UI) : le backend décrit la surface du plugin, un **renderer générique** commun aux deux frontends l'affiche. |
| Un plugin = un microservice de plus à déployer partout | Casse les périmètres de déploiement (un device LAN n'est pas joignable depuis OVH) | Plugin = **manifest déclaratif + collecteur sidecar optionnel publiant sur le bus existant** ; adaptateur backend expose l'API moderne ; descripteur UI rendu par slots génériques. |
| Réutiliser les endpoints legacy pour « faire passer » les données plugin | `/api/serverinfos`, `mystatus`, `myactions`, `done` sont **gelés** (contrat firmware) | Plugins **100 % côté moderne** : `/api/plugins/<id>/*`. Interdiction stricte de toucher le legacy et la table d'échange. |

**Décision de cadrage** : un plugin ESSENSYS est un **contrat déclaratif** (`plugin.manifest.json`) + jusqu'à 3 briques optionnelles : **(a)** un *collecteur* sidecar (comme le collecteur Sungrow) qui publie sur **Mosquitto/Redis**, **(b)** un *adaptateur backend* enregistré dans un registre compilé (pas dynamique) qui expose des routes REST modernes et persiste les séries dans **Prometheus**, **(c)** un *descripteur UI* (tuiles, pages, panneaux de réglages) rendu par un **renderer générique** partagé par les deux frontends.

---

## 0 bis. Autocritique croisée (OKF / raw / docs) — écarts bloquants à intégrer AVANT OpenSpec

Relecture du cadrage contre `okf/` (systems, processes, protocols, portals, concepts, synthesis), `docs/WORKFLOW.md` et `openspec/config.yaml`. **Corrections obligatoires.**

### 0 bis.1 Écarts bloquants

| # | Écart | Source OKF/raw/config | Correction |
|---|-------|-----------------------|------------|
| **E1** | « Un plugin tourne partout » | [Deployment Perimeters](/okf/processes/deployment-perimeters.md) : **3 périmètres** — CM5 LAN (`server-backend :7070` → armoire eth1 10.0.1.x) ; hub OVH (`:8080`) ; **armoire seule WAN** (firmware poll `mon.essensys.fr`, **pas** de `server-backend` local) | Le manifest **déclare** `perimeters` supportés et **où s'exécute chaque brique**. Un plugin *device-LAN* (Sungrow) : collecteur **sur la CM5 uniquement** ; le cloud reçoit les données via **cloudsync** (relais gateway→OVH), **jamais** en accédant au device. En « armoire seule WAN », un plugin device-LAN est **indisponible** (à déclarer, pas à bricoler). |
| **E2** | Données plugin dans une nouvelle base | `okf/systems/essensys-prometheus.md` + le collecteur Sungrow expose déjà `--influx` | **Séries temporelles → Prometheus** (déjà déployé). Pas de nouvelle TSDB. État courant/last-value → **Redis**. Config plugin → store existant. Créer une base bespoke = NIH à rejeter en MVP. |
| **E3** | Backend « appelle » le device | `okf/systems/essensys-mosquitto.md`, `essensys-redis.md` : bus MQTT + cache déjà là | Le **collecteur** publie sur **Mosquitto** (`essensys/plugins/<id>/<machine_id>/...`) ; l'adaptateur backend **s'abonne** et sert le cache Redis. Découplage collecteur ↔ backend, résilience offline, réutilisation infra. |
| **E4** | UI dupliquée sur les 2 frontends | `docs/WORKFLOW.md` §2 + règle mémoire jumeaux (17) : `server-frontend` ↔ `user-portal-frontend` **sync obligatoire** | **Server-driven UI + renderer générique partagé** (package TS commun) : le plugin fournit **un** descripteur ; les deux frontends rendent le même composant. Élimine la dérive des jumeaux **par construction**. |
| **E5** | UI plugin sans preuve UX | [UX Matrix Gate](/okf/processes/essensys-ux-matrix-gate.md) : gate **bloquante** — Playwright **desktop + iPhone + iPad**, screenshots, visual regression, `no_armoire_required` pour UI domotique | Le framework livre un **harnais de test UI** : le renderer générique est testé **une fois** sur la matrice ; chaque plugin fournit fixtures + snapshots. UI plugin doit **bloquer/mocker** toute mutation armoire (`/api/admin/inject`, `/api/portal/inject`, `/api/web/actions`, `/scenarios/*/launch`) sauf dry-run. |
| **E6** | Manifest plugin ad hoc | [Feature Lifecycle](/okf/processes/feature-lifecycle.md) : `features/<id>.json` = **source de vérité**, gates sécurité **bloquantes** ; `essensys-feature-lifecycle` existe | `plugin.manifest.json` **étend** le schéma feature (`features/schema/feature.schema.json`) — ne pas créer un système de manifest parallèle. `check_feature_gate.py` doit reconnaître les plugins. |
| **E7** | Secrets plugin en clair | Prompt audit §0-bis.3 + `okf/roadmap/essensys-secrets-sops-migration-*` | Identifiants plugin (ex. WiNet-S `user`/`pw1111`, clés API cloud) via **SOPS**, jamais en clair dans le manifest ni le repo. Le manifest **référence** un secret, ne le contient pas. |
| **E8** | Repo hôte du change flou | `openspec/config.yaml` : « OpenSpec = roadmap », change dans le **dépôt hôte** ; le framework touche **5 dépôts** | **Repo hôte primaire = `essensys-plugin-framework`** (nouveau dépôt : SDK Go + package TS + schéma manifest + plugin exemple). Les 4 apps reçoivent des **changes-satellites** liés, ou le change primaire liste les tâches par dépôt. À trancher explicitement en §0-ter. |

### 0 bis.2 Écarts majeurs (design)

| # | Risque | Détail | Action |
|---|--------|--------|--------|
| **E9** | RBAC plugin réinventé | Auth existante : JWT/session cloud + LAN trusted-devices (`okf/concepts/trusted-devices-lan.md`) | Les routes `/api/plugins/*` **réutilisent** les middlewares d'auth existants. Le manifest déclare la **visibilité** (`user`/`admin_local`/`admin_global`/`lan_user`/`lan_admin`). Aucun schéma d'autorisation maison. |
| **E10** | Registre backend « dynamique » déguisé | Even out-of-process (hashicorp go-plugin gRPC) = surcoût ops par plugin | MVP = **registre compilé** (les adaptateurs sont des packages Go compilés dans les 2 backends, activés par manifest). go-plugin/gRPC = **extension Phase 2** documentée, pas MVP. |
| **E11** | Couplage collecteur ↔ Python | Le collecteur Sungrow est en Python (stdlib) ; backends en Go | Le collecteur reste **agnostique du langage** : contrat = **topics MQTT + schéma de payload**, pas un binaire lié. Un collecteur peut être Python, Go, ou n8n (`okf/systems/essensys-n8n.md`). |
| **E12** | Idempotence / doublons cloud | Cloudsync relaie LAN→OVH ; risque double-écriture Prometheus | Clé de série `(plugin_id, machine_id, metric)` ; le cloud **agrège** ce que la gateway pousse, ne re-scrape pas le device. Définir qui expose l'endpoint Prometheus (gateway vs OVH) par périmètre. |
| **E13** | Cycle de vie plugin | Install/activation/désactivation/désinstallation non spécifiés | États : `declared → installed → enabled → disabled`. Désactiver un plugin **n'efface pas** ses séries. Health/liveness du collecteur exposé (le collecteur Sungrow doit publier un heartbeat). |
| **E14** | Versioning du contrat | Plugins et framework évoluent séparément | `manifest_version` + capacités négociées ; un plugin déclare la **version de framework** requise. |

### 0 bis.3 Lacunes process (docs/WORKFLOW + config.yaml)

| Lacune | Référence | À intégrer au change |
|--------|-----------|----------------------|
| Impact legacy vs modern à mentionner | `openspec/config.yaml` rules.proposal | `proposal.md` : section explicite « **legacy = zéro impact** ; plugins 100 % modernes ». |
| Firmware/backend/infra documentés séparément si cross-cutting | `config.yaml` rules.design | `design.md` : sous-sections **backend Go** / **frontend TS** / **infra (MQTT/Redis/Prometheus/Ansible)** distinctes. |
| Tâche « mettre à jour essensys-memory » | `config.yaml` rules.tasks | `tasks.md` : ingest wiki `wiki/concepts/plugin-framework.md` + fiche OKF `okf/concepts/` + entrée `okf/systems/essensys-plugin-framework.md` + `okf/log.md`. |
| Jumeaux détaillés | `docs/WORKFLOW.md` §2 | Tâche explicite : le renderer générique et le descripteur sont **partagés** (un package), pas copiés. |
| Publication roadmap publique | CLAUDE.md règle 18 | Après exec queue : `./scripts/publish-roadmap-public.sh`. |

### 0 bis.4 Matrice périmètre × brique plugin (alignée OKF)

| Périmètre OKF | Collecteur (device LAN) | Adaptateur backend | UI | Métriques |
|---------------|-------------------------|--------------------|----|-----------|
| **CM5 / Pi LAN** | ✅ sur CM5 (accès device 192.168.1.x) | `server-backend :7070` | LAN + cloud (via cloudsync) | Prometheus gateway → push/relay OVH |
| **Hub + gateway cloudsync** | ✅ sur gateway | LAN + `user-portal-backend :8080` (relai) | LAN + portail | Idem + agrégation OVH |
| **Armoire seule WAN** | ❌ pas de backend LAN, device non joignable | `user-portal-backend` uniquement (plugins **cloud-only**) | Portail cloud seulement | OVH direct |

### 0 bis.5 Tests manquants à exiger

- Renderer générique : matrice UX (desktop/iphone/ipad) + visual regression **une fois**, puis snapshot par plugin.
- `no_armoire_required` : la tuile Sungrow ne déclenche **aucune** mutation armoire.
- Résilience bus : collecteur down → backend sert le **dernier** état Redis + marque `stale`.
- Périmètre « armoire seule WAN » : plugin device-LAN correctement **masqué**, message clair.
- Idempotence cloudsync : pas de double comptage des séries relayées.
- Secrets : le manifest ne contient aucun secret en clair (test CI de lint).
- Non-régression legacy : aucun endpoint `mystatus`/`myactions`/`serverinfos` touché (diff-guard).

---

## 0 ter. Décisions produit à trancher dans `proposal.md` (ne pas laisser implicites)

1. **Repo hôte** : `essensys-plugin-framework` nouveau dépôt (recommandé) vs extension de `essensys-feature-lifecycle`. Le change primaire vit-il là, avec changes-satellites dans les 4 apps, ou un seul change transverse listant les tâches par dépôt ? → **Recommandation : nouveau dépôt + un change primaire qui référence les tâches satellites.**
2. **Runtime backend** : registre **compilé** (MVP recommandé) vs out-of-process gRPC (Phase 2).
3. **UI** : **server-driven UI** (recommandé — règle les jumeaux + réduit la surface UX-gate) vs slots build-time.
4. **Persistance métriques** : **Prometheus** (recommandé, déjà déployé) vs autre.
5. **Transport collecteur→backend** : **Mosquitto** (recommandé) vs Redis pub/sub vs HTTP push.
6. **Portée MVP** : livrer le framework **avec** le plugin Sungrow de référence (recommandé), ou framework seul puis Sungrow en second change.

Chaque décision : **recommandation par défaut ci-dessus**, mais l'agent OpenSpec doit la formaliser avec alternatives + conséquences.

---

## 1. Objectifs produit

### 1.1 Livrables
1. **SDK/contrat de plugin** : schéma `plugin.manifest.json` (extension de `features/schema/feature.schema.json`), versionné, avec `capabilities`, `perimeters`, `surfaces` (backend/ui/collector), `visibility` (RBAC), `secrets` (références SOPS), `metrics` (noms/labels/unités Prometheus).
2. **SDK Go** (`essensys-plugin-framework/go`) : interface `PluginAdapter` (register routes `/api/plugins/<id>/*`, souscription MQTT, exposition Prometheus, health) + **registre compilé** intégré aux 2 backends.
3. **Package TS partagé** (`essensys-plugin-framework/ts`) : **renderer générique** (tuiles dashboard, page détail, panneau réglages) piloté par descripteur serveur, consommé **identiquement** par les 2 frontends.
4. **Contrat collecteur** : topics MQTT + schéma payload + heartbeat, langage-agnostique.
5. **Plugin de référence `sungrow-solar`** : adapte `sungrow_winet_collector.py` (publie MQTT), adaptateur Go, descripteur UI (production PV, conso maison, injection/soutirage, SoC/santé batterie, températures).
6. **Harnais de tests + gates** : template UX Matrix, feature-gate reconnaissant les plugins, security-gate (secrets, no-armoire, no-legacy).
7. **Doc + mémoire** : `essensys-doc` (page « écrire un plugin »), ingest wiki/OKF.

### 1.2 Non-objectifs MVP
- Chargement dynamique de code (Go `plugin` ou module federation) — Phase 2 (go-plugin gRPC) documentée seulement.
- Marketplace / installation par l'utilisateur final — plugins déclarés par l'opérateur.
- Plugins écrivant vers l'armoire (contrôle domotique) — MVP **lecture/observabilité** ; l'écriture passera par les gates armoire existantes en Phase 2.
- Remplacement de Prometheus/Grafana pour la visualisation avancée.
- Toute modification legacy IoT / firmware / table d'échange.

---

## 2. Architecture cible (à détailler dans `design.md`)

- **Manifest** : un fichier par plugin, validé en CI ; source de vérité des surfaces et de la visibilité.
- **Flux device-LAN** : `device` → **collecteur** (CM5) → **Mosquitto** → **adaptateur backend** (`server-backend`) → Redis (last value) + Prometheus (séries) → **API moderne** `/api/plugins/<id>/*` → **renderer générique** (2 frontends). Cloud : **cloudsync** relaie vers `user-portal-backend`, qui sert le portail.
- **Frontière dual-protocol** : les plugins n'ont **aucun** accès au legacy ; garde CI (diff-guard) sur les fichiers legacy.
- **Sécurité** : auth réutilisée, RBAC déclaratif, secrets SOPS, no-armoire par défaut, isolation collecteur (process séparé).
- **Jumeaux** : descripteur + renderer **partagés** ; interdiction de composant plugin spécifique à un seul frontend.

## 3. Plugin de référence `sungrow-solar` (preuve du framework)

Réutiliser `~/ESSENSYS/sungrow_winet_collector.py` (API locale `wss://<ip>/ws/home/overview`, login `user`/`pw1111`, ~30 métriques). Le transformer en **collecteur MQTT** conforme au contrat. Métriques exposées : `pv_power`, `load_power`, `grid_export_power`, `grid_import_power`, `battery_soc`, `battery_soh`, `battery_temp`, énergies journalières/totales. UI : tuile « Solaire » (flux instantané) + page détail (historique Prometheus). Zéro mutation armoire.

---

## 4. Intégration OpenSpec — instructions à l'agent

- **Schema** : `spec-driven`. **Repo hôte** : `essensys-plugin-framework` (créer si absent) ; changes-satellites liés dans les 4 apps.
- **ID de change** : `essensys-plugin-framework-2026-07-0XX` (prochain numéro libre après `034`).
- **Artefacts** : `proposal.md` (objectifs, décisions §0-ter, **impact legacy = nul**, liens wiki), `design.md` (sous-sections **backend Go / frontend TS / infra** séparées, cf. `config.yaml`), `specs/plugin-framework/spec.md` (contrat manifest, SDK, renderer, RBAC, périmètres), `specs/sungrow-solar/spec.md` (plugin de référence), `tasks.md`.
- **`tasks.md` doit inclure** : tâche par dépôt (5), **sync jumeaux** explicite, **UX Matrix Gate** pour le renderer, **feature-gate + security-gate**, **secrets SOPS**, **diff-guard legacy**, et la tâche obligatoire « **mettre à jour essensys-memory** » (ingest `wiki/concepts/plugin-framework.md`, fiche `okf/systems/essensys-plugin-framework.md`, `okf/log.md`, page roadmap + `publish-roadmap-public.sh`).
- **Rappels config.yaml** : mentionner legacy vs modern et table d'échange (ici : aucun impact, à écrire noir sur blanc) ; lier aux entités wiki existantes ([Platform Overview](/okf/synthesis/platform-overview.md), [Dual Protocol](/okf/concepts/dual-protocol.md), [Deployment Perimeters](/okf/processes/deployment-perimeters.md), [UX Matrix Gate](/okf/processes/essensys-ux-matrix-gate.md), [Feature Lifecycle](/okf/processes/feature-lifecycle.md)).

### Definition of Done
- [ ] `proposal.md` tranche les 6 décisions §0-ter avec conséquences.
- [ ] Manifest = extension du schéma feature existant (pas parallèle).
- [ ] Renderer générique partagé (un package), rendu identique sur les 2 frontends.
- [ ] Métriques → Prometheus, last-value → Redis, transport → Mosquitto (sauf décision contraire justifiée).
- [ ] Plugin `sungrow-solar` fonctionnel end-to-end sur périmètre CM5 LAN, masqué en « armoire seule WAN ».
- [ ] UX Matrix Gate + feature-gate + security-gate verts ; diff-guard legacy vert.
- [ ] Secrets via SOPS ; aucun secret en clair (lint CI).
- [ ] `essensys-memory` mis à jour (wiki + OKF + roadmap publique).
- [ ] Jumeaux backend et UI synchronisés (docs/WORKFLOW §2).

---

### Point de départ suggéré pour l'agent
> Lance `/openspec-propose` avec ce prompt comme contexte. Commence par formaliser les décisions §0-ter (utilise les recommandations par défaut sauf objection argumentée), puis rédige `proposal.md` en affirmant l'**impact legacy nul**, puis `design.md` (3 sous-sections), puis les specs, puis `tasks.md` avec les tâches par dépôt et les gates. N'invente aucune capacité legacy ; toute zone protocolaire ou firmware est **hors périmètre** et doit être vérifiée contre `okf/protocols/` avant toute hypothèse.
