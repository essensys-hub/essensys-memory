## Context

La carte `essensys-board-SC944D` embarque un **Freescale MCF52259CAG80** (ColdFire V2, 80 MHz), flash
interne 512 KB @ `0x0`. Le layout flash (`essensys-gcc/bp/intflash.ld`) est : bootloader `0x0-0x3000` ·
en-tête `.APP_CRC/.APP_VERSION/.APP_JUMP` @ `0x3000` · vecteurs app @ `0x3010` · app `0x3000-0x7DFFF` ·
persistance `Tb_Echange[]` @ `0x7E000` (4 KB, NOLOAD) · FlashX spare `0x7F000`. Le seul chemin de
programmation existant est **P&E Micro BDM + CodeWarrior**, manuel. Ce design couvre trois plans
distincts : (a) le matériel Pi4↔BDM, (b) le logiciel programmeur, (c) le pipeline CI.

Toutes les affirmations factuelles ci-dessous sont sourcées du prompt de cadrage (§0) et de la note de
recherche R1 (phase gate, read-only, `bdm-R1-research-notes.md`). Tout ce qui n'a pas pu être vérifié par
R1 reste marqué **[À LEVER]** — ne pas deviner, ne pas résoudre par supposition.

---

## (a) Matériel — Pi 4 / connecteur BDM

### Connecteur J33 — brochage confirmé (source : R1, schéma Altium PDF page 5, feuille "Coeur")

Barrette 2×5, 2.54 mm, réf. `e2.54-D-L6`, libellée "JTAG/BDM debug" :

| Broche | Net Altium | Signal en mode BDM | Remarque |
|--------|-----------|---------------------|----------|
| 1 | `UC_TCLK` | TCLK | Rôle exact en BDM pur non requis par le protocole 3 fils (DSCLK/DSI/DSO) — **[À LEVER]** : câblage legacy JTAG/pod P&E ou usage réel par le pod historique ? À confirmer via doc P&E ou mesure passive (lecture seule, sans risque) |
| 2 | `UC_TMS/BKPT` | **BKPT** | Broche physique partagée TMS(JTAG)/BKPT(BDM), sélection par `JTAG_EN` |
| 3 | `UC_TDO/DSO` | **DSO** | Partagée TDO(JTAG)/DSO(BDM) |
| 4 | `UC_TDI/DSI` | **DSI** | Partagée TDI(JTAG)/DSI(BDM) |
| 5 | `UC_ALLPST` | ALLPST | ET logique de PST[3:0] ; assertée quand le cœur est halted (RM §33.2) |
| 6 | `UC_TRST/DSCLK` | **DSCLK** | Partagée TRST(JTAG)/DSCLK(BDM) — horloge série pilotée par l'hôte (le pod/Pi4 est maître) |
| 7 | `+3V3S` | VDD target (3.3V, sense) | Référence de niveau logique / détection présence cible — **pas** une alimentation à fournir par le pod |
| 8 | `UC_RESET` | RESET | Reset MCU |
| 9-10 | GND | GND | Masse commune obligatoire Pi4 ↔ cible |

**Jumper JC1 (sélecteur BDM/JTAG)** : découverte critique R1, même feuille schéma. Note explicite :
« Si 0 (JC1 monté) → BDM mode » / « Si 1 (JC1 non monté) → JTAG mode ». C'est le pin `JTAG_EN` du
MCF52259 qui sélectionne le comportement des broches partagées de J33. **Précondition absolue avant tout
câblage du pod** : vérifier/monter JC1 en position BDM sur la carte cible — sinon le pod verra les
signaux JTAG et non BDM.

**[À LEVER — bloquant avant câblage physique]** : position physique exacte de JC1 sur le PCB assemblé.
Non déterminable depuis le schéma seul ; à vérifier soit sur `Assembly Drawings_[No Variations].pdf`
(essensys-board-SC944D), soit par inspection visuelle directe d'une carte assemblée. Ne pas câbler avant
d'avoir confirmé ce point (tâche dédiée `tasks.md` §1).

### Niveaux électriques et alimentation

- MCF52259 I/O = 3.3 V ; RPi4 GPIO = 3.3 V natif → compatibles en direct pour un bit-bang GPIO (Piste 2),
  mais prévoir **buffers/protection** et **détection VDD cible** (broche 7, `+3V3S`) avant toute
  activité, pour éviter d'endommager le Pi si la cible est absente ou mal alimentée.
- Masse commune Pi4 ↔ cible obligatoire (broches 9-10).
- Pas de 5 V sur les GPIO.
- Alimentation stable de la carte cible pendant tout flash (E11 du prompt) : une coupure secteur en
  cours de programmation de la zone app peut corrompre l'image en cours d'écriture. Prévoir alimentation
  régulée dédiée à la carte de test CI, et une étape de **re-vérification systématique après toute
  coupure suspectée** avant de conclure à un flash réussi.

### Deux pistes matérielles pour parler BDM (à trancher — voir proposal.md D1)

**Piste 1 (recommandée MVP) — pod BDM externe (USBDM) en USB.** Le pod matériel gère le timing BDM
(DSCLK synchrone) ; le Pi 4 exécute uniquement les utilitaires côté hôte (CLI/scripts) et le stockage.
Le pod se câble à J33 (broches 2-6, 8-10 ; broche 1 TCLK et broche 7 sense selon confirmation pod).

**Piste 2 (DIY Phase 2) — bit-bang direct des GPIO Pi4.** Le Pi 4 pilote DSCLK/DSI/DSO/BKPT/RESET via
GPIO + buffers 3.3 V, en implémentant lui-même le protocole série BDM (voir (b) ci-dessous). Nécessite
soit `pigpio`/DMA/PIO, soit un noyau PREEMPT_RT, soit un co-processeur déterministe (RP2040/Pico en pont
SPI↔BDM, dont le PIO matériel est bien adapté à un protocole synchrone bit-level comme celui-ci).
Documentée comme alternative si Piste 1 échoue en POC (voir (b), USBDM ARM64 non validé).

---

## (b) Logiciel — programmeur BDM

### Protocole BDM ColdFire V2 (source : R1, MCF52259 Reference Manual Rev. 4, chapitre 33 "Debug Module")

- **Mode** : full-duplex synchrone. L'hôte (pod ou Pi4 en bit-bang) est **maître** et **doit générer
  DSCLK** ; le MCU est esclave.
- **Paquet** : 17 bits (1 bit statut/contrôle + 16 bits data), **MSB first**.
- **Fréquence** : DC à **PSTCLK/5** maximum. Contrainte réelle : synchronisation stricte à 2 cycles + pas
  de jitter dans l'échantillonnage, pas la vitesse absolue (le protocole tolère un débit très bas).
- **Séquence par bit** (5 cycles PSTCLK, RM Fig. 33-12) : C0 = DSI posé, C1/C2 = double synchronisation
  DSI (DSCLK haut), C3 = la machine à états change, C4 = DSO change. DSCLK doit être échantillonné bas
  entre chaque échange de bit.
- **Réponse "not-ready"** (S=1, data=0x0000) : nouveau transfert possible après 32 cycles processeur —
  très court en absolu (centaine de ns à 80 MHz), point de vigilance timing pour tout bit-bang (Piste 2).
- **Format trame réception (MCU→hôte)** : `S=0/data=xxxx` transfert valide ; `S=0/data=FFFF` Status OK ;
  `S=1/data=0000` not ready ; `S=1/data=0001` bus error ; `S=1/data=FFFF` commande illégale.
- **Format trame commande (hôte→MCU)** : mot d'opération 16 bits (`Operation[15:10]`, `R/W[8]`
  0=write/1=read, `Op Size[7:6]` 00=byte/01=word/10=longword, `A/D[3]`, `Register[2:0]`) + mots
  d'extension optionnels ; adresses en absolu 32 bits (2 mots d'extension, MSW first).

### Jeu de commandes utilisées (RM §33.4.1.5, Table 33-20)

| Commande | Opcode | État CPU | Usage |
|----------|--------|----------|-------|
| READ (byte/word/long) | `0x1900`/`0x1940`/`0x1980` | Steal | Backup 512 KB |
| WRITE (byte/word/long) | `0x1800`/`0x1840`/`0x1880` | Steal | Programmation flash |
| DUMP | `0x1D00/1D40/1D80` | Steal | Lecture blocs après READ initial |
| FILL | `0x1C00/1C40/1C80` | Steal | Écriture blocs après WRITE initial |
| GO | `0x0C00` | Halted | Reprise après programmation |
| RAREG/RDREG | `0x218{...}` | Halted | Lecture registres (identité / vérif halt) |
| RDMREG/WDMREG | `0x2D{...}`/`0x2C{...}` | Parallel | Accès CSR (config/status) |

READ/WRITE/DUMP/FILL fonctionnent en mode **Steal** (cycles volés, pas besoin de halter le CPU) — mais
pour un backup recovery-grade et un flash sûrs, le **halt via BKPT** reste la pratique retenue par ce
design, pour éviter toute race avec le firmware en cours d'exécution (cohérent avec E6/E11).

**Entrée BDM / halt (RM §33.4.1.1)** : le point d'entrée standard retenu est l'assertion de **BKPT dans
les 8 cycles suivant la néganation de RESET** — le CPU entre en halt avant tout démarrage du firmware, et
tous les registres/mémoire deviennent accessibles dès ce point. C'est l'entrée utilisée pour le backup
initial et pour le flash.

### Sécurité flash CFM — correction R1 par rapport au prompt initial

Le prompt (§0) indiquait un champ `0x400-0x40F`. **R1 corrige** depuis le RM (chapitre 18.3.1, Table
18-1) : le champ CFM Configuration Field fait en réalité **24 octets, `0x400-0x417`** :

| Offset | Contenu | Défaut usine |
|--------|---------|--------------|
| `0x400-0x407` | Backdoor Comparison Key | `0xFFFFFFFF_FFFFFFFF` |
| `0x408-0x40B` | Flash Protection Bytes (CFMPROT) | `0xFFFFFFFF` |
| `0x40C-0x40F` | Flash SUPV Access Bytes (CFMSACC) | `0xFFFFFFFF` |
| `0x410-0x413` | Flash DATA Access Bytes (CFMDACC) | `0xFFFFFFFF` |
| `0x414-0x417` | **Flash Security Word (CFMSEC)** | `0xFFFFFFFF` |

RM §18.4.3 (citation directe) : *« Enabling flash security disables BDM communications. »* Un mauvais
CFMSEC désactive donc le BDM — carte non reprogrammable par ce chemin (un déverrouillage backdoor existe,
RM §18.4.3.1-3, mais complexe/risqué et **hors MVP**, cf. `proposal.md` Non-Goals).
**Conséquence design** : l'interlock logiciel doit bloquer **toute** écriture dans `0x400-0x417`, pas
seulement `0x400-0x40F` — voir `specs/bdm-programmer/spec.md`.

**[À LEVER, non bloquant MVP]** : codes exacts SEC[1:0] (Table 18-7 du RM, non extraite par R1) ; détail
des registres CSR (RM §33.3.2) pour un identifiant MCU fiable en pré-check de cible — à extraire en phase
POC si un identifiant anti-mauvaise-cible plus riche que le CRC/version applicative est requis.

### CLI programmeur

Commandes exposées (non-interactif, scriptable CI) :

- `dump-info` : connecte, halte (BKPT post-reset), lit identité (version @0x3002, CRC @0x3000), affiche
  sans écrire.
- `backup` : lecture intégrale READ `0x0-0x7FFFF` (512 KB) → `.bin` + `.s19` + `sha256` + métadonnées ;
  échoue si la lecture est incomplète ou le hash ne peut être calculé ; **condition préalable dure** à
  toute commande d'écriture suivante.
- `erase-app` : erase des secteurs `0x3000-0x7DFFF` uniquement ; refuse toute plage en dehors.
- `program` : WRITE de l'image `.s19` (CRC-16 déjà injecté) dans `0x3000+` ; refuse si CRC placeholder
  détecté ou si une plage cible chevauche `0x400-0x417` ou `0x7E000+`.
- `verify` : relecture READ de la zone programmée, comparaison octet-à-octet avec le `.s19` source ;
  échec bloquant si divergence.
- `reset` : GO / négation RESET, attente boot, lecture post-boot pour confirmer que le bootloader valide
  le CRC applicatif.

### Faisabilité USBDM CLI sur Raspberry Pi OS 64-bit (ARM64) — [À LEVER, risque Piste 1]

**Statut R1 : partiellement levé.** Confirmé : USBDM supporte ColdFire V1-V4 (donc MCF52259/V2) ; un
programmeur en ligne de commande distinct du plugin Eclipse existe dans la distribution USBDM ; build
depuis les sources possible (`make -f MakeAll.mk all`). **Non confirmé, absence totale de preuve** :
support ARM64/aarch64/Raspberry Pi — la distribution binaire officielle ne couvre que i386/amd64, et les
dépendances de build (wxWidgets, TCL, Xerces-C) suggèrent un exécutable principal GUI plutôt qu'un CLI
headless pur. PEmicro (alternative propriétaire, `CPROGCFZ`/`CPROGCFV1`) n'a également aucune
documentation Linux ARM publique.

**Ce point est un risque non résolu, pas une conclusion positive ni négative.** Ce design ne tranche pas
par supposition : une tâche de **validation POC dédiée** est requise avant de committer opérationnellement
sur la Piste 1 (voir `tasks.md`). Trois issues possibles à cette validation, à documenter au moment du
POC :
1. USBDM se compile sur Raspberry Pi OS 64-bit et produit un exécutable de programmation utilisable en
   CLI headless → Piste 1 validée telle quelle.
2. Seul un exécutable GUI (wxWidgets) fonctionne → automatisation via script (moins propre pour un
   pipeline non-interactif, mais utilisable).
3. Ni l'un ni l'autre ne fonctionne de façon fiable en ARM64 → bascule vers la Piste 2 (bit-bang GPIO,
   protocole intégralement sourcé ci-dessus) ou vers un pod alternatif dont le protocole USB est
   documenté et ré-implémentable nativement en ARM64 (en acceptant le compromis NIH que le prompt
   cherche à éviter en dernier recours seulement).

---

## (c) Pipeline GitHub Actions

### Contrainte structurante

Les runners GitHub-hosted ne peuvent pas toucher le matériel → **runner self-hosted installé sur le
Pi 4**, labels `[self-hosted, rpi4, bdm, sc944d]`, branché en permanence à une **carte de test SC944D
dédiée** (jamais une carte de production, `proposal.md` D5).

### Jobs

| Job | Runner | Rôle |
|-----|--------|------|
| `build` | `ubuntu-latest` (image `ghcr.io/essensys-hub/essensys-gcc/essensys-builder`) | `build.sh bp` → `BP_MQX_ETH-<tag>.s19/.elf/.map` |
| `crc-inject` | `ubuntu-latest` | Injecte le CRC-16 à `0x3000` via l'outil issu de `essensys-gcc#14` → `.s19` flashable, publié en artefact |
| `flash` | **self-hosted `rpi4`** | (a) `backup` cible → artefact hors-machine ; (b) `erase-app` ; (c) `program` ; (d) `verify` (relecture) ; (e) `reset` + smoke boot |
| `report` | `ubuntu-latest` | Résumé versions avant/après, hashes, PASS/FAIL, commentaire/summary |

### Déclencheurs et sécurité

- Trigger : tag `fw-v*` (aligné `essensys-gcc`) ou `workflow_dispatch` (choix cible + confirmation
  explicite).
- **Environnement GitHub `hardware-flash`** avec **reviewer humain obligatoire** — gate bloquant avant le
  job `flash`.
- **Jamais** de déclenchement `pull_request` depuis un fork sur le runner matériel (E9). Restreint aux
  tags et branches protégées.
- Interlock `flash` (défense en profondeur, en plus des interlocks CLI de (b)) : le job échoue si le
  backup est absent ou non vérifié, si le CRC-16 n'est pas injecté, ou si l'IDCODE/identité lue ne
  correspond pas au MCF52259 attendu.
- Secrets : aucun secret réseau requis pour le flash local ; seul le token d'enregistrement du runner.
  Ne rien logger de sensible (pas de dump brut de flash en clair dans les logs CI — l'artefact backup est
  stocké, pas affiché).

### Rollback

`workflow_dispatch` dédié : sélectionne le backup pré-flash correspondant (par serial + date), le
reflashe intégralement sur la zone app, `verify`, `reset`. Documenté comme workflow séparé du flash
nominal pour éviter toute confusion entre "nouvelle version" et "restauration".

### Repos concernés

- **`essensys-bdm-programmer`** (nouveau) : héberge le programmeur (matériel + logiciel Pi) et les
  workflows de déploiement matériel — décision D2 de `proposal.md`.
- **`essensys-gcc`** : reste la source du `.s19` et de l'outil CRC-16 (`#14`), consommés via
  `workflow_call`/release par `essensys-bdm-programmer`.
- **`essensys-doc`** : montage matériel, recovery, runbook.
- **`essensys-memory`** : ce change OpenSpec, wiki/OKF/roadmap (voir `tasks.md` §8).
