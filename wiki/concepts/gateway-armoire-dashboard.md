---
tags: [concept, gateway, armoire, dashboard, table-d-echange, sc944d]
sources: [essensys-gateway-armoire-dashboard-2026-06-033]
created: 2026-06-29
updated: 2026-06-29
era: modern
---

# Gateway Armoire Dashboard

Panneau d'état armoire sur le dashboard gateway (`/dashboard`) : visibilité connectivité, identité firmware/MAC, santé (secouru, alarme), confort (chauffage, cumulus, arrosage, scénario) et énergie Linky.

**Scope :** `essensys-server-backend` + `essensys-server-frontend` uniquement (pas de sync portail cloud).

## Principe

L'armoire SC944D poll le gateway toutes ~2 s via le protocole legacy (`serverinfos` → `mystatus` → `myactions`). Le firmware n'accepte **≤ 30 indices** par réponse `serverinfos`.

Le backend alterne :

1. Liste **défaut** (commandes inject / volets config — identique à l'ancienne liste fixe)
2. Groupe **identité** (0, 1, 5–9, 945, 947–952)
3. Groupe **santé** (10–12, 408, 413–415, 920)
4. Groupe **confort/énergie** (349–353, 363, 459, 591, 460–464, 940)

La sync chauffage manuelle (`POST /api/admin/heating/sync`) **prioritaire** sur la rotation dashboard.

## API

`GET /api/admin/armoire/snapshot` (session LAN / admin)

Réponse JSON agrégée : `connected`, `last_poll_at`, `client_id`, `stale_seconds`, blocs `identity`, `system`, `alarm`, `comfort`, `energy`, `raw_missing`.

- Connectivité : `connected = (now - last_mystatus) < 6 s`
- **Exclut** les codes alarme utilisateur (k=417–418)
- Décodage dans `internal/armoire/` (réf. [[Table D Echange]], firmware 099-37)

## Configuration backend

```yaml
armoire:
  dashboard_pull_enabled: true   # défaut
  offline_threshold_seconds: 6
  client_id: ""                  # optionnel — sinon dernier client ayant pollé
```

Variables d'environnement : `ARMOIRE_DASHBOARD_PULL_ENABLED`, `ARMOIRE_CLIENT_ID`.

## UI

- Composant `ArmoireStatusPanel` sur `DashboardPage`
- Poll snapshot toutes **5 s**
- Disclaimer : valeurs table d'échange, pas état capteur par lampe/volet

## Limites connues

- Pas d'état live par lampe / volet (masques scénario 605–616 exclus du snapshot)
- Mono-armoire typique (un `client_id` legacy)
- Rafraîchissement complet des groupes ~6–8 s selon cadence poll armoire

## Liens

- [[Table D Echange]]
- [[Essensys Board SC944D]]
- [[Dual Protocol]]
- Change OpenSpec : `essensys-gateway-armoire-dashboard-2026-06-033`
