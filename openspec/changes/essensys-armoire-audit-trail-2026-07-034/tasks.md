# Tâches — découpage en 2 développements

| Vague | Périmètre | Cible | DoD |
|-------|-----------|-------|-----|
| **DEV 1** | Gateway CM5/CM6 LAN | `mon.essensys.local` | Journal audit + immudb + admin **autonome** sans OVH |
| **DEV 2** | Hub OVH + sync + cloud | `mon.essensys.fr` | Ingest cloud, portail, armoire seule WAN, jumeaux UI |

> Ordre impératif : **DEV 1 terminé et validé sur CM5/CM6** avant de démarrer DEV 2.

---

## DEV 0 — Prérequis communs (avant DEV 1)

- [ ] 0.1 Whitelist indices auditables (`internal/audit/whitelist.go` stub + doc brain)
- [ ] 0.2 Spec dépôt **`essensys-audit-service`** (README, API `/v1/audit/*`, CLI `audit-rebuild`)
- [ ] 0.3 Charte RGPD v1 (texte) + `audit_charter_version` — utilisable LAN puis cloud
- [ ] 0.4 Page `essensys-doc` : architecture immudb + deux vagues de livraison

---

## DEV 1 — Gateway CM5/CM6 (LAN local)

**Objectif :** boucle complète sur la gateway — collecte → immudb → projection PG locale → lecture IHM → console admin — **sans dépendance OVH**.

### 1.1 Infrastructure gateway

- [ ] 1.1.1 Créer dépôt `essensys-audit-service` : `cmd/audit-service`, client immudb, projector PG
- [ ] 1.1.2 `POST /v1/audit/append`, `POST /v1/audit/batch`, `GET /v1/audit/health`
- [ ] 1.1.3 Append immudb `armoire/{machine_id}/event/{event_id}` + hash chain SHA-256
- [ ] 1.1.4 Projector → tables PG gateway (`audit_events_local` ou projection `armoire_audit_events` locale)
- [ ] 1.1.5 CLI `audit-rebuild` (--source immudb --target postgres --machine-id M --dry-run)
- [ ] 1.1.6 Ansible `roles/immudb_gateway` + `roles/audit_service_gateway` (Docker Compose CM5/CM6)
- [ ] 1.1.7 Secrets gateway (immudb + mTLS audit-service) — pas de SOPS OVH en DEV 1
- [ ] 1.1.8 Tests : append idempotent, VerifiedGet, rebuild dry-run

### 1.2 Backend LAN (`essensys-server-backend`)

- [ ] 1.2.1 Package `internal/audit/` : types, `Authorizer` LAN, `Dedup`, client collector
- [ ] 1.2.2 Package `essensys-audit-collector` : `Emit(ctx, AuditEvent)`, dedup STATE_CHANGE, buffer outbox
- [ ] 1.2.3 Migration PG gateway `audit_outbox` + `lan_audit_charter_acceptances` (`006_audit_outbox.up.sql`)
- [ ] 1.2.4 Ansible `lan_iam_migrations.yml` — migration audit gateway
- [ ] 1.2.5 Hooks collector : inject LAN, `ActionService`, IAM login/logout, trusted devices
- [ ] 1.2.6 Delta exchange (whitelist) → collector → audit-service LAN
- [ ] 1.2.7 `GET /api/audit/events` (session LAN, RBAC `lan_user` / `lan_admin`, charte signée)
- [ ] 1.2.8 `GET/POST /api/audit/charter/accept` + export JSON/CSV LAN
- [ ] 1.2.9 Tests : dedup ≥ 10 cas, authorizer LAN, POST user → 403, couverture ≥ 85 %

### 1.3 Intégrité & admin LAN (`essensys-server-backend` + frontend)

- [ ] 1.3.1 Job `audit-integrity-check` gateway ; métrique `audit_integrity_mismatch_total`
- [ ] 1.3.2 `GET /api/audit/integrity` + rebuild dry-run (LAN `lan_admin`)
- [ ] 1.3.3 `AuditAdminPage` `/settings/audit-admin` : santé services, intégrité, rebuild, logs
- [ ] 1.3.4 Composants : `AuditServiceHealth`, `AuditIntegrityPanel`, `AuditRebuildPanel`

### 1.4 IHM utilisateur LAN (`essensys-server-frontend`)

- [ ] 1.4.1 `auditApi.ts`, `useAuditTrail.ts`, `useAuditCharter.ts`
- [ ] 1.4.2 `AuditTrailPage` + `AuditEventTable` + `AuditFiltersBar` + `AuditEventDetailDrawer`
- [ ] 1.4.3 `AuditCharterModal` bloquante
- [ ] 1.4.4 Sidebar « Journal d'activité » + `ControlCard` Settings + carte Dashboard
- [ ] 1.4.5 Route `/settings/audit` ; recherche `q` + presets date + graphique 7 jours
- [ ] 1.4.6 Masquage IP `/24` ; export JSON/CSV
- [ ] 1.4.7 Tests RTL : rôles, charte, lecture seule

### 1.5 Validation DEV 1 (CM5/CM6)

- [ ] 1.5.1 Deploy Ansible gateway : immudb + audit-service + migrations PG
- [ ] 1.5.2 Scénario manuel : inject LAN → événement visible `/settings/audit` < 5 s
- [ ] 1.5.3 Scénario : `audit-rebuild --dry-run` OK ; intégrité PG ↔ immudb OK
- [ ] 1.5.4 `go test ./internal/audit/...` vert ; `feature-gate` server-backend
- [ ] 1.5.5 Doc install gateway : section audit LAN (`essensys-raspberry-install/docs`)

**Hors scope DEV 1 :** cloudsync OVH, `user-portal-backend`, `user-portal-frontend`, legacyiot WAN, support-site `/admin/audit`.

---

## DEV 2 — OVH (cloud hub + sync + portail)

**Prérequis :** DEV 1 mergé et validé sur CM5/CM6 de référence.

**Objectif :** répliquer le modèle immudb sur OVH, ingérer les events gateway, couvrir armoire seule WAN et jumeaux portail.

### 2.1 Infrastructure OVH

- [ ] 2.1.1 Ansible `roles/immudb_cloud` + `roles/audit_service_cloud` (systemd/Docker OVH)
- [ ] 2.1.2 Secrets SOPS OVH (immudb, audit-service, token ingest gateway)
- [ ] 2.1.3 Migration OVH `armoire_audit_events` + RLS + triggers append-only
- [ ] 2.1.4 Migration `user_audit_charter_acceptances`
- [ ] 2.1.5 Deploy `essensys-audit-service` OVH + projector → `armoire_audit_events`

### 2.2 Backend cloud (`essensys-user-portal-backend`)

- [ ] 2.2.1 Porter `internal/audit/` + collector (jumeau server-backend-sync)
- [ ] 2.2.2 Routes ingest `POST /api/gateway/audit/events` + `POST /api/gateway/audit/batch` (GatewayAuth)
- [ ] 2.2.3 `GET /api/portal/audit/events` (JWT + Authorizer cloud + charte)
- [ ] 2.2.4 Routes charte cloud + `GET /api/portal/audit/export`
- [ ] 2.2.5 Writers `internal/legacyiot` (armoire seule WAN) → collector OVH
- [ ] 2.2.6 `GET /api/admin/audit/integrity` + `GET /api/admin/audit/proof` (admin_global)
- [ ] 2.2.7 Tests API cloud + legacyiot ; couverture ≥ 85 %

### 2.3 Sync gateway → OVH (`essensys-server-backend` cloudsync)

- [ ] 2.3.1 Flush `audit_outbox` batch → `POST /api/gateway/audit/batch` (idempotent)
- [ ] 2.3.2 Ordre : immudb LAN confirmé → outbox → OVH audit-service → immudb OVH
- [ ] 2.3.3 Badge IHM `pending_sync` sur server-frontend (déjà prévu DEV 1, activer avec sync)
- [ ] 2.3.4 Test offline : WAN coupé → outbox grossit → sync au retour sans doublon

### 2.4 IHM cloud (jumeaux)

- [ ] 2.4.1 Copie jumeau `essensys-user-portal-frontend` (composants Audit DEV 1)
- [ ] 2.4.2 `useAuditNavItems()` JWT / `linked_machine_id`
- [ ] 2.4.3 Checklist `portal-server-frontend-sync.mdc`
- [ ] 2.4.4 `AuditAdminPage` support-site `/admin/audit` (admin_global)

### 2.5 RGPD, doc & gates OVH

- [ ] 2.5.1 Job `audit_retention_purge` (projection PG OVH, 24 mois)
- [ ] 2.5.2 Anonymisation compte supprimé (projection PG)
- [ ] 2.5.3 `GET /api/admin/audit/charter-acceptances`
- [ ] 2.5.4 Mise à jour `audit_trail.md`, `roles_matrix.md`, `privacy_policy.md`, charte web
- [ ] 2.5.5 `feature-gate` + `security-gate` portal-backend + audit-service OVH
- [ ] 2.5.6 Deploy OVH ; test E2E CM5 → sync → lecture `mon.essensys.fr`
- [ ] 2.5.7 Non-régression `GET /api/admin/audit` (audit plateforme)

### 2.6 Documentation brain

- [ ] 2.6.1 `wiki/concepts/armoire-audit-trail.md` + `immudb-audit-ledger.md`
- [ ] 2.6.2 `wiki/roadmap/changes/essensys-armoire-audit-trail-2026-07-034.md`
- [ ] 2.6.3 `deployment-perimeters.md` + `wiki/log.md`
- [ ] 2.6.4 `openspec validate essensys-armoire-audit-trail-2026-07-034 --strict`
