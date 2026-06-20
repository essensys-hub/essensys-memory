# essensys-board-SC947-xB

> Carte détecteur de fuite d'eau (DFE) de la box domotique Essensys : petit capteur autonome à sonde résistive qui remonte une alerte de présence d'eau au système.

**Catégorie :** Firmware carte électronique
**Stack :** Microchip PIC12F1840 (8 bits, 8 broches), firmware compilé « DFE » (binaire `.hex` uniquement dans ce dépôt)
**Statut :** Production – binaire `DFE.X.production 01.03.2013 (959D).hex` ; sources C non incluses dans le dépôt (seul le firmware compilé est présent)

## Rôle dans l'architecture Essensys
Le SC947-xB est le **détecteur de fuite/présence d'eau** (DFE = Détecteur de Fuite d'Eau) de l'installation. Le chemin projet d'origine le confirme : `SC947_Detecteur_eau`. C'est un capteur dédié et bon marché bâti autour d'un microcontrôleur 8 pattes :
- une **sonde résistive** (électrodes) détecte la présence d'eau (le schéma mentionne « Resistive sensor ») ;
- le PIC mesure/temporise le signal (le schéma note des constantes RC, ex. « 100n + 47k → 34 Hz », « 100n + 10k → 159 Hz ») et déclenche une **alerte** lorsqu'une fuite est détectée.

La détection est ensuite remontée au reste du système domotique (contrôleur SC944D / sirène SC946D) pour traitement (alarme, notification, coupure d'eau côté installation).

## Stack technique & matériel (MCU, périphériques)
- **MCU :** Microchip **PIC12F1840-I** (8 bits, boîtier 8 broches, famille Enhanced Mid-Range) — identifié sur le schéma `SC947-0B_Schema_rev_c`.
- **Capteur :** sonde **résistive** (détection eau par variation de résistance entre électrodes).
- **Conditionnement :** étages RC (cellules ~34 Hz / ~159 Hz), diode de protection / zener (Vz ~5,6 V), source de courant faible (ib ≈ 17 µA) — d'après les annotations du schéma.
- **Programmation :** connecteur **ICSP standard (PICkit)**, ICSP basse tension (`RA3/MCLR`).

## Structure du dépôt
- `SC947-xB/` – projet matériel Altium (legacy 2011-2013) :
  - `Schema/SC947-0B_Schema_rev_b.PDF`, `_rev_c.PDF` – schémas électroniques ;
  - `SDEC947-xB_Schema.SchDoc`, `SDEC947-xB_Sommaire.SchDoc`, PCB `SI947B.PCBDOC` ;
  - `Gerbers/`, `GERBERS PLANCHE/`, `Fabrication/`, `Implantations/`, `Nomenclature/` (BOM `SC947B_BOM_Formaté.xlsx`), `STEP_3D/`, `PnP_Machine_CMS/` – dossier de fabrication complet.
  - `Prog/` – **firmware compilé uniquement** : `DFE.X.production 01.03.2013 (959D).hex` + `Fiche programmation SC947 v1.docx`.
- `LICENSE`, `README.md`, `docs_generation_prompt.md` – ce dépôt n'a pas encore de dossier `docs/` MkDocs généré.

## Build / Flash / Déploiement
- **Build :** projet d'origine MPLAB (firmware « DFE.X ») pour PIC12F1840 — **les sources C ne sont pas dans le dépôt**, seul le `.hex` de production est fourni.
- **Flash :** programmation ICSP du PIC12F1840 via PICkit (connecteur ICSP standard) avec le `.hex` ; le checksum `959D` est indiqué dans le nom du binaire. Voir `Prog/Fiche programmation SC947 v1.docx`.

## Intégrations (comment la carte communique)
- Capteur **terminal d'entrée** : il fournit une information de détection d'eau au système. Côté contrôleur SC944D, la détection de fuites apparaît dans les schémas (`SDEC944-xD_Machines_laver_1-2_(détection_fuites)`, arrosage/détection pluie), ce qui situe le DFE comme une entrée d'alarme « eau » du système.
- Pas de bus complexe embarqué : la carte délivre un signal d'état (présence d'eau) repris en entrée par le reste de l'installation.

## Points d'attention
- **Sources firmware absentes :** seul le binaire `DFE.hex` est versionné — pas de code C ni de mapping I/O à documenter dans ce dépôt ; les détails fonctionnels proviennent du schéma et de la fiche de programmation.
- **Dépôt le plus ancien** (fichiers 2011-2013) : matériel et toolchain legacy ; pas encore de site MkDocs généré (à créer comme pour les autres cartes).
- L'interface exacte de remontée d'alerte (filaire vers SC944D, niveau logique, polarité) doit être confirmée sur le schéma `rev_c` avant intégration.
