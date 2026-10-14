---
tags: [entity, repo, outil, debug, i2c, sigrok, python, kicad, fritzing]
sources: [analyses/2026-10-cle-acces-distance/analyse.md]
created: 2026-10-13
updated: 2026-10-14
era: modern
repo: essensys-i2c-ba-sniffer
---

# Essensys I2C BA Sniffer

> Dépôt public `essensys-hub/essensys-i2c-ba-sniffer` : espion **strictement passif** du bus I2C BP ↔ BA. Il repose sur un analyseur logique USB (`fx2lafw`), `sigrok-cli` et un décodeur Python du protocole Essensys. La sonde à trois fils est documentée en KiCad et Fritzing. Voir [[Espion I2C Passif]].

## Rôle

L'outil dit **où** se perd une commande que le BP a acquittée auprès de la gateway :
- BA absent (NACK d'adresse) ;
- trame rejetée (écho CRC `00 00`) ;
- ligne SDA ou SCL bloquée ;
- abandon du maître après répétitions ;
- aucune trame émise.

Il rapproche aussi les journaux du backend CM5 (`Sending Actions` / `Action acknowledged`) des trames observées sur le bus.

## Structure

| Dossier | Contenu |
|---|---|
| `decoder/essensys_i2c_sniffer/` | Paquet Python ≥ 3.11 sans dépendance. CLI `essensys-i2c-sniff` (live, replay, annotations, correlate) |
| `captures/corpus/` | 10 scénarios synthétiques annotés par le décodeur I2C de sigrok (oracle), avec leur sortie NDJSON attendue |
| `tests/` | 76 tests, dont `NR-i2c-ba-sniffer-1` à `-6` |
| `hardware/kicad/` | Schéma câblé généré (ERC 0, KiCad 10). `check_netlist.py` vérifie en CI la netlist exportée |
| `hardware/fritzing/` | Deux croquis générés avec pièces embarquées : implantation sur plaque à pastilles, montage d'ensemble BA → sonde → FX2 → Raspberry Pi sur batterie |
| `hardware/mecanique/` | Boîtier J1 imprimable (CadQuery → STEP) : position 4 borgne, tours détrompées, verrou, capot, calibre de contacts |
| `openspec/changes/i2c-ba-sniffer-2026-10-009/` | Change OpenSpec : 6 capacités, 8 groupes de tâches |

## Points d'attention

- **Un seul flux brut**, partagé entre le décodeur I2C de sigrok et la détection des lignes bloquées. Le rejeu est identique au direct (fusion par numéro d'échantillon).
- Le décodeur `timing` de sigrok a été écarté : il ne donne pas le niveau de la ligne.
- **CI** : pytest avec sigrok sur Ubuntu, contrôle d'anonymisation, ERC KiCad dans `kicad/kicad:10.0`. L'image 9.0 n'ouvre pas un schéma dont les symboles viennent de la bibliothèque KiCad 10.
- **Fritzing** : les pièces sont dessinées par le générateur et embarquées dans le `.fzz` (90 px par pouce). Les fils passent toujours au-dessus des pièces : les jonctions soudées sont dessinées dans la plaque. Fritzing affiche le texte des notes en HTML, donc pas de `<->` dedans.
- **J2 de la sonde** : 1 +3,3 V, 2 SCL vers D0, 3 SDA vers D1, 4 0 V. Le +3,3 V vient de la broche 1 du GPIO du Pi, car l'analyseur en boîtier n'en fournit pas.

## Avancement au 2026-10-14

**En pause** en attendant les composants. 27 tâches sur 35 sont faites ; la feature est « En cours ».

Fait :
- décodeur, corpus et 76 tests (essensys-i2c-ba-sniffer#7, fusionnée) ;
- schémas corrigés après relecture critique (essensys-i2c-ba-sniffer#8, fusionnée) ;
- doc publiée sur www.essensys.fr/docs/debug/ (essensys-doc#10 et #11, déployées avec le seul rôle `docs_site`) ;
- boîtier J1 imprimable (essensys-i2c-ba-sniffer#9, ouverte, CI verte).

Matériel retenu :
- analyseur « 24 MHz 8CH » en boîtier, à puce Cypress FX2, reconnu par `fx2lafw` dans le paquet `sigrok-cli` (Debian et Raspberry Pi OS livrent libsigrok 0.5.2). Le LA1010 a été écarté : son pilote `kingst-la2016` n'existe pas dans libsigrok 0.5.2 ;
- composants de la sonde chez Farnell France : SP0502BAHTG (1827631), SN74LVC2G17DBVT en SOT-23-6, même brochage que le SC-70 (3119648), boîtier Würth 662004113322 (1641834) et fils pré-sertis Würth 662100124015 (2113330), donc sans pince à sertir. Les adaptateurs SOT-23-6 / SC70-6 vers DIP viennent d'ailleurs, faute de stock chez Farnell ;
- résistances 1 kΩ et 1 MΩ, barrette J2 : déjà en stock.

À la réception des pièces :
1. Banc sans armoire : Pi maître I2C et module ADS1115 (0x48). `i2cdetect -y 1` produit des ACK en 0x48 et des NACK en 0x11 à 0x13, ce qui imite des BA absents (tâches 6.1 et 6.2).
2. Montage de la sonde, puis contrôles à l'ohmmètre (tâche 5.5). Avec le boîtier Würth, boucher l'alvéole 4 à l'époxy.
3. Capture passive sur l'installation (tâche 6.4), puis `/checkup` (tâche 6.5).

Restent ouverts :
- photo du connecteur J1/J2 (tâche 5.1) et 8.2 ;
- essensys-doc#9 à fermer ;
- secret `PROJECT_SYNC_TOKEN` absent : la synchronisation du Project #6 est ignorée.

## Suivi

- Feature `i2c-ba-sniffer-2026-10-009`, ticket essensys-hub/essensys-feature-lifecycle#29, sous-issues essensys-i2c-ba-sniffer#1 à #6, essensys-doc#9, essensys-memory#16.
- Doc publique : `docs/debug/espion-i2c.md` dans [[Essensys DOC]] (www.essensys.fr/docs/debug/).
- Phase 2 (capture autonome sur Raspberry Pi Pico) : [[Essensys I2c Ba Sniffer 2026 07 038]]. Version permanente : module ESP32 de [[Essensys I2C Etoile 0v]].
