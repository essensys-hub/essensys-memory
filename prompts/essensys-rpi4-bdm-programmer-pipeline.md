# Prompt : programmeur BDM Raspberry Pi 4 pour SC944D — backup + flash + pipeline GitHub Actions

Tu es un ingénieur **firmware embarqué bas niveau (ColdFire/BDM) + Linux embarqué (Raspberry Pi) + CI/CD (GitHub Actions) + sécurité**. Ta mission est de **concevoir et spécifier** (puis implémenter via **OpenSpec**, schema `spec-driven`) un **programmeur/lecteur BDM basé sur un Raspberry Pi 4** capable de :

1. **Extraire** le firmware actuellement en flash de la carte `essensys-board-SC944D` (MCF52259) et en faire un **backup vérifié** (recovery-grade) **avant toute écriture**.
2. **Programmer** en flash interne les images compilées par **`essensys-gcc`** (`BP_MQX_ETH.s19`), avec vérification par relecture.
3. Le tout piloté par un **pipeline GitHub Actions complet** : build (`essensys-gcc`) → artefact `.s19` versionné → déploiement matériel sur le Pi 4 (**self-hosted runner**) → flash → vérif → rapport, avec garde-fous anti-brick.

Respecte **library-first** (réutiliser des outils BDM open source éprouvés avant tout NIH), l'objectif **reproductibilité / non-interactif**, et la règle absolue : **jamais d'écriture avant un backup complet et vérifié**.

> ⚠️ Prompt de cadrage destiné à `/openspec-propose`. L'agent produit `proposal.md` → `design.md` → `specs/**` → `tasks.md`. Il peut aussi servir de plan d'exécution directe pour la partie POC.

---

## 0. Faits vérifiés (ne rien inventer par-dessus)

| Fait | Valeur | Source |
|------|--------|--------|
| MCU | **Freescale MCF52259CAG80**, ColdFire **V2**, 80 MHz | `essensys-doc/archi/hardware-sc944d.md` |
| Interface debug | **BDM ColdFire** (pas un JTAG générique) | `essensys-doc/archi/legacy-client-deployment.md §4` |
| Connecteur | **J33, barrette 2x5 (10 broches) 2.54 mm — « JTAG/BDM debug »** | `hardware-sc944d.md` (table connecteurs, ligne J33) |
| Programmeur historique | **P&E Micro BDM** + CodeWarrior (`.launch` `..._PEBDM.launch`) | `legacy-client-deployment.md §4` |
| Flash interne | 512 KB @ `0x00000000` | `hardware-sc944d.md`, `essensys-gcc/bp/intflash.ld` |
| Layout flash | Bootloader `0x0–0x3000` · en-tête `.APP_CRC/.APP_VERSION/.APP_JUMP` @ `0x3000` · vecteurs app @ `0x3010` · app `0x3000–0x7DFFF` · **persistance `Tb_Echange[]` @ `0x7E000` (4 KB, NOLOAD)** · FlashX spare `0x7F000` | `essensys-gcc/bp/intflash.ld`, `legacy-client-deployment.md` |
| CFM (sécurité flash) | Flash Configuration Field @ **`0x400`–`0x417`** ; Security Word (CFMSEC) @ **`0x414–0x417`**. ⚠️ « Enabling flash security **disables BDM communications** » (RM §18.4.3) | **corrigé par R1** depuis RM MCF52259 §18.4.3 (le prompt indiquait `0x40F` à tort) |
| Vérif bootloader | Post-reset : compare `.APP_CRC` @ `0x3000` vs CRC-16 calculé sur la zone app | `legacy-client-deployment.md`, `Ethernet/Download.c` |
| Sortie build | `essensys-gcc` → `BP_MQX_ETH-<VERSION>.s19` (S3, `--srec-forceS3 --srec-len=32`), `.elf`, `.map` | `essensys-gcc/bp/Makefile` |
| Versioning | `fw-vVERSION-TENTATIVE` (ex. `fw-v099-0000`), aligné logs OVH | mémoire `sc944d-ci-pipeline` |
| ⚠️ OpenOCD | **NE PAS supposer qu'OpenOCD gère cette cible** — support ColdFire BDM inexistant/marginal en amont. Outils cités : USBDM/P&E | `essensys-gcc/prompt.md` (« Ne pas supposer qu'OpenOCD fonctionne… utiliser USBDM ») |

**Dépendance dure — CRC-16** : les images `essensys-gcc` actuelles portent un **placeholder CRC** (`0x0102`) à `0x3000` ; le bootloader **rejettera** une image dont le CRC ne correspond pas. L'**injection CRC-16 post-link** (issue `essensys-gcc#14`) est un **pré-requis** avant de flasher via ce programmeur — à traiter dans le pipeline (§4).

---

## 0 bis. Autocritique — pièges à trancher AVANT OpenSpec

| # | Piège | Correction |
|---|-------|------------|
| **E1** | « JTAG générique + OpenOCD » | Cible = **BDM ColdFire V2**. OpenOCD amont ne le supporte pas. Choisir explicitement une pile BDM (voir §2 : pod USBDM/P&E **ou** bit-bang GPIO). |
| **E2** | Flasher directement le `.s19` d'`essensys-gcc` | **CRC placeholder** → bootloader rejette. Étape **injection CRC-16** obligatoire (issue #14) dans le pipeline avant flash. |
| **E3** | Mass-erase de toute la flash | **Efface le bootloader `0x0–0x3000`** → brick si tu n'as pas de quoi le reflasher. Par défaut : **erase/program de la zone app `0x3000–0x7DFFF` uniquement**, bootloader et persistance **préservés**. |
| **E4** | Écraser la zone persistance `0x7E000` | Contient `Tb_Echange[]` (état domotique). Ne pas l'effacer sauf reset volontaire d'état, documenté. |
| **E5** | Toucher au Flash Config Field `0x400` | Un mauvais Security Word CFM (`0x414–0x417`) **désactive le BDM** (RM §18.4.3) → carte non reprogrammable par BDM (déverrouillage backdoor complexe/risqué). **Interlock : bloquer toute écriture dans `0x400–0x417`** sauf procédure explicite documentée. |
| **E6** | Écrire avant backup | **Interdit.** Le flash-write est conditionné à l'existence d'un **backup complet 512 KB relu et vérifié (hash)**. Interlock logiciel. |
| **E7** | Bit-bang BDM sur Linux non-RT | Le timing BDM (horloge DSCLK synchrone) est sensible ; Linux standard n'est pas déterministe. Si bit-bang GPIO : évaluer `pigpio`/PIO/DMA ou noyau PREEMPT_RT, **ou** préférer un **pod matériel** (le MCU du pod gère le timing). |
| **E8** | Runner GitHub-hosted qui flashe | Impossible (pas d'accès HW). Il faut un **self-hosted runner sur le Pi 4**. → surface de sécurité (voir E9). |
| **E9** | Self-hosted runner exécutant des PR de forks | Un runner qui pilote du matériel **ne doit jamais** exécuter du code non fiable. Restreindre aux **tags/branches protégés**, jamais `pull_request` de forks ; environnement GitHub avec **reviewer obligatoire**. |
| **E10** | Niveaux électriques | MCF52259 I/O = **3.3 V**, RPi4 GPIO = 3.3 V (compatibles) mais prévoir **buffers/protection, masse commune, détection VDD cible**. Pas de 5 V sur les GPIO. |
| **E11** | Alimentation pendant flash | Coupure secteur en cours de programmation = brick. Prévoir alim stable + éventuellement onduleur/condensateur, et **reprise sûre** (re-vérifier avant de conclure). |
| **E12** | Legacy figé | Ne pas modifier le protocole firmware / la table d'échange / le bootloader. Ce programmeur est un **outil externe**, il n'altère pas le firmware. |

---

## 1. Objectifs produit

### 1.1 Livrables

1. **Programmeur BDM sur Pi 4** : matériel (câblage J33 ↔ GPIO/pod, buffers, brochage) + logiciel (pile BDM, CLI de haut niveau : `read-flash`, `erase-app`, `program`, `verify`, `reset`, `dump-info`).
2. **Chaîne de backup recovery-grade** : lecture **intégrale** des 512 KB → `backup-<serial>-<date>.{s19,bin}` + `sha256` + métadonnées (IDCODE/CSR MCU, version lue à `0x3002`). Stockage hors-machine (release asset / artefact / git-lfs).
3. **Chaîne de flash** : erase zone app → program `.s19` (CRC injecté) → **verify par relecture** → reset → confirmation boot (CRC bootloader OK).
4. **Injection CRC-16 post-link** (ou consommation de l'outil issu de `essensys-gcc#14`) intégrée au pipeline.
5. **Pipeline GitHub Actions** complet (§4) : build → artefact → flash matériel (self-hosted Pi 4) → vérif → rapport, avec gate d'approbation + **workflow de rollback** (reflash du backup).
6. **Doc** : montage matériel (brochage J33 sourcé du schéma), install runner, procédure recovery, `essensys-doc`.

### 1.2 Non-objectifs MVP

- Debug interactif GDB temps réel (nice-to-have Phase 2).
- Programmation de la flash SPI externe OTA (`SST25VF016B`) et de l'EEPROM SPI (`25AA02E48T` : MAC, clé serveur, code alarme) — **hors périmètre** BDM interne ; documenter que ces mémoires ne sont pas couvertes par le backup flash interne.
- Reflash du **bootloader** (Phase 2, exige backup bootloader validé + procédure recovery renforcée).
- Boundary-scan / test JTAG de production.

---

## 2. Architecture — deux pistes BDM à trancher dans `design.md`

Le Pi 4 doit parler **BDM ColdFire V2** au connecteur J33. Deux options, à évaluer avec recommandation :

### Piste 1 (recommandée MVP) — Pi 4 + pod BDM open source (USBDM/TBLCF) en USB
- Le **pod** (USBDM : hardware + firmware open source, supporte ColdFire V1/V2) gère le **timing BDM** ; le Pi 4 fait tourner les **utilitaires USBDM CLI** + un serveur GDB.
- ✅ Fiabilité timing déléguée au MCU du pod · ✅ outil éprouvé · ⚠️ dépend d'un pod (à sourcer/fabriquer).
- Vérifier : USBDM CLI headless sur ARM64 (Raspberry Pi OS 64-bit), commandes de lecture/écriture flash MCF5225x.

### Piste 2 (DIY, « reader/writer sur le Pi ») — bit-bang BDM sur GPIO
- Le Pi 4 pilote **directement** les signaux BDM (DSCLK, DSI, DSO, BKPT, RSTI, TCLK, GND, VDD-sense) via GPIO + buffers 3.3 V.
- Réutiliser l'existant : ancien driver Linux **BDM m68k / gdbproxy** (P&E/TBLCF/parallel), protocole BDM ColdFire documenté (RM MCF5225x §Debug).
- ⚠️ **Timing** : Linux non-RT → risque. Mitigations à évaluer : `pigpio`/DMA, PIO, PREEMPT_RT, ou co-processeur (RP2040/Pico en pont SPI↔BDM).
- ✅ Zéro pod, « fait maison » · ⚠️ effort et risque supérieurs.

**Décision à formaliser** : recommandation **Piste 1** pour un MVP fiable et un flash matériel en CI sans surprise ; **Piste 2** documentée comme objectif « full-DIY » Phase 2. Trancher explicitement dans `proposal.md`.

**Brochage J33 (à LEVER)** : le pinout exact des 10 broches n'est pas dans le code — l'**extraire du schéma** `essensys-board-SC944D/SC944D/SDEC944-xD_Coeur.SchDoc` (Altium). Tâche `tasks.md` : documenter le brochage J33 ↔ signaux BDM avant tout câblage. Ne pas deviner.

---

## 3. Flux fonctionnels (à détailler dans `design.md`)

### 3.1 Backup (toujours en premier)
```
Pi4 → BDM connect → halt CPU → lire IDCODE/CSR (identité MCU)
    → read flash 0x0..0x7FFFF (512 KB) → backup.bin + backup.s19
    → sha256 + métadonnées (version @0x3002, CRC @0x3000, date, serial)
    → PUSH hors-machine (release asset / artefact)  ← INTERLOCK: pas de write sans ça
```

### 3.2 Flash (zone app uniquement)
```
Pré-check: backup vérifié existe ? CRC-16 injecté dans le .s19 ? cible identifiée ?
  → erase secteurs 0x3000..0x7DFFF (PRÉSERVE 0x0-0x3000 bootloader ET 0x7E000 persistance)
  → program .s19 (app @ 0x3000+)
  → VERIFY: relire 0x3000..end et comparer octet à octet au .s19
  → reset → attendre boot → confirmer (bootloader CRC OK : device répond)
  → rapport (succès/échec, hashes, versions avant/après)
```

### 3.3 Rollback
```
workflow_dispatch rollback → reflasher le backup pré-flash correspondant → verify → reset
```

---

## 4. Pipeline GitHub Actions (cœur de la demande)

**Contrainte structurante** : les runners GitHub-hosted ne peuvent pas toucher le matériel → **self-hosted runner installé sur le Pi 4** (labels ex. `[self-hosted, rpi4, bdm, sc944d]`), branché en permanence au J33 d'une carte de test/cible.

### 4.1 Étapes

| Job | Runner | Rôle |
|-----|--------|------|
| `build` | ubuntu-latest (image `ghcr.io/essensys-hub/essensys-gcc/essensys-builder`) | `build.sh bp` → `BP_MQX_ETH-<tag>.s19/.elf/.map` |
| `crc-inject` | ubuntu-latest | Injecte le **CRC-16** à `0x3000` (outil issue #14) → `.s19` flashable + le publie en artefact |
| `flash` | **self-hosted rpi4** | (a) **backup** cible → artefact ; (b) erase app ; (c) program ; (d) **verify readback** ; (e) reset + smoke |
| `report` | ubuntu-latest | Résumé (versions avant/après, hashes, PASS/FAIL) ; commentaire/summary |

### 4.2 Déclencheurs & sécurité

- Trigger : **tag `fw-v*`** (aligné `essensys-gcc`) **ou** `workflow_dispatch` (choix cible + confirm).
- **Environnement GitHub `hardware-flash`** avec **reviewer obligatoire** (gate humain avant le job `flash`).
- **Jamais** de `pull_request` de forks sur le runner matériel (E9). Restreindre aux tags/branches protégés.
- Interlock `flash` : échoue si backup absent/non vérifié, si CRC non injecté, ou si l'IDCODE lu ≠ MCF52259 attendu.
- Secrets : aucun secret réseau requis (flash local) ; seul le token d'enregistrement runner. Ne rien logger de sensible.

### 4.3 Repos concernés
- **`essensys-gcc`** : le pipeline de flash peut vivre ici (proche du build) **ou** dans un nouveau repo `essensys-bdm-programmer` (outil + workflow de déploiement). À trancher (`proposal.md`). Recommandation : **nouveau repo `essensys-bdm-programmer`** (HW + soft Pi + workflow reusable), qui **consomme** l'artefact `.s19` d'`essensys-gcc` via `workflow_call`/release.
- **`essensys-doc`** : montage, recovery, runbook.
- **`essensys-memory`** : change OpenSpec + wiki/OKF + roadmap.

---

## 5. Décisions à trancher dans `proposal.md`

1. **Piste BDM** : pod USBDM (reco MVP) vs bit-bang GPIO (DIY Phase 2).
2. **Repo hôte** : nouveau `essensys-bdm-programmer` (reco) vs dans `essensys-gcc`.
3. **Périmètre erase** : zone app seule (reco, préserve bootloader+persistance) vs full-chip (exige backup+reflash bootloader).
4. **Injection CRC** : dépend de `essensys-gcc#14` — livrer l'outil CRC dans ce change ou consommer celui de #14 (reco : lever #14 d'abord, le pipeline en dépend).
5. **Cible CI** : une carte de test dédiée branchée au Pi 4 (reco) vs flash de cartes de prod (jamais en CI auto sans gate physique).

---

## 6. Intégration OpenSpec

- **Schema** `spec-driven`. **ID** : `essensys-rpi4-bdm-programmer-2026-07-0XX` (prochain numéro libre).
- **Artefacts** : `proposal.md` (décisions §5, **impact legacy = nul**, sécurité anti-brick), `design.md` (sous-sections **matériel Pi/BDM** / **logiciel programmeur** / **pipeline GitHub Actions** distinctes), `specs/bdm-programmer/spec.md` (exigences SHALL : backup-avant-write, verify-readback, préservation bootloader/persistance, interlocks), `specs/flash-pipeline/spec.md`, `tasks.md`.
- **`tasks.md` doit inclure** : extraction brochage J33 du schéma ; POC lecture flash (backup) ; POC flash app + verify ; injection CRC (lien #14) ; install self-hosted runner Pi 4 ; workflow build→crc→flash→report + rollback ; environnement `hardware-flash` + reviewer ; doc recovery ; **mettre à jour essensys-memory**.

### Definition of Done

- [ ] **Backup 512 KB relu et vérifié (sha256)** produit et stocké hors-machine **avant** toute écriture — interlock prouvé par test.
- [ ] Brochage J33 documenté depuis le schéma (pas deviné).
- [ ] Flash de la **zone app seule** ; bootloader `0x0-0x3000` et persistance `0x7E000` **intacts** (vérifié par relecture).
- [ ] Image flashée = `.s19` `essensys-gcc` avec **CRC-16 injecté** ; après reset, le bootloader valide le CRC et l'app démarre.
- [ ] Verify par relecture octet-à-octet OK ; rapport versions avant/après.
- [ ] Pipeline GitHub Actions : `build → crc-inject → flash (self-hosted Pi4) → report`, avec **gate reviewer** et **workflow de rollback** fonctionnels.
- [ ] Runner matériel **jamais** exposé aux PR de forks ; restreint tags/branches protégés.
- [ ] Aucune écriture en `0x400–0x40F` (CFM) non maîtrisée ; procédure recovery documentée.
- [ ] `essensys-memory` mis à jour (wiki + OKF + roadmap).

---

---

## 7. Exécution avec ruflo (agents `ruflo-core`)

Ce prompt peut être conduit par les **agents `ruflo-core`** (le plugin `ruflo-swarm`
n'étant pas installé, il n'y a pas d'orchestration « swarm » automatique : les
agents sont dispatchés séquentiellement, la coordination étant assurée par l'agent
principal). Découpage recommandé :

| Étape | Agent ruflo | Mandat | Sortie |
|-------|-------------|--------|--------|
| **R1 — Recherche / lever les inconnues** | `ruflo-core:researcher` | Extraire le **brochage J33** de `essensys-board-SC944D/SC944D/SDEC944-xD_Coeur.SchDoc` ; documenter le **protocole/registres/timing BDM** MCF5225x (RM NXP) ; valider la faisabilité **USBDM CLI sur Raspberry Pi OS 64-bit**. **Ne rien conclure sans source.** | Note factuelle « inconnues levées / restantes » |
| **C1 — Design OpenSpec** | `ruflo-core:coder` (ou skill `/openspec-propose`) | Produire `proposal.md`/`design.md`/`specs/**`/`tasks.md` à partir de ce prompt + la note R1 | Change OpenSpec `essensys-rpi4-bdm-programmer-2026-07-0XX` |
| **C2 — POC implémentation** | `ruflo-core:coder` | CLI programmeur (backup/erase/program/verify), injection CRC-16 (lien `essensys-gcc#14`), workflows GitHub Actions + rollback | Code + workflow dans `essensys-bdm-programmer` |
| **V1 — Revue anti-brick** | `ruflo-core:reviewer` | Vérifier les **interlocks de sécurité** : backup-avant-write, préservation bootloader `0x0-0x3000` + persistance `0x7E000`, non-écriture `0x400` (CFM), runner **jamais** exposé aux PR de forks | Rapport de revue bloquant |

**Règles pour tout agent ruflo sur ce prompt :**
- **Aucune écriture matérielle réelle** tant que le backup vérifié n'existe pas (interlock §0-bis E6) — vaut aussi pour tout POC.
- **Ne pas deviner** un brochage, un registre ou un timing BDM : marquer « à lever » avec la source (schéma Altium, RM MCF5225x, doc USBDM).
- Ne pas toucher au legacy / bootloader / table d'échange (E12).
- Respecter la condition d'arrêt : bloquer et rendre la main si une inconnue matérielle critique (brochage J33, timing) n'est pas levée — ne pas improviser sur du silicium.

**Comment lancer :**
- Enchaînement complet : dispatcher **R1** (`ruflo-core:researcher`) d'abord ; une fois la note d'inconnues rendue, dispatcher **C1** puis **C2** (`ruflo-core:coder`) ; enfin **V1** (`ruflo-core:reviewer`) sur le code produit.
- Raccourci « design seul » : lancer directement `/openspec-propose` avec ce prompt (les agents `coder`/`reviewer` interviennent ensuite sur l'implémentation du change).

---

### Point de départ pour l'agent

> Lance `/openspec-propose` avec ce prompt comme contexte (ou dispatche
> `ruflo-core:researcher` sur l'étape R1 du §7 en premier). Commence par formaliser les décisions §5 (recommandations par défaut sauf objection), affirme l'**impact legacy nul** et la **règle backup-avant-write** comme exigence SHALL non négociable. Rédige `design.md` en 3 sous-sections (matériel Pi/BDM · logiciel programmeur · pipeline Actions). **Ne devine aucun brochage** (J33 → schéma `SDEC944-xD_Coeur.SchDoc`) ni aucun registre/timing BDM — toute zone non vérifiée doit être marquée « à lever » avec la source à consulter (RM MCF5225x, schéma, doc USBDM). Rappelle que flasher dépend de l'injection CRC-16 (`essensys-gcc#14`).
