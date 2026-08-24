---
type: Protocol Contract
title: Bus I2C BP ↔ BA
description: Protocole propriétaire du bus I2C interne armoire entre carte maître SC944D et boîtiers auxiliaires.
tags: [essensys, protocol, firmware, armoire, i2c, legacy]
timestamp: 2026-08-24T18:04:33Z
era: legacy
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Bus interne de l'armoire reliant la carte maître [SC944D](/firmware/sc944d.md) (BP) aux boîtiers
auxiliaires [SC940](/firmware/sc940.md), [SC942C](/firmware/sc942c.md) et
[SC941C](/firmware/sc941c.md) (BA), qui portent les relais d'éclairage, les variateurs et les volets.
C'est le dernier maillon entre une action de la [Table D Echange](/protocols/table-d-echange.md) et la
commutation physique d'une sortie.

# Topologie

| Élément | Valeur | Source |
|---|---|---|
| Périphérique | `i2c0:`, mode polled, maître unique | `SC944D/.../H/application.h` |
| Fréquence | 50 kHz | `SC944D/.../C/ba_i2c.c` (`IO_IOCTL_I2C_SET_BAUD`) |
| Adresse station BP | `0x10` | `application.h` (`I2C_BUS_ADDRESS_BP`) |
| Adresses BA | `0x11` + numéro BA → `0x11` pièces de vie, `0x12` chambres, `0x13` pièces d'eau | `application.h`, `ba_i2c.c` |
| Temporisation imposée | 100 ms après chaque transaction | `ba_i2c.c` (`_time_delay(100)`) |

# Transaction

`START + addr(W)` → N octets → `repeated START + addr(R)` → 5 octets → `STOP`.

* Requête : `[code de trame][charge utile…][CRC-16 LO][CRC-16 HI]`.
* Réponse : `[écho du code][CRC de la requête LO][HI][CRC-16 de la réponse LO][HI]`.
* CRC-16/MODBUS : init `0xFFFF`, polynôme réfléchi `0xA001`, sans XOR final, transmis en little-endian
  (`SC944D/.../C/crc.c`).

# Codes de trame

| Code | Nom | Longueur sur le fil | Effet côté BA |
|---|---|---|---|
| `1` | `FORCAGE_SORTIES` | 11 octets | Masques éteindre/allumer lampes (16 bits), variateurs, volets sens 1 / sens 2 |
| `2` | `CONF_SORTIES` | 11 octets | Mode de chaque variateur (`& 0x07`), persisté en EEPROM |
| `3` | `TPS_EXTINCTION` | 19 octets | Temps maximal d'allumage par relais lampe, persisté en EEPROM |
| `4` | `TPS_ACTION` | 11 octets | Temps maximal de commande par volet, persisté en EEPROM |
| `5` | `ACTIONS` | 4 octets | Drapeaux globaux : secouru/sauvegarde, blocage volets, forçage allumage |

Sources : `SC944D/.../H/global.h` (`uc_TRAME_BA_*`), `SC942C/.../source/slavenode.c`
(`enum_CODE_TRAMES`, longueurs attendues et interprétation des champs).

# Règles de comportement

* Émission **sur changement** uniquement, jamais en polling périodique (`SC944D/.../C/ba.c`).
* Répétitions bornées en cas d'erreur, puis acquittement local du maître pour arrêter la répétition :
  une commande peut donc être abandonnée sans que le BA l'ait reçue.
* Priorités appliquées par le BA : extinction prioritaire sur allumage, montée prioritaire sur descente.

# Limites d'observabilité

* La réponse du BA prouve la réception et la validation CRC d'une trame, **pas** la commutation
  physique d'un relais.
* Les appuis locaux sur les boutons d'un BA sont traités localement et ne génèrent aucun trafic I2C.
* Les commandes de chauffage ne passent pas par ce bus (GPIO du SC944D).

# Liens

* [Armoire Architecture](/synthesis/armoire-architecture.md)
* [Table D Echange](/protocols/table-d-echange.md)
* Change OpenSpec sniffer passif : `essensys-i2c-ba-sniffer-2026-07-038`

# Citations

[1] [Armoire Architecture](/synthesis/armoire-architecture.md)
[2] [Table D Echange](/protocols/table-d-echange.md)
<!-- END GENERATED CONTENT -->
