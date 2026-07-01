## 1. Backend — store & connectivité

- [x] 1.1 Enregistrer `last_poll_at` par `client_id` dans `StatusService.UpdateStatus`
- [x] 1.2 Ajouter helper `IsClientConnected(clientID, threshold)` (défaut 6 s)

## 2. Backend — rotation serverinfos

- [x] 2.1 Définir les 3 groupes d'indices dashboard (identity, health, comfort/energy) dans `internal/armoire/pull_groups.go`
- [x] 2.2 Intégrer rotation cyclique avec `ExchangePullScheduler` sans casser `defaultServerInfoIndices` ni heating sync
- [x] 2.3 Config `armoire_dashboard_pull_enabled` (défaut `true` sur gateway)
- [x] 2.4 Tests unitaires : ≤30 indices par chunk, priorité heating sync

## 3. Backend — décodage & snapshot API

- [x] 3.1 Package `internal/armoire/decode.go` : Status, Information, Alerte, chauffage, alarme, Linky, EtatEthernet, scénario
- [x] 3.2 Handler `GET /api/admin/armoire/snapshot` + route protégée admin/LAN
- [x] 3.3 Tests table-driven décodage (ex. k=10 secouru, k=349 mode chauffage)
- [x] 3.4 Exclure codes alarme utilisateur (417–418) de la réponse

## 4. Frontend — dashboard UI

- [x] 4.1 Types `ArmoireSnapshot` + service `armoireApi.ts` (`getArmoireSnapshot`)
- [x] 4.2 Hook `useArmoireSnapshot` (poll 5 s, gestion erreur/offline)
- [x] 4.3 Composant `ArmoireStatusPanel` (badge, sections santé/confort/énergie, disclaimer)
- [x] 4.4 Intégrer dans `DashboardPage.tsx` sous le header
- [x] 4.5 `mockFetch.ts` : réponse snapshot mock pour E2E / mode test

## 5. Tests & validation

- [x] 5.1 Test E2E Playwright : panneau visible sur `/dashboard` (no-armoire gate, mock snapshot)
- [ ] 5.2 Test manuel CM5 : armoire dev `10.0.1.163` — snapshot connecté + secouru/alarme si simulable
- [x] 5.3 `go test ./internal/armoire/...` et `npm run lint` frontend

## 6. Documentation brain

- [x] 6.1 Créer `wiki/concepts/gateway-armoire-dashboard.md` (indices, API, limites)
- [x] 6.2 Entrée `wiki/roadmap/changes/essensys-gateway-armoire-dashboard-2026-06-033.md`
- [x] 6.3 Mettre à jour `wiki/index.md` et `wiki/log.md`
- [x] 6.4 `openspec validate essensys-gateway-armoire-dashboard-2026-06-033 --strict`

## 7. Déploiement gateway (hors git automatique)

- [x] 7.1 Build + deploy backend/frontend sur CM5 dev (`192.168.42.119`)
- [x] 7.2 Vérifier rotation : logs `mystatus` contiennent indices groupe A/B/C sur ~10 s
