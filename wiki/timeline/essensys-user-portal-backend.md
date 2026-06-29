---
tags: [timeline, git]
repo: essensys-user-portal-backend
updated: 2026-06-28
total_commits: 40
shown_commits: 100
---

# Timeline — essensys-user-portal-backend

**First commit:** 32851e9 2026-06-14 · **Latest:** f8cbed1 2026-06-28 · **Total:** 40

## Commits (newest first, limit 100)

- **2026-06-28** `f8cbed1` — fix(admin): show UNKNOWN serial when client_id is portal numeric id (rhinosys)
- **2026-06-28** `02a9743` — fix(migration): dedupe client_id before machines.id backfill (rhinosys)
- **2026-06-28** `588341b` — fix(inventory): stable machines.id in database for armoire links (rhinosys)
- **2026-06-28** `07619ca` — fix(legacyiot): normalize malformed mystatus JSON for armoire poll (rhinosys)
- **2026-06-28** `8872145` — fix(portal): bind armoire-seule for legacy IoT delivery (rhinosys)
- **2026-06-28** `ca26358` — feat(portal): trois modes de liaison utilisateur (armoire / gateway / serveur) (rhinosys)
- **2026-06-28** `4026145` — fix(admin): allow clearing gateway and cloud server links (rhinosys)
- **2026-06-28** `138a941` — fix(admin): interdire retrait gateway et serveur cloud une fois liés (rhinosys)
- **2026-06-26** `07cd641` — chore: ignore security-gate artifacts locaux (rhinosys)
- **2026-06-26** `fa76c77` — chore(deps): newrelic 3.44.1 et actions GitHub v6/v7 (rhinosys)
- **2026-06-26** `d1980b4` — Merge pull request #6 from essensys-hub/dependabot/go_modules/github.com/go-chi/chi/v5-5.3.0 (rhinosys)
- **2026-06-26** `077d13d` — Merge pull request #4 from essensys-hub/dependabot/go_modules/github.com/lib/pq-1.12.3 (rhinosys)
- **2026-06-26** `aee2bc7` — Merge pull request #2 from essensys-hub/dependabot/github_actions/actions/setup-go-6 (rhinosys)
- **2026-06-26** `d72e1a2` — Merge pull request #3 from essensys-hub/dependabot/github_actions/aquasecurity/trivy-action-0.36.0 (rhinosys)
- **2026-06-26** `45f6d09` — chore(deps): Bump github.com/go-chi/chi/v5 from 5.2.3 to 5.3.0 (dependabot[bot])
- **2026-06-26** `9a37fb3` — chore(deps): Bump github.com/lib/pq from 1.10.9 to 1.12.3 (dependabot[bot])
- **2026-06-26** `cce6df1` — chore(deps): Bump aquasecurity/trivy-action from 0.28.0 to 0.36.0 (dependabot[bot])
- **2026-06-26** `fb66f60` — chore(deps): Bump actions/setup-go from 5 to 6 (dependabot[bot])
- **2026-06-26** `fa15e1c` — chore: bootstrap feature lifecycle (gates, scripts, rules) (rhinosys)
- **2026-06-25** `032a806` — security: fail-closed secrets + move OAuth token to URL fragment (rhinosys)
- **2026-06-25** `90d3953` — feat(admin): interdire, réautoriser et supprimer des utilisateurs (rhinosys)
- **2026-06-22** `5b6cc31` — feat(portal): dry-run test mode sur inject et scénarios (rhinosys)
- **2026-06-21** `d5faa33` — feat(scenario): API portail scénarios et profil sync PostgreSQL. (rhinosys)
- **2026-06-20** `39a7dff` — fix(portal): merge gateway exchange cache on push (rhinosys)
- **2026-06-20** `16abc4e` — fix(legacyiot): document serverinfos 30-index firmware limit (rhinosys)
- **2026-06-20** `e957b70` — feat(portal): injection batch pour enregistrer le planning chauffage (rhinosys)
- **2026-06-20** `e380c84` — feat(portal): exposer session utilisateur et armoire liée (rhinosys)
- **2026-06-16** `e7619eb` — fix(admin): autoriser le renvoi manuel même si le modèle est désactivé (rhinosys)
- **2026-06-16** `c9137a9` — fix(data): éviter la redéclaration de nullIfEmpty (rhinosys)
- **2026-06-16** `877a019` — feat(admin): emails transactionnels avec modèles et envoi automatique (rhinosys)
- **2026-06-15** `7ec6ca2` — fix(legacyiot): myactions et done pour armoires WAN sur OVH (rhinosys)
- **2026-06-15** `8ff3703` — feat(legacyiot): géolocalisation IP machines et gateways (rhinosys)
- **2026-06-15** `132a52d` — fix(portal): remonter les temps de course volets en remote (rhinosys)
- **2026-06-15** `7d1d10c` — feat: hub cloud consolidé (identity, admin, legacy IoT, exchange). (rhinosys)
- **2026-06-14** `fd21f28` — fix(api): renvoyer [] au lieu de null pour link-requests vides (rhinosys)
- **2026-06-14** `62f874a` — feat(api): endpoints exchange, historique et alarme pour parité UI server (rhinosys)
- **2026-06-14** `83e0b8b` — fix(portal): bloquer remote mon.essensys.fr pour essensys-server (rhinosys)
- **2026-06-14** `73ecb3a` — feat(admin): endpoint gateway-sessions pour résolution serveur cloud (rhinosys)
- **2026-06-14** `5fac986` — feat(gateway): routage par triplet machine_id + MAC eth0/eth1 (rhinosys)
- **2026-06-14** `32851e9` — feat: initial user portal backend (BFF hub cloud) (rhinosys)
