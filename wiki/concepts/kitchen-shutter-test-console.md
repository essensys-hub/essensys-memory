---
tags: [concept, feature-etalon, ux, no-armoire, kitchen, volets, lifecycle, playwright, table-d-echange]
sources: [essensys-kitchen-shutter-test-console-2026-06-031]
created: 2026-06-28
updated: 2026-06-28
era: modern
---

# Kitchen Shutter Test Console

**Feature étalon** du lifecycle ESSENSYS. Console de diagnostic UI dry-run qui permet de visualiser et simuler les actions volets cuisine via le protocole legacy (table d'échange), sans jamais déclencher une vraie armoire.

## Objectif

Valider de bout en bout la chaîne lifecycle ESSENSYS :
`Idée → OpenSpec → Manifest → UI → Tests UX multi-device → no-armoire gate → Security/Lifecycle gate → Docs → OKF memory`

## Surface implémentée

- **Repo** : `essensys-server-frontend`
- **Page** : `src/pages/KitchenShutterTestConsolePage.tsx`
- **Route** : `/kitchen-shutter-test-console`
- **OpenSpec** : `essensys-kitchen-shutter-test-console-2026-06-031`

## Protocole legacy cuisine

Indices [[Table D Echange]] utilisés :

| Action                  | Indice k | Valeur v |
|-------------------------|----------|----------|
| Ouvrir volet cuisine 1  | 619      | 1        |
| Ouvrir volet cuisine 2  | 619      | 2        |
| Ouvrir les deux volets  | 619      | 3        |
| Fermer volet cuisine 1  | 622      | 1        |
| Fermer volet cuisine 2  | 622      | 2        |
| Fermer les deux volets  | 622      | 3        |
| Trigger scénario        | 590      | 1        |

## no-armoire gate

La console est en mode `dry-run` permanent pendant les tests :
- Aucun appel réel vers `/api/admin/inject` ou `/api/portal/inject`
- Toute tentative POST inject est interceptée / mockée dans les tests Playwright
- Bannière "Mode test no-armoire" toujours visible
- Gate `check_feature_gate.py --strict` vérifie la présence de `no_armoire_required: true`

Voir [[ESSENSYS UX Matrix Gate]].

## UX Matrix

- `desktop` : console complète, tous boutons visibles, payload affiché
- `iphone` : responsive, pas de scroll horizontal, payload lisible
- `ipad` : layout tablette, carte + détails en colonnes

## Fichiers clés

| Chemin | Rôle |
|--------|------|
| `src/pages/KitchenShutterTestConsolePage.tsx` | Page UI React |
| `e2e/tests/kitchen-shutter-test-console.spec.ts` | Tests Playwright multi-device |
| `e2e/fixtures/no-armoire.ts` | Fixture d'interception inject |
| `features/essensys-kitchen-shutter-test-console-2026-06-031.json` | Manifest lifecycle |
| `openspec/changes/essensys-kitchen-shutter-test-console-2026-06-031/` | OpenSpec complet |
| `docs/features/kitchen-shutter-test-console.md` | Documentation utilisateur |

## Liens

- [[Table D Echange]] — indices 619/622 cuisine
- [[ESSENSYS UX Matrix Gate]] — gate UX multi-device
- [[Scénarios domotique]] — trigger 590
