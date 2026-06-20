---
tags: [entity, repo, legacy, firmware, hardware]
sources: [essensys-board-SC944D.md]
created: 2026-06-20
updated: 2026-06-20
era: legacy
repo: essensys-board-SC944D
---

# Essensys Board Sc944d

> Carte contrôleur central (« client ») de la box domotique Essensys : cerveau Ethernet sous RTOS MQX qui agrège les boîtiers auxiliaires, dialogue avec le serveur Essensys et distribue les firmwares aux autres cartes.

| | |
|---|---|
| **Catégorie** | Firmware carte électronique |
| **Stack** | Freescale/NXP ColdFire MCF52259 (32 bits, 80 MHz, 512 Ko Flash, 64 Ko RAM), langage C, RTOS Freescale MQX 4.0, CodeWarrior |
| **Statut** | Production – build de référence `099-37` (`BP_MQX_ETH ... 099-37.elf_BOOT_CRC.S19`), versions serveur 34→37 archivées dans `Prog/_Archives` |
| **Era** | legacy |

## Rôle

Le SC944D est le **contrôleur central / passerelle** de l'installation domotique. C'est la seule carte connectée à Ethernet ; elle :
- pilote et interroge les **boîtiers auxiliaires** (BA) SC940/941/942 sur I²C ;
- dialogue avec l'**IHM** (écran tactile SC945D) en liaison série ;
- gère les fonctions domotiques de la maison : **alarme**, **chauffage / fil pilote**, **volets**, **scénarios**, **arrosage**, **télé-information** EDC (compteur électrique), **anémomètre**, **horodatage RTC**, **réveil** ;
- se connecte au **serveur Essensys** (HTTP + chiffrement) pour remonter les états, recevoir les actions/scénarios, et **télécharger les firmwares** (le sien et ceux des autres cartes) pour les redistribuer.

Toute l'installation s'articule autour d'une **Table d'échange** (`TableEchange.h` / `TableEchangeAcces.c`) indexée : chaque variable domotique (température, éclairage, consommation, état alarme…) a un index unique partagé avec l'écran et le serveur (voir le fichier généré côté SC945D `IHM_ECHANGES.INC`).

## Intégrations

_Non documenté._

## Structure

- `SC944D/` – projet matériel Altium (nombreux schémas `.SchDoc` par fonction : Coeur, Ethernet, Chargeur batterie, Fil pilote, Arrosage, Sirènes, Télé-information, Liaison IHM, Liaison boîtiers auxiliaires…), PCB `SI944D.PcbDoc`.
- `SC944D/Prog/099-37/BP_MQX_ETH/` – projet firmware CodeWarrior (cible `m52259evb`, configs Int_Flash Debug/Release, Ext_MRAM) :
  - `C/` – logique applicative : `main.c`, `ba.c` / `ba_i2c.c` (dialogue I²C avec les BA), `Ecran.c` (protocole écran), `Alarme.c`, `Chauffage.c`, `FilPilote.c`, `Scenario.c`, `Arrosage.c`, `TeleInfo.c`, `Anemo.c`, `Reveil.c`, `GestionDateHeure.c`, `TableEchangeAcces.c` / `TableEchangeFlash.c`, `bootloader.c`, `EepromSoft/Spi/AdresseMac.c`, `crc.c`, `Hard.c`.
  - `Ethernet/` – pile applicative serveur : `www.c` (tâche `Ethernet_task`),

_… voir source complète dans raw/_

## Points d'attention

- **Dépendance forte à MQX 4.0 / CodeWarrior** : environnement propriétaire Freescale ; le build Linux (`Dockerfile`) reste la voie à privilégier pour la reproductibilité.
- **Pièce maîtresse SPOF :** c'est le seul nœud réseau ; sa panne isole toute l'installation du serveur et coupe la coordination des BA et de l'écran.
- **Sécurité legacy :** AES Rijndael + MD5 maison ; schéma à auditer avant toute exposition réseau moderne.
- La Table d'échange est le contrat d'interface partagé avec l'écran et le serveur — toute renumérotation d'index doit être propagée à `IHM_ECHANGES.INC` (SC945D) et au serveur.
- Build « 099-37 » correspond à la version serveur 37 ; bien aligner version firmware ↔ version serveur.

## Liens

- [[Table D Echange]]
- [[Essensys Board SC945D]]
- [[Client Essensys Legacy]]

## Source

`raw/architecture/repos/essensys-board-SC944D.md`
