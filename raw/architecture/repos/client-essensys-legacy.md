# client-essensys-legacy

> Firmware du boîtier domotique embarqué Essensys (BP_MQX_ETH) : application C temps réel sur microcontrôleur Coldfire MCF52259 sous MQX RTOS, qui pilote alarme, chauffage, éclairage, volets, arrosage et compteur Linky, et dialogue avec le serveur via un protocole HTTP de polling au comportement non standard.

**Catégorie :** Legacy — firmware embarqué IoT (C / RTOS)
**Stack :** C, Freescale MQX RTOS, pile TCP/IP RTCS, microcontrôleur Coldfire MCF52259, périphériques I2C / SPI / UART / ADC / PWM / Ethernet, CodeWarrior
**Statut :** legacy (référence, ne pas modifier)

## Rôle dans l'architecture Essensys

`client-essensys-legacy` est le **firmware du boîtier physique** installé dans l'habitation (« BP » = boîtier principal). C'est le **terminal embarqué** de la plateforme : il lit l'état réel de la maison (capteurs, compteur Linky) et applique les commandes (relais, fil pilote, volets, sirène d'alarme).

Il est le **pendant matériel** de `essensys-web-legacy` : le boîtier interroge en boucle le serveur via un protocole de **polling HTTP** pour remonter son état (`/api/mystatus`) et récupérer les actions à exécuter (`/api/myactions`), qu'il acquitte ensuite (`/api/done`). Il reçoit aussi ses **mises à jour firmware** par ce canal (OTA).

Dans le contexte de migration, ce dépôt est **doublement structurant** :
1. Le **firmware ne peut pas être modifié facilement** (reflash matériel sur site) : c'est donc lui qui **impose le contrat** que le nouveau serveur Go (`essensys-server-backend`) doit respecter à l'identique.
2. Sa documentation (`docs/`) capture des **contraintes critiques non documentées à l'origine** (single-packet TCP, JSON malformé, en-têtes exacts), découvertes par analyse réseau (`tcpdump`) lors de la réécriture du serveur.

## Stack technique & dépendances

- **Langage** : C (style K&R, indentation 4 espaces, commentaires en français).
- **RTOS** : **MQX** (Message Queue eXecutive, Freescale/NXP) — ordonnancement préemptif + time slicing, mutex, sémaphores, files de messages, timers.
- **Pile réseau** : **RTCS** (Real-Time Communication Stack) de MQX, sockets BSD-like (`socket`, `recv`, `send`), IP via DHCP ou statique.
- **Cible matérielle** : microcontrôleur **Coldfire V2 MCF52259** (32 bits, ~80 MHz, Flash interne, RAM interne + MRAM externe optionnelle).
- **Périphériques** : I2C (boîtiers auxiliaires), SPI (EEPROM externe — adresse MAC, paramètres), UART (écran, TeleInfo/Linky, debug), ADC (détection de fuites d'eau), PWM/Timers (fil pilote chauffage), GPIO (E/S TOR), MAC Ethernet.
- **Toolchain** : CodeWarrior Development Studio pour Coldfire (`m68k-elf-gcc`), debug/flash via JTAG/BDM (P&E Micro, Segger J-Link). Configurations de build dans `*_PEBDM.launch` et `m52259evb_Int_Flash_Debug/`.
- **Crypto** : implémentation AES/Rijndael + MD5 + base64 embarquée (`Ethernet/Cryptage*.c`) pour le déchiffrement des ordres d'alarme reçus du serveur.

## Structure du dépôt

- **`C/`** — logique applicative / modules métier :
  - `main.c` — point d'entrée, init système, table des tâches MQX, boucle de la tâche principale.
  - `Alarme.c` — détection, sirènes, procédures, déchiffrement des ordres alarme.
  - `Chauffage.c` / `FilPilote.c` — pilotage chauffage par zone via 6 ordres fil pilote (confort, éco, hors-gel, confort-1, confort-2, arrêt) en PWM.
  - `arrosage.c`, `reveil.c`, `anemo.c` (anémomètre), `adcdirect.c` (détection fuite d'eau).
  - `TeleInfo.c` — lecture des trames TeleInfo du compteur **Linky** (UART), parsing, mise à jour table d'échange.
  - `Scenario.c` — scénarios (je sors, je rentre, vacances…).
  - `Ecran.c` — gestion de l'afficheur.
  - `TableEchange*.c` (`TableEchangeAcces.c`, `TableEchangeFlash.c`) — accès et persistance Flash de la **table d'échange** (≈ 600 index, cœur de l'état système).
  - `Eeprom*.c`, `Eepromspi.c` — EEPROM SPI (adresse MAC, paramètres logiciels).
  - `ba.c`, `ba_i2c.c` — boîtiers auxiliaires sur bus I2C.
  - `Hard.c`, `GestionDateHeure.c`, `EspionRS.c` (trace série), `bootloader.c`, `crc.c`.
- **`H/`** — en-têtes correspondants + définitions clés : `TableEchange.h` (énumération `enumScenario`, mapping des index), `TableEchangeDroits.h`, `application.h`, `Hard.h`, `global.h`.
- **`Ethernet/`** — communication réseau et protocole HTTP :
  - `www.c` (~1500 lignes) — **implémentation du protocole HTTP de polling** : construction des requêtes, parsing des réponses, gestion des endpoints et de l'OTA.
  - `GestionSocket.c` — ouverture/fermeture sockets RTCS, timeouts.
  - `Json.c` — génération/parsing JSON minimaliste (clés non quotées pour économiser la mémoire).
  - `Cryptage*.c` (`Cryptage`, `Cryptagecencode`/base64, `Cryptagemd5`, `Cryptagerijndael_mode`) — AES/MD5/base64.
  - `Download.c` — réception du firmware OTA.
- **`docs/`** + `mkdocs.yml` — documentation technique (protocole, client embarqué, serveur Go de remplacement, diagrammes, dépannage réseau). Voir notamment `docs/protocol/` (`http-legacy-protocol.md`, `tcp-single-packet.md`, `exchange-table.md`).
- **Configs IDE / build** : `*.launch` (CodeWarrior), `ReferencedRSESystems.xml`, `m52259evb_Int_Flash_Debug/`.
- **Racine** : `README.md`, `MKDOCS_SUMMARY.md`, `SETUP_GITHUB.md`, scripts `build-docs.sh` / `preview-docs.sh`.

## Build / Exécution / Déploiement

- **Compilation** : ouvrir le projet dans **CodeWarrior** (Coldfire), choisir la configuration `m52259evb_Int_Flash_Debug` (ou `_Release`), `Build Project` → génère un `.elf`.
- **Flash** : via le debugger CodeWarrior ou un outil externe, programmeur **JTAG/BDM** connecté, `Program Flash`.
- **Configuration matérielle** : adresse MAC stockée en **EEPROM SPI** ; IP en **DHCP par défaut** ou statique (`H/Hard.h`). Paramètres applicatifs dans `H/application.h`, réseau dans `Ethernet/GestionSocket.h`.
- **Exécution** : au boot, MQX démarre la table des tâches ; le boîtier appelle d'abord `/api/serverinfos` puis entre dans sa boucle de polling.
- **Débogage réseau** : `tcpdump`/Wireshark sont l'outil de référence pour valider le respect des contraintes protocole (voir `docs/troubleshooting/network-debugging.md`).
- **Pas de déploiement « serveur »** : c'est un firmware embarqué ; la « mise à jour » se fait par **OTA** via le serveur (endpoints `getversioncontent`/`endversioncontent`) ou par reflash physique.

### Tâches MQX (concurrence)

Cinq tâches de priorité 8 en time slicing (`main.c`) :

| Tâche | Entrée | Stack | Rôle |
|-------|--------|-------|------|
| `MAIN_TASK` | `Main_task` | 1596 | Init, RTC, chauffage, alarme, scénarios, ADC/fuites, arrosage, anémo, délestage, MAJ table d'échange, sorties locales (auto-start) |
| `ECRAN_TASK` | `vd_Ecran_task` | 1500 | Afficheur |
| `BA_TASK` | `Boitiers_task` | 1796 | Boîtiers auxiliaires I2C |
| `TELE_TASK` | `TeleInfo_task` | 1396 | Lecture TeleInfo / Linky |
| `ETH_TASK` | `Ethernet_task` | 3000 | Communication HTTP (polling, OTA) |

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
- **`GET /api/myactions`** — récupère les actions. Réponse `200 OK` ; corps `{"_de67f":…,"actions":[{"guid":…,"params":[{k,v},…]}]}`.
- **`POST /api/done/{guid}`** — acquitte une action exécutée (Content-Length: 0). Attend **`201 Created`**.
- **`POST /api/getversioncontent/{…}` et `POST /api/endversioncontent`** — téléchargement du firmware OTA par morceaux (`Download.c`).

**Contraintes non standard (impératives)** :

1. **Single-packet TCP** — toute la réponse HTTP (status + en-têtes + corps) doit être envoyée dans **un seul segment TCP**. Le client fait un unique `recv()` dans un buffer fixe, sans réassemblage ni boucle de lecture : une réponse fragmentée (ex. en-têtes et corps en paquets séparés) **bloque définitivement** le boîtier (pas de timeout, pas de retry). Découvert par `tcpdump` : le serveur Go initial envoyait 6 paquets → blocage ; la solution est de **bufferiser toute la réponse** puis l'émettre d'un bloc (« `legacyResponseWriter` »). Voir `docs/protocol/tcp-single-packet.md`.

2. **JSON malformé (clés non quotées)** — pour économiser la mémoire, le client émet et attend du JSON **non conforme RFC 8259** : `{version:"1.0",ek:[{k:613,v:"1"}]}` au lieu de `{"version":"1.0","ek":[{"k":613,"v":"1"}]}`. Le serveur doit **normaliser** (ajout des guillemets sur `version`, `ek`, `k`, `v`, `actions`, `guid`, `params`, `_de67f`) avant parsing. Voir `docs/protocol/http-legacy-protocol.md`.

3. **En-tête `Content-Type` à espace** — format **exact** : `Content-type: application/json ;charset=UTF-8` — avec un **espace AVANT le `;`**. C'est ce que le client lui-même émet (`www.c:1527`) et attend en retour. Tout autre format (`;charset` collé, espace après `;`, casse différente) est incorrect.

4. **Codes HTTP non standard** — les POST (`mystatus`, `done`, OTA) répondent **`201 Created`** (et non `200 OK`), même sans création de ressource REST. Les GET (`serverinfos`, `myactions`) répondent `200 OK`. Le client compare le statut par recherche de sous-chaîne littérale.

5. **`Connection: close`** — pas de connexion persistante (le client ne gère pas le keep-alive). Le client envoie aussi `Authorization: Basic …` (auth HTTP Basic, `c_EnteteTrameAuthorisation`), `Host:` et des en-têtes `Accept` / `Accept-Charset` fixes.

### Table d'échange et logique d'actions

État partagé serveur↔boîtier sous forme d'une **table de ~600 index** (octets 0-255 : état, valeur ou masque de bits). Définition dans `H/TableEchange.h` (enum `enumScenario`, base 600). Index notables :

- **590 — Scenario (trigger)** : doit valoir `"1"` dans chaque action, sinon les autres index sont ignorés.
- **600-612** : confirmation scénario, contrôle alarme (`601`), configuration alarme (`602-612`).
- **613-624** : masques de bits **éteindre/allumer** les éclairages par zone (PDV = pièces de vie, CHB = chambres, PDE = pièces d'eau), en paires LSB/MSB.
- **625-630** : ouvrir/fermer volets par zone. **631** prises de sécurité, **632** machines, **633-636** consignes chauffage, **637** cumulus, **638-639** réveils.

**Règles d'action critiques** (réponse `/api/myactions`) :

- Le champ **`_de67f` doit être le premier** du JSON ; il porte l'éventuel ordre d'**alarme chiffré** (`{guid, obl}`, `obl` = payload AES), déchiffré côté boîtier par `Ethernet/Cryptage.c` (`DechiffrageAlarme`). Sinon `null`.
- Chaque action doit contenir la **table d'échange complète (index 605-622) + index 590=`"1"`**, même si une seule valeur change.
- **Fusion par OU binaire** : les valeurs d'un même index reçues sont mergées avec `|` (ex. allumer lampe entrée `1` + salon `2` → `3`). Voir `docs/protocol/exchange-table.md`.

## Points d'attention

- **Statut legacy strict** : firmware de **référence, à ne pas modifier**. Toute évolution du contrat protocole est contrainte par les boîtiers déjà déployés (reflash physique nécessaire).
- **Le boîtier dicte le contrat** : les 5 contraintes ci-dessus (single-packet TCP, JSON malformé, `Content-Type` à espace, codes `201`, `Connection: close`) sont **non négociables** côté serveur Go tant que des BP_MQX_ETH sont en service. Une régression sur l'une d'elles bloque silencieusement le boîtier (sans erreur ni log côté client).
- **Robustesse pauvre côté client** : pas de timeout applicatif fiable, pas de retry, parser HTTP sans gestion de fragmentation ni de `Content-Length` progressif → tout écart serveur = blocage difficile à diagnostiquer autrement qu'au `tcpdump`.
- **Contraintes mémoire fortes** : stacks de tâches de 1,4 à 3 Ko, buffers fixes, heap rare — d'où les choix « sales » (JSON non quoté, buffer unique).
- **Sécurité** : auth **HTTP Basic** (base64, en clair sans TLS) ; chiffrement **AES** propriétaire uniquement pour les ordres d'alarme. À auditer/durcir lors de la migration, mais non modifiable sur les boîtiers existants.
- **Dépendance toolchain obsolète** : MQX (NXP, fin de vie), CodeWarrior, MCF52259 — environnement de build difficile à reconstituer ; privilégier la documentation `docs/` comme source de vérité.
- **Spécificités françaises** : intégration native **fil pilote** (chauffage) et **TeleInfo/Linky** (compteur Enedis), à reproduire fonctionnellement côté nouvelle plateforme/passerelles.
