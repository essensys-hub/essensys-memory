---
tags: [entity, repo, modern, firmware, hardware]
sources: [essensys-board-SC946D.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-board-SC946D
---

# Essensys Board Sc946d

> Carte sirène d'alarme de la box domotique Essensys : génère et amplifie les signaux sonores d'alerte via un PIC24 et un amplificateur audio classe D 25 W.

| | |
|---|---|
| **Catégorie** | Firmware carte électronique |
| **Stack** | Microchip PIC24F08KL201 (16 bits), langage C, compilateur Microchip C30/XC16, projet MPLAB X (`Sirene.X`) |
| **Statut** | Production – firmware Sirène v1.30 (19/02/2014), binaire `fw946_sirene_v1.30_chk_0x7122_14.02.19.hex` |
| **Era** | modern |

## Rôle

Le SC946D est la **sirène** du système d'alarme Essensys. À la demande du contrôleur central (SC944D) ou sur détection locale, elle produit un signal sonore d'alerte de forte puissance. Le firmware gère :
- la **génération du son** par **PWM** (signal audio de la sirène) ;
- l'**amplification** via un ampli classe D 25 W ;
- la **surveillance analogique** (ADC) pour le filtrage / la temporisation des bips (le changelog v1.30 mentionne un « correctif filtrage pendant 1 s bip après alarme ») ;
- la gestion d'interruptions pour la boucle temps réel.

## Intégrations

_Non documenté._

## Structure

- `SC946D/` – projet matériel Altium (schémas `SC946D_Alim+Batt`, `SC946D_Audio`, `SC946D_uC` ; PCB `SI946D.PcbDoc` ; variantes `SC946D.PrjPCBVariants`).
- `SC946D/Prog/Sirene2014_02_19/Sirene/Sirene.X/` – projet firmware MPLAB X :
  - `main.c` – point d'entrée, config bits, boucle principale ;
  - `pwm.c` / `pwm.h` – pilote audio sirène ;
  - `adc.c` / `adc.h` – acquisition analogique ;
  - `interrupt.c` / `interrupt.h` – routines d'interruption ;
  - `config.c` / `config.h`, `global_var.h` – configuration et variables globales.
- `SC946D/Prog/*.hex` – firmware compilé.
- `docs/` + `mkdocs.yml` – documentation MkDocs (FR, page `sirene.md` prévue) déjà générée.

## Points d'attention

- **MCU contraint** (8 Ko Flash, 512 o SRAM) : peu de marge ; le filtrage anti-rebond/bip est sensible (motif du correctif v1.30).
- Le watchdog matériel est activé en config — un blocage non rafraîchi provoque un reset (sécurité voulue pour une sirène).
- Pas de bus de données structuré côté sirène : la commande est essentiellement une activation/désactivation pilotée par le SC944D ; documenter précisément le protocole de déclenchement reste un point ouvert (cf. prompt de doc du dépôt).
- Amplificateur 25 W : attention au dimensionnement alimentation/batterie (schéma `Alim+Batt`).

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-board-SC946D.md`
