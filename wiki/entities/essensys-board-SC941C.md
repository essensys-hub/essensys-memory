---
tags: [entity, repo, modern, firmware, hardware]
sources: [essensys-board-SC941C.md, incidents/2026-08-foudre-bus-i2c/rapport-analyse.md]
created: 2026-06-20
updated: 2026-10-14
era: modern
repo: essensys-board-SC941C
---

# Essensys Board Sc941c

> Variante « Boîtier Pièce d'Eau » du contrôleur d'actionneurs domotique : commute lampes, variateurs et volets sur ordre du concentrateur via bus I2C.

| | |
|---|---|
| **Catégorie** | Firmware carte électronique |
| **Stack** | Microchip PIC16F946 (8 bits) · C (compilateur Hi-Tech C / XC8) · MPLAB X · matériel Altium Designer |
| **Statut** | Open Source Hardware, firmware en production (code BA v1.7), documentation MkDocs fournie. |
| **Era** | modern |

## Rôle

Le SC941C est la déclinaison **« pièce d'eau »** (référence interne SC941-0A) de la carte de contrôle d'actionneurs Essensys Atrium. C'est un **nœud esclave I2C** qui pilote des charges 230 V (relais d'éclairage, variateurs/dimmers, volets temporisés) en réponse aux ordres d'un concentrateur maître, tout en gérant ses entrées locales (boutons-poussoirs avec anti-rebond, appui long pour gradation, double-clic). Les états sont sauvegardés en EEPROM pour restauration après coupure secteur.

Le firmware (`code_ba`) est **identique** à celui des cartes SC940 (pièce de vie) et SC942 (chambres) : la différenciation se fait à la compilation par le `#define TYPE_*` et l'adresse I2C dans `hard.h` (pièce de vie `0x11`, chambres `0x12`, pièce d'eau `0x13`).

## Intégrations

_Non documenté._

## Structure

- `SC941C/` — projet matériel Altium Designer.
  - `SC941C_Coeur.SchDoc` (MCU), `SC941C_Borniers.SchDoc`, `SC941C_ETOR1/ETOR2.SchDoc`, `SC941C_STORRB/STORRM1/STORRM2.SchDoc`, `SC941C_Variateurs.SchDoc`, `SC941C_Sommaire.SchDoc`.
  - `SI941C.PcbDoc` (routage), `Gerbers/`, `Assembly/`, `Test/`, `Checks/`, `3D/`.
- `SC941C/Prog/` — firmware.
  - `code_ba (fichiers sources 1.7)/source/` : sources C (`main.c`, `hard.c/.h`, `gestionentrees.c`, `gestionsorties.c`, `variateur.c`, `traitement.c`, `slavenode.c`, `crc.c/.h`, `struct.h`, `constantes.h`, `global.h`).
  - `code_ba (...)/essensys_ba.X/` : projet MPLAB X + `Makefile`.
  - `ba v1_7 piece eau.hex` + `_Archives/` (versions antérieures, dont variantes « only_dimming »).
- `docs/` + `mkdocs.yml` — documentation (index, architecture, hardware, 

_… voir source complète dans raw/_

## Points d'attention

- **Watchdog désactivé au boot.**
- **`hard.h` livré configuré en `TYPE_CHAMBRES` / `I2C_ADDR 0x12`** alors que la carte est « pièce d'eau » (attendu `TYPE_PIECES_D_EAU` / `0x13`) : impérativement repositionner le `#define` avant compilation, sinon adresse I2C et mapping d'E/S erronés.
- **Firmware mutualisé** : ne pas modifier `code_ba` sans considérer l'impact sur SC940/SC942.
- **EEPROM versionnée** : incrémenter `VERSION_EEPROM` à tout changement de mapping.
- Docs `architecture.md` et `schematics.md` partiellement à compléter (sections « à insérer »).
- Commentaires source en français encodé Latin-1 (accents altérés) ; MCU 8 bits + toolchain Hi-Tech C historique.

## Incident foudre 2026-08

- **Mêmes faiblesses que les autres BA.**
  - Résistances série SDA/SCL de 0 Ω (ici **R1/R3**, et non R1/R2).
  - Le PIC16F946 conduit avant les TVS D1/D2.
  - Le rail « +12V » n'a pas de TVS : C2 tient 16 V, U1 (LMR12010) 24 V.
  - Désignateurs D1/D2, C2 et U1 relevés sur le SC940D : à vérifier sur le schéma DM de cette carte.
- **Dessert les salles de bains.**
  - Son essai d'isolement à 500 V se fait **en premier**. En dessous de 10 MΩ, la carte n'est pas remise en service.
  - Si des boutons sont en volumes 1 ou 2, la §701 de la NF C 15-100 n'y admet que la TBTS (à confirmer par l'électricien, annexe C n° 9 du rapport). Raison supplémentaire d'exclure tout éclateur entre le 0 V et la terre.
- **Désignateurs utiles.** PIC U4, pull-ups R43/R44, 0 Ω VBUS/GNDBUS R93/R94, empreinte C40 pour la TVS de +Vin, ICSP J97. Adresse 0x13 (PDE).
- **Génération 3 (RS-485).** Le signal DE est absent sur cette carte, qui demande un montage à direction automatique.
- **Réparation.** PIC16F946 (U4) en approvisionnement tendu (Microchip en direct, stock) ; TVS en SMF5V0A-E3-08 ; lire l'EEPROM avant de remplacer le PIC. Détails sur [[Essensys Board Sc940]].
- Voir [[Incident Foudre Bus I2C 2026 08]] et [[Protection Surtension Bus I2C]].

## Identité I2C

- Adresse **0x13**, figée à la compilation (`TYPE_PIECES_D_EAU` dans `hard.h`). L'image `.hex` v1.7 du type a été vérifiée.
- Aucune configuration, aucun appairage. Les trois dépôts BA ont `hard.h` réglé sur `TYPE_CHAMBRES` : recompiler en vérifiant le type, ou ne flasher que le `.hex` livré.
- Voir [[Espion I2C Passif]].
- **Versions du firmware** : de 1.30 à 1.4, somme de contrôle 8 bits, incompatible avec le BP 099-37 ; CRC16 à partir de la v1.5. L'adresse ne change pas d'une version à l'autre. Au démarrage, le BA n'attend rien du BP, et sa LED DL1 clignote indépendamment de l'I2C. Voir [[Analyse Demarrage BP BA 2026 10]].

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-board-SC941C.md`
