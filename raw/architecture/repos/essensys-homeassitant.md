# essensys-homeassitant

> Intégration personnalisée (custom component) Home Assistant qui expose les équipements domotiques Essensys (éclairages, volets, chauffage) en tant qu'entités HA, en pilotant le backend Essensys via son API d'injection d'actions.

**Catégorie :** Home Assistant / HAL
**Stack :** Python (custom component Home Assistant), `requests`, `voluptuous` ; configuration YAML
**Statut :** Fonctionnel mais minimaliste (v1.2.0) — pilotage en aller simple, sans remontée d'état réelle

## Rôle dans l'architecture Essensys

Ce dépôt est le **pont entre Home Assistant et la plateforme Essensys**. Il permet à un utilisateur de Home Assistant de contrôler les équipements d'un site Essensys (maison domotisée) comme s'il s'agissait d'entités HA natives, et donc de bénéficier de l'écosystème HA : tableaux de bord, automatisations, assistants vocaux, scènes, etc.

Concrètement, l'intégration traduit les commandes Home Assistant (allumer une lumière, fermer un volet, changer un mode de chauffage) en **actions Essensys au format `{"k": index, "v": value}`** et les envoie au backend Essensys (`essensys-server-backend`) via l'endpoint d'injection `POST /api/admin/inject`. C'est exactement le même format clé/valeur (`k`/`v`) que celui utilisé dans le reste de l'écosystème Essensys pour piloter les boards/automates.

Le dépôt appartient à l'organisation GitHub `essensys-hub` (remote `git@github.com:essensys-hub/essensys-homeassitant.git`) : il fait donc partie du cœur Essensys, et non de la plateforme HAL (interphone vocal) qui est hébergée sous l'organisation `hal-home-assitant`.

## Stack technique & dépendances

- **Langage :** Python (runtime Home Assistant).
- **Type :** `custom_components` Home Assistant chargé via `configuration.yaml`.
- **Dépendances déclarées dans `manifest.json` :** aucune (`requirements: []`). Le code utilise `requests` (présent dans l'environnement HA) pour les appels HTTP et `voluptuous` / `homeassistant.helpers.config_validation` pour valider la configuration.
- **`config_flow: false`** : pas d'interface de configuration graphique ; la configuration se fait exclusivement en YAML.
- Plateformes HA implémentées : `light`, `cover`, `select` (plus un service `essensys.send_action`).

## Structure du dépôt (et sous-projets éventuels)

```
.
├── README.md                         # une ligne (titre uniquement)
└── custom_components/essensys/
    ├── __init__.py                   # setup du composant, service send_action, chargement des plateformes
    ├── manifest.json                 # domain "essensys", version 1.2.0, config_flow false
    ├── light.py                      # entités Light (paires ON/OFF)
    ├── cover.py                      # entités Cover (volets/stores : open/close/stop)
    ├── select.py                     # entités Select (modes de chauffage)
    ├── services.yaml                 # déclaration du service send_action (index + value)
    └── table_reference.json          # table de référence des équipements et de leurs codes
```

Pas de sous-projet : un unique composant Home Assistant.

Le fichier **`table_reference.json`** est central : il contient les `entries` décrivant chaque équipement (`zone`, `piece`, `categorie`, `keys`, `value`, `attribute`, `shortDescription`, `longDescription`). C'est à partir de cette table (et non d'une découverte dynamique) que les entités HA sont générées au démarrage. Exemple d'entrée : zone « Chauffage Zone Nuit », catégorie `Chauffage`, key `350`, valeurs `1`/`17`/`32` correspondant aux modes (Automatique, Forçage confort, Anticipé…).

## Build / Exécution / Déploiement

Pas de build (composant Python interprété). Déploiement classique d'un custom component :

1. Copier le dossier `custom_components/essensys/` dans le répertoire `config/custom_components/` de l'instance Home Assistant.
2. Déclarer le composant dans `configuration.yaml` :
   ```yaml
   essensys:
     backend_url: "http://localhost:7070"
   ```
   `backend_url` est paramétrable (défaut `http://localhost:7070`) ; le slash final est retiré et l'URL d'injection devient `<backend_url>/api/admin/inject`.
3. Redémarrer Home Assistant : `setup()` enregistre le service `send_action` puis charge les plateformes `light`, `cover` et `select`.

## Intégrations (Home Assistant, ESP32, MQTT, backend...)

- **Home Assistant :** trois plateformes d'entités générées depuis `table_reference.json` :
  - **`light.py`** — regroupe les entrées par `shortDescription` et crée une entité Light pour chaque paire détectée ON/OFF (heuristiques sur l'attribut : `on/allumé/open` vs `off/eteint/close`). Mode couleur `ONOFF` uniquement.
  - **`cover.py`** — filtre les catégories contenant « Volets »/« store », crée une entité Cover par paire open/close (+ stop optionnel). `device_class` `SHUTTER`, ou `AWNING` si « store » dans le nom.
  - **`select.py`** — filtre la catégorie `Chauffage`, crée un sélecteur de mode dont les options sont les `attribute` (« Forçage confort », « OFF »…), icône `mdi:radiator`.
- **Service `essensys.send_action`** : permet d'envoyer manuellement une action arbitraire (`index` = key 0–65535, `value` = texte) — utile pour automatisations et débogage.
- **Backend Essensys :** toutes les commandes aboutissent à `POST <backend_url>/api/admin/inject` avec un payload `[{"k": <int>, "v": "<str>"}]` (timeout 5 s). Cet endpoint est servi par `essensys-server-backend` (handlers dans `internal/api/`).
- **Pas de MQTT, pas d'ESP32 :** l'intégration parle uniquement HTTP au backend Essensys ; elle n'a aucun lien avec la plateforme vocale HAL (ESP32 / MQTT).

## Points d'attention

- **Pilotage en aller simple, aucune remontée d'état réelle.** Les entités supposent leur état après commande (`_is_on`, `_attr_is_closed`, `_attr_current_option` mis à jour localement). Il n'existe pas de polling ni de feedback depuis le backend : l'état affiché dans HA peut diverger de la réalité physique. Les volets et sélecteurs démarrent à l'état « inconnu ».
- **Configuration figée :** les entités sont construites au démarrage à partir de `table_reference.json`. Toute modification du parc d'équipements impose de mettre à jour ce fichier et de redémarrer HA. Pas de découverte dynamique.
- **Heuristiques fragiles dans `light.py`** : l'attribut `open` est détecté comme « ON » alors qu'il relève sémantiquement d'un volet (le code le commente lui-même). Un équipement peut donc apparaître à la fois côté Light et côté Cover selon sa catégorie/attribut.
- **Sécurité :** appel HTTP non authentifié vers `/api/admin/inject` (endpoint « admin »). À cantonner à un réseau de confiance ; pas de gestion de credentials/token côté intégration.
- **`config_flow: false`** : pas d'UI de configuration, tout passe par le YAML — moins ergonomique que les intégrations HA modernes.
- **README quasi vide** (une ligne) : la connaissance du fonctionnement repose entièrement sur le code et `table_reference.json`.
- **Robustesse :** les appels `requests.post` sont synchrones dans le thread HA ; en cas de backend lent/indisponible, le timeout de 5 s peut impacter la réactivité. Les erreurs sont seulement journalisées.
