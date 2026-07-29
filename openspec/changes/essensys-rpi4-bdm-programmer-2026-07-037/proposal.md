## Why

La carte `essensys-board-SC944D` (MCF52259, ColdFire V2, flash interne 512 KB) n'a aujourd'hui qu'un
chemin de programmation historique : **P&E Micro BDM + CodeWarrior**, manuel, non reproductible, non
outillé en CI. `essensys-gcc` sait déjà produire `BP_MQX_ETH-<VERSION>.s19`, mais rien n'automatise
l'extraction d'un backup fiable de la flash existante ni la programmation vérifiée de la nouvelle image.
Le risque dominant est le **brick** : effacer/écraser le bootloader (`0x0-0x3000`), la persistance
domotique (`Tb_Echange[]` @ `0x7E000`), ou le champ de sécurité flash CFM (`0x400-0x417`, dont le
Security Word `0x414-0x417` **désactive le BDM** s'il est mal écrit — RM MCF52259 §18.4.3) sans backup
préalable vérifié.

Ce change spécifie un **programmeur BDM basé sur Raspberry Pi 4**, une chaîne de **backup
recovery-grade**, une chaîne de **flash zone-app avec verify par relecture**, et un **pipeline GitHub
Actions** (build → injection CRC-16 → flash matériel self-hosted → rapport) avec garde-fous anti-brick
et gate humain.

Ce document intègre les résultats de la note de recherche R1 (phase gate, read-only) : le brochage J33
est **entièrement levé** par lecture du schéma Altium (PDF), le protocole BDM ColdFire V2 est
**entièrement sourcé** du Reference Manual NXP officiel (chapitre 33), et la faisabilité d'USBDM CLI sur
ARM64/Raspberry Pi OS **reste non validée** — traitée ici comme un risque à lever en POC, pas comme un
fait acquis.

## What Changes

- Nouveau dépôt **`essensys-bdm-programmer`** : matériel (câblage J33 ↔ pod BDM), CLI programmeur
  (`read-flash` / `backup`, `erase-app`, `program`, `verify`, `reset`, `dump-info`), scripts d'injection
  CRC-16, workflows GitHub Actions et runbook recovery.
- **Chaîne de backup** (toujours en premier, interlock bloquant) : lecture intégrale 512 KB par BDM
  (commande READ, RM §33.4.1.5) → `backup-<serial>-<date>.{bin,s19}` + `sha256` + métadonnées (version
  @0x3002, CRC @0x3000, date) → export **hors-machine** (artefact CI / release asset) avant toute
  autorisation d'écriture.
- **Chaîne de flash** limitée à la **zone application `0x3000-0x7DFFF`** : erase → program (WRITE) →
  **verify par relecture octet-à-octet** → reset → confirmation boot (CRC bootloader OK). Bootloader
  `0x0-0x3000` et persistance `0x7E000` **jamais touchés** par ce MVP.
- **Interlock logiciel non-contournable** : blocage de toute écriture dans **`0x400-0x417`** (champ CFM
  complet, cf. correction R1 ci-dessous), et blocage du flash si backup absent/non vérifié ou CRC-16 non
  injecté.
- **Pipeline GitHub Actions** : `build` (essensys-gcc, ubuntu-latest) → `crc-inject` (consomme
  `essensys-gcc#14`) → `flash` (**self-hosted runner sur le Pi 4**, jamais exposé aux PR de forks) →
  `report`. Environnement GitHub `hardware-flash` avec **reviewer humain obligatoire** avant le job
  `flash`. Trigger : tag `fw-v*` ou `workflow_dispatch`.
- **Workflow de rollback** : reflash du backup pré-flash correspondant, verify, reset.
- Doc : brochage J33 sourcé du schéma, position physique du jumper JC1 (à confirmer sur carte
  assemblée), install runner, procédure recovery.
- **Correction factuelle vs le prompt initial** : le champ CFM de sécurité flash s'étend réellement de
  `0x400` à `0x417` (24 octets), pas `0x400-0x40F` comme indiqué au départ — le Security Word critique
  (`CFMSEC`) est à `0x414-0x417`, en dehors de la plage initialement citée. L'interlock d'écriture doit
  donc couvrir toute la plage `0x400-0x417`.

## Non-Goals (MVP)

- Debug interactif GDB temps réel (Phase 2).
- Programmation de la flash SPI externe OTA (`SST25VF016B`) et de l'EEPROM SPI (`25AA02E48T` : MAC, clé
  serveur, code alarme) — hors périmètre BDM interne ; documenter que ces mémoires ne sont pas couvertes
  par ce backup.
- Reflash du **bootloader** (`0x0-0x3000`) — Phase 2, exige un backup bootloader validé et une procédure
  recovery renforcée distincte.
- Boundary-scan / test JTAG de production.
- Déverrouillage backdoor CFM (RM §18.4.3.1-3) — hors MVP, documenté comme procédure de dernier recours
  séparée si un incident de sécurité flash survient malgré l'interlock.
- Piste 2 (bit-bang GPIO DIY) en implémentation — documentée dans `design.md` comme alternative Phase 2
  si la Piste 1 échoue en POC.

## Décisions (§5 du prompt de cadrage — tranchées)

### D1 — Piste BDM : pod USBDM (recommandé MVP), bit-bang GPIO en Phase 2

**Choix** : Piste 1 — Pi 4 + pod BDM open source (USBDM, supporte ColdFire V1-V4) en USB. Le pod gère le
timing BDM ; le Pi 4 pilote via CLI/scripts.
**Pourquoi** : fiabilité timing déléguée au MCU du pod, évite le risque de jitter Linux non-RT (E7),
outil éprouvé sur ColdFire V2.
**Réserve factuelle (R1)** : aucune distribution ni documentation USBDM ne mentionne ARM64/RPi (paquets
officiels i386/amd64 uniquement) ; le build depuis les sources dépend de libs GUI (wxWidgets, TCL,
Xerces-C) suggérant un exécutable principal non-headless. **La faisabilité n'est donc pas acquise** —
une tâche de validation POC dédiée est obligatoire avant de committer opérationnellement sur cette piste
(voir `tasks.md`, [À LEVER]).
**Alternative** : Piste 2 (bit-bang GPIO, éventuellement via co-processeur RP2040/PIO) reste documentée
comme repli Phase 2 ; le protocole exact (RM §33) est intégralement sourcé pour l'implémenter si besoin.

### D2 — Repo hôte : nouveau `essensys-bdm-programmer`

**Choix** : nouveau dépôt dédié (matériel + logiciel Pi + workflows), qui **consomme** l'artefact `.s19`
d'`essensys-gcc` via `workflow_call`/release, plutôt que d'ajouter ce périmètre dans `essensys-gcc`.
**Pourquoi** : sépare le cycle de vie build-firmware (essensys-gcc) du cycle de vie outillage-hardware
(BDM/Pi/CI-physique), évite de coupler les runners self-hosted à un repo de build générique.

### D3 — Périmètre erase : zone application seule

**Choix** : erase/program limités à `0x3000-0x7DFFF`. Bootloader `0x0-0x3000` et persistance `0x7E000`
préservés par défaut.
**Pourquoi** : un mass-erase efface le bootloader et bricke la carte sans backup bootloader ni procédure
de reflash bootloader (piège E3 du prompt). Le full-chip erase est explicitement **hors MVP**.

### D4 — Injection CRC-16 : dépendance externe, lever `essensys-gcc#14` d'abord

**Choix** : ce change **consomme** l'outil d'injection CRC-16 issu de `essensys-gcc#14` plutôt que d'en
livrer une réimplémentation. Le pipeline (`crc-inject`) appelle cet outil.
**Pourquoi** : évite la duplication de logique de calcul CRC-16 entre deux repos ; `essensys-gcc#14` est
un prérequis dur — sans lui, les images portent un CRC placeholder (`0x0102`) que le bootloader rejette.
**Conséquence tasks.md** : une tâche de blocage explicite tant que `essensys-gcc#14` n'est pas livré (ou,
à défaut, un stub d'injection CRC scoping-limité documenté comme dette).

### D5 — Cible CI : carte de test dédiée, jamais une carte de prod en CI automatique

**Choix** : le runner self-hosted Pi 4 reste branché en permanence à une **carte de test SC944D
dédiée**. Aucun flash de carte de production ne doit être déclenché par ce pipeline automatique ; un
flash de prod reste une opération manuelle hors CI ou un `workflow_dispatch` distinct avec gate renforcé
(hors MVP).
**Pourquoi** : élimine le risque de brick de parc en cas de bug de pipeline ; cohérent avec le principe
« self-hosted runner jamais exposé à du code non fiable » (E9) étendu à « jamais exposé à du matériel de
prod par défaut ».

## Impact legacy

**NUL.** Ce programmeur est un **outil externe** : il ne modifie ni le protocole firmware BP_MQX_ETH, ni
la table d'échange `Tb_Echange[]`, ni le bootloader, ni les endpoints legacy IoT
(`/api/serverinfos`, `mystatus`, `myactions`, `done`). Il lit/écrit la flash interne du MCU via BDM,
strictement dans la zone application, en préservant bootloader et persistance. Aucune règle de la table
d'échange n'est concernée.

## Capabilities

### New Capabilities

- `bdm-programmer` : CLI et matériel de programmation BDM Pi4→SC944D (backup, erase-app, program,
  verify, reset, dump-info) avec interlocks anti-brick.
- `flash-pipeline` : pipeline GitHub Actions build→crc-inject→flash(self-hosted)→report, avec
  environnement `hardware-flash` (gate reviewer) et workflow de rollback.

### Modified Capabilities

- _(aucune — pas de capability OpenSpec existante couvrant la programmation BDM SC944D)_

## Impact

| Zone | Impact |
|------|--------|
| `essensys-bdm-programmer` (nouveau repo) | CLI programmeur, câblage/brochage, workflows GitHub Actions, runbook recovery |
| `essensys-gcc` | Dépendance dure sur issue `#14` (injection CRC-16) ; consommation de l'artefact `.s19` versionné |
| `essensys-doc` | Doc montage matériel (brochage J33, jumper JC1), install runner, procédure recovery |
| `essensys-memory` | Ce change OpenSpec ; wiki/OKF/roadmap à mettre à jour (`tasks.md` §8) |
| Sécurité CI | Runner self-hosted Pi4, environnement `hardware-flash`, reviewer obligatoire, jamais de PR de forks |
| Matériel | Pod BDM (USBDM ou équivalent), carte de test SC944D dédiée, alimentation stable pendant flash |
