## 1. Captures automatiques — essensys-user-portal-frontend (essensys-user-portal-frontend#24)

- [x] 1.1 Ajouter Playwright (dev), `docs/user-guide/screens.ts` (écrans, routes, repères numérotés) et `docs/user-guide/capture.spec.ts` (D2, D3) avec le garde-fou « aucun hôte externe » ; vérifier qu'une requête vers un hôte externe fait échouer la capture
- [x] 1.2 Script `npm run docs:screenshots` (build démo à la racine, preview locale, projets desktop et mobile) ; vérifier qu'il produit `<slug>-desktop.png` et `<slug>-mobile.png` pour les 10 écrans du portail
- [x] 1.3 Compléter les données de démo (`mockFetch.ts`, `mockScenarios.ts`) pour que chaque écran soit représentatif et fictif ; vérifier visuellement chaque capture (aucune donnée réelle, aucun écran vide)
- [x] 1.4 CI : `docs:screenshots` à chaque PR, captures en artefact ; vérifier qu'un sélecteur cassé fait échouer la CI

## 2. Rédaction du guide — essensys-user-portal-frontend (essensys-user-portal-frontend#25)

- [x] 2.1 `docs/user-guide/index.yml` et la page « Premiers pas » (se connecter, lier son armoire, première commande) ; vérifier l'ordre et les titres
- [x] 2.2 Pages Tableau de bord, Éclairage, Volets et stores (sections fixes de D1, numéros alignés sur les repères) ; vérifier chaque numéro contre sa capture
- [x] 2.3 Pages Chauffage, Chauffe-eau, Arrosage, Scénarios, Sécurité (mention « cet écran évolue » si besoin) ; même vérification
- [x] 2.4 Pages Notifications, Réglages, Connexion et mots de passe, Profil et signalements ; même vérification
- [ ] 2.5 Relecture par une personne extérieure au projet et intégration de ses retours ; tracer en commentaire sur #26

## 3. Écrans du site et publication — essensys-support-site (essensys-support-site#13)

- [x] 3.1 `e2e/guide-screenshots.spec.js` (connexion, mot de passe temporaire, profil, signalement ; API simulée) et `scripts/sync-guide-screenshots.sh` vers le dépôt du portail (D4) ; vérifier les 8 images produites
- [x] 3.2 Pages `/guide` et `/guide/:slug` (`GuidePage.jsx`, rendu Markdown, réservé aux connectés, page inconnue, « en cours de préparation » sans données) et `npm run guide:local` ; vérifier `npm run lint` et `npm run build`
- [x] 3.3 Liens « Guide du portail » : menu (connecté), Support, Profil ; `robots.txt` `Disallow: /guide` ; vérifier dans le navigateur
- [x] 3.4 Playwright `e2e/guide.spec.js` desktop, iPhone et iPad : `NR-site-6` (visiteur, aucun contenu chargé), `NR-site-7` (retour après connexion), `NR-site-8` (375 px sans défilement horizontal), sommaire de 13 entrées, page inconnue ; vérifier que tout passe sur les 3 projets
- [x] 3.5 Manifest `features/portal-user-guide-2026-10-006.json` (site) et `features/` du portail ; vérifier `validate_feature_manifests.py` et `check_feature_gate.py --strict`

## 4. Préparation au déploiement — essensys-ansible (essensys-ansible#6)

- [x] 4.1 `roles/frontend` : clone du portail (`portal_user_guide_version`, défaut `main`) et appel de `site/scripts/prepare_guide.py` (tests `unittest` dans le site : ordre, réécriture des images et des liens, dossier absent) vers `site/public/guide-data/` avant le build (D5) ; vérifier `--syntax-check` et les tests
- [x] 4.2 Bloc nginx `location /guide-data/` avec `X-Robots-Tag: noindex` dans `essensys.nginx` du site (D6) ; vérifier `nginx -t` dans un conteneur local ou la relecture du diff

## 5. Livraison — essensys-feature-lifecycle (essensys-feature-lifecycle#27)

- [x] 5.1 `/checkup portal-user-guide-2026-10-006` vert et rapport posté sur #26
- [x] 5.2 Déployer le site (tag `prod-ovh-…`) ; vérifier en ligne : déconnecté (invitation, aucune capture), connecté (sommaire et 13 pages), mobile
- [x] 5.3 Mettre à jour essensys-memory : wiki [[Essensys Support Site]] (pages `/guide`), [[Essensys User Portal Frontend]] (guide et captures), `log.md` et roadmap
