# essensys-board-SC944D

> Carte contrôleur central (« client ») de la box domotique Essensys : cerveau Ethernet sous RTOS MQX qui agrège les boîtiers auxiliaires, dialogue avec le serveur Essensys et distribue les firmwares aux autres cartes.

**Catégorie :** Firmware carte électronique
**Stack :** Freescale/NXP ColdFire MCF52259 (32 bits, 80 MHz, 512 Ko Flash, 64 Ko RAM), langage C, RTOS Freescale MQX 4.0, CodeWarrior
**Statut :** Production – build de référence `099-37` (`BP_MQX_ETH ... 099-37.elf_BOOT_CRC.S19`), versions serveur 34→37 archivées dans `Prog/_Archives`

## Rôle dans l'architecture Essensys
Le SC944D est le **contrôleur central / passerelle** de l'installation domotique. C'est la seule carte connectée à Ethernet ; elle :
- pilote et interroge les **boîtiers auxiliaires** (BA) SC940/941/942 sur I²C ;
- dialogue avec l'**IHM** (écran tactile SC945D) en liaison série ;
- gère les fonctions domotiques de la maison : **alarme**, **chauffage / fil pilote**, **volets**, **scénarios**, **arrosage**, **télé-information** EDC (compteur électrique), **anémomètre**, **horodatage RTC**, **réveil** ;
- se connecte au **serveur Essensys** (HTTP + chiffrement) pour remonter les états, recevoir les actions/scénarios, et **télécharger les firmwares** (le sien et ceux des autres cartes) pour les redistribuer.

Toute l'installation s'articule autour d'une **Table d'échange** (`TableEchange.h` / `TableEchangeAcces.c`) indexée : chaque variable domotique (température, éclairage, consommation, état alarme…) a un index unique partagé avec l'écran et le serveur (voir le fichier généré côté SC945D `IHM_ECHANGES.INC`).

## Stack technique & matériel (MCU, périphériques)
- **MCU :** MCF52259CAG80 (ColdFire V2, 80 MHz, 512 Ko Flash, 64 Ko RAM) — réf. BOM `U10`.
- **RTOS :** Freescale MQX 4.0 (`MQX_ROOT_DIR = C:/Freescale/Freescale_MQX_4_0`), pile réseau RTCS.
- **Connectivité :** Ethernet (RTCS, DHCP par défaut via `IPConfig`), I²C0 maître vers les BA, UART/RS-485 vers l'écran et la télé-information.
- **Stockage :** EEPROM SPI externe (`Eepromspi.c`, `EepromSoft.c`) + EEPROM d'adresse MAC (`EepromAdresseMac.c`), Flash interne (FlashX) pour le bootloader et les firmwares.
- **Périphériques applicatifs :** ADC direct, anémomètre, RTC date/heure, espion RS (debug série `EspionRS.c`).
- **Sécurité :** chiffrement maison côté Ethernet — AES Rijndael (`Cryptagerijndael_mode.c`), MD5 (`Cryptagemd5.c`), base64/encode (`Cryptagecencode.c`), avec une « matricule cryptée » envoyée au serveur à chaque requête.

## Structure du dépôt
- `SC944D/` – projet matériel Altium (nombreux schémas `.SchDoc` par fonction : Coeur, Ethernet, Chargeur batterie, Fil pilote, Arrosage, Sirènes, Télé-information, Liaison IHM, Liaison boîtiers auxiliaires…), PCB `SI944D.PcbDoc`.
- `SC944D/Prog/099-37/BP_MQX_ETH/` – projet firmware CodeWarrior (cible `m52259evb`, configs Int_Flash Debug/Release, Ext_MRAM) :
  - `C/` – logique applicative : `main.c`, `ba.c` / `ba_i2c.c` (dialogue I²C avec les BA), `Ecran.c` (protocole écran), `Alarme.c`, `Chauffage.c`, `FilPilote.c`, `Scenario.c`, `Arrosage.c`, `TeleInfo.c`, `Anemo.c`, `Reveil.c`, `GestionDateHeure.c`, `TableEchangeAcces.c` / `TableEchangeFlash.c`, `bootloader.c`, `EepromSoft/Spi/AdresseMac.c`, `crc.c`, `Hard.c`.
  - `Ethernet/` – pile applicative serveur : `www.c` (tâche `Ethernet_task`), `GestionSocket.c`, `Download.c` (téléchargement + flash firmware), `Json.c`, `Cryptage*.c`.
  - `H/` – en-têtes ; `essensys_screen_protocol.md` – doc du protocole écran.
- `docs/` + `mkdocs.yml` – site MkDocs (FR), avec page I²C dédiée.
- `BUILD_ON_LINUX.md`, `Dockerfile`, `build.sh` – tentative de build conteneurisé.

## Build / Flash / Déploiement
- **Toolchain d'origine :** CodeWarrior for ColdFire + Freescale MQX 4.0 (Windows). Configurations `m52259evb_Int_Flash_Debug/Release` et `Ext_MRAM`.
- **Build alternatif :** `Dockerfile` + `build.sh` (voir `BUILD_ON_LINUX.md`) pour reproduire la compilation hors CodeWarrior.
- **Artefact :** image S-Record `*.elf_BOOT_CRC.S19` avec CRC de boot, programmée en Flash interne du ColdFire.
- **Mise à jour terrain :** via le **bootloader** interne et la commande serveur `Cmd_Go_To_Bootloader` / `Download.c` (FlashX), sans programmateur physique.

## Intégrations (comment la carte communique)
- **Vers le serveur Essensys :** tâche `Ethernet_task` (`www.c`) en TCP/HTTP, requêtes signées par chiffrement (`cryptage()` → `c_MatriculeCryptee`), réponses en JSON (`Json.c`). Le serveur pousse des actions/scénarios qui mettent à jour la Table d'échange, et la carte renvoie les statuts d'exécution.
- **Distribution de firmware :** `Download.c` récupère les binaires sur le serveur, les écrit en Flash (FlashX) et les redistribue aux cartes filles (BA, écran) — commandes `Cmd_Write_FLASH`, `Cmd_Erase_FLASH`, `Cmd_Write_FLASH_Buffer`.
- **Vers les boîtiers auxiliaires :** I²C0 maître (`ba_i2c.c`), trames CRC, adresses `0x11`/`0x12`/`0x13` (pièces de vie / chambres / pièces d'eau).
- **Vers l'IHM SC945D :** liaison série RS-485 half-duplex (gestion de direction GPIO), messages Qualifier + checksum XOR pour lire/écrire les index de la Table d'échange (cf. `essensys_screen_protocol.md`).

## Points d'attention
- **Dépendance forte à MQX 4.0 / CodeWarrior** : environnement propriétaire Freescale ; le build Linux (`Dockerfile`) reste la voie à privilégier pour la reproductibilité.
- **Pièce maîtresse SPOF :** c'est le seul nœud réseau ; sa panne isole toute l'installation du serveur et coupe la coordination des BA et de l'écran.
- **Sécurité legacy :** AES Rijndael + MD5 maison ; schéma à auditer avant toute exposition réseau moderne.
- La Table d'échange est le contrat d'interface partagé avec l'écran et le serveur — toute renumérotation d'index doit être propagée à `IHM_ECHANGES.INC` (SC945D) et au serveur.
- Build « 099-37 » correspond à la version serveur 37 ; bien aligner version firmware ↔ version serveur.
