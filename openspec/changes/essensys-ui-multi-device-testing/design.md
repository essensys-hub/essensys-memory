## Context

| Élément | État actuel |
|---------|-------------|
| Playwright | `essensys-server-frontend/e2e/` — 5 specs, ~88 lignes, **Desktop Chrome** uniquement |
| Projects | `demo`, `local`, `remote` (3 cibles, 1 device) |
| Anti-armoire | `VITE_DEMO_MODE` + `mockFetch`, `?test_mode=dry_run` + header (026), dry-run inject |
| Jumeaux UI | `essensys-server-frontend` ↔ `essensys-user-portal-frontend` — mêmes pages |
| Support-site | Aucun e2e Playwright |
| Prompt source | `prompts/ui-multi-device-testing.md` |

**Stakeholders :** équipe frontend, QA, CI, installateurs (validation écran mural).

## Goals / Non-Goals

**Goals:**

- Une commande lance la matrice **demo** (5 devices, zéro backend armoire).
- Garantie **zéro action armoire** prouvée par test négatif (fixture §3.2).
- Couverture features jumelles : dashboard, volets, lumières, chauffage, scénarios, sécurité, etc.
- Snapshots visuels par device ; CI verte sur PR (demo/support).
- 100 % stack open-source (Playwright Apache-2.0).

**Non-Goals:**

- BrowserStack / Sauce Labs / Percy obligatoires (Lost Pixel MIT = optionnel Phase ultérieure).
- Tests write live sur armoire client.
- Duplication d'une spec par couple device×cible.

## Decisions

### D1 — Emplacement source unique : étendre `essensys-server-frontend/e2e/`

**Choix :** étendre le dossier existant plutôt qu'un dépôt `essensys-e2e/` racine.

**Rationale :**

- Playwright, config et 5 specs déjà présents ; CI frontend en place.
- Les jumeaux UI sont testés via **baseURL** différente (`/portal/`), pas via duplication de code page.
- Support-site ajouté comme **projects** supplémentaires (`support-*`) pointant vers URL mockée ou staging.

**Alternative rejetée :** monorepo `essensys-e2e/` — overhead sync multi-repo, pas de gain pour les jumeaux (même composants).

### D2 — Génération matrice : projects nommés `{cible}-{device}`

```text
support-desktop | support-iphone | … | support-ecran-domo
local-desktop   | …              | local-ecran-domo
remote-desktop  | …              | remote-ecran-domo
```

- **local-cm5** et **local-rpi** : même project config (`local-*`) ; distinction documentée (hardware) — pas de duplication CI sauf flag `ESSENSYS_GATEWAY_PROFILE=cm5|rpi` pour métadonnées rapport.
- Devices Playwright : `Desktop Chrome`, `iPhone 14`, `Pixel 7`, `iPad (gen 7)`, + custom `ecran-domotique`.

### D3 — Trois couches anti-armoire (cumulatives)

| Couche | Mécanisme |
|--------|-----------|
| 1 — Exécution | demo → `VITE_DEMO_MODE` / mockFetch ; remote/local staging → `?test_mode=dry_run` + `X-Essensys-Test-Mode: dry-run` |
| 2 — Réseau | Fixture `fixtures/no-armoire.ts` — `page.route('**/api/**')` abort/throw si POST/PUT/PATCH mutant sans dry-run |
| 3 — Environnement | URLs par défaut = `demo.essensys.fr` / staging ; `ESSENSYS_ALLOW_LIVE_READONLY=1` requis pour prod read-only ; **jamais** write live |

### D4 — Specs partagées : paramétrage par `testInfo.project.name`

Une spec `shutters.spec.ts` exécutée par tous les projects ; helpers :

- `getTargetFromProject(name)` → `support` | `local` | `remote`
- `getDeviceFromProject(name)` → `desktop` | `iphone` | …
- Page Objects dans `e2e/pages/` — sélecteurs identiques jumeaux.

### D5 — Écran domotique : liste de viewports, pas une valeur figée

Fichier `e2e/devices/ecran-domotique.ts` :

| Profil | Viewport | Touch | Notes |
|--------|----------|-------|-------|
| `ecran-domo-landscape` | 1024×600 | oui | défaut mural |
| `ecran-domo-portrait` | 600×1024 | oui | rotation |
| `ecran-domo-compact` | 800×480 | oui | dalles legacy |

Phase 0 : confirmer résolutions réelles installées (CM5 clients) → ajuster liste.

### D6 — Snapshots : Playwright natif

- `expect(page).toHaveScreenshot({ maxDiffPixelRatio: 0.01 })` par device/project.
- Baseline dans `e2e/tests/**/*.spec.ts-snapshots/` (git).
- `npm run test:update-snapshots` documenté ; revue PR obligatoire sur diff visuel.

**Lost Pixel (MIT)** : optionnel post-MVP pour revue HTML — non bloquant.

### D6b — Critères autocritique visuelle support-* avant baseline

Les captures `support-*` générées en Phase 5 servent aussi de revue UX manuelle avant de figer les baselines. Les remarques issues de l'autocritique du 2026-06-27 deviennent des critères bloquants pour la DoD visuelle :

| Critère | Risque observé | Attendu |
|---------|----------------|---------|
| Navigation basse mobile | Sur iPhone, `BottomTabs` peut recouvrir la carte caméra / dernier contenu | Le contenu scrollable réserve la hauteur de la bottom-nav + `safe-area`; aucun contrôle ou état caméra n'est masqué |
| Focus cards tablette | Sur iPad dashboard, toutes les cartes peuvent apparaître avec un contour bleu excessif | Le focus visible n'apparaît que sur l'élément réellement focus, avec un ring discret et accessible |
| Header mobile | Header mobile trop haut ou trop vide | Logo compact visible, hauteur stable, contenu utile non repoussé inutilement |
| État caméra démo | “Image indisponible” peut ressembler à une panne | Message explicite “Flux caméra indisponible en mode démo” quand applicable |
| Écran domotique | Risque de densité trop forte en 800×480 | Pas de scroll horizontal, dernier contrôle atteignable, zone tactile conservée |

### D7 — CI

- **PR** : `demo` + `support` × 5 devices (~15–20 min cible, parallélisable).
- **Nightly / dispatch** : `local-*`, `remote-*` avec secrets (`ESSENSYS_BASIC_*`, JWT staging).
- Artefacts : rapport HTML Playwright + diff snapshots.

## Risks / Trade-offs

| Risque | Mitigation |
|--------|------------|
| Matrice cartésienne trop lente | PR limitée demo/support ; sharding GHA par device |
| Flaky snapshots (animations Aurora) | `prefers-reduced-motion`, masquer mesh animé en test via `data-testid` ou CSS test |
| Faux sentiment de sécurité si fixture oubliée | Test négatif dédié `no-armoire.spec.ts` ; fixture auto via `globalSetup` / `test.extend` |
| Support-site auth JWT complexe | Mock réseau total API sur projects `support-*` |
| WebKit iPhone flaky en CI | retries=1 CI, traces on failure |

## Migration Plan

1. Phase 0–2 : aucun impact prod — code e2e uniquement.
2. Phase 6 : ajout workflow GHA — activer en **required check** après baseline stable.
3. Rollback : désactiver workflow ; tests locaux inchangés.

## Open Questions

1. Résolutions exactes des dalles domotique en parc installé (800×480 vs 1024×600) — **Phase 0**.
2. URL staging support-site pour projects `support-*` en nightly : `mon.essensys.fr` ou instance dédiée ?
3. Sharding CI : 1 job par device vs matrix GitHub — à trancher en Phase 6 selon durée mesurée.
