---
tags: [concept, i2c, debug, firmware, hardware, securite]
sources: [analyses/2026-10-cle-acces-distance/analyse.md]
created: 2026-10-13
updated: 2026-10-14
era: legacy
---

# Espion I2C Passif

Observer le bus I2C BP ↔ BA de l'armoire **sans jamais y émettre**, pour savoir ce que la gateway ne peut pas voir. Mise en œuvre : [[Essensys I2C BA Sniffer]]. Contexte : [[Ajout BP Gateway CM5]] et [[Incident Foudre Bus I2C 2026 08]].

## Identité des BA sur le bus

- Chaque BA a une adresse **figée à la compilation** de son firmware PIC (`TYPE_*` dans `hard.h`, puis `I2C_ADDR`, puis `SSPADD`) :
  - `0x11` pièces de vie ([[Essensys Board Sc940]]) ;
  - `0x12` chambres ([[Essensys Board Sc942c]]) ;
  - `0x13` pièces d'eau ([[Essensys Board Sc941c]]).

  Les trois images `.hex` v1.7 ont été vérifiées en décodant l'instruction qui charge `SSPADD`.
- Le BP ([[Essensys Board Sc944d]]) prend l'adresse `0x10` et appelle chaque BA en `0x11 + n`.
- Il n'y a ni appairage, ni n° de série, ni lien avec la [[Cle Acces Distance]].
- **Piège** : dans les trois dépôts BA, `hard.h` est réglé sur `TYPE_CHAMBRES`. Recompiler les sources SC940 produit donc un BA en `0x12`. Ne flasher que les `.hex` du bon type.

## Protocole observé

| Élément | Valeur |
|---|---|
| Transaction | `START addr(W)` → trame → repeated START `addr(R)` → 5 octets → `STOP` ; 100 ms entre transactions |
| Trame | `[code 1..5][charge utile][CRC16 LE]` ; longueurs 11 / 11 / 19 / 11 / 4 octets |
| CRC | CRC-16/MODBUS (`crc.c`), confirmé dans le code BP et BA |
| Réponse | `[écho code][écho CRC][CRC des 3 octets]` ; écho `00 00` si le BA a rejeté le CRC |
| Répétitions | défaut dans l'index 12 après 5 échecs, abandon après 20, puis un seul essai par nouvel ordre |

## Connecteur J1/J2 des BA

Würth 66200421122 (WR-MPC3 2×2, pas de 3 mm). Le boîtier femelle correspondant est le Würth 662004113322.

Brochage relu dans le fichier PCB d'origine (`SI940D.PcbDoc`) :
- 1 SDA, pastille carrée ;
- 2 SCL, à côté de la 1 ;
- 3 0 V (`GNDBUS`), sous la 1 ;
- 4 +15 V (`+VBUS`), **en diagonale de la 1, du côté de la rampe de verrouillage**.

Les logements de l'embase ont chacun un coin abattu, qui sert de détrompeur.

## Règles

- **Passif** : entrées seulement, 1 kΩ en série, aucune pull-up, jamais le +15 V. La position 4 du connecteur reste vide.
- **Aucun pont de masse** : hôte sur batterie, en Wi-Fi seulement, ou isolateur USB. Voir [[Ilots TBTS Et Equipotentialite]].
- **Hors tension** pour brancher, par une personne habilitée.
- **Ce qui ne prouve rien** :
  - « acquittée par le BP » ne veut pas dire « reçue par le BA » ;
  - « trame validée CRC » ne veut pas dire « sortie commutée ».

## Voir aussi

- [[Analyse Demarrage BP BA 2026 10]] : signatures attendues (NACK ou réponse `55 55`) et contrôles à faire sans espion
- [[Protection Surtension Bus I2C]]
- [[Essensys I2c Ba Sniffer 2026 07 038]] : phase 2 sur Pico
