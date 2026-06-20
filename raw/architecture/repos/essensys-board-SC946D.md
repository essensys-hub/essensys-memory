# essensys-board-SC946D

> Carte sirène d'alarme de la box domotique Essensys : génère et amplifie les signaux sonores d'alerte via un PIC24 et un amplificateur audio classe D 25 W.

**Catégorie :** Firmware carte électronique
**Stack :** Microchip PIC24F08KL201 (16 bits), langage C, compilateur Microchip C30/XC16, projet MPLAB X (`Sirene.X`)
**Statut :** Production – firmware Sirène v1.30 (19/02/2014), binaire `fw946_sirene_v1.30_chk_0x7122_14.02.19.hex`

## Rôle dans l'architecture Essensys
Le SC946D est la **sirène** du système d'alarme Essensys. À la demande du contrôleur central (SC944D) ou sur détection locale, elle produit un signal sonore d'alerte de forte puissance. Le firmware gère :
- la **génération du son** par **PWM** (signal audio de la sirène) ;
- l'**amplification** via un ampli classe D 25 W ;
- la **surveillance analogique** (ADC) pour le filtrage / la temporisation des bips (le changelog v1.30 mentionne un « correctif filtrage pendant 1 s bip après alarme ») ;
- la gestion d'interruptions pour la boucle temps réel.

## Stack technique & matériel (MCU, périphériques)
- **MCU :** PIC24F08KL201-I/SS (16 bits, 8 Ko Flash, 512 o SRAM, ADC) — réf. BOM `U4`. Cible déclarée `PIC24F08KL201` dans `nbproject/configurations.xml`.
- **Horloge :** oscillateur interne FRC + PLL (`FNOSC_FRCPLL`), ~16 MIPS (8 MHz ×4 PLL / 2).
- **Bits de config :** watchdog matériel activé (`FWDTEN_ON`), Brown-out 1,8 V, MCLR activé pour ICSP basse tension.
- **Amplificateur audio :** Texas Instruments **TPA3112D1PWP**, classe D, 8–26 V, **25 W** — réf. BOM `U3`.
- **Périphériques firmware :** `pwm.c` (génération audio), `adc.c` (mesures analogiques), `interrupt.c` (ISR), `config.c` (init).

## Structure du dépôt
- `SC946D/` – projet matériel Altium (schémas `SC946D_Alim+Batt`, `SC946D_Audio`, `SC946D_uC` ; PCB `SI946D.PcbDoc` ; variantes `SC946D.PrjPCBVariants`).
- `SC946D/Prog/Sirene2014_02_19/Sirene/Sirene.X/` – projet firmware MPLAB X :
  - `main.c` – point d'entrée, config bits, boucle principale ;
  - `pwm.c` / `pwm.h` – pilote audio sirène ;
  - `adc.c` / `adc.h` – acquisition analogique ;
  - `interrupt.c` / `interrupt.h` – routines d'interruption ;
  - `config.c` / `config.h`, `global_var.h` – configuration et variables globales.
- `SC946D/Prog/*.hex` – firmware compilé.
- `docs/` + `mkdocs.yml` – documentation MkDocs (FR, page `sirene.md` prévue) déjà générée.

## Build / Flash / Déploiement
- **Build :** MPLAB X + compilateur Microchip C30/XC16 (projet `Sirene.X`, `Makefile` généré).
- **Flash :** programmation ICSP du PIC24 (connecteur ICSP/PICkit) avec le `.hex` ; le checksum figure dans le nom du binaire (`chk_0x7122`).
- Watchdog activé en dur — penser au refresh dans la boucle principale.

## Intégrations (comment la carte communique)
- La sirène est un **actionneur d'alerte** commandé par le système d'alarme du contrôleur SC944D (le schéma `SDEC944-xD_Sirènes_(alim+commande+ouverture)` côté SC944D décrit l'alimentation, la commande et la détection d'ouverture/auto-protection des sirènes).
- Le firmware (PWM + ADC + amplificateur) gère localement le rendu sonore une fois l'alarme déclenchée ; il inclut une détection d'autoprotection (tamper) via les entrées d'ouverture.

## Points d'attention
- **MCU contraint** (8 Ko Flash, 512 o SRAM) : peu de marge ; le filtrage anti-rebond/bip est sensible (motif du correctif v1.30).
- Le watchdog matériel est activé en config — un blocage non rafraîchi provoque un reset (sécurité voulue pour une sirène).
- Pas de bus de données structuré côté sirène : la commande est essentiellement une activation/désactivation pilotée par le SC944D ; documenter précisément le protocole de déclenchement reste un point ouvert (cf. prompt de doc du dépôt).
- Amplificateur 25 W : attention au dimensionnement alimentation/batterie (schéma `Alim+Batt`).
