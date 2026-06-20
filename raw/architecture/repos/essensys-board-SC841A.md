# essensys-board-SC841A

> Carte **banc de test usine** « Banc BP » : teste automatiquement les cartes de type BP (alimentations, alarmes, téléinfo, façade) en production.

**Catégorie :** Firmware carte électronique (banc de test de production)
**Stack :** Microchip **dsPIC33FJ256GP710A** (16 bits) · C (compilateur XC16/MPLAB) · MPLAB X (projet `.X`, NetBeans/Makefile) · matériel Altium Designer
**Statut :** Outil de production en service. Firmware versionné (V2_FAST), sources C + binaire présents.

## Rôle dans l'architecture Essensys
Le SC841A est le **banc de test (Banc BP)** de fabrication, complémentaire du Banc BA (SC840B). Il sert à valider en production les cartes de type **« BP »**. À en juger par les feuilles de schéma de la carte testée et les modules firmware, le périmètre couvre des fonctions plus riches qu'un simple actionneur : **alimentations, alarmes, téléinformation (compteur), façade/écran, détection, arrosage** — c'est un banc dédié à une carte « boîtier principal / passerelle » de l'installation.

Comme le Banc BA, il exécute une séquence de tests automatisés (lancement manuel ou à la fermeture du banc) et reporte les résultats via liaison série.

## Stack technique & matériel (MCU, périphériques)
- **MCU** : Microchip **dsPIC33FJ256GP710A** (DSC 16 bits, 100 broches), oscillateur primaire HS **avec PLL** (`FNOSC=PRIPLL`), watchdog géré par soft.
- **Périphériques utilisés** (modules firmware) : **I2C** (expanders / carte sous test), **ADC** (`Fonction_Alim` pour mesures d'alimentation), **LED** de statut (`Fonction_LED`), horloge (`Fonction_Clk`), EEPROM I2C (`i2cEmem.h`), routines de test (`Fonction_Test`).
- **Toolchain** : MPLAB X / XC16 (`MP_PROCESSOR_OPTION=33FJ256GP710A`).

## Structure du dépôt
- `SC841A/` — projet matériel Altium Designer du banc / carte testée.
  - Schémas nombreux reflétant la richesse de la carte BP : `uC.SchDoc`, `Alim.SchDoc`, `Test Alims1/2.SchDoc`, `Alarme1/Alarme2.SchDoc`, `Teleinfo.SchDoc`, `Eternet.SchDoc` (Ethernet), `Ecran.SchDoc`, `FP.SchDoc`, `DV.SchDoc`, `DPL.SchDoc`, `DFE.SchDoc`, `BA.SchDoc`, `BM.SchDoc`, `MAL&PS&CUM.SchDoc`, `Arrosage.SchDoc`, `Divers.SchDoc`.
  - `PCB_TEST_BP.PcbDoc` (+ `.htm`/preview), `PCB_Project2.PrjPCB`, `GERBERS/`, `Câblage/`, `PcbLib1.PcbLib`, `schlib.SchLib`.
- `SC841A/Prog/` — firmware.
  - `Banc_BP_V2_FAST/` : projet MPLAB X.
    - Sources : `main.c`, `Banc_BP.h`, `Fonction_Init.c`, `Fonction_Alim.c`, `Fonction_Clk.c`, `Fonction_I2C.c`, `Fonction_LED.c`, `Fonction_Test.c`, `i2cEmem.h`.
    - `Makefile` + `nbproject/`, `dist/` (`.elf`/`.hex`/`.map`), `build/`.
  - `Banc_BP_V2_FAST.production.hex`, `Notes de version V2_FAST.docx`.

## Build / Flash / Déploiement
- **Compilation** : ouvrir `Banc_BP_V2_FAST` dans **MPLAB X IDE** (XC16) ; `Makefile` fourni. Configurations debug et production présentes dans `dist/`.
- **Flash** : programmer `Banc_BP_V2_FAST.production.hex` sur le dsPIC via PICkit 3 (`ICS=PGD2`).
- **Utilisation** : séquence de test lancée manuellement ou à la fermeture du banc, résultats via UART/LED de statut.

## Intégrations (comment la carte communique)
- **I2C** : pilotage des expanders et dialogue avec la carte BP sous test.
- **ADC** : mesures d'alimentation (`Fonction_Alim`, `Test Alims`).
- **LED** : indication visuelle du résultat de test.
- La carte BP testée expose elle-même des interfaces avancées (Ethernet, téléinfo, alarme, écran/façade) d'après les schémas — le banc en exerce les sous-fonctions.

## Points d'attention
- **Banc de test de production**, pas un équipement déployé chez le client.
- Le dépôt mêle la conception de la **carte BP** (nombreux schémas fonctionnels : alarme, téléinfo, Ethernet, arrosage, écran…) et le **firmware du banc** qui la teste — bien distinguer les deux.
- Variante `V2_FAST` (séquence accélérée) ; vérifier l'existence/cohérence d'une version « non fast » si besoin de tests plus complets.
- Toolchain et MCU identiques au SC840B (dsPIC33FJ256GP710A) — bancs cousins.
- Artefacts de build (`build/`, `dist/`) commités dans le dépôt.
