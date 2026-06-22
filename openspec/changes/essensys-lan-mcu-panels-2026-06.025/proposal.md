## Why

Les installateurs et utilisateurs avancés veulent des **boutons physiques** bon marché (ESP32, Raspberry Pi Pico W) pour déclencher des **scénarios** et piloter le **chauffage** sans ouvrir l'app — comme un interrupteur mural dédié. Aujourd'hui seuls les clients Essensys (firmware SC944D, apps, web) pilotent la table d'échange ; il n'existe pas de couche **MCU LAN** enrôlée et mappée aux scénarios.

> **Roadmap ID:** 2026-06.025  
> **Horizon:** voir [[OpenSpec Queue 2026 06]]  
> **Depend de:** 013

## What Changes

- Support **ESP32** et **Raspberry Pi Pico (W)** comme panneaux boutons LAN.
- Association bouton → **scénario** (launch) ou **action chauffage** (modes / consigne / planning simplifié).
- **Uniquement réseau local** : `*.local`, IP LAN gateway — **aucune exposition WAN** ni cloud.
- Enrôlement et auth via **trusted devices** (change 013).
- UI admin (dashboard) : ajouter / configurer / révoquer un panneau MCU.
- Firmware de référence + doc install (PlatformIO / MicroPython ou C SDK).

## Capabilities

### New Capabilities

- `lan-mcu-panels` : enrollment LAN, mapping boutons, API scénario/chauffage, firmware ref, contrainte `.local` only.

## Impact

- `essensys-server-backend` — API LAN MCU, validation trusted device, launch scénario / indices chauffage
- `essensys-server-frontend` — écran configuration panneaux et mappings
- `essensys-raspberry-gateway` ou nouveau dépôt `essensys-board-mcu-lan` — firmware ESP32 / Pico
- `essensys-memory` — concept wiki, doc install
- **Non** : portail cloud `/portal/`, MQTT WAN, modification protocole legacy firmware SC944D

## Non-goals

- Panneaux accessibles depuis Internet ou via hub cloud.
- Remplacement des cartes Essensys SC940–SC947.
- Voix / intercom HAL (projet connexe ESP32 audio).
- Chauffage avancé type éditeur planning complet sur l'écran MCU (MVP : actions prédéfinies).

## Gate

Ne pas demarrer implementation tant que **2026-06.013** (trusted devices) n'est pas **completed** — l'enrôlement MCU réutilise le même modèle d'appareil de confiance LAN.
