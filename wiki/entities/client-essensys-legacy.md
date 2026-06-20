---
tags: [entity, repo, legacy, firmware, hardware]
sources: [client-essensys-legacy.md]
created: 2026-06-20
updated: 2026-06-20
era: legacy
repo: client-essensys-legacy
---

# Client Essensys Legacy

> Firmware du boîtier domotique embarqué Essensys (BP_MQX_ETH) : application C temps réel sur microcontrôleur Coldfire MCF52259 sous MQX RTOS, qui pilote alarme, chauffage, éclairage, volets, arrosage et compteur Linky, et dialogue avec le serveur via un protocole HTTP de polling au comportement non standard.

| | |
|---|---|
| **Catégorie** | Legacy — firmware embarqué IoT (C / RTOS) |
| **Stack** | C, Freescale MQX RTOS, pile TCP/IP RTCS, microcontrôleur Coldfire MCF52259, périphériques I2C / SPI / UART / ADC / PWM / Ethernet, CodeWarrior |
| **Statut** | legacy (référence, ne pas modifier) |
| **Era** | legacy |

## Rôle

`client-essensys-legacy` est le **firmware du boîtier physique** installé dans l'habitation (« BP » = boîtier principal). C'est le **terminal embarqué** de la plateforme : il lit l'état réel de la maison (capteurs, compteur Linky) et applique les commandes (relais, fil pilote, volets, sirène d'alarme).

Il est le **pendant matériel** de `essensys-web-legacy` : le boîtier interroge en boucle le serveur via un protocole de **polling HTTP** pour remonter son état (`/api/mystatus`) et récupérer les actions à exécuter (`/api/myactions`), qu'il acquitte ensuite (`/api/done`). Il reçoit aussi ses **mises à jour firmware** par ce canal (OTA).

Dans le contexte de migration, ce dépôt est **doublement structurant** :
1. Le **firmware ne peut pas être modifié facilement** (reflash matériel sur site) : c'est donc lui qui **impose le contrat** que le nouveau serveur Go (`essensys-server-backend`) doit respecter à l'identique.
2. Sa documentation (`docs/`) capture des **contraintes critiques non documentées à l'origine** (single-packet TCP, JSON malformé, en-têtes exacts), découvertes par analyse réseau (`tcpdump`) lors de la réécriture du serveur.

## Intégrations

- **Serveur Essensys** (`essensys-web-legacy` historique, puis `essensys-server-backend` en Go) — via le **protocole HTTP de polling legacy** (ci-dessous).
- **Compteur Linky** — trames **TeleInfo** lues sur UART (`TeleInfo.c`), spécification Enedis.
- **Boîtiers auxiliaires** — bus **I2C** (`ba_i2c.c`).
- **EEPROM SPI** — adresse MAC et paramètres persistants.
- **Périphériques domotiques** — fil pilote (PWM), relais volets/éclairage (GPIO), sirène alarme, ADC fuites d'eau, anémomètre.

### Protocole HTTP legacy IoT (contraintes critiques)

Le boîtier embarque un **parser HTTP volontairement minimal** (mémoire ≈ 2-4 Ko par stack) qui impose plusieurs contraintes **non standard**, à respecter à l'identique côté serveur. Référence code : `Ethernet/www.c`, `Ethernet/Json.c`.

**Endpoints (polling toutes les ~1-2 s, `serverinfos` ~20 s)** :

- **`GET /api/serverinfos`** — récupère la liste des index à surveiller + signal de nouvelle version firmware. Réponse `200 OK`.
- **`POST /api/mystatus`** — remonte l'état : `{version:"1.0",ek:[{k:605,v:"0"},…]}` (`ek` = exchange keys). Le client attend **`201 Created`** (il teste littéralement `strstr(rx, "HTTP/1.1 201 Created")`).
- **`GET /api

_… voir source complète dans raw/_

## Structure

- **`C/`** — logique applicative / modules métier :
  - `main.c` — point d'entrée, init système, table des tâches MQX, boucle de la tâche principale.
  - `Alarme.c` — détection, sirènes, procédures, déchiffrement des ordres alarme.
  - `Chauffage.c` / `FilPilote.c` — pilotage chauffage par zone via 6 ordres fil pilote (confort, éco, hors-gel, confort-1, confort-2, arrêt) en PWM.
  - `arrosage.c`, `reveil.c`, `anemo.c` (anémomètre), `adcdirect.c` (détection fuite d'eau).
  - `TeleInfo.c` — lecture des trames TeleInfo du compteur **Linky** (UART), parsing, mise à jour table d'échange.
  - `Scenario.c` — scénarios (je sors, je rentre, vacances…).
  - `Ecran.c` — gestion de l'afficheur.
  - `TableEchange*.c` (`TableEchangeAcces.c`, `TableEchangeFlash.c`) — accès et persistance Flash de la **ta

_… voir source complète dans raw/_

## Points d'attention

- **Statut legacy strict** : firmware de **référence, à ne pas modifier**. Toute évolution du contrat protocole est contrainte par les boîtiers déjà déployés (reflash physique nécessaire).
- **Le boîtier dicte le contrat** : les 5 contraintes ci-dessus (single-packet TCP, JSON malformé, `Content-Type` à espace, codes `201`, `Connection: close`) sont **non négociables** côté serveur Go tant que des BP_MQX_ETH sont en service. Une régression sur l'une d'elles bloque silencieusement le boîtier (sans erreur ni log côté client).
- **Robustesse pauvre côté client** : pas de timeout applicatif fiable, pas de retry, parser HTTP sans gestion de fragmentation ni de `Content-Length` progressif → tout écart serveur = blocage difficile à diagnostiquer autrement qu'au `tcpdump`.
- **Contraintes mémoire fortes** : stacks de tâches de 1,4 à 3 Ko, buffers fixes, heap rare — d'où les choix « sales » (JSON non quoté, buffer unique).
- **Sécurité** : auth **HTTP Basic** (base64, en clair sans TLS) ; chiffrement **AES** propriétaire uniquement pour les ordres d'alarme. À auditer/durcir lors de la migration, mais non modifiable sur les boîtiers existants.
- **Dépendance toolchain obsolète** : MQX (NXP, 

_… voir source complète dans raw/_

## Liens

- [[Dual Protocol]]
- [[Table D Echange]]
- [[Essensys Web Legacy]]
- [[Essensys Server Backend]]

## Source

`raw/architecture/repos/client-essensys-legacy.md`
