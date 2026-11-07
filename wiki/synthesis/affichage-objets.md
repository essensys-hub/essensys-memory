---
tags: [synthesis, feature, domotique, lumieres, volets, droits, synchronisation]
sources: [openspec/changes/affichage-objets-2026-11-006/design.md]
created: 2026-11-07
updated: 2026-11-07
---

# Affichage Objets

> Feature `affichage-objets-2026-11-006` (ticket essensys-hub/essensys-feature-lifecycle#55, sous-ticket essensys-hub/essensys-memory#30) : l'administrateur de l'armoire désactive les lumières, volets et stores inutilisés et choisit leur ordre d'affichage, partout : portails, apps, groupes, Temporisations, « Temps de course ». Prolonge [[Noms Personnalises Lumieres]] (#41) et [[Noms Personnalises Volets]] (#52).

## Constat

Les 33 lumières et les 16 volets et stores ont déjà un `id` commun aux quatre clients (deux portails, Android, iPhone). Aucune écriture dans l'armoire : la disposition est une donnée d'affichage, jamais envoyée à la [[Table D Echange]]. Les endpoints legacy et les indices de commande ne changent pas.

## Un document par genre

Contrairement aux noms (une entrée par objet), la disposition est **un document par armoire et par genre** (`lights`, `shutters`) : `order` (identifiants sans doublon), `disabled` (sous-ensemble du catalogue), `version`, `updated_at`. Un réordonnancement est ainsi atomique et n'entre pas en conflit avec les noms. Disposition par défaut : version 0, `order` et `disabled` vides (ordre d'origine, rien de masqué).

## Règle de repli (tolérance des clients)

Fonction commune `effectiveLayout(catalogue, layout)` : les identifiants connus absents de `order` sont ajoutés à la fin dans l'ordre du catalogue, les identifiants inconnus sont ignorés. L'ordre est global mais appliqué **à l'intérieur de chaque groupe d'affichage** : un objet ne change jamais de groupe (Monter/Descendre échange avec le voisin du même groupe). Lecture impossible ou ancien serveur (404) : catalogue complet dans l'ordre d'origine, sans message bloquant.

## Effet d'un objet désactivé

Masqué pour tous : listes, « Tout allumer / éteindre », « Tout ouvrir / fermer » (les commandes de groupe l'excluent), Temporisations, « Temps de course ». Aucune commande envoyée. Groupe sans objet actif : boutons masqués, texte « Aucune lumière activée » / « Aucun volet activé ». Les scénarios gardent le catalogue complet (hors périmètre).

## Routes jumelles

Pas d'API générique, comme pour les noms :

- Cloud : lecture `GET /api/portal/{lights|shutters}/layout`, écriture `PUT /api/portal/admin/{lights|shutters}/layout`, synchronisation `POST /api/gateway/{lights|shutters}/layout/sync` (`GatewayAuth`).
- Gateway : lecture `GET /api/{lights|shutters}/layout`, écriture `PUT /api/admin/{lights|shutters}/layout` (`lan_admin`, ouvert si l'IAM LAN est désactivé).
- Corps d'écriture `{"order":[…],"disabled":[…]}` (deux clés obligatoires) ou `{"reset":true}` (version `n+1`, pour que le retour au défaut se propage). Le serveur valide sans compléter `order`.
- Erreurs : `unknown_light` / `unknown_shutter`, `invalid_layout`, `invalid_body`, 403 `forbidden`, 503 `names_unavailable` (code réutilisé). Les réponses aux clients n'exposent pas `updated_by`. Mode essai à blanc comme pour les noms ; événement d'audit `object_layout` (champ `kind`).

## Fusion cloud et gateway

Document entier, sans fusion champ par champ : on compare `(updated_at, version, updated_by)`, le plus grand gagne, égalité parfaite = valeur du cloud ; `updated_at` futur de plus de 5 minutes ramené à l'heure du cloud. L'agent de la gateway fait deux appels de plus par cycle (lumières, volets) en plus des deux appels de noms : l'échec de l'un des quatre ne bloque pas les autres. Hors ligne, la réplique locale fait foi.

## Stockage

- **Cloud** : table `object_layout (machine_id, kind, order_json, disabled_json, version, updated_at, updated_by)`, migration idempotente `021` ; `light_names` et `shutter_names` ne sont pas modifiées ([[Essensys User Portal Backend]]).
- **Gateway** : **même fichier** `light-names.json` et **même clé** `light_names.path`, deux sections de plus `lights_layout` et `shutters_layout`. Ce sont des **objets** et non des tables d'entrées : décodeur dédié et écriture brute, sous le même verrou et la même écriture atomique ; écrire une section préserve toutes les autres ([[Essensys Server Backend]]).
- Conséquence : **Raspberry Pi et Ansible ne sont pas concernés**. Un autre chemin, une autre clé ou un autre fichier les ferait redevenir concernés (matrice à corriger par un humain).

## Risques ouverts

- **Gateway restée à la version de #41 ou #52** : elle efface les sections `*_layout` à sa prochaine écriture de nom ; le cloud les rétablit à la synchronisation suivante. D'où l'ordre de déploiement : cloud, puis gateway.
- Dérive d'horloge de plus de 5 minutes : arbitrage faussé (NTP installé sur CM5).
- Fusion du document entier : deux administrateurs qui modifient en même temps ne voient que le plus récent.

## Suivi

Process : [[Feature Lifecycle]]. Clients : [[Essensys User Portal Frontend]], [[Essensys Server Frontend]], [[Essensys Android Phone Apps]], [[Essensys IOS Phone Apps]]. Doc publique : page « Masquer et ordonner les lumières et les volets » et page « Fichier des noms (gateway) » ([[Essensys DOC]]).
