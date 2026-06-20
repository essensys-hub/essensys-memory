---
tags: [entity, repo, modern, infra]
sources: [essensys-mosquitto.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-mosquitto
---

# Essensys Mosquitto

> Broker MQTT (Eclipse Mosquitto) de la gateway Essensys, point d'echange temps reel entre les objets domotiques IoT et le backend.

| | |
|---|---|
| **Catégorie** | Infrastructure |
| **Stack** | Eclipse Mosquitto (Alpine `apk`), Docker (multi-arch arm64/amd64), image de base `essensyshub/essensys-base` |
| **Statut** | Actif |
| **Era** | modern |

## Rôle

Mosquitto est le bus de messages MQTT de la gateway. C'est le canal temps reel par lequel les equipements IoT/domotiques (cartes/boards Essensys, capteurs, actionneurs) publient leurs etats et recoivent leurs commandes, en interaction avec le backend Essensys. Il tourne dans la stack Docker de la gateway en `network_mode: host`.

## Intégrations

_Non documenté._

## Structure

_Voir dépôt source._

## Points d'attention

- `chmod -R 777 /mosquitto` dans le Dockerfile : permissions tres larges (simplifie le montage de volumes mais a surveiller cote securite).
- Listener `1883` en clair (pas de TLS) : acceptable car broker interne, mais ne doit pas etre expose hors du LAN.
- L'authentification depend du fichier `passwd` : il doit etre provisionne (via Ansible) sinon aucun client ne peut se connecter (`allow_anonymous false`).
- Port 1883 standard non chiffre ; pas de listener `8883` (MQTT/TLS) configure.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-mosquitto.md`
