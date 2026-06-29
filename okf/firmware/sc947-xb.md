---
type: Firmware Board
title: Essensys Board SC947-xB
description: Détecteur de fuite d'eau autonome relié à l'écosystème armoire.
resource: file:///Users/nrineau/ESSENSYS/essensys-board-SC947-xB
tags: [essensys, firmware, armoire, legacy]
timestamp: 2026-06-28T19:07:32Z
repo: essensys-board-SC947-xB
layer: firmware
era: legacy
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Détecteur de fuite d'eau autonome relié à l'écosystème armoire.

# Position dans l'armoire

* [SC944D](/firmware/sc944d.md) joue le rôle de maître quand la fiche existe.
* Les cartes actionneurs et IHM participent à l'état partagé via [Table D Echange](/protocols/table-d-echange.md).
* Les backends modernes doivent préserver la compatibilité avec le comportement firmware legacy.

# Interfaces

* Dépôt : [Essensys Board Sc947 Xb](/systems/essensys-board-SC947-xB.md)
* Architecture : [Armoire Architecture](/synthesis/armoire-architecture.md)
* Protocole : [Legacy HTTP](/protocols/legacy-http.md) selon implication firmware.

# Code pointers

* `essensys-board-SC947-xB/README.md`

# Risques

* Compatibilité firmware et protocole à préserver.
* Vérifier les constantes d'indices avant toute modification affectant scénarios, alarmes, lumières ou volets.

# Citations

[1] [Repository concept](/systems/essensys-board-SC947-xB.md)
[2] [Wiki source](../../wiki/entities/essensys-board-sc947-xb.md)
<!-- END GENERATED CONTENT -->
