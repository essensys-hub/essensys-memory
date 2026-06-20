# hal-home-intercom

> Monorepo de référence du système d'interphone vocal HAL : orchestrateur FastAPI + routeur MQTT + clients STT/TTS/intent, firmware ESP32, et une stack Docker Compose réunissant Mosquitto, Whisper, Piper et OpenClaw — le tout *local-first* sur le LAN.

**Catégorie :** Home Assistant / HAL
**Stack :** Python 3 / FastAPI / Pydantic / paho-mqtt / httpx (serveur) ; C++ Arduino + PlatformIO (ESP32) ; Docker Compose ; Mosquitto, whisper.cpp, Piper, OpenClaw
**Statut :** Implémentation fonctionnelle (POC avancé), testée (pytest) — déploiement LAN-only

## Rôle dans l'architecture Essensys

`hal-home-intercom` est le **dépôt monolithique qui implémente concrètement la plateforme HAL** décrite par `hal-architecture`/`hal-docs`. Là où le dossier `hal-home-assitant` éclate HAL en dépôts séparés (architecture, docs, firmware, services…), ce dépôt **regroupe tout le système en un seul endroit exécutable** : serveur d'orchestration, firmware ESP32, services IA conteneurisés et documentation.

C'est un système d'**interphone domestique distribué piloté à la voix** : un utilisateur appuie sur un bouton dans une pièce, parle (« HAL appelle les enfants », « HAL parle à la cuisine »), et l'orchestrateur transcrit (Whisper), interprète l'intention (OpenClaw ou règles locales), synthétise une réponse (Piper) et la joue sur le bon nœud via MQTT.

**Lien avec Essensys :** comme l'ensemble HAL, ce dépôt relève d'un **projet connexe distinct du cœur Essensys** (organisation GitHub `hal-home-assitant`). Il ne pilote pas les boards/équipements Essensys et ne parle pas au backend Essensys. Il partage le contexte « maison domotisée » et le matériel (ESP32, Mosquitto, cluster local) mais constitue la **couche voix/intercom** complémentaire — l'intégration avec Home Assistant / Essensys est listée comme une évolution future, non implémentée.

## Stack technique & dépendances

- **Serveur (`server/`)** : Python, **FastAPI** (API + service de fichiers média statiques), **Pydantic / pydantic-settings** (modèles & config par `.env`), **paho-mqtt** (routeur MQTT), **httpx** (appels async aux services IA). Tests **pytest**.
- **Firmware (`esp32/firmware/`)** : C++ Arduino, **PlatformIO** (`board = esp32dev`), libs MQTT/JSON/audio (PubSubClient, ArduinoJson, ESP8266Audio).
- **Services IA (conteneurs)** : wrappers FastAPI minces autour de **whisper.cpp** (STT), **Piper** (TTS) et **OpenClaw** (intent, avec repli déterministe).
- **Infra** : **Docker Compose**, broker **Mosquitto**.

## Structure du dépôt (et sous-projets éventuels)

```
hal-home-intercom/
├── README.md / .env.example          # config globale (MQTT, ports, modèles, URLs services)
├── server/                           # orchestrateur FastAPI
│   ├── main.py                       # app FastAPI, handler MQTT, endpoints
│   ├── config.py                     # Settings (pydantic) + topics dérivés (racine "home")
│   ├── models.py                     # schémas (sessions audio, intents, playback…)
│   ├── mqtt_router.py                # connexion/reconnexion + routage MQTT
│   ├── audio_store.py                # bufferisation des sessions PCM -> WAV sur disque
│   ├── speech_to_text.py / tts_engine.py   # clients HTTP Whisper / Piper
│   ├── intent_parser.py              # OpenClaw + parser à règles (alias de pièces)
│   ├── services/                     # bridge_service, command_service, message_service
│   └── tests/test_intent_parser.py   # tests unitaires
├── esp32/firmware/                   # firmware nœud (main.cpp, AudioPipeline, MqttGateway…)
├── docker/                           # stack runtime
│   ├── docker-compose.yml            # mosquitto, whisper, piper, openclaw, orchestrator
│   ├── mosquitto/ (Dockerfile, mosquitto.conf, passwd)
│   ├── whisper/ (Dockerfile, app.py, requirements)   # wrapper whisper.cpp
│   ├── piper/   (Dockerfile, app.py, requirements)   # wrapper Piper
│   ├── openclaw/(Dockerfile, app.py, requirements)   # wrapper intent
│   └── orchestrator/Dockerfile
└── docs/
    ├── architecture.md   # composants + flux (command / talk / fiabilité)
    ├── mqtt_spec.md      # contrat MQTT (topics, payloads, QoS)
    ├── setup.md          # mise en route
    └── wiring.md         # câblage ESP32 (INMP441, MAX98357A, GPIO)
```

Trois « sous-projets » logiques : **serveur** (Python), **firmware** (ESP32), **infra Docker** ; plus la doc.

### Système d'interphone — fonctionnement

- **Flux commande vocale** : bouton → `home/voice/session/start` → stream PCM sur `home/voice/audio/{session_id}` → `home/voice/session/stop` → l'orchestrateur écrit un WAV (`audio_store`) → Whisper transcrit → `intent_parser` (OpenClaw, sinon règles) → Piper synthétise → commande de lecture publiée sur `home/audio/play` / `home/intercom/room/{room}` / `home/intercom/broadcast` → le nœud cible récupère et joue le WAV.
- **Talk mode (interphone live)** : « HAL talk to kitchen » crée une *bridge session* ; la pièce source reçoit `talk_mode`, la cible `listen_mode` ; l'orchestrateur réachemine les frames PCM vers `home/audio/stream/room/{target}/{session}` que le nœud cible joue directement.
- **Messages différés** : intent `leave_message` → message stocké par pièce (en mémoire) → drainé/joué ultérieurement (`play_messages/{room}`).
- **Intents** : `intent_parser.py` normalise le texte, tente OpenClaw (`POST /intent`), et retombe sur un parser à règles avec **alias de pièces** (`kids/child → children`, `living → living_room`, etc.).

## Build / Exécution / Déploiement

1. `cp .env.example .env` puis ajuster WiFi, MQTT, chemins des modèles.
2. Créer le fichier de mots de passe Mosquitto :
   `mosquitto_passwd -c docker/mosquitto/passwd hal`.
3. Démarrer la stack : `cd docker && docker compose up --build`.
   - Services exposés : Mosquitto `1883`, Whisper `9001`, Piper `9002`, OpenClaw `9003`, orchestrateur `8080`.
   - Volumes : modèles `../models/{whisper,piper}`, runtime, et média `../server/media` → `/app/media`.
4. Flasher un nœud ESP32 avec les valeurs de `esp32/firmware/include/Config.h`.
5. API orchestrateur : `http://localhost:8080/docs` (Swagger FastAPI).

**Validation** : syntaxe `python3 -m compileall server docker` ; tests `python3 -m pytest server/tests`.

## Intégrations (Home Assistant, ESP32, MQTT, backend...)

- **MQTT (Mosquitto)** : bus central, racine de topics `home` (configurable via `MQTT_ROOT_TOPIC`), auth user/password (`hal`). Topics de contrôle en QoS 1, flux PCM en QoS 0. PCM : 16 bit little-endian, mono, 16 kHz.
- **ESP32** : nœuds thin (capture I2S, lecture WAV HTTP, OTA, reconnexion WiFi/MQTT). Matériel : micro **INMP441** (I2S RX, GPIO26/25/33), ampli **MAX98357A** (I2S TX, GPIO27/14/22), bouton GPIO0, LED GPIO2 (cf. `docs/wiring.md`).
- **Whisper** (`docker/whisper/app.py`) : wrapper HTTP `/healthz` + `/transcribe` exécutant `whisper-cli` (whisper.cpp) sur le WAV uploadé (modèle `ggml-base.en.bin`).
- **Piper** : wrapper HTTP `/synthesize` → WAV (voix par défaut `en_US-lessac-medium`).
- **OpenClaw** : endpoint `/intent` ; peut proxifier un OpenClaw réel (`OPENCLAW_UPSTREAM_URL`) ou retomber sur un parsing déterministe.
- **Orchestrateur** : sert les WAV générés (`/media`, `MEDIA_BASE_URL`) que les nœuds récupèrent en HTTP.
- **Home Assistant / backend Essensys** : aucune intégration directe à ce stade.

## Points d'attention

- **Recouvrement avec `hal-home-assitant`** : ce monorepo et la version éclatée en dépôts (`hal-architecture`, `hal-esp32-node-firmware`, `hal-orchestrator`, services…) couvrent le même système. Deux copies du firmware coexistent (`esp32/firmware/` ici vs `hal-esp32-node-firmware`). Définir la source de vérité pour éviter la dérive.
- **Orientation langue EN** : modèle Whisper `base.en`, voix Piper `en_US`, intents et alias en anglais — à adapter pour un usage francophone.
- **Sécurité (POC home-lab)** : réseau de confiance supposé, broker MQTT en user/password partagé, ports services exposés sur l'hôte, pas d'authentification sur l'API orchestrateur. Le fichier `passwd` Mosquitto et le `.env` (défaut `change-me`) sont à durcir hors dev.
- **État en mémoire** : files de messages par pièce et registrations de bridge sont volatiles (perte au redémarrage de l'orchestrateur).
- **Dépendances binaires** : les conteneurs Whisper/Piper attendent les binaires/modèles montés en volume ; le wrapper Whisper renvoie 503 si `whisper-cli` est absent. Prévoir le téléchargement des modèles (`models/whisper`, `models/piper`).
- **Fiabilité** : reconnexion MQTT avec backoff côté orchestrateur, reconnexion WiFi/MQTT à chaque passe de boucle côté ESP32 ; les sessions audio sont écrites sur disque avant STT (rejouables/déboguables).
- **README et scripts** utilisent des chemins absolus locaux (`/Users/nrineau/ESSENSYS/hal-home-intercom/...`) — peu portables, à généraliser pour un autre poste.
