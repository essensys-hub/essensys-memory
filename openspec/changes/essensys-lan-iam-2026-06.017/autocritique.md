# Autocritique — IAM LAN user / mot de passe (2026-06.017)

> Revue critique avant promotion **active** du change. Objectif : cadrer la gestion utilisateurs et mots de passe sur `mon.essensys.local` sans dupliquer le cloud ni casser le legacy IoT.

## 1. État des lieux (code réel, juin 2026)

### Ce qui existe déjà sur la gateway

| Couche | État | Fichiers / comportement |
|--------|------|-------------------------|
| **Basic Auth HTTP** | ⚠️ Passif | `internal/middleware/auth.go` — capture user/IP/credentials Base64 dans Redis, **n'envoie jamais 401** |
| **Auth web legacy (PG)** | 🟡 Partiel | `WebHandler` + `UserService` — login/register SHA1, table `users` PostgreSQL locale |
| **Sessions** | 🟡 Mémoire | `auth.SessionStore` — cookie session après login, **aucun middleware** ne protège `/api/*` |
| **Routes auth** | 🟡 Exposées | `/api/auth/login`, `/logout`, `/register`, `/api/user/me` — montées si `db != nil` |
| **Frontend React** | ❌ Absent | `essensys-server-frontend` — pas de pages Login/Register ; 401 → reload Basic Auth navigateur |
| **Edge TLS `.local`** | ✅ Ansible | Traefik + CA locale `mon.essensys.local` ; basicauth Traefik/Caddy sur certains profils WAN |
| **Cloud IAM** | ✅ Séparé | `essensys-user-portal-backend` — JWT, OAuth, rôles `admin_global` / `admin_local` / `guest_local` sur **mon.essensys.fr** |

### Constat principal

Le change **017** ne part **pas de zéro** : il hérite d'une **moitié de migration ASP.NET** (backend) sans UI ni enforcement, cohabitant avec un Basic Auth **documenté mais désactivé en pratique** (mode passif).

```
┌─────────────────────────────────────────────────────────────────┐
│  AUJOURD'HUI — mon.essensys.local                               │
├─────────────────────────────────────────────────────────────────┤
│  Navigateur ──► Traefik (TLS) ──► Nginx ──► Go :7070            │
│                     │                              │            │
│              basicauth? (profil)          BasicAuth PASSIF      │
│              (WAN / Caddy)                  (capture seulement) │
│                                              │                  │
│                                    /api/auth/* si PG OK         │
│                                    (sessions RAM, non gardées)  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CLOUD — mon.essensys.fr (HORS SCOPE direct 017)                │
│  JWT + OAuth + admin UserManager — PostgreSQL OVH partagé       │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Autocritique du scaffold actuel

| Faiblesse | Impact | Action proposée |
|-----------|--------|-----------------|
| Proposal une ligne (« RBAC LAN ») | Scope flou, confusion avec cloud | Détailler personas LAN vs cloud dans `proposal.md` |
| Spec TBD | Non testable, gate CI impossible | Remplacer par exigences SHALL + scénarios Gherkin |
| Design vide | Pas de décision hash, rôles, bootstrap | Remplir `design.md` (voir §4) |
| Dépendance « — » | Ignore 013 (trusted device) et dette PG locale | Déclarer **013 recommandée**, **016** pour 1er admin |
| Ignore code existant | Risque de réécrire UserService | Expliciter **réutiliser / durcir / migrer hash** |
| SHA1 UTF-16 legacy | Faiblesse crypto, mais compat legacy web | Phase 1 conserver SHA1 ; Phase 2 argon2 + colonne `password_algo` |
| Basic Auth passif | Sécurité illusoire, credentials loggés Redis | **Activer mode strict** ou **retirer** au profit sessions |
| Deux modèles user | PG local vs cloud PG | **Ne pas fusionner** les bases v1 ; comptes LAN locaux à la gateway |
| Pas d'UI admin LAN | Impossible de créer user sans curl | Pages Settings/Admin LAN dans server-frontend |
| Firmware legacy | Port 80, pas de cookie | Routes IoT `/api/mystatus` **restent hors auth session** |

## 3. Périmètre recommandé v1

### In scope

1. **Comptes LAN locaux** (email + mot de passe) stockés PostgreSQL **gateway** (table existante ou `lan_users` dédiée — voir décision).
2. **CRUD admin LAN** : créer / désactiver / reset mot de passe / lister (rôle `lan_admin` minimum).
3. **Login session** cookie HttpOnly Secure SameSite=Lax sur `mon.essensys.local`.
4. **Middleware** : routes domotique UI (`/api/admin/inject`, scénarios, profil user) exigent session ; legacy IoT inchangé.
5. **UI** : Login, changement mot de passe, écran admin users (installateur / propriétaire).
6. **Bootstrap** : premier compte `lan_admin` via CLI/Ansible ou wizard 016 (mot de passe initial rotatable).

### Out of scope v1

- OAuth Google/Apple sur `.local`
- Parité rôles cloud `admin_global` / `guest_local` (mapping futur optionnel)
- Sync comptes LAN ↔ cloud OVH
- MFA / WebAuthn (sauf spike post-013)
- Modification protocole BP_MQX_ETH

## 4. Décisions proposées (à valider)

| # | Sujet | Recommandation | Alternative rejetée |
|---|-------|----------------|---------------------|
| D1 | Identité | Comptes **locaux gateway** (PG embarqué) | Réutiliser JWT cloud — fuite dépendance WAN |
| D2 | Hash v1 | Conserver **SHA1 UTF-16** pour users migrés ; **bcrypt/argon2** pour nouveaux (`password_algo`) | Rehash massif day-1 — casse comptes importés |
| D3 | Transport | **Session cookie** + CSRF sur mutations | Basic Auth navigateur — UX iPad, pas de logout |
| D4 | Basic Auth passif | **Désactiver capture credentials Redis** ou opt-in audit | Garder passif — fuite mots de passe en clair encodés |
| D5 | Rôles v1 | `lan_admin`, `lan_user`, `lan_guest` (local enum) | Copier enum cloud — sémantique différente |
| D6 | Bootstrap | `essensys-cli users bootstrap` ou tâche Ansible idempotente | Register public ouvert — n'importe qui sur LAN |
| D7 | Register public | **Fermé** v1 ; création par admin uniquement | Open register — même risque que legacy WAN |
| D8 | Dépendance 013 | Sessions longues iPad **après** IAM de base | 013 avant login — ordre inversé |

## 5. Risques ouverts

1. **PostgreSQL non démarré sur certaines gateways** → auth web désactivée aujourd'hui (`webHandler nil`). IAM LAN **requiert PG** : documenter dans install + health check.
2. **Conflit Traefik basicauth vs session app** — choisir une seule couche auth pour le dashboard (recommandé : session app, Traefik TLS seulement).
3. **Jumeau frontend** — reporter dans `essensys-user-portal-frontend` ? **Non** (portail distant = cloud JWT).
4. **Tests** — réactiver tests auth (skippés SCRUM-9) avec comportement **actif**, pas passif.

## 5. Décisions produit (2026-06-26)

| Question | Décision |
|----------|----------|
| Table legacy `users` vs `lan_users` ? | **`lan_users` dédiée** — IAM LAN autonome ; legacy `users` non lue au login v1 |
| Droits `lan_guest` ? | **Pilotage LAN = `lan_user`** (inject, scénarios, dashboard) ; **sans** admin users |
| Durée session ? | **7 jours** (168 h, sliding) — aligné change **013** trusted-devices |

## 6. Critères de promotion active

- [x] Spec `lan-iam` ≥ 8 scénarios testables
- [x] Design validé (D1–D9 + décisions produit)
- [x] Accord produit : register fermé v1
- [ ] Spike : PG présent sur CM5 prod (192.168.0.14)
- [ ] Lien explicite change **016** (wizard) pour bootstrap UX

## 7. Prochaine itération doc

1. ~~Mettre à jour `proposal.md`, `design.md`, `specs/lan-iam/spec.md`, `tasks.md`~~ — fait (2026-06-26).
2. Ajouter entrée wiki concept `lan-iam.md` à l'ingest brain.
3. Commit brain + promotion change **active** quand PG CM5 confirmé.
