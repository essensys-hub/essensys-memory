---
tags: [entity, repo, modern, firmware, hardware]
sources: [essensys-board-SC940.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-board-SC940
---

# Essensys Board Sc940

> Carte « Boîtier Pièce de Vie » : contrôleur d'actionneurs domotiques (éclairage, variateurs, volets) piloté sur bus I2C par le concentrateur central.

| | |
|---|---|
| **Catégorie** | Firmware carte électronique |
| **Stack** | Microchip PIC16F946 (8 bits) · C (compilateur Hi-Tech C / XC8) · MPLAB X · matériel Altium Designer |
| **Statut** | Open Source Hardware, firmware en production (code BA v1.7), documentation MkDocs fournie. |
| **Era** | modern |

## Rôle

Le SC940D est une **unité de contrôle d'actionneurs** installée dans la « pièce de vie » d'un logement de la solution domotique **Essensys Atrium**. Elle commute des charges 230 V via des relais embarqués et gère trois familles de sorties :
- **Lampes / relais monostables** (On/Off),
- **Variateurs** (gradation d'éclairage),
- **Volets roulants** (commande temporisée ouverture/fermeture).

Elle se comporte comme un **nœud esclave I2C** générique : elle exécute les ordres reçus du concentrateur maître (carte type SC944D), tout en lisant ses propres entrées (boutons-poussoirs muraux) avec anti-rebond. Les états (relais, niveaux de variateurs, temps de volets/extinction) sont persistés en EEPROM pour restauration après coupure secteur.

Le SC940 partage exactement le même firmware (`code_ba`) que le SC941C (pièces d'eau) et le SC942 (chambres) ; seul le `#define TYPE_*` et l'adresse I2C dans `hard.h` distinguent les variantes. (Remarque : dans le code livré, le bloc actif est `TYPE_CHAMBRES` / `I2C_ADDR 0x12` — la sélection se fait à la compilation.)

## Intégrations

_Non documenté._

## Structure

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
| `main.c` | Init, boucle principale

_… voir source complète dans raw/_

## Points d'attention

- **Watchdog désactivé au boot** — toute robustesse anti-blocage doit être réactivée explicitement.
- **Codebase partagée multi-cartes** : le `.hex` dépend du `#define TYPE_*` et de l'adresse I2C ; un mauvais build/adresse rend la carte muette sur le bus. Le code livré a `TYPE_CHAMBRES` actif alors que la carte est « pièce de vie » — vérifier la cohérence avant flash.
- **Mapping d'entrées figé à la compilation** : une entrée physiquement câblée n'est vue que si elle figure dans les tables de mapping.
- **EEPROM versionnée** : tout changement de mapping impose d'incrémenter `VERSION_EEPROM` sous peine d'états corrompus.
- **Commentaires source en français encodé Latin-1** (caractères accentués altérés) ; MCU 8 bits ancien et compilateur Hi-Tech C historique.
- Le module RF « Cœur » SC943-0C est documenté comme « probable » : protocole RF exact non confirmé dans ce dépôt.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-board-SC940.md`
