# essensys-gcc

> Chaîne de compilation (toolchain) libre et reproductible migrant le firmware Essensys de CodeWarrior/MPLAB vers GCC, avec build cross-compile sous Docker, tests host et CI GitHub Actions.

**Catégorie :** Outillage (build / compilation firmware)
**Stack :** Docker · crosstool-NG → m68k-elf-gcc 14.2 (ColdFire MCF52259) · Microchip XC8 (PIC16F946) · GNU Make · C · Unity (tests) · MQX 4.x RTOS
**Statut :** Fonctionnel et actif — toolchain multi-cibles opérationnelle, builds BP/BA + tests câblés en CI (itérations récentes sur la compat MQX/GCC)

## Rôle dans l'architecture Essensys

Contrairement à ce que son nom pourrait laisser penser, `essensys-gcc` **n'est pas un simple wrapper de gcc** : c'est le **dépôt de build du firmware embarqué** d'Essensys. Son objectif est de **remplacer les chaînes propriétaires CodeWarrior (ColdFire) et MPLAB/MPLAB-X (PIC)** par une toolchain **GCC libre, reproductible et conteneurisée**, afin de pouvoir compiler les firmwares en CI sans licence propriétaire ni IDE.

Il produit les firmwares des cartes matérielles de la passerelle/des modules domotiques :

| Board   | MCU        | Rôle                              | Artefact              |
|---------|------------|-----------------------------------|-----------------------|
| SC944D  | MCF52259   | **BP** — passerelle Ethernet/MQ   | `BP_MQX_ETH.elf/.s19` |
| SC940   | PIC16F946  | **BA** — pièces de vie (0x11)     | `SC940.hex`           |
| SC941C  | PIC16F946  | **BA** — pièces d'eau (0x13)      | `SC941C.hex`          |
| SC942C  | PIC16F946  | **BA** — chambres (0x12)          | `SC942C.hex`          |

- **BP** (Board Principale) : carte ColdFire V2 MCF52259 sous **RTOS MQX 4.x**, assure la passerelle Ethernet et la file de messages (lien avec la queue Redis côté backend, cf. `essensys-utils`).
- **BA** (Board Annexe) : modules PIC16F946 par type de pièce, compilés avec XC8.

## Stack technique & dépendances

- **Conteneurisation** : `Dockerfile` multi-stage (`debian:bookworm-slim`).
  - *Stage 1 (toolchain-builder)* : compile **crosstool-NG 1.26.0** depuis les sources, puis génère le cross-toolchain **m68k-elf** (GCC 14.2.0, binutils 2.43, newlib 4.5, GDB 15.2) à partir de `ct-ng.config`.
  - *Stage 2 (essensys-builder)* : image finale = m68k-elf-gcc copié du stage 1 + **Microchip XC8 v3.10** (téléchargé dynamiquement, mode *Free*, installeur non redistribuable) + GCC host + `srecord`/`make`. `ENTRYPOINT []`, `CMD ["bash"]`, `WORKDIR /workspace`.
  - Argument `SKIP_XC8=1` pour builder l'image **sans XC8** (build BP seul, utilisé en CI).
- **Cible ColdFire** : `m68k-elf-gcc -mcpu=52259 -msoft-float`.
- **Build** : GNU Make top-level déléguant à `bp/` et `ba/`.
- **Tests host** : framework **Unity** (submodule), compilé avec le GCC de la machine (sans Docker).
- **RTOS** : **Freescale MQX 4.x** (submodule), avec une couche de compat CodeWarrior → GCC dans `bp/compat/` et des patches (`combined.patch`, `bp/patches/`).
- **Submodules** (`.gitmodules`) :
  - `mqx` → `https://github.com/Mr-Shannon/Freescale_MQX_4_2`
  - `tests/unity` → `https://github.com/ThrowTheSwitch/Unity`

## Structure du dépôt

```
.
├── Dockerfile            # Image multi-toolchain (m68k-elf-gcc + XC8 + host)
├── ct-ng.config          # Config crosstool-NG pour m68k-elf-gcc
├── build.sh              # Orchestrateur de build (copié dans l'image)
├── Makefile              # Build top-level → délègue à bp/ et ba/
├── combined.patch        # Patches MQX/compat appliqués au build
├── bp/                   # Firmware BP (MCF52259 + MQX)
│   ├── Makefile
│   ├── intflash.ld       # Linker script GNU ld
│   ├── compat/           # Couche de compatibilité CodeWarrior → GCC
│   ├── bsp/              # BSP adapté GCC (m52259evb)
│   ├── patches/
│   └── build/
├── ba/                   # Firmware BA (PIC16F946)
│   ├── Makefile
│   └── source/           # Sources applicatives
├── mqx/                  # MQX 4.x RTOS (submodule)
├── tests/
│   ├── unity/            # Framework Unity (submodule)
│   ├── stubs/            # Stubs hardware pour tests host
│   ├── bp/               # Tests unitaires BP (7 suites)
│   ├── ba/               # Tests unitaires BA (4 suites, 19 tests)
│   └── integration/      # Tests d'intégration (3 suites, 11 tests)
├── scripts/
│   └── validate.sh       # Validation structure + tests
├── docs/
│   └── phase0-checklist.md
└── .github/workflows/
    └── firmware.yml      # Pipeline CI
```

> Le dépôt embarque aussi des artefacts de travail volumineux : l'installeur `xc8-v3.10-full-install-linux-x64-installer.run` (~98 Mo), `logs.zip`/`logs_extracted/`, `deep-research-report.md`, `prompt.md`, `job_info.json` — traces d'une migration assistée (recherche/itérations) plutôt que sources de production.

## Build / Exécution / Déploiement

**Construction de l'image de build :**

```bash
docker build -t essensys-builder .            # avec XC8 (BP + BA)
docker build --build-arg SKIP_XC8=1 ...       # sans XC8 (BP seul)
```

**Compilation des firmwares (volume monté sur `/workspace`) :**

```bash
docker run --rm -v $(pwd):/workspace essensys-builder make -C /workspace all   # BP + BA
docker run --rm -v $(pwd):/workspace essensys-builder make -C /workspace bp    # BP seul
docker run --rm -v $(pwd):/workspace essensys-builder make -C /workspace ba    # 3 boards BA
```

**Tests (sur l'hôte, sans Docker) :**

```bash
make test                          # toutes les suites
make -C tests/bp run_tests
make -C tests/ba run_tests
make -C tests/integration run_tests
./scripts/validate.sh             # validation structure + tests
```

**CI/CD (`.github/workflows/firmware.yml`)** — déclenchée sur push `main`/`develop` et PR vers `main` :

1. **unit-tests** (host, rapide, sans Docker) : tests BP, BA et intégration, checkout avec `submodules: recursive`.
2. **build-bp** : build image Docker `--build-arg SKIP_XC8=1`, compile BP, rapporte la taille via `m68k-elf-size`, uploade `BP_MQX_ETH.elf/.s19/.map`.
3. **build-ba** (matrice SC940 / SC941C / SC942C) : compile chaque board, uploade les `.hex`.

## Intégrations

- **Submodules Git** (MQX, Unity) : indispensables, d'où `submodules: recursive` partout.
- **Microchip** : téléchargement de l'installeur XC8 depuis `ww1.microchip.com` au build (dépendance réseau externe, licence *Free* — non redistribuable, d'où le téléchargement dynamique).
- **GitHub Actions** : artefacts firmware publiés en sortie de pipeline (`.elf/.s19/.map/.hex`).
- **Cohérence système** : les firmwares produits ici (notamment BP/SC944D) consomment/émettent les actions véhiculées par la queue Redis Essensys ciblée dans `essensys-utils` ; les codes de carte (0x11/0x12/0x13) structurent le mapping des pièces.
- **Pas de dépendance à `essensys-base`** : ce dépôt utilise ses propres images Debian de build, distinctes de l'image runtime Alpine partagée.

## Points d'attention

- **Reproductibilité vs poids du dépôt** : l'installeur XC8 (~98 Mo) et des `logs.zip` sont versionnés/présents dans l'arbre — alourdissent le clone ; à externaliser (release/artefact) idéalement, d'autant que XC8 est aussi téléchargé dynamiquement au build.
- **Dépendance réseau au build** : l'URL XC8 Microchip est codée en dur ; sa rupture ou un changement de version casserait le build BA. Prévoir un cache/miroir.
- **Migration encore en stabilisation** : les commits récents portent sur la **compatibilité MQX ↔ GCC** (`mqx_assert.h`, `cf_assert.c`, `psp_comp.h`, includes, multilib m68k, flags `-mcpu=52259`). Le portage ColdFire+MQX reste la partie la plus délicate.
- **Submodule MQX d'origine tierce** (`Mr-Shannon/Freescale_MQX_4_2`, non officiel Freescale/NXP) : pérennité/licence à surveiller.
- **Artefacts de migration** (`deep-research-report.md`, `prompt.md`, `job_*`) mêlés au code de prod : à ranger pour clarifier ce qui est source vs documentation d'effort.
