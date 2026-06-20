---
tags: [entity, repo, legacy, firmware, hardware]
sources: [essensys-board-SC947-xB.md]
created: 2026-06-20
updated: 2026-06-20
era: legacy
repo: essensys-board-SC947-xB
---

# Essensys Board Sc947 XB

> Carte détecteur de fuite d'eau (DFE) de la box domotique Essensys : petit capteur autonome à sonde résistive qui remonte une alerte de présence d'eau au système.

| | |
|---|---|
| **Catégorie** | Firmware carte électronique |
| **Stack** | Microchip PIC12F1840 (8 bits, 8 broches), firmware compilé « DFE » (binaire `.hex` uniquement dans ce dépôt) |
| **Statut** | Production – binaire `DFE.X.production 01.03.2013 (959D).hex` ; sources C non incluses dans le dépôt (seul le firmware compilé est présent) |
| **Era** | legacy |

## Rôle

Le SC947-xB est le **détecteur de fuite/présence d'eau** (DFE = Détecteur de Fuite d'Eau) de l'installation. Le chemin projet d'origine le confirme : `SC947_Detecteur_eau`. C'est un capteur dédié et bon marché bâti autour d'un microcontrôleur 8 pattes :
- une **sonde résistive** (électrodes) détecte la présence d'eau (le schéma mentionne « Resistive sensor ») ;
- le PIC mesure/temporise le signal (le schéma note des constantes RC, ex. « 100n + 47k → 34 Hz », « 100n + 10k → 159 Hz ») et déclenche une **alerte** lorsqu'une fuite est détectée.

La détection est ensuite remontée au reste du système domotique (contrôleur SC944D / sirène SC946D) pour traitement (alarme, notification, coupure d'eau côté installation).

## Intégrations

_Non documenté._

## Structure

- `SC947-xB/` – projet matériel Altium (legacy 2011-2013) :
  - `Schema/SC947-0B_Schema_rev_b.PDF`, `_rev_c.PDF` – schémas électroniques ;
  - `SDEC947-xB_Schema.SchDoc`, `SDEC947-xB_Sommaire.SchDoc`, PCB `SI947B.PCBDOC` ;
  - `Gerbers/`, `GERBERS PLANCHE/`, `Fabrication/`, `Implantations/`, `Nomenclature/` (BOM `SC947B_BOM_Formaté.xlsx`), `STEP_3D/`, `PnP_Machine_CMS/` – dossier de fabrication complet.
  - `Prog/` – **firmware compilé uniquement** : `DFE.X.production 01.03.2013 (959D).hex` + `Fiche programmation SC947 v1.docx`.
- `LICENSE`, `README.md`, `docs_generation_prompt.md` – ce dépôt n'a pas encore de dossier `docs/` MkDocs généré.

## Points d'attention

- **Sources firmware absentes :** seul le binaire `DFE.hex` est versionné — pas de code C ni de mapping I/O à documenter dans ce dépôt ; les détails fonctionnels proviennent du schéma et de la fiche de programmation.
- **Dépôt le plus ancien** (fichiers 2011-2013) : matériel et toolchain legacy ; pas encore de site MkDocs généré (à créer comme pour les autres cartes).
- L'interface exacte de remontée d'alerte (filaire vers SC944D, niveau logique, polarité) doit être confirmée sur le schéma `rev_c` avant intégration.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-board-SC947-xB.md`
