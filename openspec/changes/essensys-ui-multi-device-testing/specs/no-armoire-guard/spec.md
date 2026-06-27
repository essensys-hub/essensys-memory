# no-armoire-guard

Garantie **zéro action armoire** — trois couches cumulatives pour tous les tests UI.

## ADDED Requirements

### Requirement: Couche 1 — exécution en mode neutralisé

Les projects MUST s'exécuter en mode neutralisé selon la cible :

- **support / demo** : build ou mock où aucune écriture firmware n'est possible (`mockFetch`, stubs réseau).
- **local / remote staging** : `?test_mode=dry_run` et header `X-Essensys-Test-Mode: dry-run` sur toute requête mutante.

#### Scenario: Demo n'émet aucun POST inject réel

- **WHEN** un test demo clique un contrôle domotique
- **THEN** `window.fetch` mocké ou route Playwright intercepte l'appel
- **AND** aucun paquet HTTP n'atteint `/api/admin/inject` sans mock

#### Scenario: Local staging avec dry-run

- **WHEN** un test local envoie un inject
- **THEN** l'URL contient `test_mode=dry_run` ou le header dry-run est présent
- **AND** la réponse contient `dry_run: true`

### Requirement: Couche 2 — fixture réseau Playwright

Une fixture globale `no-armoire` MUST être appliquée à **tous** les projects et MUST rejeter les appels mutants non neutralisés :

Patterns bloqués (POST/PUT/PATCH) : `/inject`, `/web/actions`, `/scenarios/{id}/launch`.

#### Scenario: Inject live bloqué

- **WHEN** un test tente `POST /api/admin/inject` sans `test_mode=dry_run` ni header dry-run
- **THEN** la fixture lève une erreur explicite contenant `BLOQUÉ` et l'URL
- **AND** le test échoue avant toute action firmware

#### Scenario: Inject dry-run autorisé

- **WHEN** un test envoie `POST /api/admin/inject?test_mode=dry_run`
- **THEN** la fixture laisse passer la requête
- **AND** la réponse `{ status: 'test_ok', dry_run: true }` est assertée

#### Scenario: Test négatif dédié

- **WHEN** la spec `no-armoire.spec.ts` simule un inject live volontaire
- **THEN** le test MUST échouer à cause de la fixture (comportement attendu documenté)

### Requirement: Couche 3 — interdiction environnement prod client

Par défaut, les projects MUST NOT cibler une IP gateway de client réel pour des écritures.

- Variable `ESSENSYS_ALLOW_LIVE_READONLY=1` requise pour prod read-only.
- Même en read-only, la couche 2 MUST rester active.
- Documentation MUST interdire explicitement le ciblage d'armoire client en write.

#### Scenario: URL prod sans flag live

- **WHEN** `ESSENSYS_LOCAL_URL` pointe vers une gateway prod sans `ESSENSYS_ALLOW_LIVE_READONLY=1`
- **THEN** la suite refuse de démarrer ou force le mode demo/mock
- **AND** un message documente le risque armoire

### Requirement: Aucun test ne pilote l'armoire réelle

Un test qui provoque une action réelle (volet, lumière, alarme) MUST être considéré comme **échec de conception**, pas comme bug produit.

#### Scenario: Revue PR bloque inject sans garde

- **WHEN** une PR ajoute une spec qui appelle `/api/web/actions` en POST sans dry-run ni mock
- **THEN** la CI MUST échouer via la fixture couche 2
- **AND** le rapport indique le risque action armoire
