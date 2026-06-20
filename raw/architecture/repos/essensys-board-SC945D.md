# essensys-board-SC945D

> Carte IHM tactile murale de la box domotique Essensys : écran couleur 2,8" piloté par un contrôleur graphique 4D Systems PICASO-GFX2, interface utilisateur de l'installation.

**Catégorie :** Firmware carte électronique
**Stack :** ASIC graphique 4D Systems PICASO-GFX2 (cœur 4DGL), application en langage **4DGL** (4D Systems Workshop4 / ScreenDesigner), ressources sur carte µSD
**Statut :** Production – application IHM v `Main 1.0`, ressources écran `uSD IHM 2.0`, fiches de programmation v3 ; versions antérieures dans `Prog/_Archives`

## Rôle dans l'architecture Essensys
Le SC945D est l'**interface homme-machine** murale de l'installation. Il affiche et permet de contrôler l'ensemble du système domotique géré par le contrôleur central SC944D : chauffage, éclairages, volets, scénarios, alarme/mise en alerte, consommations (élec/eau/gaz), température/humidité/luminosité, date/heure, réveil, etc.

L'écran est **maître de la liaison** avec le contrôleur : il initie les requêtes de synchronisation, de lecture et d'écriture sur la **Table d'échange** du SC944D. Le fichier `IHM_ECHANGES.INC` est explicitement « Generated from SC944D TableEchange.h » : l'IHM et le contrôleur partagent donc le **même dictionnaire d'index** (ex. `Temperature_Salon=33`, `Eclairage_Salon=52`, `Conso_Eau=50`, commandes `Cmd_Reboot=9`, `Cmd_Go_To_Bootloader=7`…).

## Stack technique & matériel (MCU, périphériques)
- **Contrôleur graphique :** 4D Systems **PICASO-GFX2** (ASIC graphique + audio, moteur 4DGL embarqué) — réf. BOM `U10`.
- **Afficheur :** TFT tactile 2,8" 240×320, dalle résistive 4 fils, bus CPU 16 bits, rétro-éclairage 4 LED (réf. `AFFICHEUR_4DLCD28Q`, `U12`).
- **Périphériques carte (d'après schémas) :** écran tactile, audio (haut-parleur / buzzer), rétro-éclairage piloté, boutons-poussoirs, lecteur **carte SD** (stockage des écrans/ressources), interface de programmation.
- **Stockage applicatif :** carte µSD contenant les écrans compilés (`.4FN`, `.Gci`, `.Dat`) et le rapport UI (`essensys_ui_report.json`).

## Structure du dépôt
- `SC945D/` – projet matériel Altium (schémas `SC945D_Afficheur`, `Audio`, `Backlight`, `Touchscreen`, `Micro`, `SD_Card`, `Interface_BP_et_Prog`, `Alimentations` ; PCB `SI945D.PCBDOC`).
- `SC945D/Prog/Main 1.0/` – source de l'application 4DGL :
  - `_Main.4dg` – programme principal 4DGL ;
  - `IHM_ECHANGES.INC` – constantes des index de la Table d'échange (générées depuis le SC944D) ;
  - `IHM_ECRANS.INC`, `IHM_COULEURS.INC`, `IHM_DIVERS.INC` – définitions d'écrans, palette, divers.
- `SC945D/Prog/uSD IHM 2.0/` – ressources écran compilées pour la carte µSD (un fichier par écran : `Home`, `StpChfg`, `Alrm`, `ScnrJ*`, `Conso`, `Setup*`, …).
- `SC945D/Prog/*.PmmC` – firmware PmmC du PICASO (mise à jour du cœur graphique).
- `docs/` (incl. `firmware_logic.md`) + `mkdocs.yml` – documentation MkDocs (FR) déjà générée.

## Build / Flash / Déploiement
- **Outil :** 4D Systems **Workshop4** (mode ScreenDesigner / 4DGL) pour compiler `_Main.4dg` et les écrans.
- **Déploiement écran :** copie des ressources compilées (`uSD IHM 2.0`) sur une **carte µSD** insérée dans la carte ; le PICASO charge les écrans depuis la SD à l'exécution.
- **Mise à jour du cœur :** flash du fichier `.PmmC` dans le PICASO via l'interface de programmation (cf. fiche `Fiche de programmation SC945D v3.docx`).

## Intégrations (comment la carte communique)
- **Liaison série** (UART/RS-485 half-duplex) avec le contrôleur SC944D. L'écran est l'**initiateur** : trames `Qualifier + checksum XOR` pour synchronisation, lecture (`0x55/0x5A`) et écriture (`0xA5/0xAA`) d'index dans la Table d'échange (protocole détaillé dans `essensys_screen_protocol.md` côté SC944D).
- Aucune connectivité réseau propre : l'écran ne « voit » le serveur Essensys qu'à travers le contrôleur, via les valeurs de la Table d'échange.
- Les actions utilisateur (changer une consigne, lancer un scénario, armer l'alarme) deviennent des écritures d'index ; les retours d'état sont des lectures d'index.

## Points d'attention
- **Couplage fort au SC944D :** `IHM_ECHANGES.INC` est généré depuis `TableEchange.h` du contrôleur ; toute évolution de la table côté SC944D doit être régénérée ici, sinon les écrans lisent/écrivent les mauvaises variables.
- **Toolchain propriétaire 4D Systems** (Workshop4 / 4DGL) ; pas de chaîne open source équivalente.
- Les ressources écran sont des binaires opaques sur µSD (`.4FN`, `.Gci`, `.Dat`) ; la source éditable est `_Main.4dg` + les `.INC`.
- Plusieurs index de la table sont marqués « Non utilisé » (WIFI, GSM, FTP/SMTP…) : vestiges d'options non déployées, à ignorer.
