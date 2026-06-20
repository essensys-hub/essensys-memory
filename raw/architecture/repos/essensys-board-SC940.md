# essensys-board-SC940

> Carte « Boîtier Pièce de Vie » : contrôleur d'actionneurs domotiques (éclairage, variateurs, volets) piloté sur bus I2C par le concentrateur central.

**Catégorie :** Firmware carte électronique
**Stack :** Microchip PIC16F946 (8 bits) · C (compilateur Hi-Tech C / XC8) · MPLAB X · matériel Altium Designer
**Statut :** Open Source Hardware, firmware en production (code BA v1.7), documentation MkDocs fournie.

## Rôle dans l'architecture Essensys
Le SC940D est une **unité de contrôle d'actionneurs** installée dans la « pièce de vie » d'un logement de la solution domotique **Essensys Atrium**. Elle commute des charges 230 V via des relais embarqués et gère trois familles de sorties :
- **Lampes / relais monostables** (On/Off),
- **Variateurs** (gradation d'éclairage),
- **Volets roulants** (commande temporisée ouverture/fermeture).

Elle se comporte comme un **nœud esclave I2C** générique : elle exécute les ordres reçus du concentrateur maître (carte type SC944D), tout en lisant ses propres entrées (boutons-poussoirs muraux) avec anti-rebond. Les états (relais, niveaux de variateurs, temps de volets/extinction) sont persistés en EEPROM pour restauration après coupure secteur.

Le SC940 partage exactement le même firmware (`code_ba`) que le SC941C (pièces d'eau) et le SC942 (chambres) ; seul le `#define TYPE_*` et l'adresse I2C dans `hard.h` distinguent les variantes. (Remarque : dans le code livré, le bloc actif est `TYPE_CHAMBRES` / `I2C_ADDR 0x12` — la sélection se fait à la compilation.)

## Stack technique & matériel (MCU, périphériques)
- **MCU** : Microchip **PIC16F946-I/PT**, CMOS 8 bits, boîtier 64 broches TQFP (choisi pour son grand nombre d'E/S).
- **Horloge** : oscillateur High Speed (HS). **Watchdog désactivé au démarrage** (`__CONFIG(HS & WDTDIS)`).
- **Mémoire** : EEPROM interne pour la configuration et l'état persistants (mapping versionné à l'adresse `0x000D`, marqueur d'init `0xAA55`).
- **Module de communication « Cœur »** : carte fille personnalisée **SC943-0C** (empreinte `SI943C_REV_A`) — probablement liaison RF/propriétaire vers le réseau Atrium.
- **Alimentation** : entrée 12 V DC, régulateur buck **LMR12010YMK** (TI) ; protections varistances (VDR) et diodes TVS (SMF5V0A).
- **Actionneurs** : relais **Finder 40.61** (16 A SPDT, charges principales) et **Finder 34.51** (6 A ultra-minces), pilotés par MOSFET canal-N **ZXMN3A01F**.
- **Connectique** : borniers Phoenix Contact série FFKDS pour le câblage terrain ; connecteur nappe IDC 26 broches (programmation/extension).
- **PCB** : 4 couches (Top / plan GND / plan VCC / Bottom).

## Structure du dépôt
- `SC940D/` — projet matériel Altium Designer.
  - `SC940D_Coeur.SchDoc` (MCU), `SC940D_Borniers.SchDoc`, `SC940D_ETOR1/ETOR2.SchDoc` (E/S TOR), `SC940D_STORRB/STORRM.SchDoc` (relais bistables/monostables), `SC940D_Variateurs.SchDoc`.
  - `SI940D.PcbDoc` (routage), `Gerbers/`, `Assembly/`, `3D/`.
- `SC940D/Prog/` — firmware.
  - `code_ba (fichiers sources 1.7)/source/` : sources C (voir ci-dessous).
  - `code_ba (...)/essensys_ba.X/` : projet MPLAB X + `Makefile`.
  - `ba v1_7 piece vie.hex` (binaire courant) et `_Archives/` (versions antérieures).
  - `Fiche programmation SC940 v1.docx`.
- `docs/` + `mkdocs.yml` — documentation (Architecture, Hardware, Firmware, Power Budget, DFM…).

Fichiers source clés (`source/`) :
| Fichier | Rôle |
| :--- | :--- |
| `main.c` | Init, boucle principale, gestion EEPROM (lecture/écriture config + état). |
| `hard.c/.h` | HAL : assignation des broches, `I2C_ADDR`, sélection du type de boîtier. |
| `gestionentrees.c` | Acquisition des entrées + anti-rebond. |
| `gestionsorties.c` | Pilotage des relais (mono/bistables). |
| `variateur.c` | Gradation des variateurs (rampes, consignes). |
| `traitement.c` | Logique applicative / machine à états, `vd_Traitement_I2C`. |
| `slavenode.c` | Protocole esclave I2C (ISR SSP, buffers, CRC). |
| `crc.c/.h`, `struct.h`, `constantes.h`, `global.h` | CRC, structures d'état, constantes. |

## Build / Flash / Déploiement
- **Compilation** : ouvrir le projet `essensys_ba.X` dans **MPLAB X IDE** (compilateur Hi-Tech C / XC8) ; un `Makefile` est fourni. La cible de compilation (pièce de vie / chambres / eau) se choisit via le `#define TYPE_*` dans `hard.h`.
- **Programmation** : flasher le `.hex` (`ba v1_7 piece vie.hex`) avec un PICkit / MPLAB IPE (voir `Fiche programmation SC940 v1.docx`). Vérifier que le checksum affiché correspond à celui indiqué entre parenthèses dans le nom du fichier `.hex`.
- **Documentation** : `pip install mkdocs-material` puis `mkdocs serve`.

## Intégrations (comment la carte communique)
- **Bus I2C esclave** vers le concentrateur maître (type SC944D). Réception des trames en interruption (`SSP_Handler` → `RXBuffer`), validation par checksum/CRC (`us_CalculerCRCSurTrame`), copie vers `CmdBuf`, puis exécution dans la boucle principale (`vd_Traitement_I2C`).
- **Commandes du protocole applicatif** :
  | ID | Nom | Effet |
  | :--- | :--- | :--- |
  | `0x01` | `C_FORCAGE_SORTIES` | Force l'état relais / variateurs / volets. |
  | `0x02` | `C_CONF_SORTIES` | Configure le mode variateur (On/Off ou gradation). |
  | `0x03` | `C_TPS_EXTINCTION` | Temps d'extinction auto des lampes. |
  | `0x04` | `C_TPS_ACTION` | Temps de mouvement des volets. |
  | `0x05` | `C_ACTIONS` | Actions globales (ex. sauvegarde d'état en EEPROM). |
- **Liaison RF/montante** : via le module fille « Cœur » SC943-0C vers le reste du système Atrium.
- **Entrées terrain** : boutons-poussoirs muraux sur borniers, mappés statiquement (tables logique↔physique dans `gestionentrees.c`).

## Points d'attention
- **Watchdog désactivé au boot** — toute robustesse anti-blocage doit être réactivée explicitement.
- **Codebase partagée multi-cartes** : le `.hex` dépend du `#define TYPE_*` et de l'adresse I2C ; un mauvais build/adresse rend la carte muette sur le bus. Le code livré a `TYPE_CHAMBRES` actif alors que la carte est « pièce de vie » — vérifier la cohérence avant flash.
- **Mapping d'entrées figé à la compilation** : une entrée physiquement câblée n'est vue que si elle figure dans les tables de mapping.
- **EEPROM versionnée** : tout changement de mapping impose d'incrémenter `VERSION_EEPROM` sous peine d'états corrompus.
- **Commentaires source en français encodé Latin-1** (caractères accentués altérés) ; MCU 8 bits ancien et compilateur Hi-Tech C historique.
- Le module RF « Cœur » SC943-0C est documenté comme « probable » : protocole RF exact non confirmé dans ce dépôt.
