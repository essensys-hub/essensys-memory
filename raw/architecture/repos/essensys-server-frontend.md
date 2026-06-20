# essensys-server-frontend

> Interface web domotique en React + TypeScript + Vite qui pilote les boîtiers Essensys via l'API du backend Go, en remplacement de l'ancienne interface jQuery « Legacy ».

**Catégorie :** Frontend (SPA web responsive)
**Stack :** React 19, TypeScript 5.9, Vite 7, React Router 7, Tailwind CSS 4, Heroicons
**Statut :** actif (réécriture moderne de l'interface web legacy, v1.2.0)

## Rôle dans l'architecture Essensys

`essensys-server-frontend` est le **tableau de bord utilisateur** de la plateforme. C'est une Single Page Application qui remplace l'ancienne interface jQuery (`essensys-web-legacy`). Elle permet à l'utilisateur de contrôler son installation domotique : éclairages, chauffage, volets, alarme, arrosage, cumulus (chauffe-eau), notifications, ainsi que la visualisation des caméras UniFi Protect.

L'application ne contient pas de logique métier domotique propre : elle traduit les interactions UI en **injections d'actions** envoyées au backend Go (`essensys-server-backend`), qui les relaie ensuite aux boîtiers embarqués via la table d'échange (indices `k`/valeurs `v`). Le frontend manipule directement ces indices (« dindex »/« dvalue ») hérités du protocole legacy.

En production, les fichiers statiques compilés sont servis par nginx (`essensys-nginx`) qui proxifie `/api/*` vers le backend. En développement, Vite assure ce proxy.

## Stack technique & dépendances

`package.json` (`name: essensys-web-react`, `version: 1.2.0`, `type: module`) :
- **React 19** + **react-dom 19** — UI
- **react-router-dom 7** — routage SPA (`BrowserRouter`)
- **@heroicons/react** — icônes
- **Tailwind CSS 4** (`@tailwindcss/postcss`, `autoprefixer`, `postcss`) — styling
- **Vite 7** + `@vitejs/plugin-react` — bundler / dev server
- **TypeScript ~5.9**, **ESLint 9** (`typescript-eslint`, plugins react-hooks / react-refresh)
- **body-parser** (devDependency) — utilisé dans `vite.config.ts` pour corriger le proxy (voir Points d'attention)

Scripts : `npm run dev` (Vite, port 5173), `npm run build` (`tsc -b && vite build` → `dist/`), `npm run lint`, `npm run preview`.

## Structure du dépôt

```
essensys-server-frontend/
├── index.html                       # Point d'entrée HTML
├── vite.config.ts                   # Config Vite + proxy /api vers http://127.0.0.1:80
├── tsconfig*.json, eslint.config.js, postcss.config.js
├── Dockerfile                       # Build statique → /var/www/html (image essensys-base)
├── public/                          # Assets statiques (images, vite.svg)
├── dist/                            # Build de production (généré)
├── test/                            # Scripts Python de validation/reverse-engineering API
│   ├── test_chb3.py
│   └── test_degamenet2.py
└── src/
    ├── main.tsx                     # Bootstrap React
    ├── App.tsx                      # Définition des routes (React Router)
    ├── layouts/MainLayout.tsx       # Layout principal (Outlet)
    ├── pages/                       # Une page par domaine fonctionnel
    │   ├── DashboardPage.tsx        #   /dashboard (accueil, redirection par défaut)
    │   ├── LightingPage.tsx         #   /lighting
    │   ├── HeatingPage.tsx          #   /heating
    │   ├── ShuttersPage.tsx         #   /shutters
    │   ├── SecurityPage.tsx         #   /security (alarme)
    │   ├── WaterHeaterPage.tsx      #   /water-heater (cumulus)
    │   ├── SprinklerPage.tsx        #   /sprinkler (arrosage)
    │   ├── NotificationsPage.tsx    #   /notifications
    │   ├── UniFiProtectPage.tsx     #   /unifi-protect (caméras)
    │   └── SettingsPage.tsx         #   /settings
    ├── components/
    │   ├── Dashboard/               # Contrôles métier : LightingControl, HeatingControl,
    │   │                            #   ShutterControl, AlarmControl, SprinklerControl,
    │   │                            #   WaterHeaterControl, NotificationControl, BackendConfig
    │   ├── Layout/                  # Header, Layout
    │   ├── Navigation/              # SidebarMenu, BottomTabs, MobileDrawer, MobileHeader
    │   ├── UI/                      # ActionButton, CardSummary, ControlCard, PageHeader
    │   └── UniFi/                   # CameraCard
    ├── context/
    │   ├── DashboardContext.tsx     # État global du dashboard (DashboardState)
    │   └── ThemeContext.tsx         # Thème (clair/sombre)
    ├── hooks/useLastAction.ts       # Hook de récupération de la dernière action (history/latest)
    ├── services/
    │   ├── legacyApi.ts             # Communication backend : injections, exchange, alarme, history
    │   └── unifiApi.ts              # Récupération caméras + snapshots UniFi
    └── mockFetch.ts                 # Mock réseau pour tests/dev
```

## Build / Exécution / Déploiement

Développement :
```bash
npm install
npm run dev          # http://localhost:5173, proxy /api -> http://127.0.0.1:80
```

Production :
```bash
npm run build        # tsc -b && vite build -> dist/
```

Docker (`Dockerfile`, multi-stage) :
- Stage builder `node:20-alpine` → `npm ci` + `npm run build`.
- Stage final sur `essensyshub/essensys-base:raspberry.2026.02` : copie `dist/` dans `/var/www/html` (servi ensuite par nginx). `VOLUME ["/var/www/html"]`.

CI : `.github/workflows/`.

## Intégrations (composants Essensys et protocoles)

L'unique interlocuteur réseau est le **backend Go** (`essensys-server-backend`), via `fetch` HTTP/JSON. L'URL de base est résolue dynamiquement par `getBackendUrl()` (`src/components/Dashboard/BackendConfig.tsx`) selon le contexte :
- **Local / `mon.essensys.fr`** (HTTP) → URL relative `''` : nginx proxifie `/api/` vers le backend.
- **WAN** (HTTPS, ex. `essensys.rhinosys.io`) → `https://<host>`.
- **DNS configuré** stocké dans `localStorage` (`essensys_backend_dns`, `essensys_backend_port`) → `http://<dns>[:port]`.

Endpoints consommés :

| Service frontend | Endpoint backend | Méthode | Usage |
|------------------|------------------|---------|-------|
| `legacyApi.sendInjection` / `sendBatchInjections` | `/api/admin/inject` | POST | Injection d'actions `{k, v}` (lumières, volets, chauffage…). |
| `legacyApi.getExchangeValues` | `/api/admin/exchange?keys=` | GET | Relecture des valeurs remontées par le firmware (ex. temps de course volets 566–589). |
| `legacyApi.sendAlarmAction` | `/api/web/actions` | POST | Commande alarme `{alarme, codealarme}`. |
| `legacyApi.getHistoryLatest` (via `useLastAction`) | `/api/web/history/latest` | GET | Dernière action envoyée (avec `credentials: 'include'`). |
| `unifiApi.getCameras` | `/api/unifi/cameras` | GET | Liste des caméras UniFi Protect. |
| `unifiApi.getCameraSnapshot` / `getCameraSnapshotUrl` | `/api/unifi/cameras/{id}/snapshot` | GET | Snapshot caméra (blob, cache-busting `?t=`). |

Gestion de l'authentification : sur un retour `401`, `legacyApi` affiche une alerte et recharge la page pour déclencher le prompt Basic Auth du navigateur (`AuthenticationError`).

## Points d'attention

- **Couplage fort au protocole legacy** : l'UI manipule directement les indices de la table d'échange (`dindex`/`dvalue`, ex. lumières/volets 605–622). La logique de mapping (`buildLegacyPayload`, `LegacyMapping`) reprend telle quelle des conventions de l'ancien `essensys.js` (champs `newar`, `cfzj`, `vl_<dindex>_<i>`…). Toute évolution doit rester alignée sur le backend et le firmware.
- **Fix proxy Vite / chunked encoding** : `vite.config.ts` ajoute un middleware `body-parser` et force `Content-Length` sur les requêtes proxifiées. Sans cela le backend renvoie `400 Bad Request` car il ne supporte pas `Transfer-Encoding: chunked`. Ne pas retirer ce contournement.
- **Pas de gestion d'auth centralisée / pas de store de token** : authentification déléguée au Basic Auth navigateur ; recharge de page sur 401. Pas de route protégée côté React (toutes les routes sont accessibles, redirection par défaut vers `/dashboard`).
- **Configuration backend persistée en `localStorage`** (DNS/port saisis par l'utilisateur dans `BackendConfig`), avec résolution d'URL différente selon HTTP local vs HTTPS WAN — source potentielle de confusion lors des tests multi-environnements.
- **Logs verbeux en console** : `legacyApi.ts` journalise abondamment chaque injection (à nettoyer pour la production).
- **README vs structure réelle** : le `README.md` mentionne un sous-dossier `essensys-web-react/`, mais le code source est en réalité directement sous `src/` à la racine du dépôt.
- **Tests** : pas de tests unitaires JS ; le dossier `test/` contient uniquement des scripts Python de validation directe de l'API backend.
