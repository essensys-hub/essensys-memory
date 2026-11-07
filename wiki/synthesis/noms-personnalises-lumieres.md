---
tags: [synthesis, feature, domotique, lumieres, droits, synchronisation]
sources: [openspec/changes/noms-lumieres-2026-11-004/design.md]
created: 2026-11-07
updated: 2026-11-07
---

# Noms Personnalises Lumieres

> Feature `noms-lumieres-2026-11-004` (ticket essensys-hub/essensys-feature-lifecycle#41, sous-ticket essensys-hub/essensys-memory#26) : donner à chacune des 33 lumières un nom choisi par l'administrateur de l'armoire (par exemple « WC 3 » pour Dressing), partout : portails, apps, menu des temporisations.

## Constat

Les clients (deux portails, Android, iPhone) identifiaient déjà les 33 lumières par un `id` commun (`dressing`, `salon`…) et un libellé fixe. Aucune écriture dans l'armoire n'est nécessaire : le nom est une donnée d'affichage, jamais envoyée à la [[Table D Echange]]. Les endpoints legacy ne changent pas.

## Catalogue des 33 lumières

- **21 principales** : `terrasse`, `entree`, `escalier`, `deg1`, `deg2`, `pieceserv`, `ann1`, `ann2`, `salon`, `sam`, `cuisine`, `sdb1`, `sdb2`, `wc1`, `wc2`, `bureau`, `gdchamb`, `ptchamb1`, `ptchamb2`, `ptchamb3`, `dressing`.
- **12 indirectes** : `isalonind`, `isalonind2`, `icuisine`, `isdb1`, `isdb2`, `igdchamb1`, `igdchamb2`, `iptchamb1`, `iptchamb2`, `iptchamb22`, `iptchamb3`, `idressing`.
- Le nom d'origine reste affiché tant qu'aucun nom n'est défini ; un nom vide ou `null` remet le nom d'origine.

## Modèle de droits

- **Écriture** : administrateur de l'armoire seulement. Cloud : rôle `admin_local` ou `admin_global` **avec l'armoire liée au compte** (même règle que les temporisations, voir [[Lumieres Temporisees]]). Gateway : `lan_admin` (ouvert si l'IAM LAN est désactivé).
- **Lecture** : tout utilisateur authentifié de l'armoire.
- **Une armoire par compte** : un administrateur global qui a plusieurs armoires n'agit que sur celle qui est liée à son compte ; le sélecteur d'armoire est un ticket suivant.
- Règle du nom : 1 à 40 caractères après suppression des espaces de bord, sans caractère de contrôle ni `<` `>`, affiché comme texte brut.

## Fusion cloud et gateway

- Le cloud est l'arbitre. Deux sources d'écriture : le portail cloud écrit dans le cloud ; le portail local et les apps en mode local écrivent dans la gateway.
- À chaque cycle, l'agent de la gateway envoie ses 33 entrées au cloud (`POST /api/gateway/lights/names/sync`, `GatewayAuth`) et remplace sa réplique par l'état fusionné.
- **Dernier écrit gagne**, lumière par lumière : on compare `(updated_at, version, updated_by)` dans cet ordre. `updated_at` est en UTC ; le cloud ramène à son heure un `updated_at` plus de 5 minutes dans le futur (horloge de gateway fausse).
- La remise à zéro (`name = null`) est une valeur à part entière, version incrémentée, pour qu'elle se propage.
- Hors ligne, la réplique locale fait foi ; la synchronisation reprend au retour de la connexion.

## Stockage

- **Cloud** : table des noms dans la base du portail, un enregistrement par lumière et par armoire ; événement d'audit `light_name` (qui, quand, ancien et nouveau nom) ([[Essensys User Portal Backend]]).
- **Gateway** : fichier JSON unique `light-names.json`, écriture atomique, clé `light_names.path` ; sur CM5 : `/opt/data/light-names` (hôte, sauvegardé avec `/opt/data`) monté sur `/var/lib/essensys/names` (conteneur). Sans stockage : lecture des noms d'origine et écriture refusée en 503 `names_unavailable` ([[Essensys Server Backend]]).
- Le montage en écriture impose la **recréation** du conteneur backend (un `docker restart` ne suffit pas) : voir [[Essensys Raspberry Install]] pour le Pi.

## Risques ouverts

- Une horloge de gateway qui dérive de plus de 5 minutes fausse l'arbitrage (NTP est installé sur CM5 et Pi).
- Le menu Temporisations (#45) affichait des libellés d'origine : il doit utiliser les noms personnalisés.

## Suivi

Process : [[Feature Lifecycle]]. Clients : [[Essensys User Portal Frontend]], [[Essensys Server Frontend]], [[Essensys Android Phone Apps]], [[Essensys IOS Phone Apps]]. Doc publique : page « Renommer une lumière » et page « Fichier des noms de lumières (gateway) » ([[Essensys DOC]]).

Les volets et stores ont la même fonction : voir [[Noms Personnalises Volets]].

L'activation et l'ordre d'affichage des objets : voir [[Affichage Objets]].
