# Architecture Essensys — Documentation complète des dépôts

> Référentiel d'architecture de la plateforme domotique **Essensys** : du firmware des cartes électroniques jusqu'au cloud, en passant par les passerelles Raspberry, les services Go/React et l'infrastructure Docker.

Cette documentation a été générée à partir de l'exploration des **40 dépôts Git** présents dans `/Users/nrineau/ESSENSYS`. Chaque dépôt dispose d'une fiche détaillée dans [`repos/`](repos/). Ce document fournit la vue d'ensemble et les liens transverses.

---

## 1. Qu'est-ce qu'Essensys ?

Essensys est une **solution domotique résidentielle** (alarme, chauffage, éclairage/variateurs, volets, arrosage, chauffe-eau/cumulus, détection de fuite). Une installation type comprend :

- une **armoire** d'automatismes composée de plusieurs **cartes électroniques** propriétaires (firmware embarqué) reliées en **bus I²C** autour d'une carte maîtresse Ethernet ;
- une **passerelle** (historiquement le boîtier embarqué C/MQX, aujourd'hui un **Raspberry Pi / CM5**) qui relie l'armoire au réseau ;
- un **serveur central** (historiquement ASP.NET, aujourd'hui **Go + React**) accessible en local et via le **cloud** (`mon.essensys.fr`) ;
- des **clients** : interface web, applications mobiles iOS/Android, écran tactile mural, intégration Home Assistant.

Le projet est dans une phase de **migration** : remplacement du legacy .NET/SQL Server par une stack Go/React/PostgreSQL, et remplacement du boîtier embarqué C par une passerelle Raspberry containerisée. **La compatibilité avec le protocole legacy IoT est maintenue à 100 %.**

---

## 2. Vue en couches (C4 — niveau conteneurs)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                          CLOUD (OVH — mon.essensys.fr)                      │
│                                                                             │
│   essensys-user-portal-frontend ──► essensys-user-portal-backend           │
│        (SPA /portal/)                  (Go/chi, CONSOLIDATED_MODE)          │
│                                          │  PostgreSQL · JWT · New Relic    │
│   essensys-support-site (SPA + docs, backend Go déprécié) ─┘               │
│                                          ▲                                  │
│                                          │ polling sortant (NAT traversal)  │
└──────────────────────────────────────────┼─────────────────────────────────┘
                                            │ /api/gateway/exchange
                                            │ /api/gateway/pending-actions
┌───────────────────────────────────────────┼─────────────────────────────────┐
│                  SITE CLIENT (LAN) — Passerelle Raspberry Pi / CM5          │
│                                            │                                 │
│   essensys-traefik (TLS bordure) ─ essensys-nginx (web LAN :80)             │
│         │                                                                   │
│         ▼                                                                   │
│   essensys-server-backend (Go :7070) ◄──► essensys-server-frontend (React) │
│         │   ▲          ▲           ▲                                         │
│         │   │          │           │                                         │
│   essensys-redis   essensys-     essensys-control-plane (orchestration      │
│   (cache/bus)      mosquitto      flotte Docker, registre Redis, :9100)      │
│                    (MQTT :1883)                                              │
│         │                                                                   │
│         ▼ HTTP legacy (single-packet TCP, JSON malformé) / bus armoire      │
└─────────┼───────────────────────────────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────────────────────────────┐
│         ▼            ARMOIRE — Cartes électroniques (firmware)               │
│                                                                             │
│   SC944D (ColdFire MCF52259 / MQX, Ethernet) ── carte MAÎTRESSE             │
│     ├─ I²C ─► SC940 / SC941C / SC942C (PIC16F946, actionneurs esclaves)     │
│     ├─ RS-485/série ─► SC945D (écran tactile PICASO 4DGL)                   │
│     ├─ SC946D (sirène d'alarme PIC24F)                                       │
│     ├─ SC843D (gradateur/dimmer PIC12F1840)                                  │
│     └─ SC947-xB (détecteur de fuite d'eau PIC12F1840)                        │
│                                                                             │
│   Bancs de test usine : SC840B (Banc BA), SC841A (Banc BP) — dsPIC33        │
└───────────────────────────────────────────────────────────────────────────┘
```

> **Note legacy** : le boîtier C `client-essensys-legacy` (BP_MQX_ETH) joue *à la fois* le rôle de carte maîtresse et de passerelle dans les installations historiques. Le couple Raspberry + cartes PIC/ColdFire est la cible moderne.

---

## 3. Les deux flux de données fondamentaux

### 3.1 Architecture dual-protocol du serveur

Le backend doit parler **deux langages incompatibles** simultanément (voir [`essensys-server-backend`](repos/essensys-server-backend.md) et `MIGRATION_PLAN.md`) :

| Protocole | Clients | Caractéristiques | Règle |
|---|---|---|---|
| **Legacy IoT** | Boîtiers embarqués (C/MQX) | JSON malformé (clés non quotées), header `Content-Type: application/json ;charset=UTF-8` (espace avant `;`), réponse en **un seul paquet TCP**, codes HTTP non standard (`201 Created`), Basic Auth, ordres alarme chiffrés AES | **NE JAMAIS MODIFIER** — endpoints `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}` |
| **Web moderne** | Frontend React, apps mobiles, Home Assistant | REST/JSON standard, sessions/JWT | Nouveaux endpoints `/api/auth/*`, `/api/user/*`, `/api/admin/inject`, `/api/gateway/*` |

### 3.2 Pilotage distant via le cloud (traversée du NAT)

L'armoire n'est jamais joignable directement depuis Internet. Le pilotage à distance fonctionne en **pull/push sortant** :

1. L'utilisateur agit sur [`essensys-user-portal-frontend`](repos/essensys-user-portal-frontend.md) (`mon.essensys.fr/portal/`).
2. Le [backend cloud](repos/essensys-user-portal-backend.md) dépose une `cloud_action` en base PostgreSQL.
3. La [passerelle Raspberry](repos/essensys-raspberry-gateway.md) **interroge le cloud en sortie** (`GET /api/gateway/pending-actions`), récupère l'action et remonte l'état (`POST /api/gateway/exchange`).
4. La passerelle traduit l'action en commande sur le bus de l'armoire.

L'accès distant nécessite une **liaison d'armoire validée par un admin** (`link_requests`).

### 3.3 La « Table d'échange » — contrat d'interface matériel

Le cœur du dialogue armoire ↔ serveur est une **table d'échange indexée** (clé `k` / valeur `v`). Tous les clients « modernes » (apps mobiles, Home Assistant) pilotent via `POST /api/admin/inject` avec un payload `{"k": <indice>, "v": <valeur>}`.

- La table de référence vit côté firmware dans `TableEchange.h` ([SC944D](repos/essensys-board-SC944D.md)) et est dupliquée côté écran ([SC945D](repos/essensys-board-SC945D.md), `IHM_ECHANGES.INC`).
- ⚠️ **Toute renumérotation d'indices doit être propagée** au firmware, à l'écran et au serveur. La doc ([essensys-doc](repos/essensys-doc.md)) signale une dérive corrigée (~600 → 953 indices).

---

## 4. Index complet des dépôts (40)

### Services applicatifs — sur site (LAN)
| Dépôt | Rôle | Stack |
|---|---|---|
| [essensys-server-backend](repos/essensys-server-backend.md) | Passerelle HTTP dual-protocol (legacy IoT ↔ web/MQTT) | Go 1.23, Redis, PostgreSQL, MQTT, Prometheus |
| [essensys-server-frontend](repos/essensys-server-frontend.md) | Tableau de bord domotique local | React 19, TS, Vite, Tailwind 4 |

### Services applicatifs — cloud (OVH)
| Dépôt | Rôle | Stack |
|---|---|---|
| [essensys-user-portal-backend](repos/essensys-user-portal-backend.md) | Hub cloud (relais actions, identité, admin) | Go 1.25, go-chi, PostgreSQL, JWT |
| [essensys-user-portal-frontend](repos/essensys-user-portal-frontend.md) | Portail utilisateur distant `/portal/` | React 19, TS, Vite, Tailwind 4 |
| [essensys-support-site](repos/essensys-support-site.md) | Portail de support + docs (backend Go déprécié) | React 19, Vite, MkDocs, Go (legacy) |

### Passerelles & plan de contrôle
| Dépôt | Rôle | Stack |
|---|---|---|
| [essensys-raspberry-gateway](repos/essensys-raspberry-gateway.md) | Passerelle CM5 (HW KiCad + déploiement NixOS dual-NIC) | NixOS/Nix Flakes, KiCad |
| [essensys-raspberry-install](repos/essensys-raspberry-install.md) | Bootstrap de provisioning RPi (délègue à Ansible) | Bash, Ansible, Docker |
| [essensys-control-plane](repos/essensys-control-plane.md) | Orchestration flotte Docker + registre Redis des cartes | Go 1.24, React, Docker SDK, SQLite |
| [essensys-gateway](repos/essensys-gateway.md) | ⚠️ **Stub** (placeholder, rôle réel tenu par raspberry-gateway) | — |

### Firmware — cartes produit (armoire)
| Dépôt | Rôle | MCU |
|---|---|---|
| [essensys-board-SC944D](repos/essensys-board-SC944D.md) | **Carte maîtresse** Ethernet, agrège le bus I²C, dialogue serveur, OTA | ColdFire MCF52259 / MQX |
| [essensys-board-SC940](repos/essensys-board-SC940.md) | Actionneurs « Pièce de vie » (esclave I²C) | PIC16F946 |
| [essensys-board-SC941C](repos/essensys-board-SC941C.md) | Actionneurs « Pièce d'eau » (esclave I²C, même firmware) | PIC16F946 |
| [essensys-board-SC942C](repos/essensys-board-SC942C.md) | Actionneurs « Chambres » (esclave I²C) | PIC16F946 |
| [essensys-board-SC945D](repos/essensys-board-SC945D.md) | Écran tactile mural 2,8" (IHM) | 4D Systems PICASO / 4DGL |
| [essensys-board-SC946D](repos/essensys-board-SC946D.md) | Sirène d'alarme (ampli classe D 25 W) | PIC24F08KL201 |
| [essensys-board-SC843D](repos/essensys-board-SC843D.md) | Module gradateur/dimmer éclairage (binaire seul) | PIC12F1840 |
| [essensys-board-SC947-xB](repos/essensys-board-SC947-xB.md) | Détecteur de fuite d'eau (binaire seul) | PIC12F1840 |

### Firmware — bancs de test usine
| Dépôt | Rôle | MCU |
|---|---|---|
| [essensys-board-SC840B](repos/essensys-board-SC840B.md) | Banc de test « BA » (cartes actionneurs) | dsPIC33FJ256GP710A |
| [essensys-board-SC841A](repos/essensys-board-SC841A.md) | Banc de test « BP » (cartes principales) | dsPIC33FJ256GP710A |

### Infrastructure (Docker, déployée par Ansible)
| Dépôt | Rôle | Stack |
|---|---|---|
| [essensys-traefik](repos/essensys-traefik.md) | Reverse-proxy de bordure, terminaison TLS, filtrage WAN | Traefik v2.11 |
| [essensys-nginx](repos/essensys-nginx.md) | Serveur web LAN, proxy interne (api/mcp/admin) | Nginx Alpine |
| [essensys-mosquitto](repos/essensys-mosquitto.md) | Broker MQTT (`:1883`, auth) | Eclipse Mosquitto |
| [essensys-redis](repos/essensys-redis.md) | Cache / bus clé-valeur (`:6379`) partagé backend/MCP | Redis Alpine |
| [essensys-prometheus](repos/essensys-prometheus.md) | ⚠️ **Stub** (le monitoring réel utilise l'image upstream via Ansible) | — |
| [essensys-base](repos/essensys-base.md) | Image Docker socle commune (`FROM essensyshub/essensys-base`) | Docker/Alpine multi-arch |

### Déploiement & automatisation
| Dépôt | Rôle | Stack |
|---|---|---|
| [essensys-ansible](repos/essensys-ansible.md) | Déploiement complet (passerelles RPi/CM5 + cloud OVH) | Ansible, Docker Compose |
| [essensys-n8n](repos/essensys-n8n.md) | ⚠️ **Stub** (automatisation workflows prévue) | — |

### Outillage & build firmware
| Dépôt | Rôle | Stack |
|---|---|---|
| [essensys-gcc](repos/essensys-gcc.md) | Toolchain libre de build firmware (migration CodeWarrior/MPLAB → GCC) | Docker, m68k-elf-gcc, XC8 |
| [essensys-utils](repos/essensys-utils.md) | Utilitaires (ex : bruteforce code SC944D via Redis) | Go, Redis |
| [essensys-mcp](repos/essensys-mcp.md) | ⚠️ **Stub** (serveur MCP pour agents IA prévu) | — |
| [essensys-memory](repos/essensys-memory.md) | ⚠️ **Stub** (mémoire d'agents IA prévue) | — |

### Documentation
| Dépôt | Rôle | Stack |
|---|---|---|
| [essensys-doc](repos/essensys-doc.md) | Référentiel doc technique central (modèle C4, table d'échange) | Markdown, Mermaid |
| [essensys-api-doc](repos/essensys-api-doc.md) | Doc du protocole HTTP legacy (rétro-ingénierie Wireshark, **pas OpenAPI**) | MkDocs Material |

### Clients (legacy & mobiles)
| Dépôt | Rôle | Stack |
|---|---|---|
| [client-essensys-legacy](repos/client-essensys-legacy.md) | Firmware boîtier historique BP_MQX_ETH (carte+passerelle) | C, MQX RTOS, ColdFire |
| [essensys-web-legacy](repos/essensys-web-legacy.md) | Serveur applicatif & portail web historiques | ASP.NET MVC 4, NHibernate, SQL Server |
| [essensys-android-phone-apps](repos/essensys-android-phone-apps.md) | App mobile Android (télécommande) | Kotlin, Jetpack Compose, OkHttp |
| [essensys-ios-phone-apps](repos/essensys-ios-phone-apps.md) | App mobile iOS (télécommande) | Swift, SwiftUI, URLSession |

### Home Assistant / HAL
| Dépôt | Rôle | Stack |
|---|---|---|
| [essensys-homeassitant](repos/essensys-homeassitant.md) | Intégration HA (entités → `/api/admin/inject`) | Python (custom component HA) |
| [hal-home-assitant](repos/hal-home-assitant.md) | Méta-dépôt plateforme HAL (interphone vocal) | Markdown, ESP32 C++, FastAPI |
| [hal-home-intercom](repos/hal-home-intercom.md) | Monorepo interphone vocal HAL (STT/TTS/MQTT local-first) | FastAPI, ESP32, Docker Compose |

---

## 5. Chaînes technologiques par couche

- **Firmware armoire** : C / C++ sur PIC (HI-TECH PICC, XC8/XC16) et ColdFire (CodeWarrior + RTOS MQX). Migration en cours vers GCC libre via [essensys-gcc](repos/essensys-gcc.md). Écran en 4DGL propriétaire.
- **Bus & protocoles matériels** : I²C (cartes esclaves, adresses `0x11/0x12/0x13`), RS-485/série (écran), Ethernet + HTTP chiffré AES (carte maîtresse ↔ serveur).
- **Backend** : Go (`net/http`, sqlx, paho MQTT). Deux variantes — serveur **local** sur site et **hub cloud** consolidé.
- **Frontend** : React 19 + TypeScript + Vite + Tailwind 4 (3 SPA distinctes : dashboard local, portail distant, site support).
- **Persistance** : PostgreSQL (données métier), Redis (cache + registre/bus des cartes). Legacy : SQL Server + NHibernate.
- **Infra** : Docker (`network_mode: host`), Traefik (bordure TLS), Nginx (web LAN), Mosquitto (MQTT). Déploiement par Ansible ; alternative déclarative NixOS sur la passerelle CM5.
- **Observabilité** : Prometheus (image upstream) + New Relic (cloud).

---

## 6. Points d'attention transverses

> Relevés par les agents lors de l'exploration — utiles pour cadrer la dette et les risques.

- **Deux voies de déploiement concurrentes** sur la passerelle : NixOS déclaratif ([raspberry-gateway](repos/essensys-raspberry-gateway.md)) vs Ansible/Docker ([raspberry-install](repos/essensys-raspberry-install.md)). La cible de production gagnerait à être tranchée.
- **README obsolète** de `essensys-raspberry-install` (décrit l'ancienne archi native alors que le script délègue désormais à Ansible/Docker).
- **Backend `essensys-support-site` déprécié** (juin 2026) au profit de `essensys-user-portal-backend` en `CONSOLIDATED_MODE=true` (PostgreSQL et `JWT_SECRET` partagés).
- **Dépôts stub** à clarifier (archiver ou peupler) : `essensys-gateway`, `essensys-prometheus`, `essensys-n8n`, `essensys-mcp`, `essensys-memory`.
- **Incohérences de namespace** : `essensys-base` (README `nrineau/` vs CI `essensyshub/`), `essensys-utils` et `essensys-api-doc` hébergés sous `rhinosys` au lieu de `essensys-hub` — risque de `FROM`/liens cassés.
- **Contrat « Table d'échange » fragile** : indices dupliqués entre firmware SC944D, écran SC945D et serveur ; toute renumérotation doit être synchronisée.
- **Sécurité** : apps mobiles en HTTP clair + mots de passe WAN stockés en clair ; [essensys-utils](repos/essensys-utils.md) est un outil offensif (bruteforce) pouvant bricker le panneau ; stack HAL en sécurité minimale (POC home-lab).
- **HAL ≠ Essensys** : famille de dépôts connexe (interphone vocal ESP32 + IA locale) sous une organisation GitHub distincte, sans intégration directe au backend Essensys aujourd'hui. `hal-home-intercom` et `hal-home-assitant` couvrent **le même système** (risque de double source de vérité).
- **Artefacts lourds versionnés** : ~3 Go de fichiers parasites dans l'app Android, installeur XC8 ~98 Mo dans `essensys-gcc`.

---

## 7. Comment naviguer cette doc

- Pour **comprendre une brique précise**, ouvrez sa fiche dans [`repos/`](repos/). Chaque fiche suit la même structure : rôle, stack & dépendances, structure du dépôt, build/déploiement, intégrations, points d'attention.
- Pour le **contexte de migration legacy → Go/React**, voir `../MIGRATION_PLAN.md` (à la racine du projet) et la fiche [essensys-web-legacy](repos/essensys-web-legacy.md).
- Pour le **protocole legacy IoT**, voir [client-essensys-legacy](repos/client-essensys-legacy.md) et [essensys-api-doc](repos/essensys-api-doc.md).

---

*Documentation générée le 2026-06-16 par exploration automatisée des 40 dépôts. Les fiches reflètent l'état du code à cette date.*
