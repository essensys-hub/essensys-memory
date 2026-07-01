## Context

### État actuel

- L'armoire **SC944D** (`BP_MQX_ETH`) poll le CM5 toutes ~2 s : `GET /api/serverinfos` → `POST /api/mystatus` → `GET /api/myactions`.
- `GetServerInfos` renvoie une liste fixe de **29 indices** (`handlers.go` : chauffage 349–352, masques scénario 607/613/615, temps volets 566–585, etc.).
- `PostMyStatus` stocke les paires `{k,v}` en Redis ; lecture via `GET /api/admin/exchange?keys=…`.
- Le **dashboard** (`DashboardPage.tsx`) affiche dernière action UI, caméras, cartes navigation — **pas** l'armoire.
- Référence indices : `essensys-doc/archi/exchange-table.md`, firmware `TableEchange.h` (099-37).

### Contraintes

- **Pas de changement firmware** ni endpoints legacy.
- **Max 30 indices** par réponse `serverinfos` (firmware `ERREUR_INFOS_NB_VALEURS_MAX`).
- Gateway **mono-armoire** typique (un `client_id` legacy auth).
- UI jumeau portail **hors scope** (armoire sur segment `10.0.1.x` uniquement).

## Goals / Non-Goals

**Goals:**

- Visibilité immédiate sur `/dashboard` : connectée/hors ligne, identité (MAC, FW), santé (secouru, alarme, défauts), confort (chauffage, cumulus, arrosage, dernier scénario).
- Rotation automatique des indices « dashboard » sans bloquer les indices existants (commandes / volets config).
- API snapshot stable pour E2E Playwright (mode mock + no-armoire gate).

**Non-Goals:**

- Position volets / état lampes individuelles.
- Édition planning chauffage depuis le bandeau.
- Sync cloud OVH de l'état armoire.

## Decisions

### D1 — Rotation `serverinfos` par groupes (pas liste unique)

**Choix :** trois groupes cycliques injectés via `ExchangePullScheduler` (ou scheduler dédié `DashboardPullScheduler`) en **alternance** avec la liste par défaut actuelle.

| Groupe | Indices (k) | Contenu |
|--------|-------------|---------|
| **A — Identité & lien** | 0, 1, 5–9, 945, 947–952 | Versions BP, horloge, `EtatEthernet`, MAC |
| **B — Santé** | 10, 11, 12, 408, 413, 414, 415, 920 | Status, alertes, info BA/IHM, alarme |
| **C — Confort & énergie** | 349–353, 363, 459, 591, 460–464, 940 | Chauffage, cumulus, arrosage, délestage, scénario, Linky, vent |

Chaque groupe ≤ 18 indices ; un groupe par cycle (~2 s) → rafraîchissement complet ~6–8 s.

**Alternatives :**

- *Étendre `defaultServerInfoIndices`* — dépasse 30 → rejet firmware.
- *Poll HTTP admin séparé côté armoire* — impossible sans firmware.

### D2 — Endpoint `GET /api/admin/armoire/snapshot`

**Choix :** endpoint agrégé (auth admin/session LAN) retournant :

```json
{
  "connected": true,
  "last_poll_at": "2026-06-29T20:14:10Z",
  "client_id": "734254c282ba9b66",
  "stale_seconds": 2,
  "identity": { "firmware_embedded": "99", "mac": "d8:80:39:e1:35:ba", ... },
  "system": { "secouru": false, "heures_creuses": true, ... },
  "alarm": { "mode": "croisiere", "armed": true, ... },
  "comfort": { "heating": {...}, "cumulus": "hc", "sprinkler": "auto" },
  "energy": { "tariff": "HC", "apparent_power_va": 2400 },
  "raw_missing": [464]
}
```

Décodage dans `internal/armoire/` (package dédié) avec table statique k → sémantique.

**Alternatives :**

- *Frontend décode seul via `/api/admin/exchange`* — duplication logique, fuite indices firmware dans UI.

### D3 — Détection connectivité

**Choix :** `connected = (now - last_mystatus) < 6s` par `client_id` legacy (seuil = 3× intervalle poll).

Stocker `last_poll_at` dans le store à chaque `UpdateStatus` (extension `StatusService`).

### D4 — Widget UI `ArmoireStatusPanel`

**Choix :** bandeau sous le header dashboard, poll snapshot toutes **5 s**, badge vert/gris, sections repliables.

Conserver la bannière jaune « boucle ouverte » ; ajouter sous-titre « Valeurs remontées par l'armoire (table d'échange) ».

**Alternatives :**

- *Page dédiée `/armoire`* — plus de navigation ; le dashboard est le bon point d'entrée installateur.

### D5 — Pas de sync portail

Feature **gateway-only** : pas de report dans `essensys-user-portal-frontend` (armoire ne joint pas le cloud hub pour ce flux).

## Risks / Trade-offs

| Risque | Mitigation |
|--------|------------|
| Indices stale si rotation lente | Afficher `stale_seconds` / `raw_missing` ; badge « partiel » |
| Confusion masques 607/613 vs état lampes | Ne pas afficher ces indices ; doc UI |
| Plusieurs clients legacy | MVP : premier client connecté ou config `armoire_client_id` |
| Rotation entre en conflit avec heating sync | `TryStart` exclusif existant — priorité heating sync manuel > dashboard auto |
| Linky absent (460 timeout) | Section énergie masquée si `Information` bit0 ou valeurs `0xFF` |

## Migration Plan

1. Déployer backend (rotation + snapshot) — compatible ancien frontend.
2. Déployer frontend avec panneau (dégradé gracieux si 404 snapshot).
3. Pas de migration données Redis.
4. Rollback : désactiver rotation dashboard via config `armoire_dashboard_pull_enabled: false`.

## Open Questions

- Faut-il un réglage admin pour le seuil hors-ligne (6 s vs 10 s) ?
- Exposer l'IP armoire (`10.0.1.x`) depuis les logs nginx ou middleware auth ?
