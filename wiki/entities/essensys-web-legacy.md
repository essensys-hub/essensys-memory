---
tags: [entity, repo, legacy]
sources: [essensys-web-legacy.md]
created: 2026-06-20
updated: 2026-06-20
era: legacy
repo: essensys-web-legacy
---

# Essensys WEB Legacy

> Application serveur historique de la plateforme domotique Essensys : portail web ASP.NET MVC 4 / Web API qui pilote les boîtiers domotiques embarqués via un protocole de polling HTTP et persiste l'état en SQL Server via NHibernate.

| | |
|---|---|
| **Catégorie** | Legacy — serveur applicatif & API (.NET Framework) |
| **Stack** | ASP.NET MVC 4 + ASP.NET Web API (.NET Framework 4.0, C#), NHibernate + FluentNHibernate, SQL Server, Razor/jQuery, IIS |
| **Statut** | legacy (référence, ne pas modifier) |
| **Era** | legacy |

## Rôle

`essensys-web-legacy` est le **serveur central historique** de la plateforme domotique Essensys. C'est le contrepartie serveur du client embarqué `client-essensys-legacy` (boîtier BP_MQX_ETH). Son rôle :

- Exposer l'**API de polling legacy** (`/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}`) que le boîtier embarqué interroge en permanence pour remonter son état et récupérer les commandes à exécuter.
- Fournir le **portail web utilisateur** (Razor + jQuery) permettant à l'occupant de piloter sa maison : alarme, chauffage (fil pilote), arrosage, cumulus, volets/stores, éclairage, scénarios.
- Gérer l'**authentification des machines et des utilisateurs**, la persistance de l'historique des états, la file d'actions, et la **distribution de mises à jour firmware** (OTA) aux boîtiers (`/api/getversioncontent`, `/api/endversioncontent`).
- Servir de **source de vérité fonctionnelle** pour la migration vers la nouvelle architecture Go + React (`essensys-server-backend`, `essensys-server-frontend`, `essensys-user-portal-*`). C'est ce dépôt qui définit le contrat exact du protocole legacy que le nouveau backend Go doit ré-implémenter à l'identique.

Le dépôt contient également un **plan de migration documenté** (MkDocs, dossier `docs/`) et des **amorces de réécriture React** (`Essensys.Web.UI.React`, `Essensys.Web.Admin.React`) qui ne sont pas la cible de production mais des prototypes.

## Intégrations

- **Boîtier embarqué BP_MQX_ETH** (`client-essensys-legacy`) — consommateur principal de l'API de polling. Communication HTTP/1.1 avec les contraintes legacy décrites ci-dessous (auth Basic, codes `201 Created`, JSON spécifique).
- **SQL Server** — persistance via NHibernate (états, actions, machines, utilisateurs, versions firmware).
- **AWS (AWSSDK)** — services cloud annexes.
- **SMS / E-mail** (`Essensys.Common.SMS`, `SMSSender`, `EMailSender`) — notifications utilisateur (ex. alertes alarme).
- **Cible de migration** — `essensys-server-backend` (Go) ré-implémente ce protocole ; `essensys-server-frontend` / `essensys-user-portal-frontend` (React) remplacent l'IHM Razor.

### Protocole legacy IoT exposé par le serveur

L'API de polling est définie côté serveur dans `Essensys.Web.UI/Controllers/api/` et côté client dans `client-essensys-legacy/Ethernet/www.c`. Tous les endpoints sont protégés par `[EssensysAuthorize]` → **authentification HTTP Basic** : le boîtier envoie un en-tête `Authorization: Basic <base64(user:pass)>` ; `UserService.ValidateAPIAccess` valide et place l'`EsMachine` en session (`HttpContext.Current.Session["Machine"]`). En cas d'échec : `401` avec `WWW-Authen

_… voir source complète dans raw/_

## Structure

Solution Visual Studio `Essensys.Web/Essensys.Web.sln` découpée en projets :

- **`Essensys.Web.UI`** — projet web principal (MVC + Web API).
  - `Controllers/api/` — **API legacy du boîtier** : `ServerInfosController`, `MyStatusController`, `MyActionsController`, `DoneController`, plus l'OTA firmware `GetVersionContentController` / `EndVersionContentController`.
  - `Controllers/` — IHM web : `HomeController`, `AccountController`, `PhoneController`, `SimulateController`.
  - `App_Start/` — `WebApiConfig` (route `api/{controller}/{id}`, suppression XML), `RouteConfig` (routes MVC : `Login`, `Signup`, `Default`), `BundleConfig`, `FilterConfig`.
  - `Views/`, `Content/`, `Scripts/`, `Global.asax(.cs)`, `Web.config`.
- **`Essensys.Service`** — couche métier (logique applicative).
  - `Fonctio

_… voir source complète dans raw/_

## Points d'attention

- **Statut legacy strict** : dépôt de **référence à ne pas modifier**. Toute évolution fonctionnelle doit aller dans la nouvelle stack Go/React.
- **Stack obsolète** : .NET Framework **4.0**, MVC 4 / Web API 1, NHibernate — versions non maintenues, dépendantes de Windows/IIS et SQL Server. Pas de portage direct possible.
- **État en session HTTP** : l'authentification stocke la machine dans `HttpContext.Current.Session`, ce qui couple fortement le protocole boîtier à l'état de session ASP.NET (à reconcevoir en stateless côté Go).
- **Sécurité** : authentification **HTTP Basic** (identifiants en base64, donc en clair sans TLS), chiffrement **AES** propriétaire des ordres d'alarme (clé par machine `Pkey`). À auditer lors de la migration. L'historique git montre des commits récents retirant des secrets en clair des configs (`fix(security): retirer les secrets en clair`).
- **Contrat protocole figé** : codes `201 Created`, en-tête `Content-Type` à espace, single-packet TCP, JSON à clés non quotées, ordre du champ `_de67f`, table d'échange complète + index 590 — **toutes ces particularités doivent être reproduites à l'identique** par le backend Go tant que des boîtiers BP_MQX_ETH sont e

_… voir source complète dans raw/_

## Liens

- [[Client Essensys Legacy]]
- [[Migration Legacy To Modern]]

## Source

`raw/architecture/repos/essensys-web-legacy.md`
