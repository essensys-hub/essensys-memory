## Why

Les utilisateurs et administrateurs Essensys n'ont pas aujourd'hui de **journal d'audit par armoire** couvrant les actions domotiques, les changements de configuration et les transitions d'état — seulement un audit **plateforme** (login, rôles) dans `audit_logs` / `portal_audit_log`. Sans trace append-only par `machine_id`, il est impossible de répondre de façon fiable à une demande utilisateur (« qui a fait quoi ? »), de corréler une anomalie ou de détecter une intrusion sur une installation.

Ce change formalise un audit **lecture seule** accessible depuis la gateway LAN (`mon.essensys.local`) et le portail distant (`mon.essensys.fr`), avec résilience offline (outbox gateway) et alignement sur les trois périmètres de déploiement documentés dans [[Deployment Perimeters]].

> **Roadmap ID:** 2026-07.034  
> **Source:** `prompts/essensys-armoire-audit-trail.md`  
> **Livraison :** **DEV 1** gateway CM5/CM6 (LAN) → **DEV 2** OVH (cloud)  
> **Baseline runtime :** release **V.1.5.0** figée le 2026-07-03 — voir `essensys-memory/wiki/releases/V.1.5.0.md`

## Delivery strategy (2 devs)

| Vague | Où | Quand démarrer | DoD |
|-------|-----|----------------|-----|
| **DEV 1** | CM5/CM6 — `mon.essensys.local` | Immédiat | Journal + immudb + admin LAN autonomes |
| **DEV 2** | OVH — `mon.essensys.fr` | Après validation DEV 1 sur CM5 référence | Sync, portail, armoire seule WAN |

## What Changes

- Nouvelle table canonique OVH **`armoire_audit_events`** (domotique + config + états) — **distincte** de `audit_logs` (auth plateforme) et `portal_audit_log` (legacy portail).
- **RBAC lecture** par armoire : `user`, `admin_local`, `admin_global` (cloud) et `lan_user`, `lan_admin` (LAN) ; exclusion `guest_*` / `lan_guest`.
- **BREAKING (produit)** : un `user` cloud lié à l'armoire `M` voit **tout** le journal de `M` (pas seulement ses actions) — différent de `essensys-support-site/docs/audit_trail.md` actuel.
- Writers **services uniquement** (backends Go, agent gateway) — aucune route d'écriture pour JWT/cookie utilisateur.
- Déduplication **`STATE_CHANGE`** si la valeur est identique au dernier événement stocké pour la même clé (whitelist d'indices table d'échange).
- Outbox **`audit_outbox`** sur PostgreSQL gateway (même instance que [[LAN IAM]]) + sync idempotent vers OVH.
- Périmètre **armoire seule WAN** : writers dans `internal/legacyiot` sur OVH uniquement (pas d'outbox gateway).
- IHM read-only **intégrée utilisateur** : sidebar « Journal d'activité », carte Paramètres, carte Dashboard, `/settings/audit` (jumeaux frontends).
- Chaîne de hash SHA-256 calculée à l'ingest OVH ; triggers append-only PostgreSQL.
- **immudb** comme journal immuable canonique (preuve cryptographique, détection falsification) ; **PostgreSQL** comme modèle de lecture reconstruisible depuis immudb.
- **`essensys-audit-service`** (gateway LAN + OVH) : service SQL/append dédié ; seul writer immudb autorisé.
- **`essensys-audit-collector`** : collecte normalisée des actions/updates depuis les autres services (backends, cloudsync, legacyiot).
- Tests unitaires poussés (`internal/audit/*`, ≥ 85 % couverture cible).
- **Charte RGPD** « collecte et journal d'audit domotique » à **faire signer** (cloud + LAN) avant premier accès au journal.
- **Registre des consentements** versionné + features RGPD (rétention, export, minimisation, ré-consentement).

## Capabilities

### New Capabilities

- `armoire-audit-trail` : journal append-only par `machine_id`, RBAC lecture, writers internes, dedup états, sync gateway ↔ OVH, IHM read-only LAN + cloud, périmètre armoire seule WAN, **charte RGPD signée**, contrôles conformité, **immudb + audit-service + audit-collector**.

### Modified Capabilities

- _(aucune spec existante dans `openspec/specs/` — change autonome)_

## Impact

### DEV 1 — Gateway CM5/CM6 (LAN)

| Dépôt | Changement |
|-------|------------|
| **`essensys-audit-service`** (nouveau) | MVP append immudb + projection PG + `audit-rebuild` |
| `essensys-server-backend` | `internal/audit`, collector, outbox PG, writers LAN, `GET /api/audit/events` |
| `essensys-server-frontend` | `/settings/audit` + `/settings/audit-admin` |
| `essensys-ansible` | `immudb_gateway`, `audit_service_gateway`, migration `006_audit_outbox` |

### DEV 2 — OVH (cloud)

| Dépôt | Changement |
|-------|------------|
| `essensys-user-portal-backend` | Migration `armoire_audit_events`, ingest gateway, legacyiot, lecture portail |
| `essensys-user-portal-frontend` | Jumeau UI audit (copie DEV 1) |
| `essensys-server-backend` | cloudsync flush outbox → OVH |
| `essensys-support-site` | `/admin/audit`, doc, charte, privacy |
| `essensys-ansible` | `immudb_cloud`, `audit_service_cloud`, secrets SOPS OVH |
| `essensys-doc` / `essensys-memory` | Doc + brain (Phase 2) |

### Vue d'ensemble (après DEV 2)

**Dépendances :** [[Cloud Relay]], [[LAN IAM]], [[Trusted Devices LAN]], cloud sync scheduler, jumeaux portal/server.

**Non-impacté :** endpoints legacy IoT (`/api/mystatus`, `/api/myactions`, …) — instrumentation côté handlers sans modification du wire protocol ; control-plane Redis audit hors scope.
