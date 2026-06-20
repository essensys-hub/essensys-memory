---
tags: [entity, repo, modern, firmware, hardware]
sources: [essensys-gcc.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-gcc
---

# Essensys GCC

> Chaîne de compilation (toolchain) libre et reproductible migrant le firmware Essensys de CodeWarrior/MPLAB vers GCC, avec build cross-compile sous Docker, tests host et CI GitHub Actions.

| | |
|---|---|
| **Catégorie** | Outillage (build / compilation firmware) |
| **Stack** | Docker · crosstool-NG → m68k-elf-gcc 14.2 (ColdFire MCF52259) · Microchip XC8 (PIC16F946) · GNU Make · C · Unity (tests) · MQX 4.x RTOS |
| **Statut** | Fonctionnel et actif — toolchain multi-cibles opérationnelle, builds BP/BA + tests câblés en CI (itérations récentes sur la compat MQX/GCC) |
| **Era** | modern |

## Rôle

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

## Intégrations

- **Submodules Git** (MQX, Unity) : indispensables, d'où `submodules: recursive` partout.
- **Microchip** : téléchargement de l'installeur XC8 depuis `ww1.microchip.com` au build (dépendance réseau externe, licence *Free* — non redistribuable, d'où le téléchargement dynamique).
- **GitHub Actions** : artefacts firmware publiés en sortie de pipeline (`.elf/.s19/.map/.hex`).
- **Cohérence système** : les firmwares produits ici (notamment BP/SC944D) consomment/émettent les actions véhiculées par la queue Redis Essensys ciblée dans `essensys-utils` ; les codes de carte (0x11/0x12/0x13) structurent le mapping des pièces.
- **Pas de dépendance à `essensys-base`** : ce dépôt utilise ses propres images Debian de build, distinctes de l'image runtime Alpine partagée.

## Structure

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
├── mqx/                  # MQX 4.x RTOS (submo

_… voir source complète dans raw/_

## Points d'attention

- **Reproductibilité vs poids du dépôt** : l'installeur XC8 (~98 Mo) et des `logs.zip` sont versionnés/présents dans l'arbre — alourdissent le clone ; à externaliser (release/artefact) idéalement, d'autant que XC8 est aussi téléchargé dynamiquement au build.
- **Dépendance réseau au build** : l'URL XC8 Microchip est codée en dur ; sa rupture ou un changement de version casserait le build BA. Prévoir un cache/miroir.
- **Migration encore en stabilisation** : les commits récents portent sur la **compatibilité MQX ↔ GCC** (`mqx_assert.h`, `cf_assert.c`, `psp_comp.h`, includes, multilib m68k, flags `-mcpu=52259`). Le portage ColdFire+MQX reste la partie la plus délicate.
- **Submodule MQX d'origine tierce** (`Mr-Shannon/Freescale_MQX_4_2`, non officiel Freescale/NXP) : pérennité/licence à surveiller.
- **Artefacts de migration** (`deep-research-report.md`, `prompt.md`, `job_*`) mêlés au code de prod : à ranger pour clarifier ce qui est source vs documentation d'effort.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-gcc.md`
