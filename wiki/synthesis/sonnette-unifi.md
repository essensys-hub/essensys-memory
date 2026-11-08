---
tags: [synthesis, feature, domotique, unifi, sonnette, lumieres, gateway]
sources: [openspec/changes/sonnette-unifi-2026-11-007/design.md]
created: 2026-11-08
updated: 2026-11-08
---

# Sonnette Unifi

> Feature `sonnette-unifi-2026-11-007` (ticket essensys-hub/essensys-feature-lifecycle#58, sous-ticket essensys-hub/essensys-memory#32) : quand la sonnette UniFi est pressée, le portail local de la CM5 affiche la vidéo de la caméra et la gateway fait clignoter des lumières choisies, qui finissent allumées. Prolonge [[Noms Personnalises Lumieres]] (#41) et [[Affichage Objets]] (#55).

## Constat

La gateway embarque déjà un client UniFi Protect (`internal/unifi`, bloc de configuration `unifi:`) mais ne reçoit aucun événement. Les lumières se commandent par des écritures dans la [[Table D Echange]] (bits 605 à 622) que l'armoire lit à son rythme. Fonction **locale** : aucune synchronisation cloud.

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

## Suivi

Process : [[Feature Lifecycle]]. Doc publique : pages « Sonnette UniFi » et « Configuration UniFi (sonnette) » ([[Essensys DOC]]).
