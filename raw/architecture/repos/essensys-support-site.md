# essensys-support-site

> Portail de support communautaire d'Essensys : SPA React (vitrine + espace utilisateur/admin) doublée d'une documentation MkDocs, autour d'un backend Go aujourd'hui déprécié au profit du hub cloud unifié.

**Catégorie :** Documentation / Site
**Stack :** Frontend React 19 + Vite 7 + react-router 7 (Leaflet, Mermaid, react-markdown) ; docs MkDocs Material ; backend Go (legacy, déprécié) ; shim PHP `api/serverinfos`
**Statut :** En évolution — branche active `V.1.0.0` (remote `github.com/essensys-hub/essensys-support-site`). Backend Go **déprécié depuis juin 2026** (remplacé par `essensys-user-portal-backend`).

## Rôle dans l'architecture Essensys
Le dépôt porte le **site web de support du projet Essensys Open Source** (l'éditeur d'origine, Valentinéa, n'existe plus ; le site officiel a fermé). Ses objectifs : pérenniser les installations existantes (documentation, support), moderniser la solution (Raspberry Pi, apps iOS/Android) et héberger le portail communautaire centralisant ces ressources.

Le dépôt a dépassé sa phase « conception » initiale : il contient désormais une SPA React fonctionnelle (vitrine + comptes utilisateurs + back-office admin), une documentation MkDocs, et un ancien backend Go de gestion des comptes/machines/newsletters.

## Public visé
Deux personas explicites (cf. `synopsis_design.md`) :
- **Le propriétaire historique** — possède une maison équipée Essensys, cherche réassurance et guides pas-à-pas simples.
- **Le tech / maker** — veut le contrôle total via Raspberry Pi, API et code source.

Ton recherché : « Premium », technique mais accessible, communautaire, épuré, dark mode (références visuelles : docs Vercel/Stripe).

## Contenu / structure
- **`site/` — application web (livrable principal) :** Vite + React 19. `src/pages/` : `Home`, `Support`, `RaspberryPi`, `DownloadPage`, pages auth (`Login`, `Register`, `Profile`), pages mobiles (`ios`, `android`), et **back-office** (`Admin`, `UserManager`, `NewsletterManager`, `LinkRequestsPanel`, `Catalog`), plus `Privacy`. Routage via react-router. Observabilité New Relic Browser Agent. Artefacts de build versionnés (`dist/`, `site-dist.tar.gz`).
- **`docs/` — documentation MkDocs :** `index.md`, `features.md`, `authentication.md`, `roles_matrix.md`, `audit_trail.md`, `configuration.md`, `portal-link-workflow.md`, `privacy_policy.md`, + table de référence (`TableReference.csv/.json/.numbers`).
- **`backend/` — backend Go (déprécié) :** API REST (`internal/api/handlers_*.go` : auth, admin, user, newsletter, oauth), middleware, modèles, `gatewayrules`, service systemd `essensys-backend.service`, binaire `essensys-passive-backend`.
- **`api/serverinfos/index.php`** — shim PHP exposant `serverinfos` (compat protocole legacy côté hébergement web).
- **Docs fondatrices** : `historique.md`, `specifications.md`, `synopsis_design.md`, `catalog.md` (processus Catalogue : référentiel versionné des actions, format `YYYY.MM.NNN`), `essensys-client.md` (protocole HTTP du firmware BP_MQX_ETH : endpoints `/api/serverinfos`, `/api/mystatus`, `/api/myactions`), `LEGACY_IOT_AUTHENTICATION.md`, `prompts.md`.
- **Scripts d'exploitation** : `install.sh`, `update.sh`, `uninstall.sh`, `manage.sh`, `manage_ssl.sh`, `setup_ssl.sh`, `debug_ssl.sh`, `console.py`, `essensys.nginx`. Sous-dossiers `rpi-client/`, `maintenance/`, `stitch/`, `img/`.

## Build / Publication (générateur, hébergement)
- **Site React :** `npm run build` (Vite) → `site/dist/`. Pas de workflow CI dédié au build de la SPA dans le dépôt (déploiement via les scripts d'install/update + nginx `essensys.nginx`).
- **Documentation :** GitHub Actions `.github/workflows/deploy-docs.yml` — sur push `master`/`main`/`collect`, installe `mkdocs-material` et exécute `mkdocs gh-deploy --force` (publication GitHub Pages). Le `mkdocs.yml` racine définit une nav Features/Configuration (thème Material, palette teal/purple).
- **Backend Go :** déployé historiquement via `essensys-backend.service` (systemd) ; aujourd'hui non déployé.

## Intégrations
- **Frontend ↔ backend cloud :** l'app consomme désormais le hub unifié `essensys-user-portal-backend` (`CONSOLIDATED_MODE=true`, service `essensys-cloud-backend:8080`) plutôt que le backend Go local.
- **Protocole legacy :** `essensys-client.md` + `api/serverinfos/index.php` assurent la compatibilité avec le firmware BP_MQX_ETH (`mon.essensys.fr`).
- **Référence catalogue :** `catalog.md` s'appuie sur la page de debug publiée par `essensys-raspberry-install` (`essensys-hub.github.io/essensys-raspberry-install/maintenance/debug/`).
- **Apps mobiles :** liens vers `essensys-ios-phone-apps` et `essensys-android-phone-apps`.
- **Cartographie :** Leaflet/react-leaflet (localisation des installations) ; observabilité New Relic.

## Points d'attention
- **Dette/migration en cours :** le `backend/` Go est explicitement déprécié (README backend) mais conservé « jusqu'à fin de soak » (OpenSpec Phase 7.6) — code mort à terme, risque de confusion sur la source d'autorité.
- **Dépôt hétérogène :** mélange vitrine React, doc MkDocs, backend Go, shim PHP, scripts shell d'exploitation et docs de conception dans un seul repo — périmètre flou.
- **Binaires et artefacts versionnés** (`essensys-passive-backend`, `server`, `dist/`, `site-dist.tar.gz`, gros PNG `fond-inprogress.png` ~7,8 Mo) → poids du dépôt et bruit dans l'historique.
- **Secrets :** présence de `.env` à la racine et `.env.template` backend — vérifier qu'aucun secret réel n'est commité.
- Branche par défaut `V.1.0.0` (et non `main`) alors que le workflow docs déploie sur `master`/`main`/`collect` — risque que la doc ne se publie pas depuis la branche active.
- README encore présenté comme « phase de conception » alors que l'implémentation est avancée → documentation racine à actualiser.
