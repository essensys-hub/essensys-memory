---
tags: [entity, repo, modern, firmware, hardware]
sources: [essensys-board-SC840B.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-board-SC840B
---

# Essensys Board Sc840b

> Carte **banc de test usine** « Banc BA » : teste automatiquement les cartes d'actionneurs (type BA / SC940-SC942) — alimentation, relais et variateurs.

| | |
|---|---|
| **Catégorie** | Firmware carte électronique (banc de test de production) |
| **Stack** | Microchip **dsPIC33FJ256GP710A** (16 bits) · C (compilateur XC16/MPLAB) · MPLAB X (projet `.X`, NetBeans/Makefile) · matériel Altium Designer |
| **Statut** | Outil de production en service. Firmware versionné (V3 et V3_Fast), sources C présentes. |
| **Era** | modern |

## Rôle

Le SC840B n'est **pas** une carte installée chez le client : c'est le **banc de test (Banc BA)** utilisé en fabrication pour valider les cartes d'actionneurs « BA » (boîtiers pièce de vie / chambres / pièce d'eau, c.-à-d. SC940/SC941/SC942). Au moment de la fermeture du banc (ou via barre espace), il lance une séquence de tests automatisés et reporte le résultat sur liaison série (hyperterminal).

Tests réalisés (d'après la spécification du banc) :
- **Alimentation** : mesure ADC 12 bits, moyenne sur 8 échantillons, tolérance ±10 % autour de ~90 % de Vcc.
- **Relais** : commande de contacts secs et vérification du changement d'état (état initial ≠ intermédiaire = relais OK, sinon HS).
- **Variateurs** : sélection du relais, double-clic → max, appui long → ~50 %, contact sec → min ; mesure de la valeur moyenne par ADC (moyenne sur 100 échantillons) pour valider la gradation.

## Intégrations

_Non documenté._

## Structure

- `SC840B/` — projet matériel Altium Designer du banc.
  - Schémas : `uC.SchDoc`, `Alim.SchDoc`, `ETOR1-1/ETOR1-2.SchDoc`, `STOR.SchDoc`, `RMS_DC.SchDoc`, `Interfacage.SchDoc`, `Liaison Debug.SchDoc`, `Page de garde.SchDoc`.
  - `PCB_Test_BA.PcbDoc`, `PCB_Project1.PrjPCB`, `GERBERS/`, `Câblage/`.
- `SC840B/Prog/` — firmware (deux variantes) :
  - `Banc_BA_V3.X/` et `Banc_BA_V3_Fast.X/` : projets MPLAB X.
    - Sources : `main.c`, `Fonction_Alim.c`, `Fonction_Clk.c`, `Fonction_I2C.c`, `Fonction_SPI.c`, `Fonction_UART.c`, `Fonction_Variateur.c`, `Fonction_Test.c`, `i2cEmem.h`.
    - `Makefile` + `nbproject/`, `documentation/Spécification du banc de test BA.docx`.
  - `Banc_BA_V3.X.production.hex`, `Banc_BA_V3_Fast.X.production.hex`.
  - `Notice v1.docx`, `Notes de version V3 et V3_Fast.docx`

_… voir source complète dans raw/_

## Points d'attention

- **Banc de test, pas un produit terrain** : à ne pas confondre avec les cartes d'actionneurs qu'il valide.
- **Deux variantes** : `V3` teste les variateurs avec point milieu 50 %, `V3_Fast` sans point milieu (plus rapide). Choisir la variante selon la cadence de production souhaitée.
- Builds livrées en configuration **debug** (`__DEBUG`/PICkit 3) — vérifier la config pour une vraie build de production.
- Commentaires/auteur mêlant français et caractères non-ASCII altérés (encodage).
- Seuils de test (tolérance ±10 %, % de Vcc) codés en dur d'après la spécification : à revalider si le matériel testé évolue.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-board-SC840B.md`
