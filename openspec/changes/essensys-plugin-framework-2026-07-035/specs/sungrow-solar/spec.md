## ADDED Requirements

### Requirement: Collecteur Sungrow WiNet-S sur MQTT
Le plugin SHALL fournir un collecteur dérivé de `sungrow_winet_collector.py` qui interroge l'API locale WiNet-S (`wss://<ip>/ws/home/overview`, login `user`/`pw1111` référencé via SOPS) et publie les métriques sur Mosquitto selon le contrat collecteur, avec heartbeat. Le collecteur MUST s'exécuter sur le périmètre où le device est joignable (CM5/gateway).

#### Scenario: Publication des métriques temps réel
- **WHEN** le collecteur lit une trame temps réel de l'onduleur SH6.0RS
- **THEN** il publie `pv_power`, `load_power`, `grid_export_power`, `grid_import_power`, `battery_soc`, `battery_soh`, `battery_temp` et les énergies sur les topics `essensys/plugins/sungrow-solar/<machine_id>/…`

#### Scenario: Identifiants via SOPS
- **WHEN** le collecteur démarre
- **THEN** il lit les identifiants WiNet-S depuis SOPS et jamais depuis un secret en clair du manifest

### Requirement: Métriques exposées via l'API moderne
Le plugin SHALL exposer ses métriques via `/api/plugins/sungrow-solar/*` (dernière valeur depuis Redis, historique depuis Prometheus) derrière l'auth existante. Il MUST NOT toucher au protocole legacy.

#### Scenario: Lecture du flux instantané
- **WHEN** un utilisateur autorisé appelle `/api/plugins/sungrow-solar/current`
- **THEN** l'API renvoie le flux consolidé (production PV, conso maison, injection/soutirage, batterie) depuis Redis

#### Scenario: Lecture de l'historique
- **WHEN** un utilisateur autorisé demande l'historique d'une métrique
- **THEN** l'API renvoie la série depuis Prometheus, clé `(sungrow-solar, machine_id, metric)`

### Requirement: UI solaire lecture seule sur les deux frontends
Le plugin SHALL fournir un descripteur UI (tuile « Solaire » flux instantané + page détail historique) rendu par le renderer générique partagé. L'UI MUST être lecture seule et MUST NOT déclencher aucune mutation armoire.

#### Scenario: Tuile identique LAN et cloud
- **WHEN** la tuile Solaire est rendue sur le frontend LAN et sur le portail cloud
- **THEN** elle affiche les mêmes métriques via le même composant partagé

#### Scenario: Zéro mutation armoire
- **WHEN** l'UtIlisateur interagit avec l'UI Solaire
- **THEN** aucune requête de mutation armoire n'est émise et le test no-armoire passe

### Requirement: Résilience à la perte du collecteur
Quand le collecteur ne publie plus (heartbeat expiré), le plugin SHALL servir la dernière valeur connue depuis Redis en la marquant `stale`, sans échec dur de l'UI.

#### Scenario: Onduleur/collecteur injoignable
- **WHEN** le collecteur cesse de publier au-delà du seuil de heartbeat
- **THEN** l'API renvoie la dernière valeur avec `stale: true` et l'UI l'indique visuellement

### Requirement: Indisponibilité en armoire seule WAN
Le plugin `sungrow-solar` étant device-LAN, il MUST être déclaré indisponible en périmètre « armoire seule WAN » et l'UI MUST l'expliquer sans tenter d'accès device.

#### Scenario: Périmètre sans backend LAN
- **WHEN** l'installation est en « armoire seule WAN »
- **THEN** la tuile Solaire affiche un message d'indisponibilité et aucun collecteur n'est démarré
