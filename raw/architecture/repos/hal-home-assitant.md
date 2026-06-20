# hal-home-assitant

> Méta-dépôt (workspace local) regroupant les briques de la plateforme HAL — un système d'interphone vocal domestique distribué basé sur des nœuds ESP32, MQTT et des services IA locaux (Whisper/Piper/OpenClaw) ; on y documente ici ses trois sous-projets de référence : `hal-architecture`, `hal-docs` et `hal-esp32-node-firmware`.

**Catégorie :** Home Assistant / HAL
**Stack :** Documentation Markdown + diagrammes Mermaid (architecture/docs) ; firmware C++ ESP32 (Arduino / PlatformIO) ; services Python FastAPI hébergés ailleurs (Whisper, Piper, OpenClaw, orchestrateur)
**Statut :** POC / home-lab actif — déploiement LAN-only, cible de migration vers un cluster Turing Pi 2

## Rôle dans l'architecture Essensys

`hal-home-assitant` n'est pas un dépôt unique mais un **dossier de travail local** réunissant plusieurs dépôts Git distincts de la plateforme **HAL** (organisation GitHub `hal-home-assitant`, ex. `git@github.com:hal-home-assitant/hal-architecture.git`). HAL est un projet d'**interphone vocal domestique** (« HAL appelle la cuisine », « HAL annonce le dîner », « HAL parle à la cuisine ») conçu *local-first* : tous les flux cœur tournent sur le LAN, sans dépendance cloud.

**Lien avec Essensys :** HAL est un projet **connexe mais distinct** du cœur Essensys. Il vit dans une autre organisation GitHub (`hal-home-assitant` vs `essensys-hub`), avec sa propre stack (ESP32 audio + MQTT + IA vocale) sans rapport direct avec le pilotage des boards Essensys. Il partage néanmoins le même contexte « maison domotisée » et le même type de matériel (ESP32, Mosquitto, Raspberry/cluster local). À ce stade, **aucune intégration directe HAL ↔ backend Essensys n'est implémentée** : la doc d'architecture HAL liste explicitement Home Assistant comme une intégration *future*. HAL constitue donc la **couche « voix / intercom »** de l'écosystème domotique de l'auteur, complémentaire de la couche « pilotage équipements » couverte par `essensys-homeassitant` et le backend Essensys.

Le dossier contient aussi d'autres dépôts HAL non couverts ici (`hal-orchestrator`, `hal-whisper-service`, `hal-piper-service`, `hal-openclaw-adapter`, `hal-infra-docker`, plus des dossiers `voix`, `hal-piper-service`, `hal-whisper-service`). Le code applicatif complet et fonctionnel de l'interphone se trouve par ailleurs dans le dépôt sœur **`hal-home-intercom`** (monorepo server + esp32 + docker).

## Stack technique & dépendances

- **`hal-architecture`** : Markdown + diagrammes **Mermaid** (`.mmd`), assets Fritzing/photos. Aucune dépendance exécutable.
- **`hal-docs`** : Markdown pur (architecture, spec MQTT, setup, wiring).
- **`hal-esp32-node-firmware`** : **C++ Arduino** compilé via **PlatformIO** (`platform = espressif32`, `board = esp32dev`). Libs : `ArduinoJson@^7.3.1`, `PubSubClient@^2.8` (MQTT), `ESP8266Audio@^1.9.7` (lecture audio). Environnement Python `.venv` embarqué pour PlatformIO.
- **Services référencés (hébergés dans d'autres dépôts)** : FastAPI (orchestrateur), `whisper.cpp` (STT), Piper (TTS), OpenClaw (intent), Mosquitto (broker MQTT).
- **Cible d'infra** : cluster **Turing Pi 2** à `192.168.0.37` pour l'IA et l'orchestration ; Mac mini comme poste opérateur / UI de contrôle local.

## Structure du dépôt (et sous-projets éventuels)

### Sous-projet 1 — `hal-architecture` (source de vérité système)

Référentiel d'architecture de la plateforme HAL.

```
hal-architecture/
├── README.md                 # carte du dépôt + ordre de lecture
├── adr/
│   ├── 0001-repository-boundaries.md   # ADR : découpage multi-dépôts (Accepté)
│   └── 0002-local-first-runtime.md     # ADR : runtime local-first (Accepté)
├── docs/
│   ├── system-overview.md    # mission, principes, cas d'usage, contraintes
│   ├── repository-map.md     # rôle de chaque dépôt HAL (ownership)
│   ├── runtime-topology.md   # nœuds, ports, réseau, stockage, cible Turing Pi 2
│   ├── control-flows.md      # flux voix/broadcast/call/talk/deferred
│   ├── hardware-node-diagrams.md / first-esp-wroom-32-test-node.md / fritzing-esp32-audio-node.md
│   ├── security-model.md     # frontières de confiance, secrets, LAN
│   ├── operations.md / scaling-roadmap.md
│   └── assets/               # SVG/PNG Fritzing, photos du nœud de test
└── diagrams/*.mmd            # diagrammes Mermaid (platform-context, audio-bus, séquences…)
```

Contenu clé : trois domaines runtime (Edge audio / Core control / AI processing), contraintes (latence MQTT < 300 ms, retour d'annonce < 1 s à modèles chauds, 10+ pièces visées), et une feuille de route de migration vers le cluster Turing Pi 2.

### Sous-projet 2 — `hal-docs` (documentation opérateur)

```
hal-docs/
├── README.md
├── architecture.md   # vue composants + flux (command/talk)
├── mqtt_spec.md      # contrat MQTT (topics, payloads, QoS)
├── setup.md          # mise en route
└── wiring.md         # câblage ESP32 (micro INMP441, ampli MAX98357A)
```

C'est la doc « implémentation/opération » (par opposition à `hal-architecture` qui porte la gouvernance et les décisions). La **spec MQTT** y est précise : topics sous racine `home/`, payloads JSON pour le contrôle de session, frames PCM binaires 16 bit mono 16 kHz, QoS 1 pour le contrôle et QoS 0 pour les flux PCM.

### Sous-projet 3 — `hal-esp32-node-firmware` (firmware nœud de pièce)

```
hal-esp32-node-firmware/
├── README.md
├── platformio.ini            # esp32dev, arduino, lib_deps (ArduinoJson, PubSubClient, ESP8266Audio)
├── .env.example / .env.home.nodeXXX / .env.fablab.nodeXXX   # config par nœud (WiFi/MQTT/services/room)
├── include/Config.h.example  # défauts compilés (HAL_* defines) ; Config.h réel ignoré par git
├── scripts/load_env.py       # injecte le .env dans les build_flags PlatformIO
├── stitch-import/            # maquette HTML/PNG de l'UI web
└── src/
    ├── main.cpp              (~751 l.) boucle principale, OTA, sessions, talk mode
    ├── AudioPipeline.{h,cpp} (~406 l.) capture I2S micro / lecture HTTP WAV
    ├── MqttGateway.{h,cpp}   client MQTT (PubSubClient)
    ├── NodeWebUi.{h,cpp}     (~822 l.) page web embarquée (port 80) par nœud
    └── StatusLog.{h,cpp}     journal runtime
```

Firmware d'un **nœud de pièce** : connexion WiFi + MQTT avec reconnexion, capture micro I2S, lecture WAV via HTTP, push-to-talk, talk bridge, OTA Arduino, et une **UI web locale** par nœud (état WiFi/RSSI, MQTT, session/talk, santé des services orchestrator/whisper/piper/openclaw, logs récents). La configuration par nœud passe par des fichiers `.env` (un par site/pièce, ex. `node001` = `CHAMBRE_NICO`) injectés à la compilation.

## Build / Exécution / Déploiement

- **`hal-architecture` / `hal-docs`** : pas de build. Documentation lue directement ; les `.mmd` se rendent avec n'importe quel viewer Mermaid.
- **`hal-esp32-node-firmware`** :
  1. Renseigner `.env` (ou réutiliser un `.env.home.nodeXXX`) : `WIFI_*`, `MQTT_*`, `SERVICE_HOST` + ports services, `NODE_ID`, `ROOM_NAME`.
  2. `scripts/load_env.py` (extra_script PlatformIO) convertit le `.env` en `build_flags`.
  3. Compiler/flasher : `pio run` → `pio run --target upload` → `pio device monitor`.
  4. Accéder à l'UI du nœud sur `http://<esp32-ip>/`.
- **Déploiement plateforme** : services IA + orchestrateur + broker via Docker (cf. `hal-infra-docker` / `hal-home-intercom`), cible cluster Turing Pi 2 `192.168.0.37` ; nœuds ESP32 sur le même LAN WiFi pointant vers les services du cluster.

## Intégrations (Home Assistant, ESP32, MQTT, backend...)

- **ESP32 ↔ MQTT (Mosquitto)** : port `1883`, auth user/password (`hal`/…). Topics sous `home/` : `voice/session/start|stop` (JSON), `voice/audio/{session_id}` (PCM binaire 16 kHz mono), `audio/play` (commande `play_url`/`talk_mode`/`listen_mode`), `intercom/broadcast`, `intercom/room/{room}`, `audio/stream/room/{room}/{session_id}` (PCM talk mode).
- **ESP32 ↔ services HTTP** : santé orchestrator (8080), whisper (9001), piper (9002), openclaw (9003) ; lecture des WAV servis par l'orchestrateur.
- **Orchestrateur ↔ IA** : Whisper (`/transcribe`), Piper (`/synthesize`), OpenClaw (`/intent`) — voir `hal-home-intercom` pour l'implémentation.
- **Matériel** : micro I2S INMP441, ampli I2S MAX98357A + haut-parleur 3W, bouton (GPIO0), LED (GPIO2). Câblage détaillé dans `hal-docs/wiring.md` et `hal-architecture/docs/hardware-node-diagrams.md`.
- **Home Assistant** : cité comme **intégration future** dans la doc d'architecture — non implémenté à ce stade. (Le pont HA ↔ équipements existe côté Essensys, dépôt `essensys-homeassitant`, mais indépendamment de HAL.)

## Points d'attention

- **Dossier ≠ dépôt unique** : `hal-home-assitant` est un workspace local agrégeant plusieurs dépôts Git indépendants (organisation `hal-home-assitant`). Chaque sous-projet a son propre cycle de vie ; l'ADR 0001 assume ce découpage multi-dépôts (cadences firmware/IA/infra différentes).
- **Redondance avec `hal-home-intercom`** : l'implémentation complète et exécutable (server FastAPI + firmware + docker) vit dans le dépôt sœur `hal-home-intercom`. Risque de divergence entre le firmware de `hal-esp32-node-firmware` et celui embarqué dans `hal-home-intercom/esp32/firmware`. Clarifier lequel fait foi.
- **Maturité POC** : déploiement LAN-only, modèle de sécurité minimal (réseau de confiance, auth MQTT user/password partagée, UI nœud sans authentification sur port 80). Pistes recommandées par la doc : credentials MQTT par appareil, certificats clients, bind loopback de l'UI, registre d'enrôlement.
- **Cible d'infra mouvante** : migration en cours du Mac mini vers le cluster Turing Pi 2 (`192.168.0.37`) ; les ports/IP sont codés dans les `.env` et la doc, à maintenir cohérents.
- **Secrets** : `Config.h` et `.env` réels sont (volontairement) ignorés par git ; seuls les `.example` et des `.env.home/fablab.nodeXXX` (potentiellement avec mots de passe par défaut `change-me`) sont versionnés — vérifier qu'aucun secret réel n'a fuité.
- **Anglais vs français** : la doc et le code HAL sont en anglais et orientés langue EN (`en_US-lessac-medium`, intents « call the children »…), alors que le parc Essensys est francophone — point à anticiper pour une éventuelle convergence.
