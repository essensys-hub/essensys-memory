## Why

Sur la **gateway CM5** (`https://mon.essensys.local/dashboard`), l'utilisateur ne voit pas si l'armoire SC944D est connectée ni son état système (secouru, alarme, chauffage, défauts BA). Pourtant le firmware remonte déjà des valeurs via `POST /api/mystatus` et la [[Table D Echange]] — elles sont stockées côté backend mais non exposées dans l'UI locale.

> **Roadmap ID:** 2026-06.033  
> **Horizon:** voir [[Roadmap OpenSpec]]  
> **Périmètre:** gateway LAN uniquement (pas portail cloud `/portal/`)

## What Changes

- **Rotation `serverinfos`** : groupes d'indices table d'échange (≤30/cycle firmware) pour remonter connexion, santé, confort et Linky sans modifier le protocole legacy.
- **API admin** `GET /api/admin/armoire/snapshot` : agrégat structuré (connectivité, versions, MAC, status bits, alarme, chauffage, cumulus, arrosage, scénario, téléinfo optionnelle).
- **Décodage métier** côté backend : mapping indices `TableEchange.h` → libellés français (ex. `Status` bit2 secouru, `Chauf_zj_Mode` consigne/mode).
- **Widget dashboard** `ArmoireStatusPanel` sur `/dashboard` : bandeau état armoire + sections santé/confort/énergie.
- **Documentation brain** : concept wiki « état armoire gateway » + indices k utilisés.
- **Honnêteté UI** : rappel que les valeurs sont la **dernière remontée armoire** (pas feedback capteur temps réel pour lampes/volets).

## Capabilities

### New Capabilities

- `gateway-armoire-dashboard` : pull indices exchange, snapshot API, décodage, panneau UI dashboard gateway.

### Modified Capabilities

- _(aucune spec existante dans `openspec/specs/` — change autonome)_

## Impact

| Dépôt | Changement |
|-------|------------|
| `essensys-server-backend` | Rotation `serverinfos`, endpoint snapshot, décodeur indices, `last_poll_at` client |
| `essensys-server-frontend` | `ArmoireStatusPanel`, hook `useArmoireSnapshot`, intégration `DashboardPage` |
| `essensys-memory` | OpenSpec, wiki concept, entrée roadmap |
| `essensys-user-portal-*` | **N/A** — feature gateway locale uniquement |
| Firmware `essensys-board-SC944D` | **Aucune modification** — réutilise poll existant |

## Non-goals

- Afficher l'état **réel** de chaque lampe/volet (données sur BA I2C, pas bitmask live BP).
- Modifier les endpoints legacy `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done`.
- Répliquer le panneau sur `mon.essensys.fr` / portail cloud (phase ultérieure possible).
- Remplacer les pages métier existantes (chauffage, sécurité, éclairage).

## Contraintes protocole

- Limite firmware **30 indices** par cycle `serverinfos` → rotation obligatoire (`ExchangePullScheduler` existant).
- Indices **607/613/615** actuels = masques scénario commande — **exclus** de l'affichage « état équipement ».
