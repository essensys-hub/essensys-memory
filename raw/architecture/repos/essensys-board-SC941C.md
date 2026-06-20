# essensys-board-SC941C

> Variante « Boîtier Pièce d'Eau » du contrôleur d'actionneurs domotique : commute lampes, variateurs et volets sur ordre du concentrateur via bus I2C.

**Catégorie :** Firmware carte électronique
**Stack :** Microchip PIC16F946 (8 bits) · C (compilateur Hi-Tech C / XC8) · MPLAB X · matériel Altium Designer
**Statut :** Open Source Hardware, firmware en production (code BA v1.7), documentation MkDocs fournie.

## Rôle dans l'architecture Essensys
Le SC941C est la déclinaison **« pièce d'eau »** (référence interne SC941-0A) de la carte de contrôle d'actionneurs Essensys Atrium. C'est un **nœud esclave I2C** qui pilote des charges 230 V (relais d'éclairage, variateurs/dimmers, volets temporisés) en réponse aux ordres d'un concentrateur maître, tout en gérant ses entrées locales (boutons-poussoirs avec anti-rebond, appui long pour gradation, double-clic). Les états sont sauvegardés en EEPROM pour restauration après coupure secteur.

Le firmware (`code_ba`) est **identique** à celui des cartes SC940 (pièce de vie) et SC942 (chambres) : la différenciation se fait à la compilation par le `#define TYPE_*` et l'adresse I2C dans `hard.h` (pièce de vie `0x11`, chambres `0x12`, pièce d'eau `0x13`).

## Stack technique & matériel (MCU, périphériques)
- **MCU** : Microchip **PIC16F946** (CMOS 8 bits), boîtier 64 broches.
- **Horloge** : oscillateur HS. **Watchdog désactivé au démarrage** (`__CONFIG(HS & WDTDIS)`).
- **Mémoire** : EEPROM interne pour la configuration des sorties (Lampe/Variateur/Volet), les états sauvegardés, les temps d'action volets et temps d'extinction lampes ; mapping versionné.
- **Actionneurs** : relais bistables et monostables (sous-schémas `STORRB`/`STORRM1`/`STORRM2`), étage variateurs (`Variateurs`).
- **Architecture firmware** : boucle principale (`while(1)`) + interruptions (Timer pour temporisations/anti-rebond ; SSP/I2C pour la réception des trames).

## Structure du dépôt
- `SC941C/` — projet matériel Altium Designer.
  - `SC941C_Coeur.SchDoc` (MCU), `SC941C_Borniers.SchDoc`, `SC941C_ETOR1/ETOR2.SchDoc`, `SC941C_STORRB/STORRM1/STORRM2.SchDoc`, `SC941C_Variateurs.SchDoc`, `SC941C_Sommaire.SchDoc`.
  - `SI941C.PcbDoc` (routage), `Gerbers/`, `Assembly/`, `Test/`, `Checks/`, `3D/`.
- `SC941C/Prog/` — firmware.
  - `code_ba (fichiers sources 1.7)/source/` : sources C (`main.c`, `hard.c/.h`, `gestionentrees.c`, `gestionsorties.c`, `variateur.c`, `traitement.c`, `slavenode.c`, `crc.c/.h`, `struct.h`, `constantes.h`, `global.h`).
  - `code_ba (...)/essensys_ba.X/` : projet MPLAB X + `Makefile`.
  - `ba v1_7 piece eau.hex` + `_Archives/` (versions antérieures, dont variantes « only_dimming »).
- `docs/` + `mkdocs.yml` — documentation (index, architecture, hardware, schematics, firmware, downloads).

## Build / Flash / Déploiement
- **Compilation** : projet `essensys_ba.X` sous **MPLAB X IDE** (Hi-Tech C / XC8), `Makefile` fourni. Sélectionner la variante « pièce d'eau » via `#define TYPE_PIECES_D_EAU` dans `hard.h` (adresse I2C `0x13`).
- **Flash** : programmer le `.hex` (`ba v1_7 piece eau.hex`) via PICkit / MPLAB IPE ; vérifier la correspondance du checksum nom-de-fichier/outil.
- **Documentation** : `pip install mkdocs-material` puis `mkdocs serve`.

## Intégrations (comment la carte communique)
- **Bus I2C esclave** vers le concentrateur maître Atrium : ISR SSP remplit `RXBuffer`, validation CRC, exécution via `vd_Traitement_I2C`.
- **Jeu de commandes** identique au SC940 : `C_FORCAGE_SORTIES` (0x01), `C_CONF_SORTIES` (0x02), `C_TPS_EXTINCTION` (0x03), `C_TPS_ACTION` (0x04), `C_ACTIONS` (0x05).
- **Entrées** : structure `struct_EntreeVariateur` distinguant appui simple, appui long (gradation) et double-clic ; mapping logique↔physique figé en `#define`.

## Points d'attention
- **Watchdog désactivé au boot.**
- **`hard.h` livré configuré en `TYPE_CHAMBRES` / `I2C_ADDR 0x12`** alors que la carte est « pièce d'eau » (attendu `TYPE_PIECES_D_EAU` / `0x13`) : impérativement repositionner le `#define` avant compilation, sinon adresse I2C et mapping d'E/S erronés.
- **Firmware mutualisé** : ne pas modifier `code_ba` sans considérer l'impact sur SC940/SC942.
- **EEPROM versionnée** : incrémenter `VERSION_EEPROM` à tout changement de mapping.
- Docs `architecture.md` et `schematics.md` partiellement à compléter (sections « à insérer »).
- Commentaires source en français encodé Latin-1 (accents altérés) ; MCU 8 bits + toolchain Hi-Tech C historique.
