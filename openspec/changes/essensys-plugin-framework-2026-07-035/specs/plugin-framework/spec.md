## ADDED Requirements

### Requirement: Manifest de plugin déclaratif
Le framework SHALL définir un contrat `plugin.manifest.json` comme **extension** de `features/schema/feature.schema.json`. Le manifest MUST déclarer au minimum : `id` (kebab-case), `manifest_version`, `framework_version` requis, `capabilities`, `perimeters` supportés, `surfaces` (backend/ui/collector), `visibility` (rôles autorisés), `secrets` (références SOPS), `metrics` (nom, label, unité). Le framework MUST rejeter un manifest invalide en CI.

#### Scenario: Manifest valide accepté
- **WHEN** un plugin fournit un `plugin.manifest.json` conforme au schéma étendu
- **THEN** la validation CI passe et le plugin devient `declared`

#### Scenario: Manifest invalide rejeté
- **WHEN** un manifest omet un champ obligatoire (ex. `perimeters`) ou viole le schéma
- **THEN** la validation CI échoue avec un message pointant le champ fautif

### Requirement: Aucun chargement dynamique de code
Le framework MUST intégrer les adaptateurs backend via un **registre compilé** dans les binaires ; il MUST NOT utiliser `plugin.Open` ni le chargement de code au runtime. Un plugin backend est activé/désactivé par le manifest, sans recompilation à chaud en MVP.

#### Scenario: Adaptateur activé par manifest
- **WHEN** un adaptateur compilé est présent et son manifest est `enabled`
- **THEN** ses routes `/api/plugins/<id>/*` sont montées au démarrage du backend

#### Scenario: Adaptateur désactivé
- **WHEN** le manifest d'un plugin est `disabled`
- **THEN** ses routes ne sont pas montées et aucune souscription bus n'est ouverte

### Requirement: Frontière dual-protocol garantie en CI
Les plugins MUST exposer leurs données exclusivement via l'API moderne `/api/plugins/<id>/*`. Le framework MUST fournir un **diff-guard** CI bloquant qui interdit toute référence, depuis le code plugin, aux handlers/constantes legacy (`serverinfos`, `mystatus`, `myactions`, `done`, table d'échange).

#### Scenario: Référence legacy bloquée
- **WHEN** du code plugin importe ou appelle un handler/constante legacy
- **THEN** le diff-guard CI échoue et le merge est bloqué

#### Scenario: Plugin moderne conforme
- **WHEN** un plugin n'expose que des routes `/api/plugins/*` sans toucher au legacy
- **THEN** le diff-guard CI passe

### Requirement: UI dirigée par le serveur, rendue par les deux jumeaux
Le framework MUST fournir un **renderer générique** unique (package TS partagé) piloté par un descripteur serveur. Les deux frontends (`essensys-server-frontend`, `essensys-user-portal-frontend`) MUST consommer ce même composant ; aucun composant de plugin spécifique à un seul frontend n'est autorisé.

#### Scenario: Rendu identique LAN et cloud
- **WHEN** un plugin fournit un descripteur UI et les deux frontends le rendent
- **THEN** la tuile/page produite est identique (même composant partagé) sur LAN et cloud

#### Scenario: Composant spécifique interdit
- **WHEN** un plugin ajoute un composant React dans un seul frontend
- **THEN** la revue/CI le refuse au titre de la règle jumeaux

### Requirement: Contrat collecteur sur bus MQTT
Le framework MUST définir un contrat collecteur langage-agnostique : publication sur Mosquitto sous `essensys/plugins/<id>/<machine_id>/…`, schéma de payload, et **heartbeat** périodique. L'adaptateur backend MUST s'abonner et alimenter Redis (last-value) et Prometheus (séries).

#### Scenario: Ingestion d'une mesure
- **WHEN** un collecteur publie une métrique sur son topic MQTT
- **THEN** l'adaptateur écrit la dernière valeur en Redis et la série en Prometheus

#### Scenario: Collecteur hors ligne marqué stale
- **WHEN** aucun heartbeat n'est reçu au-delà du seuil déclaré
- **THEN** l'adaptateur marque l'état `stale` et l'API le signale sans échec dur

### Requirement: Persistance sur l'infra existante
Le framework MUST persister les séries temporelles dans Prometheus et l'état courant dans Redis. Il MUST NOT introduire de nouvelle base de données. Les séries MUST être clés par `(plugin_id, machine_id, metric)` pour garantir l'idempotence à travers le relais cloudsync.

#### Scenario: Pas de double comptage cloud
- **WHEN** la gateway relaie des séries plugin vers OVH via cloudsync
- **THEN** le cloud agrège sans re-scraper le device et sans dupliquer la série

### Requirement: Réutilisation de l'authentification et RBAC déclaratif
Les routes `/api/plugins/*` MUST passer par les middlewares d'auth existants (JWT/session cloud, trusted-devices LAN). La visibilité d'un plugin MUST être déclarée dans le manifest (`user`, `admin_local`, `admin_global`, `lan_user`, `lan_admin`) ; le framework MUST NOT introduire de schéma d'autorisation maison.

#### Scenario: Accès refusé hors visibilité
- **WHEN** un utilisateur dont le rôle n'est pas dans `visibility` appelle une route plugin
- **THEN** l'API répond 403 via le middleware existant

#### Scenario: Accès autorisé selon visibilité
- **WHEN** un utilisateur au rôle listé dans `visibility` appelle la route
- **THEN** l'API renvoie les données du plugin

### Requirement: Respect des périmètres de déploiement
Le manifest MUST déclarer les `perimeters` supportés. Un plugin device-LAN MUST exécuter son collecteur uniquement là où le device est joignable (CM5/gateway) et MUST être indisponible en « armoire seule WAN », avec un message clair côté UI.

#### Scenario: Plugin device-LAN masqué en armoire seule WAN
- **WHEN** l'installation est en périmètre « armoire seule WAN » et le plugin est device-LAN
- **THEN** l'UI indique l'indisponibilité et aucune tentative d'accès device n'est faite

#### Scenario: Cloud sans accès device direct
- **WHEN** le backend cloud sert les données d'un plugin device-LAN
- **THEN** il les obtient via cloudsync et jamais par un accès direct au device

### Requirement: Secrets via SOPS
Le manifest MUST référencer les secrets (identifiants device, clés API) par référence SOPS et MUST NOT contenir de secret en clair. Un lint CI bloquant MUST détecter tout secret en clair.

#### Scenario: Secret en clair rejeté
- **WHEN** un manifest contient un mot de passe ou une clé en clair
- **THEN** le lint CI échoue et bloque le merge

### Requirement: Gates lifecycle applicables aux plugins
Le framework MUST rendre les plugins reconnaissables par `check_feature_gate.py`. Toute UI de plugin MUST satisfaire l'UX Matrix Gate (Playwright desktop + iPhone + iPad, screenshots, visual regression). L'UI plugin MUST bloquer ou mocker les mutations armoire (`/api/admin/inject`, `/api/portal/inject`, `/api/web/actions`, `/scenarios/*/launch`) sauf dry-run explicite.

#### Scenario: UI plugin sans preuve UX bloquée
- **WHEN** un plugin ajoute une UI sans matrice UX complète
- **THEN** la feature-gate échoue

#### Scenario: Mutation armoire bloquée par défaut
- **WHEN** une UI de plugin tente une mutation armoire sans dry-run
- **THEN** l'appel est bloqué/mocké et le test no-armoire passe

### Requirement: Cycle de vie et versioning du plugin
Le framework MUST gérer les états `declared → installed → enabled → disabled`. Désactiver un plugin MUST NOT effacer ses séries Prometheus. Un plugin MUST déclarer la version de framework requise ; une incompatibilité MUST être refusée au chargement.

#### Scenario: Désactivation conserve l'historique
- **WHEN** un plugin passe `enabled → disabled`
- **THEN** ses routes s'arrêtent mais ses séries Prometheus restent consultables

#### Scenario: Version de framework incompatible
- **WHEN** un plugin exige une `framework_version` non satisfaite
- **THEN** le framework refuse de l'activer avec une erreur explicite
