---
tags: [ui, playwright, testing, domotique, no-armoire]
sources: [essensys-ui-multi-device-testing]
created: 2026-06-27
updated: 2026-06-27
era: modern
---

# UI Multi Device Testing

La matrice UI multi-device ESSENSYS valide les interfaces domotiques et support sur plusieurs formats sans piloter une armoire réelle.

## Objectif

- Tester les surfaces **local**, **remote portail** et **support OVH** sur desktop, iPhone, Android, iPad et écran domotique tactile.
- Générer des captures Playwright pour vérifier visuellement menus, boutons de navigation et objets UI.
- Garantir **zéro action armoire** pendant les tests.

## URLs démo autorisées

| Cible | URL démo |
|---|---|
| local | `https://demo.essensys.local` |
| support OVH | `https://demo.essensys.fr` |
| remote portail | `https://demo.portail.essensys.fr` |

Si une URL démo ne résout pas, le test doit s'arrêter et signaler le DNS manquant. Il ne faut pas remplacer par une IP ou gateway client.

## Garde no-armoire

Le dossier `essensys-server-frontend/e2e/` contient une fixture `fixtures/no-armoire.ts` qui intercepte `**/api/**` :

- POST/PUT/PATCH/DELETE sans dry-run vers `/inject`, `/web/actions` ou `/scenarios/*/launch` → réponse bloquée `451`, motif `BLOQUÉ no-armoire`.
- Mutation avec `test_mode=dry_run` ou `X-Essensys-Test-Mode: dry-run` → mock local `{ status: 'test_ok', dry_run: true }` pour éviter toute sortie armoire.
- Support-site → API mockée côté navigateur.

## Commandes de référence

```bash
cd essensys-server-frontend/e2e
npm run test:matrix
npm run test:support
npm run test:local
npm run test:remote
npm run test:device -- iphone
npm run test -- no-armoire.spec.ts --project=support-desktop
```

Les captures sont produites dans `essensys-server-frontend/e2e/artifacts/screenshots/` par `ui-smoke.spec.ts`.

## Résolutions écran domotique

Profils initiaux à maintenir tant que le parc installé n'est pas plus précis :

- `ecran-domo` : 1024×600 paysage, tactile.
- `ecran-domo-compact` : 800×480 paysage, tactile.
- `ecran-domo-portrait` : 600×1024 portrait, tactile.

Une dalle confirmée 1280×800 devra ajouter un profil dédié avant création de snapshots baseline.

## Autocritique visuelle support 2026-06-27

La première passe de captures `support-*` a validé la structure globale desktop/tablette/écran domotique, mais a ajouté des corrections bloquantes avant baseline :

- iPhone : la navigation basse ne doit jamais masquer une carte, un bouton ou un état caméra ; le contenu doit réserver `bottom-nav + safe-area`.
- iPad : les cartes dashboard ne doivent pas toutes afficher un contour bleu de focus simultanément ; le ring doit être discret et limité à l'élément réellement focus.
- Mobile : le header doit rester compact avec logo visible.
- Caméras : en mock/support, l'état vide doit préciser que le flux est indisponible ou désactivé en mode démo, pas seulement “Image indisponible”.
- Écran domotique : vérifier la densité 800×480 et l'atteignabilité du dernier contrôle par scroll/tap.

## Code pointers

- `essensys-server-frontend/e2e/playwright.config.ts`
- `essensys-server-frontend/e2e/fixtures/no-armoire.ts`
- `essensys-server-frontend/e2e/tests/ui-smoke.spec.ts`
- `essensys-server-frontend/e2e/tests/no-armoire.spec.ts`
- `essensys-server-frontend/e2e/devices/ecran-domotique.ts`
