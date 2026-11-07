---
tags: [synthesis, feature, domotique, volets, droits, synchronisation]
sources: [openspec/changes/noms-volets-2026-11-005/design.md]
created: 2026-11-07
updated: 2026-11-07
---

# Noms Personnalises Volets

> Feature `noms-volets-2026-11-005` (ticket essensys-hub/essensys-feature-lifecycle#52, sous-ticket essensys-hub/essensys-memory#28) : donner à chacun des 16 volets et stores un nom choisi par l'administrateur de l'armoire (par exemple « Volet baie vitrée » pour Volet 1 Salon), partout : portails, apps, écran « Temps de course ». Jumelle de [[Noms Personnalises Lumieres]] (#41).

## Constat

Les 16 volets et stores sont déjà identifiés par un `id` commun aux quatre clients (deux portails, Android, iPhone) : `volet1salon`… `store`. Les 16 libellés d'origine sont identiques sur les quatre clients. Aucune écriture dans l'armoire : le nom est une donnée d'affichage, jamais envoyée à la [[Table D Echange]]. Les endpoints legacy ne changent pas, les indices de commande non plus.

## Catalogue des 16 volets et stores

- **14 volets** : `volet1salon`, `volet2salon`, `volet3salon`, `volet1salleamanger`, `volet2salleamanger`, `volet1cuisine`, `volet2cuisine`, `voletsdb`, `volet1gdchamb`, `volet2gdchamb`, `volet1ptchamb`, `volet2ptchamb`, `volet3ptchamb`, `voletbureau`.
- **2 éléments spéciaux** : `voletstore` (nom d'origine `Volet "Store"`, avec des guillemets droits, permis dans les noms) et `store` (« Store (banne) »).
- Le widget historique `ShutterControl.tsx` (14 volets, sans « (banne) ») n'est pas une source du catalogue : la référence est `ShuttersPage.tsx`, Android et iPhone.
- Un nom vide ou `null` remet le nom d'origine.

## Routes jumelles

Pas d'API générique : `/shutters/names` à côté de `/lights/names`, mêmes droits, mêmes erreurs (`unknown_shutter` à la place de `unknown_light`), même mode essai à blanc, même règle de nom (1 à 40 caractères, sans caractère de contrôle ni `<` `>`, texte brut).

- Cloud : lecture `GET /api/portal/shutters/names`, écriture `PUT /api/portal/admin/shutters/names/{id}`, synchronisation `POST /api/gateway/shutters/names/sync` (`GatewayAuth`).
- Gateway : lecture `GET /api/shutters/names`, écriture `PUT /api/admin/shutters/names/{id}` (`lan_admin`, ouvert si l'IAM LAN est désactivé).
- Événement d'audit `shutter_name`. Écriture réservée à l'administrateur de l'armoire (cloud : `admin_local` ou `admin_global` avec l'armoire liée), lecture pour tout utilisateur de l'armoire. Une armoire par compte, comme pour les lumières.

## Fusion cloud et gateway

Identique aux lumières : le cloud arbitre, dernier écrit gagne volet par volet sur `(updated_at, version, updated_by)`, `updated_at` futur de plus de 5 minutes ramené à l'heure du cloud, remise à zéro propagée. L'agent de la gateway fait **deux appels distincts** par cycle (lumières, volets) : l'échec de l'un ne bloque pas l'autre. Hors ligne, la réplique locale fait foi.

## Stockage

- **Cloud** : nouvelle table `shutter_names (machine_id, shutter_id, name, version, updated_at, updated_by)`, migration idempotente `020` ; la table `light_names` n'est pas modifiée ([[Essensys User Portal Backend]]).
- **Gateway** : **même fichier** `light-names.json` et **même clé** `light_names.path` que les lumières, avec une seconde section `shutters` à côté de `lights`. `version` du fichier reste 1, une section absente est vide. L'écriture d'une section préserve l'autre et toute section inconnue (le code de #41 a été refactoré pour cela), écriture atomique et un seul verrou ([[Essensys Server Backend]]).
- Conséquence : **Raspberry Pi et Ansible ne sont pas concernés** (répertoire, montage, droits et clé existent depuis #41) ; un redémarrage du conteneur suffit, aucun nouveau montage. Un autre chemin ou une autre clé ferait redevenir ces deux briques concernées.

## Risques ouverts

- **Retour arrière** : une gateway repassée en #41 efface la section `shutters` à sa prochaine écriture de lumière ; le cloud rétablit les noms à la synchronisation suivante.
- Dérive d'horloge de plus de 5 minutes de la gateway : arbitrage faussé (NTP installé sur CM5).
- Un nom de 40 caractères doit tenir sur une ligne de l'écran « Temps de course » (iPhone SE, iPad).

## Livraison

Cloud, puis gateway CM5 (SHA épinglés), puis portails ; APK 2.7.0 sur le site support ; build iPhone 2.7.0 sur TestFlight.

## Suivi

Process : [[Feature Lifecycle]]. Clients : [[Essensys User Portal Frontend]], [[Essensys Server Frontend]], [[Essensys Android Phone Apps]], [[Essensys IOS Phone Apps]]. Doc publique : page « Renommer un volet ou un store » et page « Fichier des noms (gateway) » ([[Essensys DOC]]).
