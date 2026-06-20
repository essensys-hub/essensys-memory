# essensys-user-portal-frontend

> SPA React du portail domotique distant Essensys, servie sur `https://mon.essensys.fr/portal/`, qui permet à un utilisateur final de piloter son armoire à distance via le hub cloud (et non sur le réseau local).

**Catégorie :** Frontend / SPA (Single Page Application)
**Stack :** React 19, TypeScript 5.9, Vite 7, React Router 7, Tailwind CSS 4, New Relic Browser
**Statut :** Actif — v0.2.0, déployé sous le préfixe `/portal/` (base Vite `/portal/`), build statique servi par Nginx sur OVH

## Rôle dans l'architecture Essensys

C'est l'interface web grand public du **portail domotique distant**. Elle se distingue de `essensys-server-frontend` (l'UI de l'installation **locale**, sur site) sur plusieurs points :

- **Accès distant** : l'utilisateur pilote son armoire depuis Internet, hors LAN. Les requêtes ne vont pas directement à l'armoire mais au hub cloud `essensys-user-portal-backend` qui dépose des actions relayées ensuite par la gateway du client.
- **Servie sous `/portal/`** sur `mon.essensys.fr`, pas à la racine d'un serveur local.
- **Authentification mutualisée avec le support-site** : le JWT est récupéré depuis `localStorage`/`sessionStorage` (clés `essensys_token` / `adminToken`), ou capté depuis l'URL après un redirect OAuth (`?token=...`). La déconnexion renvoie vers `/login?return=/portal/` (page de login du support-site).
- **Étape de liaison obligatoire** (`LinkGate`) : avant d'accéder à la domotique, l'utilisateur doit déposer une **demande de liaison** de son armoire (numéro de série) qu'un administrateur Essensys doit approuver. Tant que `portal_access` est `false`, seul cet écran s'affiche. Une armoire rattachée à la gateway legacy `essensys-server` est déclarée non éligible au portail distant.

Utilisateurs cibles : propriétaires d'armoires Essensys souhaitant un pilotage à distance. L'admin/support intervient côté backend pour valider les liaisons.

## Stack technique & dépendances

- **UI** : React 19 + React DOM 19, `react-router-dom` 7 (routing avec `basename="/portal"`).
- **Build** : Vite 7 (`@vitejs/plugin-react`), TypeScript 5.9 en mode strict (`tsc -b && vite build`).
- **Styles** : Tailwind CSS 4 (`@tailwindcss/postcss`, PostCSS, autoprefixer), couleur de marque `essensys-primary`.
- **Icônes** : `@heroicons/react`.
- **Observabilité** : `@newrelic/browser-agent` (chargé en lazy si `VITE_NEW_RELIC_ENABLED=true`).
- **Lint** : ESLint 9 + `typescript-eslint`, plugins React Hooks / React Refresh.

## Structure du dépôt

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
    Navigation/            # SidebarMenu, BottomTabs, MobileDrawer, MobileHeader, LogoutButton
    Dashboard/            # contrôles : Heating, Sprinkler, Notification, WaterHeater, Alarm, Lighting, Shutter, BackendConfig
    UniFi/                 # CameraCard
  pages/                   # Dashboard, Security, Heating, Lighting, Shutters, WaterHeater, Sprinkler, Notifications, Settings, UniFiProtect
  layouts/MainLayout.tsx
  context/                 # DashboardContext (état des items), ThemeContext
  hooks/                   # useLastAction, …
  observability/           # newrelic.ts, NewRelicPageTracker.tsx
docs/                      # index.md, deployment.md, observability.md
dist/                      # build de production (servi par Nginx)
```

Routing (`App.tsx`, `basename="/portal"`) : `/dashboard` (défaut), `/security`, `/heating`, `/lighting`, `/shutters`, `/water-heater`, `/sprinkler`, `/notifications`, `/settings`. Toute route inconnue redirige vers `/dashboard`.

## Build / Exécution / Déploiement

Développement local :

```bash
npm install
npm run dev      # Vite sur :5174, proxy /api/portal → http://127.0.0.1:8081 (backend local)
```

Build production :

```bash
npm run build    # tsc -b && vite build → dist/
npm run preview  # prévisualisation locale
npm run lint     # ESLint
```

Le `dist/` est déployé sur le VPS OVH dans `/opt/essensys/portal-frontend/dist/` et servi par Nginx :

```nginx
location ^~ /portal/ {
    alias /opt/essensys/portal-frontend/dist/;
    try_files $uri $uri/ /portal/index.html;
}
```

En mode consolidé, les appels `/api/portal/*` passent par `location /api/` → backend `:8080`.

Déploiement Ansible : rôle `essensys-ansible/roles/portal_frontend` (clone + `npm run build`, ou fallback `rsync` du `dist/` local si le build casse). Variables de build Vite injectées par Ansible/CI : `VITE_NEW_RELIC_ENABLED`, `VITE_NEW_RELIC_ACCOUNT_ID`, `VITE_NEW_RELIC_APPLICATION_ID`, `VITE_NEW_RELIC_AGENT_ID`, `VITE_NEW_RELIC_TRUST_KEY` (valeurs prod dans `group_vars/essensys/main.yml` ; license key Browser en vault).

CI : `.github/workflows/ci.yml` — Node 20, `npm install` → `npm run lint` → `npm run build`.

## Intégrations

- **essensys-user-portal-backend** : toutes les requêtes domotiques passent par `/api/portal/*` (statut de liaison, `POST /inject`, `GET /exchange`, `GET /gateway/status`) sur le même host. Le client gère le flag `stale` renvoyé par `GET /api/portal/exchange`.
- **Auth support-site** : JWT partagé (mêmes clés de stockage que `Login.jsx` du support-site) ; redirect login/logout vers `/login?return=/portal/`.
- **UniFi Protect** (`services/unifiApi.ts`) : proxy backend (URL configurable, défaut `http://localhost:7070`, endpoint `/api/unifi/cameras`) pour les caméras (page `UniFiProtectPage`).
- **New Relic Browser** : app `essensys-user-portal-frontend` (ID `538864961`), distincte du support-site (`538864962`).

## Points d'attention

- **Garde d'accès à deux niveaux** : `App.tsx` n'affiche le tableau de bord que si `fetchLinkStatus().portal_access === true` ; sinon `LinkGate`. Toute régression côté backend sur `/portal/link-request/status` bloque toute l'app.
- **Gestion du token éparpillée** : récupération du JWT depuis plusieurs sources (`essensys_token`, `adminToken` en localStorage ET sessionStorage) plus capture depuis l'URL — couplage fort et fragile avec les conventions de stockage du support-site.
- **`legacyApi.ts` duplique l'API domotique de `essensys-server-frontend`** mais route l'inject via le cloud (`POST /api/portal/inject`). Les mappings d'indices (table d'échange) doivent rester synchronisés avec le serveur local et le firmware.
- **`unifiApi.ts` lit une URL backend en `localStorage` (`backend_url`, défaut `localhost:7070`)** et logge dans la console : configuration hétérogène par rapport au reste de l'app (qui utilise des chemins relatifs `/api/portal`).
- **Build New Relic fragile** : si `@newrelic/browser-agent` n'est pas installé, `npm run build` échoue (`Cannot find module …/loaders/browser-agent`) ; d'où le fallback rsync du `dist/` local documenté.
- **Base Vite figée à `/portal/`** : l'app n'est pas servable à une autre racine sans rebuild (le routing dépend de `basename="/portal"`).
- **Armoires legacy `essensys-server` non supportées** : `LinkGate` affiche un message d'indisponibilité — logique d'éligibilité dupliquée côté front, à garder alignée avec `domain.IsRemoteEligibleGateway()` du backend.
