> Ticket : [essensys-hub/essensys-feature-lifecycle#41](https://github.com/essensys-hub/essensys-feature-lifecycle/issues/41). Feature ID : `noms-personnalises-2026-11-002`.
> Feature répartie sur 3 changes du même nom : les apps Android et iPhone (un change dans chaque dépôt) et la **plateforme** (ce change, dans `essensys-memory`) : cloud, gateway, portails, installations CM5 et Raspberry Pi 4. Ce change ne décrit pas le code des apps.

## Why

Les noms des objets d'Essensys (« Petite Chambre 3 », « Volet 1 Salon », « Salle de Bain 1 »…) sont codés en dur et dupliqués dans les tables d'indices Android et iPhone, dans les deux portails, et dans les backends (éditeur de scénarios, MCP). Un occupant ne peut pas les adapter à sa maison : « Petite Chambre 3 » ne deviendra jamais « Chambre de Nico ». Rien ne sait aujourd'hui synchroniser une donnée saisie par l'utilisateur entre le cloud, la gateway et les apps : `cloudsync` ne transporte que des indices de l'armoire.

## What Changes

- **Noms personnalisés** pour les pièces et les objets : lumières, volets, zones de chauffage, prises de sécurité, chauffe-eau, arrosage, scénarios.
- **Propagation** : un nom de pièce se propage par défaut aux objets de la pièce (chevets, volet) ; un nom forcé sur un objet prime ; vider un nom rétablit le nom hérité, puis le nom d'origine.
- **Droits** : seul l'administrateur de l'armoire renomme ; les autres utilisateurs consultent.
- **Stockage** dans le cloud, par installation, avec une **réplique** dans la gateway et une **synchronisation dans les deux sens**. Jamais dans l'armoire.
- **API** cloud et gateway (lecture, écriture, suppression), avec un numéro de révision pour ne recharger que ce qui change.
- **Écran « Noms »** (Réglages) sur les portails cloud et local, et affichage du nom choisi partout où l'objet apparaît.
- **Installation** : la gateway pose son stockage des noms sans intervention, sur CM5 (Ansible) comme sur Raspberry Pi 4 (scripts d'installation).

## Capabilities

### New Capabilities

- `custom-names-model` : catalogue des objets, règle de nom affiché, validation d'un nom, droits.
- `custom-names-cloud` : stockage et API du cloud, synchronisation avec la gateway, traçabilité.
- `custom-names-gateway` : stockage local de la gateway, API du réseau local, synchronisation avec le cloud, installation CM5 et Raspberry Pi 4.
- `custom-names-portals` : écran « Noms » et affichage des noms sur les portails cloud et local.
- `custom-names-quality` : tests, non-régression et déploiement.

### Modified Capabilities

Aucune (les specs existantes ne sont pas archivées sous `openspec/specs/`).

## Impact

- **essensys-user-portal-backend** : nouveau paquet de noms, migration `018`, routes `/api/names` et `/api/gateway/names`, audit.
- **essensys-server-backend** : stockage par fichier, routes `/api/names` du réseau local, extension de `cloudsync`.
- **essensys-user-portal-frontend** et **essensys-server-frontend** (jumeaux, à garder synchronisés) : hook de noms, écran « Noms », remplacement des libellés codés en dur.
- **essensys-ansible** (CM5) et **essensys-raspberry-install** (Raspberry Pi 4) : répertoire et droits du stockage des noms.
- **Apps** : décrites dans les changes du même nom d'`essensys-android-phone-apps` et `essensys-ios-phone-apps`.
- **Déploiement** : cloud, puis gateway (CM5 et Raspberry Pi 4), puis portails, puis apps. Les backends sortent sans effet visible tant que les clients ne les appellent pas.
- **Hors périmètre** : assistant MCP, notifications, noms par langue, noms propres à chaque utilisateur, renommage de l'installation, écriture hors ligne dans les apps.
