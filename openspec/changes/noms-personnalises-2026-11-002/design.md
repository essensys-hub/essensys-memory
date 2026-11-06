## Context

Voir `proposal.md` (Why). État actuel :

- Les noms sont des libellés codés en dur : `IndexTable` (Android, iPhone), `LightingPage.tsx`, `LightingControl.tsx`, `ShutterControl.tsx`, `heating/constants.ts` et `mockScenarios.ts` (portails cloud et local, jumeaux), éditeur de scénarios (`bitmasks.go`) et MCP côté backends. Les **clés** (`ptchamb3`, `volet1ptchamb`, `sdb1`…) sont déjà stables et communes.
- Rien ne synchronise de donnée libre entre le cloud et la gateway : `cloudsync` transporte des indices de l'armoire (`/api/gateway/exchange`, `heartbeat`, `sync-config`…) et rien d'autre. Le « profil Scénarios » n'est qu'un interrupteur d'activation.
- Le cloud rattache un utilisateur à une armoire par `linked_machine_id` (et `linked_gateway_id`). Ses rôles sont `admin_global`, `admin_local`, `user`, `guest_local`, `support`. La gateway a `lan_admin`, `lan_user`, `lan_guest`.
- La gateway CM5 a PostgreSQL ; le Raspberry Pi 4 (scripts `essensys-raspberry-install`) n'a que Redis, nginx, Traefik et Docker.
- La gateway dialogue avec le cloud par un cycle d'environ 5 s, authentifié par `X-Gateway-ID` et un jeton.

## Goals / Non-Goals

**Goals:**
- Un nom saisi une fois, visible partout en moins d'une minute, y compris sans internet en réseau local.
- Le même résultat de nom affiché dans les quatre clients et les deux serveurs.
- Une installation sans gateway et une gateway sans cloud fonctionnent.

**Non-Goals:**
- Assistant MCP, notifications, SMS : ils gardent les noms d'origine.
- Noms par langue, noms propres à chaque utilisateur, renommage de l'installation.
- Écriture hors ligne dans les apps (seule la gateway met en file).
- Raccourci de renommage depuis l'écran d'un objet (appui long) : l'écran « Noms » suffit.

## Decisions

**1. Catalogue copié, vérifié par un test de parité.** Un `catalog.json` décrit chaque objet : type, clé, nom d'origine, pièce, patron (`{room}`). Sa copie de référence vit dans `essensys-user-portal-backend` (`internal/names/catalog.json`, embarquée) ; chaque dépôt en garde une copie, et un script de parité d'`essensys-feature-lifecycle` compare les copies. Les patrons reproduisent les libellés actuels : lumière principale `{room}`, chevet `{room} (chevet)`, volet `Volet {room}`, etc. *Alternatives écartées :* un catalogue servi par le cloud (une dépendance réseau de plus pour afficher un écran) ; génération de code depuis une source unique (aucun dépôt commun à tous les langages).

**2. Règle de nom affiché identique partout, prouvée par des vecteurs.** Résolution : nom forcé, sinon patron rempli avec le nom de la pièce, sinon nom d'origine. Des **vecteurs de test communs** (`names_vectors.json` : cas de résolution et de validation) sont copiés dans chaque dépôt et joués par Go, TypeScript, Kotlin et Swift. C'est ce qui empêche quatre implémentations de diverger.

**3. Validation.** 1 à 40 **points de code** (pas des unités UTF-16), après `trim`, réduction des espaces répétés et normalisation NFC. Rejet des caractères de contrôle et des caractères de direction du texte (U+200E, U+200F, U+202A à U+202E, U+2066 à U+2069). Les émojis passent. Le texte est toujours affiché comme texte brut (échappé par React, `Text` natif sur les apps).

**4. Cloud : source de vérité, par installation.** Table `custom_names` (`machine_id`, `kind`, `key`, `name` nul pour un rétablissement, `rev`, `updated_at`, `updated_by`, `origin`) et un compteur `revision` par installation, incrémenté dans la même transaction que chaque écriture. Les rétablissements restent des lignes (pierres tombales) pour apparaître dans les changements. Migration `018`, idempotente (le cloud rejoue toutes ses migrations au démarrage).

**5. API cloud.**

| Appel | Rôle |
|---|---|
| `GET /api/names?since=<rev>` | noms, `revision`, `can_rename` ; `ETag` = révision ; 304 si inchangé ; `since` ne renvoie que les changements |
| `PUT /api/names/{kind}/{key}` `{ "name": "…" }` | enregistre (administrateur) ; répond avec l'entrée et la révision |
| `DELETE /api/names/{kind}/{key}` | rétablit (administrateur) |
| `GET /api/gateway/names?since=<rev>` | pour la gateway : changements depuis une révision |
| `POST /api/gateway/names/sync` `{ "base_rev": n, "changes": [...] }` | pour la gateway : envoie ses changements, reçoit l'état fusionné et la révision |

Codes d'erreur : `name_invalid` (400), `names_forbidden` (403), `name_unknown_object` (404), 429 au-delà de la limite. L'installation d'un utilisateur est toujours son `linked_machine_id` : le client ne choisit jamais la machine.

**6. Droits.** Écriture cloud : utilisateur lié à la machine **et** rôle `admin_local` ou `admin_global`. Écriture gateway : `lan_admin`. Le serveur décide, le client ne fait que masquer (`can_rename`).

**7. Gateway : un fichier, pas de base.** Les noms vivent dans `names.json` dans le répertoire de configuration du backend, écrit de façon atomique (fichier temporaire, `fsync`, renommage), avec : les entrées, `local_rev` (pour l'`ETag` des clients du réseau local), `cloud_rev` (dernière révision du cloud reprise) et la liste `pending` (changements pas encore reçus par le cloud). *Alternatives écartées :* PostgreSQL (absent du Raspberry Pi 4) ; Redis (pas fait pour de la configuration, persistance non garantie) ; SQLite (dépendance et compilation en plus pour quelques dizaines de lignes).

**8. Synchronisation.** À chaque cycle de `cloudsync`, la gateway envoie `POST /api/gateway/names/sync` avec `base_rev = cloud_rev` et `pending`. Le cloud applique les changements de la gateway dans l'ordre, avec sa propre révision, puis renvoie **tous** les changements depuis `base_rev` ; la gateway les reprend, vide `pending` et met à jour `cloud_rev`. Les changements du cloud arrivent par la même réponse. Une gateway sans changement ni nouvelle révision à recevoir échange une requête très courte. **Règle de conflit : la dernière modification reçue par le cloud gagne**, sans comparer d'horloges (un Raspberry Pi sans horloge temps réel peut dériver).

**9. Clients : un référentiel de noms, un rafraîchissement.** Chaque client (hook `useNames` des portails, `NamesRepository` des apps) garde `{ revision, entrées, can_rename }`, un cache persistant des derniers noms, et une fonction `displayName(kind, key)` qui applique la règle. Rafraîchissement : au démarrage et à la connexion, au retour au premier plan, et toutes les 30 s tant que l'écran est visible, avec `If-None-Match` (réponse 304 quasi vide). Après une écriture, le client reprend l'entrée renvoyée sans attendre le cycle. Une app en mode Cloud interroge le cloud, en mode Réseau local la gateway.

**10. Interface.** Écran « Noms » dans les Réglages, réservé aux administrateurs : catégories repliables, une ligne par pièce ou objet (nom affiché + puce « personnalisé », « hérité de la pièce » ou « d'origine »), feuille de modification (champ limité à 40, compteur, boutons « Enregistrer » et « Rétablir »). Pour une pièce, un aperçu liste les objets qui changent et ceux au nom forcé qui ne changent pas. Tous les écrans remplacent leurs libellés codés en dur par `displayName`.

**11. Installation.** Le fichier `names.json` vit dans le répertoire de configuration déjà conservé par Ansible et ses sauvegardes (le `rsync --delete` du rôle ne touche que `backend/`). Les tâches ajoutées créent le fichier absent avec le propriétaire du service et le mode `0640`, et vérifient qu'une mise à jour ne l'écrase pas. Même logique dans `install.sh` du Raspberry Pi 4.

**12. Données personnelles.** Un nom comme « Chambre de Nico » est une donnée personnelle : il est supprimé avec l'installation, absent des journaux techniques et du bundle Support, et présent seulement dans le journal d'audit.

## Risks / Trade-offs

- **Le propriétaire n'a peut-être pas le rôle d'administrateur** : les comptes actuels ont des rôles hétérogènes → vérifier en production, et prévoir si besoin un écran d'administration pour promouvoir le propriétaire.
- **Une modification faite hors ligne depuis longtemps peut écraser une modification récente du cloud** (la règle suit l'ordre d'arrivée, pas l'heure de la saisie) → accepté pour la version 1 et documenté ; l'audit permet de retrouver l'ancien nom.
- **Divergence des catalogues ou des quatre implémentations** → parité de catalogue et vecteurs de test communs, exécutés dans chaque dépôt.
- **Portails jumeaux qui divergent** → mêmes scénarios Playwright sur les deux, un seul ticket.
- **Charge d'interrogation** : 30 s par client visible → `ETag` et réponse 304 ; à surveiller si le nombre d'installations grossit.
- **Authentification du Raspberry Pi 4 sans réseau local IAM** : l'ancienne authentification web ne distingue peut-être pas d'administrateur → voir Open Questions.

## Migration Plan

1. Cloud : migration `018` et routes, sans effet visible (les clients actuels n'appellent rien).
2. Gateway : CM5 par Ansible, Raspberry Pi 4 par ses scripts ; création du fichier au premier démarrage.
3. Portails, puis apps : les clients reçoivent `404` d'un serveur ancien et affichent les noms d'origine.
4. Retour arrière : désactiver la route côté serveur ; les clients retombent sur les noms d'origine, aucun indice n'est touché.

## Open Questions

- **Gateway sans réseau local IAM (Raspberry Pi 4)** : quel utilisateur compte comme administrateur quand seule l'ancienne authentification web existe ? Hypothèse de travail : l'unique compte web est administrateur ; à confirmer à l'implémentation sans changer les specs.
