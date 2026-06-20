---
tags: [entity, repo, modern, firmware, hardware]
sources: [essensys-board-SC841A.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-board-SC841A
---

# Essensys Board Sc841a

> Carte **banc de test usine** « Banc BP » : teste automatiquement les cartes de type BP (alimentations, alarmes, téléinfo, façade) en production.

| | |
|---|---|
| **Catégorie** | Firmware carte électronique (banc de test de production) |
| **Stack** | Microchip **dsPIC33FJ256GP710A** (16 bits) · C (compilateur XC16/MPLAB) · MPLAB X (projet `.X`, NetBeans/Makefile) · matériel Altium Designer |
| **Statut** | Outil de production en service. Firmware versionné (V2_FAST), sources C + binaire présents. |
| **Era** | modern |

## Rôle

Le SC841A est le **banc de test (Banc BP)** de fabrication, complémentaire du Banc BA (SC840B). Il sert à valider en production les cartes de type **« BP »**. À en juger par les feuilles de schéma de la carte testée et les modules firmware, le périmètre couvre des fonctions plus riches qu'un simple actionneur : **alimentations, alarmes, téléinformation (compteur), façade/écran, détection, arrosage** — c'est un banc dédié à une carte « boîtier principal / passerelle » de l'installation.

Comme le Banc BA, il exécute une séquence de tests automatisés (lancement manuel ou à la fermeture du banc) et reporte les résultats via liaison série.

## Intégrations

_Non documenté._

## Structure

- `SC841A/` — projet matériel Altium Designer du banc / carte testée.
  - Schémas nombreux reflétant la richesse de la carte BP : `uC.SchDoc`, `Alim.SchDoc`, `Test Alims1/2.SchDoc`, `Alarme1/Alarme2.SchDoc`, `Teleinfo.SchDoc`, `Eternet.SchDoc` (Ethernet), `Ecran.SchDoc`, `FP.SchDoc`, `DV.SchDoc`, `DPL.SchDoc`, `DFE.SchDoc`, `BA.SchDoc`, `BM.SchDoc`, `MAL&PS&CUM.SchDoc`, `Arrosage.SchDoc`, `Divers.SchDoc`.
  - `PCB_TEST_BP.PcbDoc` (+ `.htm`/preview), `PCB_Project2.PrjPCB`, `GERBERS/`, `Câblage/`, `PcbLib1.PcbLib`, `schlib.SchLib`.
- `SC841A/Prog/` — firmware.
  - `Banc_BP_V2_FAST/` : projet MPLAB X.
    - Sources : `main.c`, `Banc_BP.h`, `Fonction_Init.c`, `Fonction_Alim.c`, `Fonction_Clk.c`, `Fonction_I2C.c`, `Fonction_LED.c`, `Fonction_Test.c`, `i2cEmem.h`.
    - `Makefile` + `nbproject/`

_… voir source complète dans raw/_

## Points d'attention

- **Banc de test de production**, pas un équipement déployé chez le client.
- Le dépôt mêle la conception de la **carte BP** (nombreux schémas fonctionnels : alarme, téléinfo, Ethernet, arrosage, écran…) et le **firmware du banc** qui la teste — bien distinguer les deux.
- Variante `V2_FAST` (séquence accélérée) ; vérifier l'existence/cohérence d'une version « non fast » si besoin de tests plus complets.
- Toolchain et MCU identiques au SC840B (dsPIC33FJ256GP710A) — bancs cousins.
- Artefacts de build (`build/`, `dist/`) commités dans le dépôt.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-board-SC841A.md`
