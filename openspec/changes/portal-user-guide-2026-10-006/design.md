## Context

Voir proposal.md (section Why). Ce qui existe aujourd'hui et contraint la conception :

- **Portail** (`essensys-user-portal-frontend`, React 19 + TypeScript + Vite) :
  - les écrans sont déclarés dans `src/App.tsx`, sous `/portal` en production ;
  - un **mode démo** (`VITE_DEMO_MODE=true`) remplace `fetch` par `src/mockFetch.ts` et `src/mockScenarios.ts` : API simulée, « zéro action armoire » ;
  - `VITE_DEMO_ROOT=true` sert le portail à la racine ;
  - Playwright n'est pas installé ; un dossier `docs/` existe déjà (déploiement, observabilité).
- **Site** (`essensys-support-site`, React + Vite) :
  - la session est le jeton `adminToken` (localStorage ou sessionStorage) ;
  - `/signaler` montre déjà le modèle « réservé aux connectés » (invitation à se connecter, retour par `?return=`) ;
  - `react-markdown` est déjà utilisé (`Privacy.jsx`) ;
  - le **blog** est publié depuis un autre dépôt : le rôle Ansible `frontend` clone `essensys-memory`, `prepare_blog_from_memory.py` produit `site/public/blog-data/` (index JSON et Markdown) avant `npm run build`, et `Blog.jsx` lit ces fichiers.
- **Déploiement** : le rôle `frontend` construit le site sur le serveur à partir d'un tag (`support_site_version`).

## Goals / Non-Goals

**Goals**
- Un guide complet (12 écrans) qui se régénère en une commande quand l'interface change.
- Publication sans copie manuelle entre dépôts.

**Non-Goals**
- Pas de guide de l'application iPhone ni Android dans cette version (écrans proches, guide séparé plus tard).
- Pas de traduction (français seulement).
- Pas de recherche plein texte dans le guide.
- Pas de protection serveur des fichiers du guide : voir le risque D6.

## Decisions

**D1. Format de la source.**
- `docs/user-guide/index.yml` liste les pages dans l'ordre, avec `slug`, `title`, `summary` et `screen` (route du portail ou du site).
- Une page par écran, `docs/user-guide/<slug>.md` : sections fixes « À quoi sert cet écran », « Y accéder », « L'écran en détail » (liste numérotée qui correspond aux repères de la capture), « Messages courants », « Un problème ? ».
- Les captures sont dans `docs/user-guide/images/<slug>-desktop.png` et `<slug>-mobile.png`.
- Slugs : `premiers-pas`, `connexion`, `tableau-de-bord`, `eclairage`, `volets`, `chauffage`, `chauffe-eau`, `arrosage`, `scenarios`, `securite`, `notifications`, `reglages`, `profil-signalements`.

**D2. Repères numérotés sur les captures.**
- Au moment de la capture, le script Playwright pose des pastilles numérotées sur les éléments cités. Les éléments sont désignés par des sélecteurs stables : `data-testid`, ou rôle et nom accessibles, listés dans `docs/user-guide/screens.ts`.
- La capture se fait ensuite, puis les pastilles sont retirées.
- Le texte et l'image utilisent les mêmes numéros. Si un sélecteur ne trouve plus son élément, le script échoue : c'est le signal que le guide doit être mis à jour.
- *Alternative écartée* : annoter les images à la main. C'est impossible à maintenir quand l'interface change.

**D3. Commande `npm run docs:screenshots` (portail).**
- Elle construit le portail en mode démo à la racine (`VITE_DEMO_MODE=true`, `VITE_DEMO_ROOT=true`), lance `vite preview` sur un port local et exécute `docs/user-guide/capture.spec.ts` avec Playwright, projets `desktop` (1280×800) et `mobile` (iPhone 14).
- Garde-fou : le script fait échouer la capture si une requête part vers un hôte autre que `localhost`. Pour cela, `page.route('**/*')` refuse et signale tout hôte externe.
- Une capture en thème sombre est faite pour le tableau de bord.
- Les données de démo (`mockFetch.ts`) sont complétées si un écran est vide ou peu représentatif : au moins 3 pièces, 2 volets, 2 zones de chauffage et 1 scénario. Toutes sont fictives.

**D4. Écrans du site** (connexion, profil, signalement).
- Le spec Playwright du site `e2e/guide-screenshots.spec.js` capture `/login`, `/change-password`, `/profile` et `/signaler`, avec l'API simulée par `page.route` (modèle des tests existants).
- Les images sont copiées dans `essensys-user-portal-frontend/docs/user-guide/images/` par le script `scripts/sync-guide-screenshots.sh` du site, pour garder une seule source.

**D5. Publication.**
- Le rôle Ansible `frontend` clone `essensys-user-portal-frontend` à la version `portal_user_guide_version` (défaut : `main`). Ensuite, `prepare_guide_from_portal.py` produit `site/public/guide-data/` avant le build :
  - `index.json` (ordre, titres, résumés) ;
  - un fichier `<slug>.md` par page, avec les liens d'images réécrits vers `/guide-data/images/…` ;
  - les images.
- Le site ajoute les routes `/guide` (sommaire) et `/guide/:slug` (page), rendues avec `react-markdown`.
- Sans `guide-data` (build local), la page affiche « Guide en cours de préparation ». La commande `npm run guide:local` prépare les données depuis un checkout voisin du portail.

**D6. Accès réservé aux connectés.**
- `GuidePage.jsx` lit le jeton comme `Home.jsx` et `Report.jsx`. Sans jeton, il affiche l'invitation à se connecter, avec `return=/guide/<slug>`, et **ne charge pas** les fichiers du guide.
- Les fichiers `/guide-data/*` restent des fichiers statiques. Ils sont donc techniquement lisibles par quelqu'un qui connaît leur adresse.
- *Pourquoi c'est acceptable* : le guide ne contient que des données fictives et rien de sensible. On ajoute `X-Robots-Tag: noindex` (bloc nginx `location /guide-data/`) et `Disallow: /guide` dans `robots.txt`.
- *Alternative écartée pour cette version* : faire servir le guide par le backend derrière la session (`/api/guide/*`). C'est plus robuste, mais il faut une route backend et un stockage. Ce sera possible plus tard sans changer les pages du site.

**D7. Liens d'accès.** Lien « Guide du portail » dans le menu (`Layout.jsx`, connecté seulement), sur la page Support et dans le profil.

### Tests et non-régression
- **Portail** :
  - `docs:screenshots` en CI : il échoue si un sélecteur de `screens.ts` ne trouve plus son élément, ou si une requête sort vers un hôte externe ;
  - les captures produites sont publiées en artefact de CI.
- **Site** (Playwright `e2e/guide.spec.js`, desktop, iPhone et iPad, API et `guide-data` simulés) :
  - `NR-site-6` : visiteur → invitation, aucun contenu chargé ;
  - `NR-site-7` : retour après connexion sur la page demandée ;
  - `NR-site-8` : page lisible à 375 px, sans défilement horizontal ;
  - plus : sommaire complet (13 entrées), page inconnue, liens depuis le profil et le menu.
- **Script de préparation** (`unittest`) : ordre, réécriture des liens d'images, slug inconnu ignoré, dossier absent signalé.

## Risks / Trade-offs

- [Le guide se périme quand l'interface change] → les sélecteurs de `screens.ts` font échouer la CI du portail. Le sommaire est testé contre la liste des routes.
- [Fichiers du guide lisibles sans session (D6)] → contenu fictif et non sensible, `noindex`. L'évolution possible est la route backend.
- [Le mode démo diverge du vrai portail] → les captures se font sur le vrai code des écrans ; seule l'API est simulée.
- [Écrans encore en évolution (chauffage, chauffe-eau, arrosage, sécurité)] → ils sont inclus, avec une mention « cet écran évolue ». Leurs captures se régénèrent à chaque évolution.

## Migration Plan

1. Fusionner le portail (guide et captures), puis Ansible (préparation), puis le site (pages `/guide`).
2. Déployer le site avec le rôle `frontend`, qui récupère le guide.
3. Vérifier en ligne : déconnecté (invitation), connecté (sommaire et pages).
4. **Retour arrière** : redéployer le tag précédent du site. Le guide disparaît, sans effet sur le reste.
