---
tags: [entity, repo, modern, firmware, hardware]
sources: [essensys-board-SC940.md, incidents/2026-08-foudre-bus-i2c/rapport-analyse.md]
created: 2026-06-20
updated: 2026-10-14
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
- Le module RF « Cœur » SC943-0C est documenté comme « probable » : protocole RF exact non confirmé dans ce dépôt (source : essensys-board-SC940.md, d'après `docs/Architecture_Overview.md`). **Contredit** par [[Rapport Analyse Foudre Bus I2C 2026 08]] (annexe E) : le SC943 est un module variateur à IGBT (voir [[Essensys Board Sc843d]]), et non un module RF. La doc du dépôt est à corriger (tâche 8.9 du change i2c-surge-protection-2026-10-007).

## Incident foudre 2026-08

- **SC940D (pièces de vie, 0x11) en bout de chaîne sur le site touché.**
  - Son seuil d'équilibrage est environ 3 fois plus bas que celui du SC942C.
  - Cela ne le désigne pas pour autant comme la carte défaillante.
- **R1/R2 = 0 Ω.**
  - La diode interne du PIC16F946 (RC7/RC6) conduit vers 5,5 V, avant que D1/D2 (SMF5V0A) ne claquent à 6,4 V, et sans aucune limite de courant.
  - Retouche prévue : 47 Ω anti-impulsion, ou 33 Ω selon l'écart de masse mesuré.
- **Rail « +12V » (14,3 V) sans TVS.**
  - C2 tient 16 V, D6 20 V et U1 (LMR12010) 24 V.
  - Le fil +15 V du bus peut porter U1 à 24 V dès un écart de masse d'environ 10 V.
  - Retouche prévue : C2 en 35 V, D6 en 40 V, PTC puis TVS après R79.
- **Isolement 230 V / TBT.** J1/J2 sont estimés à 2-3 mm du relais K1 (« Entrée »), et la varistance VR1 est voisine de J2. Un essai d'isolement à 500 V est obligatoire.
- **Firmware BA v1.7.**
  - Watchdog désactivé (`main.c:17`), et branche `else;` sans traitement d'erreur SSP (`slavenode.c:361`).
  - Un PIC bloqué tient SCL basse jusqu'à une coupure d'alimentation.
  - Ces points sont prévus en BA 1.8.
- **Réparation.**
  - D1/D2 se commandent en SMF5V0A-E3-08 (le suffixe GS08 n'est plus commandable).
  - Le PIC16F946 (U4) est en approvisionnement tendu : passer par Microchip en direct et constituer un stock.
  - Avant de remplacer un PIC qui répond encore, lire son EEPROM (bit CPD à vérifier). Après un changement de PIC, les variateurs repartent en mode gradateur par défaut.
- **Documentation.** Le rapport contredit la mention d'un module RF SC943 (voir « Points d'attention » plus haut).
- Voir [[Incident Foudre Bus I2C 2026 08]] et [[Ilots TBTS Et Equipotentialite]].

## Identité I2C

- Adresse **0x11**, figée à la compilation (`TYPE_PIECES_DE_VIE` dans `hard.h`). L'image `.hex` v1.7 du type a été vérifiée.
- Aucune configuration, aucun appairage. Les trois dépôts BA ont `hard.h` réglé sur `TYPE_CHAMBRES` : recompiler en vérifiant le type, ou ne flasher que le `.hex` livré.
- Voir [[Espion I2C Passif]].
- **Versions du firmware** : de 1.30 à 1.4, somme de contrôle 8 bits, incompatible avec le BP 099-37 ; CRC16 à partir de la v1.5. L'adresse ne change pas d'une version à l'autre. Au démarrage, le BA n'attend rien du BP, et sa LED DL1 clignote indépendamment de l'I2C. Voir [[Analyse Demarrage BP BA 2026 10]].

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-board-SC940.md`
