---
tags: [entity, repo, hardware, kicad, foudre, i2c, tbts]
sources: [incidents/2026-08-foudre-bus-i2c/rapport-analyse.md]
created: 2026-10-12
updated: 2026-10-12
era: modern
repo: essensys-i2c-etoile-0v
---

# Essensys I2C Etoile 0v

> Carte passive N2 « étoile 0 V » sur rail DIN : relie le BP aux trois BA en étoile autour d'un plan 0 V, à la place du chaînage d'origine, pour relever le seuil du courant d'équilibrage qui a détruit le bus I2C lors de la foudre d'août 2026.

| | |
|---|---|
| **Catégorie** | Matériel – carte annexe (KiCad 9) |
| **Dépôt** | `essensys-hub/essensys-i2c-etoile-0v` (public) |
| **Statut** | Révision A conçue (schéma, BOM, Gerber, ERC/DRC 0 erreur), non fabriquée ; essais de banc à faire |
| **Change** | `i2c-surge-protection-2026-10-007`, tâche 4.1, ticket `essensys-hub/essensys-board-SC944D#1` |

## Rôle

Mesure de court terme décrite dans [[Ilots TBTS Et Equipotentialite]] (variante N2) à la suite de l'[[Incident Foudre Bus I2C 2026 08]]. Le bus du BP ([[Essensys Board Sc944d]], connecteur J31) arrive sur la carte et repart vers chaque BA ([[Essensys Board Sc940]], [[Essensys Board Sc941c]], [[Essensys Board Sc942c]]) par deux faisceaux AWG20 de 15 cm au plus (J1 et J2 du BA). Le 0 V du BP est doublé par une queue de cochon soudée sur la broche traversante J31-3.

## Contenu

- 110 × 68 mm, 2 couches, cuivre 2 oz, plan 0 V double face ; trous de fixation non reliés, support DIN isolant.
- Par port BA : cavalier 2×3 qui coupe SDA, SCL et +15 V (jamais le 0 V), PTC 1812 ≥ 30 V puis TVS SMAJ16A sur le +15 V.
- Connecteurs WR-MPC3 2×2 (1 SDA, 2 SCL, 3 0 V, 4 +15 V) ; empreinte et PTC à confirmer avant fabrication.
- Le 0 V TBTS n'est jamais relié au PE ; repérage « 0 V TBTS – NE PAS RELIER À LA TERRE ».

## Vérifications restantes

Tâches 4.2 (faisceaux < 60 mΩ), 4.3 (seuil d'équilibrage ≥ 4 fois la référence, ΔVg ≤ 0,05 V) et 4.4 (sélectivité des PTC), sur banc uniquement. Le modèle corrigé du change donne ≈ 80 à 120 A en 8/20 et ≈ 50 à 65 A en front rapide.

## Voir aussi

- [[Incident Foudre Bus I2C 2026 08]]
- [[Ilots TBTS Et Equipotentialite]]
- [[Protection Surtension Bus I2C]]
