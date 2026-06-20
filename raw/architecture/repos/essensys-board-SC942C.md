# essensys-board-SC942C

> Carte auxiliaire « Chambres » de la box domotique Essensys : relais, lampes, volets et variateurs d'éclairage, pilotée en esclave I²C par le contrôleur central.

**Catégorie :** Firmware carte électronique
**Stack :** PIC16F946 (8 bits Microchip), langage C, compilateur HI-TECH PICC, projet MPLAB X (`essensys_ba.X`)
**Statut :** Production – firmware « ba » v1.7 (binaire `ba v1_7 piece chambre.hex`), versions antérieures archivées dans `Prog/_Archives`

## Rôle dans l'architecture Essensys
Le SC942C est un **boîtier auxiliaire (BA) de sorties** dédié aux chambres. Il étend les capacités du contrôleur central SC944D en pilotant un grand nombre d'actionneurs locaux. Le firmware partage une base de code commune à plusieurs boîtiers, sélectionnée à la compilation par les macros `TYPE_PIECES_DE_VIE` (SC940), `TYPE_PIECES_D_EAU` (SC941) et `TYPE_CHAMBRES` (SC942) ; pour ce dépôt c'est `TYPE_CHAMBRES` qui est activé (adresse I²C `0x12`).

Fonctions concrètes pilotées par la carte :
- **Lampes / relais monostables** et **relais bistables** (la BOM liste 7 relais 1RT 6 A et 10 relais bistables 16 A) avec temporisation d'extinction par lampe ;
- **Volets roulants** avec temps d'action (course) configurable par volet ;
- **Variateurs d'éclairage** (jusqu'à 8 voies, voir schéma `SC942C_Variateurs.SchDoc`), avec état d'allumage courant et sauvegardé.

## Stack technique & matériel (MCU, périphériques)
- **MCU :** PIC16F946-I/PT (8 bits, Microchip), oscillateur HS, watchdog désactivé au démarrage (`__CONFIG(HS & WDTDIS)`).
- **EEPROM interne :** stockage de l'état des sorties et de la configuration (mapping documenté dans `main.c`, ex. `0x0010` sorties lampes, `0x0012+` variateurs, `0x002A+` temps d'action volets, `0x0032+` temps d'extinction lampes). Un octet de version de mapping (`VERSION_EEPROM`) force la réinitialisation en cas d'évolution.
- **Entrées TOR :** lecture directe des ports B/F/G via macros `ENTREEx_INIT` / `ENTREEx_ETAT` dans `hard.h`.
- **Sorties :** relais monostables, relais bistables (commandes ON/OFF séparées) et voies variateur.
- **Bus :** module SSP du PIC en mode esclave I²C.

## Structure du dépôt
- `SC942C/` – projet matériel Altium (schémas `.SchDoc` : Coeur, ETOR1/2, STOR RB/RM, Variateurs, Borniers ; PCB `SI942C.PcbDoc` ; librairies).
- `SC942C/Prog/code_ba (fichiers sources 1.7)/source/` – code firmware C :
  - `main.c` – point d'entrée, boucle principale, gestion/version EEPROM ;
  - `hard.h` / `hard.c` – mapping E/S et sélection du type de boîtier ;
  - `gestionentrees.c` / `gestionsorties.c` – lecture des entrées et pilotage des sorties ;
  - `variateur.c` – gestion des variateurs ;
  - `traitement.c` – logique applicative ;
  - `slavenode.c` – protocole esclave I²C (base Microchip « slave node network protocol ») ;
  - `crc.c` – contrôle d'intégrité des trames.
- `SC942C/Prog/*.hex` – firmwares compilés ; `_Archives/` versions historiques.
- `docs/` + `mkdocs.yml` – site MkDocs Material (FR) déjà généré.
- `BOM_[No Variations].csv` – nomenclature.

## Build / Flash / Déploiement
- **Build :** MPLAB X + compilateur HI-TECH PICC (projet `essensys_ba.X`, `Makefile` généré). Cible déclarée `PIC16F946` dans `nbproject/configurations.xml`.
- **Flash :** programmation du PIC via ICSP avec le `.hex` (ex. `ba v1_7 piece chambre.hex`).
- La doc HTML est publiée via GitHub Actions / MkDocs (`mkdocs gh-deploy`).

## Intégrations (comment la carte communique)
- **Bus I²C esclave** vers le contrôleur central SC944D. Adresse `0x12` pour la variante Chambres (`0x11` pièces de vie, `0x13` pièces d'eau).
- Le maître écrit les commandes de sortie et lit l'état des entrées ; les trames sont protégées par **CRC** (`crc.c`).
- La carte n'a pas de connectivité réseau propre : tout passe par le SC944D qui agrège les BA sur I²C et dialogue avec le serveur Essensys.

## Points d'attention
- **Firmware multi-cibles :** le même code sert SC940/941/942 ; bien vérifier la macro `TYPE_*` active avant de compiler/flasher (risque d'écrire la mauvaise adresse I²C / le mauvais mapping).
- `VERSION_EEPROM` doit être incrémentée à chaque changement de mapping EEPROM, sinon l'état stocké devient incohérent.
- Base PIC ancienne (HI-TECH PICC, commentaires Latin-1 mal encodés) ; toolchain à figer pour reproduire les builds.
- `slavenode.c` dérive d'un exemple Microchip pour PIC16C72A — vérifier l'adéquation registres SSP avec le 16F946.
