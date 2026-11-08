---
tags: [synthesis, feature, domotique, unifi, sonnette, lumieres, gateway, push, cloud, notifications]
sources: [openspec/changes/sonnette-unifi-2026-11-007/design.md, openspec/changes/sonnette-plages-push-2026-11-008/design.md]
created: 2026-11-08
updated: 2026-11-08
---

# Sonnette Unifi

> Feature `sonnette-unifi-2026-11-007` (ticket essensys-hub/essensys-feature-lifecycle#58, sous-ticket essensys-hub/essensys-memory#32) : quand la sonnette UniFi est pressée, le portail local de la CM5 affiche la vidéo de la caméra et la gateway fait clignoter des lumières choisies, qui finissent allumées. Prolonge [[Noms Personnalises Lumieres]] (#41) et [[Affichage Objets]] (#55).

## Constat

La gateway embarque déjà un client UniFi Protect (`internal/unifi`, bloc de configuration `unifi:`) mais ne reçoit aucun événement. Les lumières se commandent par des écritures dans la [[Table D Echange]] (bits 605 à 622) que l'armoire lit à son rythme. Fonction **locale** dans #58 ; #61 (plus bas) ajoute les plages, le signalement au cloud et les notifications push.

## Événement

Source : l'API d'intégration UniFi Protect (clé d'API déjà supportée) ; la gateway filtre l'événement de sonnette (`ring`) de la caméra choisie. Si la console ne l'expose pas, **repli par interrogation** de l'état toutes les 2 s. Les deux sources sont derrière une même interface ; un essai de faisabilité en lecture seule tranche (tâche 1.1, fait par Nicolas sur la console réelle). Console injoignable ou UniFi désactivé : la gateway fonctionne normalement, `available` vaut faux, reconnexion avec attente de 1 à 60 s. Aucune adresse ni clé n'est journalisée.

## Vidéo

Le navigateur ne lit pas le RTSPS. Version 1 : suite d'**instantanés, environ une image par seconde**, servie par la gateway (`GET /api/doorbell/stream`, `GetCameraSnapshot`) derrière l'authentification ; la clé d'API ne quitte jamais la gateway. Un transcodage ffmpeg vers HLS serait préférable mais hors de ce ticket.

## Clignotement, sans restauration

Décision de Nicolas : la gateway ne peut pas lire l'état réel des lumières, donc **pas de restauration**. Pour chaque lumière choisie : alternance éteint puis allumé `blinks` fois (1 à 10, phase d'au moins 2 s car l'armoire lit les ordres lentement), et la séquence **termine allumée**. Limite assumée : une lumière éteinte avant la sonnerie reste allumée. Aucune autre lumière ni aucun volet n'est touché. Une seule séquence à la fois ; une pression pendant une séquence met à jour `ringing` et `last_ring_at` sans relancer de clignotement, de même dans les 30 s qui suivent son début. Une commande manuelle sur une lumière en cours de clignotement l'exclut de la séquence (son ordre n'est pas écrasé). `ringing` reste vrai 60 s.

## Réglages dans le fichier existant

Section `doorbell` du fichier de `light_names.path` : `{"enabled","camera_id","lights","blinks","version","updated_at","updated_by"}`. Défaut : désactivé, aucune lumière, 5 clignotements. Même magasin à sections brutes, même verrou et même écriture atomique que les noms et les dispositions : écrire une section préserve les autres. **Aucune nouvelle clé de chemin** : le déploiement de l'armoire ne change pas pour ce fichier ([[Essensys Server Backend]]).

## Routes (gateway uniquement)

- Utilisateur authentifié (ouvert si l'IAM LAN est désactivé) : `GET /api/doorbell/status` (`enabled`, `available`, `ringing`, `ringing_until`, `last_ring_at`), `GET /api/doorbell/stream`.
- Administrateur : `GET/PUT /api/admin/doorbell/settings`, `POST /api/admin/doorbell/test` (essai à sec avec l'en-tête `X-Essensys-Test-Mode: dry-run`, aucune écriture dans l'armoire).
- `POST .../test` répond `{"status":"started"|"dry_run","ringing","ringing_until","sequence","lights"}` ; un essai à sec n'arme pas l'anti-rafale. La réponse administrateur des réglages contient `updated_by`, pas celles de `lan_user`. Le flux est une image affichable par `<img>` (le portail ajoute `?ring=<clé>`, ignoré par la gateway).
- Erreurs : 400 `invalid_settings` (corps illisible ou sans `enabled`, `camera_id`, `lights`), 400 `invalid_blinks` (absent, mal typé, hors 1 à 10), `unknown_light`, `unknown_camera`, 503 `names_unavailable`, 503 `doorbell_unavailable`.

Le portail interroge l'état toutes les 2 s fenêtre ouverte, 5 s sinon ([[Essensys Server Frontend]]).

## Limites et risques

- Instantanés environ 1 image par seconde, sans son : pas une vidéo fluide, à annoncer.
- Clignotement lent, limité par la cadence de lecture de l'armoire.
- Le clignotement écrit dans l'armoire réelle : seul l'essai administrateur et la vraie sonnette le déclenchent, jamais les tests automatiques.
- Une seule caméra de sonnette suivie.
- Dépôts publics : adresse de la console, clé et identifiant de caméra vivent dans la configuration déployée (SOPS), jamais dans les dépôts.

## Plages horaires, signalement et notifications push (Feature `sonnette-plages-push-2026-11-008`)

Ticket essensys-hub/essensys-feature-lifecycle#61, sous-ticket essensys-hub/essensys-memory#34. Prolonge #58. Avant : la sonnette clignotait à toute heure et ne prévenait que sur le réseau de la maison ; aucune notification push n'existait dans les apps ni dans le cloud.

### Décisions

- **La gateway décide, le cloud relaie.** La plage est évaluée sur la CM5 à l'instant de l'appui ; le cloud ne connaît pas la grille et notifie pour chaque appui reçu.
- **Push via le cloud** : FCM (Android) et APNs (iPhone) depuis [[Essensys User Portal Backend]], jamais depuis la gateway ni les apps.
- **La fenêtre vidéo locale reste active hors plage** : quelqu'un à la maison veut voir qui sonne. Hors plage, seuls le clignotement et le signalement au cloud sont coupés ; l'état expose `in_window`. « Essayer » ignore la plage.
- **Notification en opt-in par appareil** : `doorbell_notify` vaut faux par défaut.

### Plages 7×24 et fuseau

Section `doorbell.schedule` du même fichier gateway (aucune nouvelle clé de chemin) : `{"mode":"always"|"custom","timezone":"<nom IANA>","grid":[7 chaînes de 24 caractères 0/1]}`. `grid[0]` = lundi ; le caractère `h` = heure locale `h` à `h+1`. Sans section : `mode=always`, fuseau `Europe/Paris` (comportement de #58 inchangé). Une grille sans aucun `1` est valide : la sonnette ne réagit jamais. Le conteneur tourne en UTC : le fuseau est un réglage validé, la base de fuseaux est embarquée dans le binaire, le changement d'heure est géré par la bibliothèque. Un fuseau faux décale la plage, d'où l'affichage du fuseau et de l'heure locale dans l'éditeur du portail local. Erreur : 400 `invalid_schedule`. Hors plage, l'anti-rafale de 30 s n'est pas armé. Écriture réservée à `lan_admin`, tracée dans l'audit (`doorbell_schedule`).

### Signalement gateway vers cloud

`POST /api/gateway/doorbell/ring` (`GatewayAuth`), corps `{"ring_id","at"}`, idempotent sur `(gateway_id, ring_id)`, réponse `{"status":"accepted","recipients":n}`, 429 au-delà d'un appui par 10 s et par gateway, en-tête `X-Essensys-Test-Mode: dry-run` sans envoi. Côté gateway : tâche de fond, 3 tentatives (attentes 1 s puis 3 s), abandon après 60 s, jamais de retard du clignotement, aucun jeton ni adresse journalisé.

### Notifications push et table `push_devices`

Migration 022 : table `push_devices` (`id`, `user_id`, `platform` `android`|`ios`, `token`, `app_version`, `doorbell_notify`, dates, unicité `(platform, token)`). Routes : `PUT /api/portal/push/devices`, `DELETE /api/portal/push/devices/{id}`, `GET /api/portal/doorbell/preferences` (jamais de jeton en lecture ni en journal). Destinataires : utilisateurs liés à la gateway appelante ayant un appareil avec `doorbell_notify=true`. Deux expéditeurs derrière une interface commune, configurés par variables d'environnement du cloud (valeurs via SOPS et [[Essensys Ansible]], jamais dans un dépôt) ; sans configuration, l'appui est accepté et rien n'est envoyé (`push_unavailable` journalisé une fois). Jeton rejeté définitivement par le fournisseur : l'appareil est supprimé. Contenu sans nom d'armoire ni image : « Quelqu'un sonne », priorité haute, donnée `ring_id` pour dédoublonner.

### `gateway_state` et option « Sonnette » dans les apps

`GET /api/portal/session` gagne `gateway_state` : `none` (aucune gateway liée ou éligible), `offline`, `online` ; le bloc `gateway` existant est conservé. Le portail cloud ([[Essensys User Portal Frontend]]), [[Essensys Android Phone Apps]] et [[Essensys IOS Phone Apps]] affichent « Gateway en ligne », « Gateway hors ligne » ou « Aucune gateway liée ». L'option « Sonnette » des apps n'apparaît que si `gateway_state != "none"` : un interrupteur demande la permission de notification du système, enregistre l'appareil et pose `doorbell_notify` ; permission refusée, il revient à zéro ; déconnexion, l'appareil est supprimé côté cloud. Aucune clé de fournisseur dans les apps (Android : fichier de configuration du projet à la compilation ; iPhone : APNs sans SDK Firebase).

### Limites et risques (#61)

- **Pas de garantie de livraison** : appareil éteint, économie d'énergie ou panne d'un fournisseur ; la notification ne remplace pas la sonnette physique.
- Cloud injoignable : l'appui est abandonné après 60 s, pas de notification tardive ; le clignotement local n'est jamais retardé.
- Sans compte Firebase ni clé APNs fournis hors dépôt, aucune notification réelle ; le simulateur iPhone ne reçoit pas d'APNs réelles (test par `xcrun simctl push`).
- L'option « Sonnette » apparaît dès qu'une gateway est présente, même sans sonnette configurée : la notification n'arrive que si la sonnette est activée sur la gateway.
- Une armoire par compte : pas de sélecteur d'armoire. Hors périmètre : vidéo dans les apps ou la notification, réponse audio, historique des appuis, plusieurs sonnettes.
- Aucun endpoint legacy IoT modifié, aucune écriture dans l'armoire ; Raspberry Pi et firmware non concernés.

## Suivi

Process : [[Feature Lifecycle]]. Doc publique : pages « Sonnette UniFi » et « Configuration UniFi (sonnette) » ([[Essensys DOC]]).
