---
tags: [entity, repo, modern, firmware, hardware]
sources: [essensys-board-SC942C.md, incidents/2026-08-foudre-bus-i2c/rapport-analyse.md]
created: 2026-06-20
updated: 2026-10-14
era: modern
repo: essensys-board-SC942C
---

# Essensys Board Sc942c

> Carte auxiliaire « Chambres » de la box domotique Essensys : relais, lampes, volets et variateurs d'éclairage, pilotée en esclave I²C par le contrôleur central.

| | |
|---|---|
| **Catégorie** | Firmware carte électronique |
| **Stack** | PIC16F946 (8 bits Microchip), langage C, compilateur HI-TECH PICC, projet MPLAB X (`essensys_ba.X`) |
| **Statut** | Production – firmware « ba » v1.7 (binaire `ba v1_7 piece chambre.hex`), versions antérieures archivées dans `Prog/_Archives` |
| **Era** | modern |

## Rôle

Le SC942C est un **boîtier auxiliaire (BA) de sorties** dédié aux chambres. Il étend les capacités du contrôleur central SC944D en pilotant un grand nombre d'actionneurs locaux. Le firmware partage une base de code commune à plusieurs boîtiers, sélectionnée à la compilation par les macros `TYPE_PIECES_DE_VIE` (SC940), `TYPE_PIECES_D_EAU` (SC941) et `TYPE_CHAMBRES` (SC942) ; pour ce dépôt c'est `TYPE_CHAMBRES` qui est activé (adresse I²C `0x12`).

Fonctions concrètes pilotées par la carte :
- **Lampes / relais monostables** et **relais bistables** (la BOM liste 7 relais 1RT 6 A et 10 relais bistables 16 A) avec temporisation d'extinction par lampe ;
- **Volets roulants** avec temps d'action (course) configurable par volet ;
- **Variateurs d'éclairage** (jusqu'à 8 voies, voir schéma `SC942C_Variateurs.SchDoc`), avec état d'allumage courant et sauvegardé.

## Intégrations

_Non documenté._

## Structure

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
- `docs/` + `mkdocs.yml` – site Mk

_… voir source complète dans raw/_

## Points d'attention

- **Firmware multi-cibles :** le même code sert SC940/941/942 ; bien vérifier la macro `TYPE_*` active avant de compiler/flasher (risque d'écrire la mauvaise adresse I²C / le mauvais mapping).
- `VERSION_EEPROM` doit être incrémentée à chaque changement de mapping EEPROM, sinon l'état stocké devient incohérent.
- Base PIC ancienne (HI-TECH PICC, commentaires Latin-1 mal encodés) ; toolchain à figer pour reproduire les builds.
- `slavenode.c` dérive d'un exemple Microchip pour PIC16C72A — vérifier l'adéquation registres SSP avec le 16F946.

## Incident foudre 2026-08

- **Premier BA après le BP sur le site touché.** Il n'est relié que par un seul tronçon de 33 cm, d'environ 0,12 Ω en onde 8/20. Son seuil d'équilibrage est donc le plus haut des trois BA.
- **Mêmes faiblesses que les autres BA.**
  - Résistances série R1/R2 de 0 Ω : le PIC16F946 écrête avant les TVS D1/D2.
  - Rail « +12V » sans TVS : C2 tient 16 V, U1 24 V.
  - Désignateurs D1/D2, C2 et U1 relevés sur le SC940D : à vérifier sur le schéma DM de cette carte, qui diffère sur plusieurs repères (U5, U4, C42, R84/R85).
- **Désignateurs utiles.** PIC **U5**, NCP803 U4, pull-ups R51/R52, 0 Ω VBUS/GNDBUS R84/R85, empreinte **C42** pour la TVS de +Vin, ICSP J92. Adresse 0x12 (CHB).
- **Réparation.** PIC16F946 (U5) en approvisionnement tendu (Microchip en direct, stock) ; TVS en SMF5V0A-E3-08 ; lire l'EEPROM avant de remplacer le PIC. Détails sur [[Essensys Board Sc940]].
- **Firmware BA 1.8 prévu.** Chien de garde, gestion des erreurs SSP, NACK quand `CmdBuf` est occupé, octet d'état rétrocompatible.
- Voir [[Incident Foudre Bus I2C 2026 08]] et [[Ilots TBTS Et Equipotentialite]].

## Identité I2C

- Adresse **0x12**, figée à la compilation (`TYPE_CHAMBRES` dans `hard.h`). L'image `.hex` v1.7 du type a été vérifiée.
- Aucune configuration, aucun appairage. Les trois dépôts BA ont `hard.h` réglé sur `TYPE_CHAMBRES` : recompiler en vérifiant le type, ou ne flasher que le `.hex` livré.
- Voir [[Espion I2C Passif]].
- **Versions du firmware** : de 1.30 à 1.4, somme de contrôle 8 bits, incompatible avec le BP 099-37 ; CRC16 à partir de la v1.5. L'adresse ne change pas d'une version à l'autre. Au démarrage, le BA n'attend rien du BP, et sa LED DL1 clignote indépendamment de l'I2C. Voir [[Analyse Demarrage BP BA 2026 10]].

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-board-SC942C.md`
