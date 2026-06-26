---
tags: [entity, repo, modern, frontend]
sources: [essensys-user-portal-frontend.md]
created: 2026-06-20
updated: 2026-06-26
era: modern
repo: essensys-user-portal-frontend
---

# Essensys User Portal Frontend

> SPA React du portail domotique distant Essensys, servie sur `https://mon.essensys.fr/portal/`, qui permet à un utilisateur final de piloter son armoire à distance via le hub cloud (et non sur le réseau local).

| | |
|---|---|
| **Catégorie** | Frontend / SPA (Single Page Application) |
| **Stack** | React 19, TypeScript 5.9, Vite 7, React Router 7, Tailwind CSS 4, New Relic Browser |
| **Statut** | Actif — v0.2.0, déployé sous le préfixe `/portal/` (base Vite `/portal/`), build statique servi par Nginx sur OVH |
| **Era** | modern |

## Rôle

C'est l'interface web grand public du **portail domotique distant**. Elle se distingue de `essensys-server-frontend` (l'UI de l'installation **locale**, sur site) sur plusieurs points :

- **Accès distant** : l'utilisateur pilote son armoire depuis Internet, hors LAN. Les requêtes ne vont pas directement à l'armoire mais au hub cloud `essensys-user-portal-backend` qui dépose des actions relayées ensuite par la gateway du client.
- **Servie sous `/portal/`** sur `mon.essensys.fr`, pas à la racine d'un serveur local.
- **Authentification mutualisée avec le support-site** : le JWT est récupéré depuis `localStorage`/`sessionStorage` (clés `essensys_token` / `adminToken`), ou capté depuis l'URL après un redirect OAuth (`?token=...`). La déconnexion renvoie vers `/login?return=/portal/` (page de login du support-site).
- **Étape de liaison obligatoire** (`LinkGate`) : avant d'accéder à la domotique, l'utilisateur doit déposer une **demande de liaison** de son armoire (numéro de série) qu'un administrateur Essensys doit approuver. Tant que `portal_access` est `false`, seul cet écran s'affiche. Une armoire rattachée à la gateway legacy `essensys-server` est déclarée non éligible au portail distant.

Utilisateurs cibles : propriétaires d'armoires Essensys souhaitant un pilotage à distance. L'admin/support intervient côté backend pour valider les liaisons.

## Intégrations

- **essensys-user-portal-backend** : toutes les requêtes domotiques passent par `/api/portal/*` (statut de liaison, `POST /inject`, `GET /exchange`, `GET /gateway/status`) sur le même host. Le client gère le flag `stale` renvoyé par `GET /api/portal/exchange`.
- **Auth support-site** : JWT partagé (mêmes clés de stockage que `Login.jsx` du support-site) ; redirect login/logout vers `/login?return=/portal/`.
- **UniFi Protect** (`services/unifiApi.ts`) : proxy backend (URL configurable, défaut `http://localhost:7070`, endpoint `/api/unifi/cameras`) pour les caméras (page `UniFiProtectPage`).
- **New Relic Browser** : app `essensys-user-portal-frontend` (ID `538864961`), distincte du support-site (`538864962`).

## Structure

```
index.html                 # point d'entrée HTML (lang fr, #root)
vite.config.ts             # base '/portal/', port dev 5174, proxy /api/portal → :8081
src/
  main.tsx                 # bootstrap React
  App.tsx                  # garde d'accès (LinkGate vs PortalRoutes), routing
  api/portalApi.ts         # client /api/portal/* : token, fetch, link-status, inject, logout
  services/
    legacyApi.ts           # adaptateur domotique (inject + lecture table d'échange) — même API que server-frontend
    unifiApi.ts            # proxy UniFi Protect (caméras)
  components/
    LinkGate.tsx           # écran de demande/suivi de liaison d'armoire
    UI/                    # PageHeader, ActionButton, CardSummary, ControlCard
    Layout/                # Layout, Header
    Navigation/       

_… voir source complète dans raw/_

## Points d'attention

- **Garde d'accès à deux niveaux** : `App.tsx` n'affiche le tableau de bord que si `fetchLinkStatus().portal_access === true` ; sinon `LinkGate`. Toute régression côté backend sur `/portal/link-request/status` bloque toute l'app.
- **Gestion du token éparpillée** : récupération du JWT depuis plusieurs sources (`essensys_token`, `adminToken` en localStorage ET sessionStorage) plus capture depuis l'URL — couplage fort et fragile avec les conventions de stockage du support-site.
- **`legacyApi.ts` duplique l'API domotique de `essensys-server-frontend`** mais route l'inject via le cloud (`POST /api/portal/inject`). Les mappings d'indices (table d'échange) doivent rester synchronisés avec le serveur local et le firmware.
- **`unifiApi.ts` lit une URL backend en `localStorage` (`backend_url`, défaut `localhost:7070`)** et logge dans la console : configuration hétérogène par rapport au reste de l'app (qui utilise des chemins relatifs `/api/portal`).
- **Build New Relic fragile** : si `@newrelic/browser-agent` n'est pas installé, `npm run build` échoue (`Cannot find module …/loaders/browser-agent`) ; d'où le fallback rsync du `dist/` local documenté.
- **Base Vite figée à `/portal/`** : l'

_… voir source complète dans raw/_

- **[[Feature Lifecycle]] bootstrap (2026-06-26) :** gates CI + security gate **vert** sur `main`. Jumeau [[Essensys Server Frontend]] — toute modif `legacyApi` / indices k/v doit être reportée.
- **Pilotage éclairage distant (2026-06-26) :** `LightingPage` chevet Petite Chambre 3 (`iptchamb3`) — ON `k=613 v=64`, OFF `k=607 v=64` via `POST /api/portal/inject`. Panne résolue côté gateway : cloudsync désactivé (mauvais `config.yaml` systemd) → actions `pending` sur hub ; fix Ansible `raspberry_backend` `-config` central.

## Liens

- [[Essensys User Portal Backend]]
- [[Essensys Server Frontend]]

## Source

`raw/architecture/repos/essensys-user-portal-frontend.md`
