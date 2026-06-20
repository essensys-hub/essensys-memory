---
tags: [entity, repo, legacy, frontend]
sources: [essensys-server-frontend.md]
created: 2026-06-20
updated: 2026-06-20
era: legacy
repo: essensys-server-frontend
---

# Essensys Server Frontend

> Interface web domotique en React + TypeScript + Vite qui pilote les boîtiers Essensys via l'API du backend Go, en remplacement de l'ancienne interface jQuery « Legacy ».

| | |
|---|---|
| **Catégorie** | Frontend (SPA web responsive) |
| **Stack** | React 19, TypeScript 5.9, Vite 7, React Router 7, Tailwind CSS 4, Heroicons |
| **Statut** | actif (réécriture moderne de l'interface web legacy, v1.2.0) |
| **Era** | legacy |

## Rôle

`essensys-server-frontend` est le **tableau de bord utilisateur** de la plateforme. C'est une Single Page Application qui remplace l'ancienne interface jQuery (`essensys-web-legacy`). Elle permet à l'utilisateur de contrôler son installation domotique : éclairages, chauffage, volets, alarme, arrosage, cumulus (chauffe-eau), notifications, ainsi que la visualisation des caméras UniFi Protect.

L'application ne contient pas de logique métier domotique propre : elle traduit les interactions UI en **injections d'actions** envoyées au backend Go (`essensys-server-backend`), qui les relaie ensuite aux boîtiers embarqués via la table d'échange (indices `k`/valeurs `v`). Le frontend manipule directement ces indices (« dindex »/« dvalue ») hérités du protocole legacy.

En production, les fichiers statiques compilés sont servis par nginx (`essensys-nginx`) qui proxifie `/api/*` vers le backend. En développement, Vite assure ce proxy.

## Intégrations

_Non documenté._

## Structure

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
    ├── layouts/MainLayout.tsx       # Layout princ

_… voir source complète dans raw/_

## Points d'attention

- **Couplage fort au protocole legacy** : l'UI manipule directement les indices de la table d'échange (`dindex`/`dvalue`, ex. lumières/volets 605–622). La logique de mapping (`buildLegacyPayload`, `LegacyMapping`) reprend telle quelle des conventions de l'ancien `essensys.js` (champs `newar`, `cfzj`, `vl_<dindex>_<i>`…). Toute évolution doit rester alignée sur le backend et le firmware.
- **Fix proxy Vite / chunked encoding** : `vite.config.ts` ajoute un middleware `body-parser` et force `Content-Length` sur les requêtes proxifiées. Sans cela le backend renvoie `400 Bad Request` car il ne supporte pas `Transfer-Encoding: chunked`. Ne pas retirer ce contournement.
- **Pas de gestion d'auth centralisée / pas de store de token** : authentification déléguée au Basic Auth navigateur ; recharge de page sur 401. Pas de route protégée côté React (toutes les routes sont accessibles, redirection par défaut vers `/dashboard`).
- **Configuration backend persistée en `localStorage`** (DNS/port saisis par l'utilisateur dans `BackendConfig`), avec résolution d'URL différente selon HTTP local vs HTTPS WAN — source potentielle de confusion lors des tests multi-environnements.
- **Logs verbeux en co

_… voir source complète dans raw/_

## Liens

- [[Essensys Server Backend]]
- [[Table D Echange]]

## Source

`raw/architecture/repos/essensys-server-frontend.md`
