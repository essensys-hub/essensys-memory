---
tags: [synthesis, platform, architecture]
sources: [README.md, architecture-readme.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
---

# Platform Overview

Essensys est une **solution domotique résidentielle** : alarme, chauffage, éclairage, volets, arrosage, cumulus, détection de fuite.

## Couches

1. **Armoire** — firmware cartes ([[Essensys Board SC944D]] maîtresse, esclaves [[Essensys Board SC940]] / [[Essensys Board SC941C]] / [[Essensys Board SC942C]], écran [[Essensys Board SC945D]], sirène [[Essensys Board SC946D]])
2. **Passerelle** — [[Essensys Raspberry Gateway]] (CM5/NixOS) ou legacy [[Client Essensys Legacy]] (BP_MQX_ETH)
3. **LAN** — [[Essensys Server Backend]] + [[Essensys Server Frontend]] + [[Essensys Redis]] + [[Essensys Mosquitto]] + [[Essensys Traefik]] + [[Essensys Nginx]]
4. **Cloud** — [[Essensys User Portal Backend]] + [[Essensys User Portal Frontend]] sur `mon.essensys.fr`

## Concepts clés

- [[Dual Protocol]] — legacy IoT vs REST moderne
- [[Table D Echange]] — contrat k/v armoire ↔ serveur
- [[Cloud Relay]] — pilotage distant NAT traversal
- [[Gateway Exchange]] — API sync passerelle ↔ hub
- [[Migration Legacy To Modern]] — ASP.NET/MQX → Go/React/Raspberry

## Mémoire projet

- [[Essensys Memory]] — ce vault (ESSENSYS-BRAIN)
- [[Roadmap OpenSpec]] — changes actifs
- Timeline Git : `wiki/timeline/<repo>.md` (38 dépôts)

## 40 dépôts

Index complet dans [[Index]] section Entities. Catégories :

| Couche | Exemples |
|--------|----------|
| Firmware | SC940–SC947, SC840/841 bancs test |
| Services LAN | server-backend/frontend, control-plane |
| Cloud | user-portal-*, support-site |
| Infra | ansible, traefik, nginx, redis, mosquitto |
| Legacy | client-essensys-legacy, essensys-web-legacy |
| Outillage | essensys-gcc, essensys-mcp, essensys-memory |
| HAL (connexe) | hal-home-intercom, hal-home-assitant |

## Sources

- [[Architecture README]]
- `raw/architecture/README.md`
