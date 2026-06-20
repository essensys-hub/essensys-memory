# essensys-web-legacy

> Application serveur historique de la plateforme domotique Essensys : portail web ASP.NET MVC 4 / Web API qui pilote les boîtiers domotiques embarqués via un protocole de polling HTTP et persiste l'état en SQL Server via NHibernate.

**Catégorie :** Legacy — serveur applicatif & API (.NET Framework)
**Stack :** ASP.NET MVC 4 + ASP.NET Web API (.NET Framework 4.0, C#), NHibernate + FluentNHibernate, SQL Server, Razor/jQuery, IIS
**Statut :** legacy (référence, ne pas modifier)

## Rôle dans l'architecture Essensys

`essensys-web-legacy` est le **serveur central historique** de la plateforme domotique Essensys. C'est le contrepartie serveur du client embarqué `client-essensys-legacy` (boîtier BP_MQX_ETH). Son rôle :

- Exposer l'**API de polling legacy** (`/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}`) que le boîtier embarqué interroge en permanence pour remonter son état et récupérer les commandes à exécuter.
- Fournir le **portail web utilisateur** (Razor + jQuery) permettant à l'occupant de piloter sa maison : alarme, chauffage (fil pilote), arrosage, cumulus, volets/stores, éclairage, scénarios.
- Gérer l'**authentification des machines et des utilisateurs**, la persistance de l'historique des états, la file d'actions, et la **distribution de mises à jour firmware** (OTA) aux boîtiers (`/api/getversioncontent`, `/api/endversioncontent`).
- Servir de **source de vérité fonctionnelle** pour la migration vers la nouvelle architecture Go + React (`essensys-server-backend`, `essensys-server-frontend`, `essensys-user-portal-*`). C'est ce dépôt qui définit le contrat exact du protocole legacy que le nouveau backend Go doit ré-implémenter à l'identique.

Le dépôt contient également un **plan de migration documenté** (MkDocs, dossier `docs/`) et des **amorces de réécriture React** (`Essensys.Web.UI.React`, `Essensys.Web.Admin.React`) qui ne sont pas la cible de production mais des prototypes.

## Stack technique & dépendances

- **Langage / Runtime** : C#, .NET Framework **4.0** (`TargetFrameworkVersion v4.0`).
- **Web** : ASP.NET **MVC 4** (`Microsoft.AspNet.Mvc 4.0`) + ASP.NET **Web API** (`Microsoft.AspNet.WebApi 4.0`), hébergé sur IIS / `System.Web`. Les contrôleurs API héritent de `ApiController`, les contrôleurs MVC de `Controller`.
- **ORM / Persistance** : **NHibernate** + **FluentNHibernate** (mappings `*Map.cs` dans `Essensys.Repository/DTO`), base **SQL Server**. Session factory dans `EsSessionFactory.cs`, repository de base `BaseRepository.cs`.
- **Vues** : Razor (`Views/`), jQuery + CSS (`Content/`, `Scripts/`).
- **Sérialisation API** : JSON uniquement (le formateur XML est explicitement retiré dans `WebApiConfig`).
- **Autres dépendances** : AWSSDK (notifications/stockage), Antlr3.Runtime (dépendance NHibernate/HQL), Iesi.Collections.
- **Composants annexes** : `Essensys.Notifier` (application WinForms de notification), `Essensys.Console` (utilitaire console), `Essensys.Common` (SMS, e-mail, hashing, logging, exceptions).

## Structure du dépôt

Solution Visual Studio `Essensys.Web/Essensys.Web.sln` découpée en projets :

- **`Essensys.Web.UI`** — projet web principal (MVC + Web API).
  - `Controllers/api/` — **API legacy du boîtier** : `ServerInfosController`, `MyStatusController`, `MyActionsController`, `DoneController`, plus l'OTA firmware `GetVersionContentController` / `EndVersionContentController`.
  - `Controllers/` — IHM web : `HomeController`, `AccountController`, `PhoneController`, `SimulateController`.
  - `App_Start/` — `WebApiConfig` (route `api/{controller}/{id}`, suppression XML), `RouteConfig` (routes MVC : `Login`, `Signup`, `Default`), `BundleConfig`, `FilterConfig`.
  - `Views/`, `Content/`, `Scripts/`, `Global.asax(.cs)`, `Web.config`.
- **`Essensys.Service`** — couche métier (logique applicative).
  - `Fonctions/` — **services métier domotiques** : `AlarmeService`, `ChauffageService`, `ArrosageService`, `CumulusService`, `VoletService`, `VoletAndStoreService`, `StoreService`, `FonctionService`.
  - `Transaction/` — services de persistance/transaction : `ActionService` (file d'actions + acquit), `StateService` (enregistrement des états), `ServerService` (infos serveur / index), `VersionMachineService` (OTA), `Tbb_Donnees_Index` (énumération des index de la table d'échange).
  - `Response/` — DTO de sortie API : `EsServerInfo`, `EsActionsInfo`, `EsStatusMessage`, `EsKeyValue`, `EsVersionPart`.
  - `Security/` — `EssensysAuthorizeAttribute` (authentification HTTP Basic des boîtiers), `UserService`.
  - `Phone/` — `PhoneService`.
- **`Essensys.Repository`** — accès données NHibernate : `BaseRepository`, `EsSessionFactory`, `EsListener`, et `DTO/` (entités + mappings Fluent : `EsMachine`, `EsAction`, `EsActionIndex`, `EsState`, `EsStateIndex`, `EsDataIndex`, `EsUser`, `EsVersion`, `EsVersionMachine`, `EsPhone`, `EsSmssend`, `EsClemachine`…).
- **`Essensys.Common`** — utilitaires transverses : `LogManager`, `EssensysException`, `HashHelper`, `EMailSender`, `SMSSender`.
- **`Essensys.Notifier`** — agent de notification (WinForms).
- **`Essensys.Console`** — utilitaire en ligne de commande.
- **`Externals/`, `packages/`** — DLL tierces et packages NuGet.

À la racine du dépôt :

- `docs/` + `mkdocs.yml` — **plan de migration** complet (analyse legacy, architecture cible React/Node, schéma BDD moderne, sécurité, ROI, stratégie de tests…). C'est de la documentation projet, pas du code exécutable.
- `Essensys.Web.UI.React/`, `Essensys.Web.Admin.React/` — prototypes React (non production).
- `src/`, `tests/`, `static_preview.html`, `docker-compose.yml` — outillage de migration/documentation.
- `Procédure_de_création_de_compte_Essensys-v3.pdf`, `README.md`, `GETTING_STARTED.md` — documentation utilisateur/projet.

## Build / Exécution / Déploiement

- **Build** : ouvrir `Essensys.Web/Essensys.Web.sln` dans Visual Studio (ciblant .NET Framework 4.0) et compiler, ou via MSBuild. Restauration NuGet requise (`packages/`).
- **Exécution** : hébergement IIS / IIS Express, application `System.Web` classique (pas de Kestrel/.NET Core). La configuration (chaîne de connexion SQL Server, paramètres) est dans `Web.config` (+ `Web.Debug.config` / `Web.Release.config`).
- **Base de données** : SQL Server, schéma piloté par les mappings FluentNHibernate.
- **Déploiement** : publication IIS (le projet contient `Essensys.Web.UI.Publish.xml`).
- **Documentation de migration** : `mkdocs serve` (Python, `requirements.txt`) sert le site `docs/` ; un `docker-compose.yml` et `deploy-docs.sh` accompagnent la publication GitHub Pages.

> Remarque : la stack étant .NET Framework 4.0 (Windows/IIS), ce dépôt n'est pas conçu pour tourner nativement sur l'environnement Linux/Go de la nouvelle plateforme. Il sert de **référence fonctionnelle** pour la réécriture.

## Intégrations

- **Boîtier embarqué BP_MQX_ETH** (`client-essensys-legacy`) — consommateur principal de l'API de polling. Communication HTTP/1.1 avec les contraintes legacy décrites ci-dessous (auth Basic, codes `201 Created`, JSON spécifique).
- **SQL Server** — persistance via NHibernate (états, actions, machines, utilisateurs, versions firmware).
- **AWS (AWSSDK)** — services cloud annexes.
- **SMS / E-mail** (`Essensys.Common.SMS`, `SMSSender`, `EMailSender`) — notifications utilisateur (ex. alertes alarme).
- **Cible de migration** — `essensys-server-backend` (Go) ré-implémente ce protocole ; `essensys-server-frontend` / `essensys-user-portal-frontend` (React) remplacent l'IHM Razor.

### Protocole legacy IoT exposé par le serveur

L'API de polling est définie côté serveur dans `Essensys.Web.UI/Controllers/api/` et côté client dans `client-essensys-legacy/Ethernet/www.c`. Tous les endpoints sont protégés par `[EssensysAuthorize]` → **authentification HTTP Basic** : le boîtier envoie un en-tête `Authorization: Basic <base64(user:pass)>` ; `UserService.ValidateAPIAccess` valide et place l'`EsMachine` en session (`HttpContext.Current.Session["Machine"]`). En cas d'échec : `401` avec `WWW-Authenticate: Basic`.

- **`GET /api/serverinfos`** (`ServerInfosController`) — renvoie `EsServerInfo { isconnected, infos (liste des index à surveiller via ServerService.GetDataIndex), newversion }`. C'est aussi le canal qui signale au boîtier qu'une **nouvelle version firmware** est disponible (`newversion = "V<id>"` sinon `"no"`), déclenchant l'OTA. Code `200 OK`.
- **`POST /api/mystatus`** (`MyStatusController`) — le boîtier remonte son état sous forme `EsStatusMessage { version, ek: [ {k, v}, … ] }` (`ek` = *exchange keys*). `StateService.RegisterState` persiste l'historique. Réponse **`201 Created`** (non standard). Si `ek == null` → `400`.
- **`GET /api/myactions`** (`MyActionsController`) — renvoie `EsActionsInfo { _de67f, actions: [ { guid, params: [{k,v}, …] }, … ] }`. Le champ **`_de67f`** porte l'éventuelle **action d'alarme chiffrée** (`EsAlarmAction { guid, obl }`, `obl` = données chiffrées AES) ; il doit apparaître **en premier**. Les `params` contiennent la **table d'échange complète** (index 605-622 + index 590 = trigger scénario). Code `200 OK`.
- **`POST /api/done/{guid}`** (`DoneController`) — acquittement d'une action exécutée. `ActionService.AcquitAction` retire l'action de la file. Réponse **`201 Created`** ; `guid` inconnu → `404 Not Found`.
- **`POST /api/getversioncontent/{...}` et `POST /api/endversioncontent`** — distribution du firmware par morceaux (OTA), pilotée par `VersionMachineService`.

Particularités legacy à respecter à l'identique côté nouveau backend :

- **Codes HTTP non standard** : les POST (`mystatus`, `done`, OTA) répondent **`201 Created`** et non `200`. Le client vérifie littéralement la présence de `"HTTP/1.1 201 Created"` / `"HTTP/1.1 200 OK"` dans le buffer reçu (`www.c`).
- **En-tête `Content-Type` exact** : le boîtier lui-même émet `Content-type: application/json ;charset=UTF-8` (espace **avant** le `;`, vu dans `www.c:1527`). Le serveur doit répondre dans le même format.
- **`Connection: close`** — pas de keep-alive (le boîtier ne gère pas les connexions persistantes).
- **Single-packet TCP** — voir le dépôt client : toute la réponse HTTP doit tenir dans un seul segment TCP, sinon le parser embarqué se bloque.
- **JSON malformé en entrée** — le boîtier émet du JSON à clés non quotées (`{version:"1.0",ek:[{k:605,v:"0"}]}`) ; le binding ASP.NET historique tolérait ce format, le nouveau backend doit le normaliser.

### Services métier (couche `Essensys.Service.Fonctions`)

Tous transforment une commande utilisateur en une **action** (paire(s) index/valeur de la table d'échange) enregistrée via `ActionService.RegisterAction`, qui sera ensuite remontée au boîtier par `/api/myactions` :

- **`AlarmeService`** — activation/désactivation de l'alarme. Vérifie une **question de sécurité** (`UserService.TestQuestion`) plutôt qu'un code (la saisie par code est marquée obsolète). L'ordre (`ALARMEON_…` / `ALARMEOFF_…` horodaté) est **chiffré en AES** (`EncryptString`/`AesManaged`, clé `m.Pkey`) et transmis via le champ `_de67f` de `/api/myactions`. C'est le seul service à passer par un canal chiffré dédié.
- **`ChauffageService`** — pilotage du chauffage par zone (`zj`, `zn`, `sdb1`, `sdb2`) via les index `Chauf_z*_Mode` (mode = ordre fil pilote : confort, éco, hors-gel, arrêt…).
- **`ArrosageService`** — mode d'arrosage via l'index `Arrose_Mode`.
- **`CumulusService`** — pilotage du chauffe-eau (cumulus) via l'index `Cumulus_Mode`.
- **`VoletService` / `VoletAndStoreService` / `StoreService`** — pilotage des volets et stores : agrège plusieurs ordres en **masques de bits fusionnés par OU binaire** (`int nv = old | val`), puis envoie la **table d'échange complète** (605-622 mis à 0 sauf cibles) avec l'index `Scenario` (590) à `"1"` pour déclencher l'exécution.

Le mapping index ↔ fonction est centralisé dans l'énumération `Tbb_Donnees_Index` (`Essensys.Service/Transaction/Tbb_Donnees_Index.cs`).

## Points d'attention

- **Statut legacy strict** : dépôt de **référence à ne pas modifier**. Toute évolution fonctionnelle doit aller dans la nouvelle stack Go/React.
- **Stack obsolète** : .NET Framework **4.0**, MVC 4 / Web API 1, NHibernate — versions non maintenues, dépendantes de Windows/IIS et SQL Server. Pas de portage direct possible.
- **État en session HTTP** : l'authentification stocke la machine dans `HttpContext.Current.Session`, ce qui couple fortement le protocole boîtier à l'état de session ASP.NET (à reconcevoir en stateless côté Go).
- **Sécurité** : authentification **HTTP Basic** (identifiants en base64, donc en clair sans TLS), chiffrement **AES** propriétaire des ordres d'alarme (clé par machine `Pkey`). À auditer lors de la migration. L'historique git montre des commits récents retirant des secrets en clair des configs (`fix(security): retirer les secrets en clair`).
- **Contrat protocole figé** : codes `201 Created`, en-tête `Content-Type` à espace, single-packet TCP, JSON à clés non quotées, ordre du champ `_de67f`, table d'échange complète + index 590 — **toutes ces particularités doivent être reproduites à l'identique** par le backend Go tant que des boîtiers BP_MQX_ETH sont en service (firmware non modifiable sans reflash).
- **Mélange documentation/code** : le dépôt contient à la fois le code legacy (`Essensys.Web/`) et le plan de migration (`docs/`, MkDocs) plus des prototypes React — ne pas confondre le code de production legacy avec les amorces de réécriture.
