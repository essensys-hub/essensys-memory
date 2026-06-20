---
tags: [entity, repo, modern]
sources: [hal-home-intercom.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: hal-home-intercom
---

# HAL Home Intercom

> Monorepo de référence du système d'interphone vocal HAL : orchestrateur FastAPI + routeur MQTT + clients STT/TTS/intent, firmware ESP32, et une stack Docker Compose réunissant Mosquitto, Whisper, Piper et OpenClaw — le tout *local-first* sur le LAN.

| | |
|---|---|
| **Catégorie** | Home Assistant / HAL |
| **Stack** | Python 3 / FastAPI / Pydantic / paho-mqtt / httpx (serveur) ; C++ Arduino + PlatformIO (ESP32) ; Docker Compose ; Mosquitto, whisper.cpp, Piper, OpenClaw |
| **Statut** | Implémentation fonctionnelle (POC avancé), testée (pytest) — déploiement LAN-only |
| **Era** | modern |

## Rôle

`hal-home-intercom` est le **dépôt monolithique qui implémente concrètement la plateforme HAL** décrite par `hal-architecture`/`hal-docs`. Là où le dossier `hal-home-assitant` éclate HAL en dépôts séparés (architecture, docs, firmware, services…), ce dépôt **regroupe tout le système en un seul endroit exécutable** : serveur d'orchestration, firmware ESP32, services IA conteneurisés et documentation.

C'est un système d'**interphone domestique distribué piloté à la voix** : un utilisateur appuie sur un bouton dans une pièce, parle (« HAL appelle les enfants », « HAL parle à la cuisine »), et l'orchestrateur transcrit (Whisper), interprète l'intention (OpenClaw ou règles locales), synthétise une réponse (Piper) et la joue sur le bon nœud via MQTT.

**Lien avec Essensys :** comme l'ensemble HAL, ce dépôt relève d'un **projet connexe distinct du cœur Essensys** (organisation GitHub `hal-home-assitant`). Il ne pilote pas les boards/équipements Essensys et ne parle pas au backend Essensys. Il partage le contexte « maison domotisée » et le matériel (ESP32, Mosquitto, cluster local) mais constitue la **couche voix/intercom** complémentaire — l'intégration avec Home Assistant / Essensys est listée comme une évolution future, non implémentée.

## Intégrations

_Non documenté._

## Structure

_Voir dépôt source._

## Points d'attention

- **Recouvrement avec `hal-home-assitant`** : ce monorepo et la version éclatée en dépôts (`hal-architecture`, `hal-esp32-node-firmware`, `hal-orchestrator`, services…) couvrent le même système. Deux copies du firmware coexistent (`esp32/firmware/` ici vs `hal-esp32-node-firmware`). Définir la source de vérité pour éviter la dérive.
- **Orientation langue EN** : modèle Whisper `base.en`, voix Piper `en_US`, intents et alias en anglais — à adapter pour un usage francophone.
- **Sécurité (POC home-lab)** : réseau de confiance supposé, broker MQTT en user/password partagé, ports services exposés sur l'hôte, pas d'authentification sur l'API orchestrateur. Le fichier `passwd` Mosquitto et le `.env` (défaut `change-me`) sont à durcir hors dev.
- **État en mémoire** : files de messages par pièce et registrations de bridge sont volatiles (perte au redémarrage de l'orchestrateur).
- **Dépendances binaires** : les conteneurs Whisper/Piper attendent les binaires/modèles montés en volume ; le wrapper Whisper renvoie 503 si `whisper-cli` est absent. Prévoir le téléchargement des modèles (`models/whisper`, `models/piper`).
- **Fiabilité** : reconnexion MQTT avec backoff côté orchestrateur, recon

_… voir source complète dans raw/_

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/hal-home-intercom.md`
