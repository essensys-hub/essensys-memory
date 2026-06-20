---
tags: [entity, repo, modern]
sources: [hal-home-assitant.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: hal-home-assitant
---

# HAL Home Assitant

> Méta-dépôt (workspace local) regroupant les briques de la plateforme HAL — un système d'interphone vocal domestique distribué basé sur des nœuds ESP32, MQTT et des services IA locaux (Whisper/Piper/OpenClaw) ; on y documente ici ses trois sous-projets de référence : `hal-architecture`, `hal-docs` et `hal-esp32-node-firmware`.

| | |
|---|---|
| **Catégorie** | Home Assistant / HAL |
| **Stack** | Documentation Markdown + diagrammes Mermaid (architecture/docs) ; firmware C++ ESP32 (Arduino / PlatformIO) ; services Python FastAPI hébergés ailleurs (Whisper, Piper, OpenClaw, orchestrateur) |
| **Statut** | POC / home-lab actif — déploiement LAN-only, cible de migration vers un cluster Turing Pi 2 |
| **Era** | modern |

## Rôle

`hal-home-assitant` n'est pas un dépôt unique mais un **dossier de travail local** réunissant plusieurs dépôts Git distincts de la plateforme **HAL** (organisation GitHub `hal-home-assitant`, ex. `git@github.com:hal-home-assitant/hal-architecture.git`). HAL est un projet d'**interphone vocal domestique** (« HAL appelle la cuisine », « HAL annonce le dîner », « HAL parle à la cuisine ») conçu *local-first* : tous les flux cœur tournent sur le LAN, sans dépendance cloud.

**Lien avec Essensys :** HAL est un projet **connexe mais distinct** du cœur Essensys. Il vit dans une autre organisation GitHub (`hal-home-assitant` vs `essensys-hub`), avec sa propre stack (ESP32 audio + MQTT + IA vocale) sans rapport direct avec le pilotage des boards Essensys. Il partage néanmoins le même contexte « maison domotisée » et le même type de matériel (ESP32, Mosquitto, Raspberry/cluster local). À ce stade, **aucune intégration directe HAL ↔ backend Essensys n'est implémentée** : la doc d'architecture HAL liste explicitement Home Assistant comme une intégration *future*. HAL constitue donc la **couche « voix / intercom »** de l'écosystème domotique de l'auteur, complémentaire de la couche « pilotage équipements » couverte par `essensys-homeassitant` et le backend Essensys.

Le dossier contient aussi d'autres dépôts HAL non couverts ici (`hal-orchestrator`, `hal-whisper-service`, `hal-piper-service`, `hal-openclaw-adapter`, `hal-infra-docker`, plus des dossiers `voix`, `hal-piper-service`, `hal-w

_… voir source complète dans raw/_

## Intégrations

_Non documenté._

## Structure

_Voir dépôt source._

## Points d'attention

- **Dossier ≠ dépôt unique** : `hal-home-assitant` est un workspace local agrégeant plusieurs dépôts Git indépendants (organisation `hal-home-assitant`). Chaque sous-projet a son propre cycle de vie ; l'ADR 0001 assume ce découpage multi-dépôts (cadences firmware/IA/infra différentes).
- **Redondance avec `hal-home-intercom`** : l'implémentation complète et exécutable (server FastAPI + firmware + docker) vit dans le dépôt sœur `hal-home-intercom`. Risque de divergence entre le firmware de `hal-esp32-node-firmware` et celui embarqué dans `hal-home-intercom/esp32/firmware`. Clarifier lequel fait foi.
- **Maturité POC** : déploiement LAN-only, modèle de sécurité minimal (réseau de confiance, auth MQTT user/password partagée, UI nœud sans authentification sur port 80). Pistes recommandées par la doc : credentials MQTT par appareil, certificats clients, bind loopback de l'UI, registre d'enrôlement.
- **Cible d'infra mouvante** : migration en cours du Mac mini vers le cluster Turing Pi 2 (`192.168.0.37`) ; les ports/IP sont codés dans les `.env` et la doc, à maintenir cohérents.
- **Secrets** : `Config.h` et `.env` réels sont (volontairement) ignorés par git ; seuls les `.example` et des

_… voir source complète dans raw/_

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/hal-home-assitant.md`
