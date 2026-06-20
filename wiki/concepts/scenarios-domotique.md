---
tags: [concept, firmware, scenario, domotique, sync]
sources: [TableEchange.h, Scenario.c, essensys-scenario-management]
created: 2026-06-20
updated: 2026-06-16
era: modern
---

# Scénarios domotique

Les **scénarios mémorisés** (Je sors, vacances, Personnalisé 1/2, …) sont définis dans le firmware BP_MQX_ETH (SC944D 099-37) : **8 slots** × **41 paramètres** (`Scenario_NB_VALEURS`), indices absolus **592–919** dans la [[Table D Echange]].

## Indices clés

| Indice | Rôle |
|--------|------|
| **590** | Trigger — lancer un scénario (`0`=aucun, `1`=serveur/Mode B, `2`–`8`=slot mémorisé) |
| **591** | Dernier scénario lancé (lecture UI) |
| **592–632** | Scenario1 (slot 1 — réservé serveur) |
| **633–673** | Scenario2 — **Je sors** |
| **674–714** | Scenario3 — vacances |
| **797–837** | Scenario6 — Personnalisé 1 |
| **879–919** | Scenario8 |

Formule : `base(slot) = 592 + (slot - 1) × 41`.

## Mode A vs Mode B

| Mode | Inject | Usage |
|------|--------|-------|
| **A — Mémorisé** | `{590: "N"}` seul (N=2..8) | Boutons dashboard `/scenarios` |
| **B — Serveur** | `{590: "1"}` + bloc 605–622 (ou 592–632 option full) | Actions lumières/volets immédiates |

Le firmware **remet 590 à 0** après exécution — index **exclu du push cloud** continu.

## API (gateway LAN)

| Route | Rôle |
|-------|------|
| `GET /api/scenarios` | Liste slots + dernier lancé |
| `GET /api/scenarios/{slot}` | Définition 41 paramètres |
| `PUT /api/scenarios/{slot}` | Écriture slot 2–8 (batch 2×30 max) |
| `POST /api/scenarios/{slot}/launch` | Mode A |
| `POST /api/scenarios/{slot}/restore` | Restaurer preset firmware |
| `GET /api/scenarios/meta/bitmasks` | Labels masques lumières/volets |
| `GET/PUT /api/admin/scenarios/sync` | Toggle profil sync **Scénarios** |

Parité portail : `/api/portal/scenarios/*` sur `mon.essensys.fr`.

## Sync cloud

Profil PostgreSQL **Scénarios** (migration `009_scenarios_sync_profile.sql`) :

- Plage pull/push : **591–919** (inclut dernier lancé + 8 slots)
- `exclude_indices: [590]`
- Intervalle : **3 h** (scheduler [[Gateway Exchange]])

Toggle utilisateur : **Réglages → Synchronisation → Synchroniser les scénarios**.

## UI

- LAN : `/scenarios` (`essensys-server-frontend`)
- Portail : `/portal/scenarios` (`essensys-user-portal-frontend`) — boutons désactivés si gateway offline

Éditeur MVP : onglets *Lumières & volets* (bitmasks) + *Avancé*.

## Voir aussi

- [[Table D Echange]] — contrat k/v global
- [[Gateway Exchange]] — scheduler sync profils
- [[Essensys Scenario Management]] — OpenSpec change
- `essensys-memory/openspec/changes/essensys-scenario-management/audit-protocol.md`
