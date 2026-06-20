# essensys-board-SC843D

> Module **gradateur** (variateur d'éclairage / dimmer) Essensys SC943D, à base d'un petit PIC 8 broches.

**Catégorie :** Firmware carte électronique
**Stack :** Microchip PIC12F1840-I/SN (8 bits) · firmware C compilé en `.hex` (binaire fourni, pas de sources C dans le dépôt) · matériel Altium Designer
**Statut :** Carte en production (firmware « Grad » v02, 2013). Dépôt matériel + binaire ; sources C non versionnées.

## Rôle dans l'architecture Essensys
Le SC843D / **SC943D** est un **module gradateur** (« Gradateur » d'après le schéma `SC943D_Sommaire`). Il assure la **variation de puissance d'une charge d'éclairage** (dimming). Dans l'écosystème Atrium, ce module SC943 est notamment réutilisé comme carte fille de communication/puissance sur les boîtiers d'actionneurs (le SC940D embarque par exemple un module dérivé « SC943-0C » comme cœur). Ici le dépôt documente le module SC943D autonome avec son firmware de gradation.

Le firmware embarqué (`Grad_V02_2013_05_03 (287A).hex`) implémente la logique de gradateur sur un microcontrôleur minimaliste 8 broches.

## Stack technique & matériel (MCU, périphériques)
- **MCU** : Microchip **PIC12F1840-I/SN** (8 bits, boîtier SO-8, 8 broches) — confirmé par la fiche de programmation.
- **Firmware** : binaire `Grad_V02_2013_05_03 (287A).hex` (checksum `287A`). Le nommage « Grad » désigne la fonction gradateur. **Aucun code source C n'est présent** dans le dépôt — seul le `.hex` est fourni.
- **Étage de puissance** : gradateur (commande de charge éclairage ; typiquement triac/coupure de phase — voir schéma `SC943D_Schema.SchDoc`).

## Structure du dépôt
- `SC943D/` — projet matériel Altium Designer.
  - `SC943D_Schema.SchDoc`, `SC943D_Sommaire.SchDoc` (mention « Gradateur »).
  - `SC943D.SCHLIB`, `SI943D.PCBDOC` (+ `.htm`), `SC943D.PrjPcb`, `SC943D.OutJob`.
  - `Gerbers/`, `Assembly/`, `Checks/`, `3D/`, `__Previews/`, `SI943D working gerber.rar`.
- `SC943D/Prog/` — firmware.
  - `Grad_V02_2013_05_03 (287A).hex` (binaire de production).
  - `Fiche programmation SC943 v1.docx` (procédure de flash).
- `README.md` (minimal), `LICENSE`.

> Note : le dépôt s'appelle `essensys-board-SC843D` mais tout le contenu (projet, fichiers, fiche) porte la référence **SC943D** — il s'agit du même produit (vraisemblablement un alias/typo de nommage de dépôt).

## Build / Flash / Déploiement
Procédure de programmation (d'après `Fiche programmation SC943 v1.docx`) :
1. Outils : **MPLAB IPE** + **PICkit 3** avec l'outil de programmation PIC SO-8.
2. Activer le mode avancé (`Settings → Advanced mode`, mot de passe `Microchip`).
3. Onglet `Power` : cocher « Power Target Circuit from Tool ».
4. Onglet `Production Mode` : `Reset Counters`.
5. Onglet `Operate` : sélectionner le device **PIC12F1840**, charger le `.hex`, **vérifier que le checksum affiché correspond à celui entre parenthèses dans le nom du fichier** (sinon mauvais device sélectionné).
6. `Connect` puis `Program` (un verify est inclus).

Pas de build à partir des sources possible depuis ce dépôt (sources C absentes).

## Intégrations (comment la carte communique)
- Module de **gradation de charge éclairage** ; commande locale de la puissance délivrée à la lampe.
- Réutilisé comme **sous-module SC943** intégré sur les cartes d'actionneurs Atrium (cf. le module « cœur » SC943-0C du SC940D).
- Le protocole/bus exact d'intégration n'est pas documenté dans ce dépôt (pas de sources) ; l'interface se déduit du schéma `SC943D_Schema.SchDoc`.

## Points d'attention
- **Sources firmware absentes** : seule la version binaire `.hex` v02 (2013) est disponible — toute évolution logicielle nécessite de retrouver les sources hors dépôt.
- **Incohérence de nommage** dépôt (`SC843D`) vs contenu (`SC943D`).
- Flash dépendant d'outils Microchip spécifiques (PICkit 3, support SO-8) et de la vérification de checksum.
- Firmware ancien (2013) ; MCU 8 broches très contraint en ressources.
