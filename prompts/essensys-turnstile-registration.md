# Prompt : Cloudflare Turnstile sur l'inscription — anti-spam comptes fictifs (OpenSpec)

Tu es un ingénieur **full-stack (Go + React/TypeScript) + sécurité + ops Ansible/SOPS**. Ta mission est de **concevoir et spécifier** (puis implémenter via **OpenSpec**, schema `spec-driven`) la mise en place de **Cloudflare Turnstile** sur le parcours d'**inscription** Essensys, pour stopper le flux de **comptes fictifs** créés via `POST /api/auth/register`.

Respecte **library-first** (réutiliser rate-limit existant, SOPS, patterns auth) et les **jumeaux** si l'inscription est servie par le hub consolidé.

> ⚠️ Ce fichier est un **prompt de cadrage** destiné à `/openspec-propose`. Il ne remplace pas la proposition : l'agent OpenSpec produit `proposal.md` → `design.md` → `specs/**` → `tasks.md`.

---

## 0. Contexte produit (vérifié)

| Fait | Détail |
|------|--------|
| Symptôme | Trop d'utilisateurs fictifs à l'enregistrement sur `www.essensys.fr` / hub OVH |
| Endpoint actuel | `POST /api/auth/register` — **aucune** CAPTCHA, **aucune** vérif email, **aucun** rate-limit dédié |
| UI | `essensys-support-site/site/src/pages/Register.jsx` → `fetch('/api/auth/register')` |
| Backend historique | `essensys-support-site/backend/internal/api/handlers_auth.go` → `HandleRegister` |
| Hub consolidé OVH | Nginx proxy `/api/*` → `essensys-cloud-backend` (`essensys-user-portal-backend`) qui expose aussi `POST /api/auth/register` (`internal/identity`) |
| Consentement cookies | `CookieConsent.jsx` déjà présent — Turnstile doit être documenté (privacy / cookies tiers) |

**Décision de cadrage** : **Cloudflare Turnstile** (invisible ou managed) + **vérification serveur obligatoire** + **rate-limit IP** + **honeypot** optionnel. Pas de reCAPTCHA Google en MVP (privacy / dépendance).

---

## 0 bis. Autocritique — pièges à éviter avant OpenSpec

| # | Piège | Correction |
|---|-------|------------|
| **E1** | Widget frontend seul, sans verify backend | **Fail-closed** : sans `turnstile_token` valide → `400`/`403`, aucun `CreateUser` |
| **E2** | Patcher seulement `essensys-support-site/backend` | Sur OVH consolidé, le handler réel est **`essensys-user-portal-backend`**. Spec + tasks doivent cibler le **binaire qui sert `/api/auth/register` en prod** ; garder le support-site backend en sync si encore déployable. |
| **E3** | Secrets Turnstile en clair dans le repo | `TURNSTILE_SITE_KEY` (public, frontend build) + `TURNSTILE_SECRET_KEY` (SOPS / `.env` OVH). Jamais commit du secret. |
| **E4** | Turnstile en dur, pas de bypass test | Mode **dev/test** : secret/site de test Cloudflare **ou** env `TURNSTILE_DISABLED=true` **uniquement** hors prod (interdit si `ENV=production`). |
| **E5** | CAPTCHA sans rate-limit | Bots peuvent encore hammerer siteverify. Ajouter **rate-limit** `POST /auth/register` (ex. 5 / IP / heure) — pattern `RateLimiter` déjà dans portal-backend. |
| **E6** | Oublier login / forgot-password | MVP = **register uniquement**. Login Turnstile = Phase 2 optionnelle (documenter). |
| **E7** | Admin « Ajouter un utilisateur » cassé | Les créations **admin** (`UserManager` / routes admin) **ne passent pas** par Turnstile utilisateur. Ne pas bloquer le provisionnement support. |
| **E8** | UX Matrix / Playwright | Widget Turnstile casse les e2e si non stubbé. Fournir **fixture / mock** siteverify en CI + clé test Cloudflare. |
| **E9** | Domaine non autorisé Turnstile | Documenter ajout des hostnames `www.essensys.fr`, `mon.essensys.fr`, `test.essensys.fr` (et local si besoin) dans le dashboard Cloudflare. |

---

## 1. Objectifs produit

### 1.1 Livrables MVP

1. **Widget Turnstile** sur la page `/register` (support-site SPA).
2. **Payload** : `turnstile_token` (ou `cf-turnstile-response`) envoyé avec email/password.
3. **Vérification serveur** : appel HTTPS `https://challenges.cloudflare.com/turnstile/v0/siteverify` avec `secret`, `response`, `remoteip` (optionnel) **avant** hash password / `CreateUser`.
4. **Rate-limit** IP sur `POST /api/auth/register`.
5. **Honeypot** HTML caché (ex. `website`) : si rempli → rejet silencieux `400`.
6. **Secrets** : Ansible/SOPS + env cloud-backend ; site key exposée au build Vite (`VITE_TURNSTILE_SITE_KEY`) ou endpoint public config non sensible.
7. **Observabilité** : log audit `REGISTER_BLOCKED_TURNSTILE` / `REGISTER_BLOCKED_RATELIMIT` (sans token en clair).
8. **Doc** : courte note ops (création site Turnstile, domaines, rotation clés) + mention privacy.

### 1.2 Non-objectifs MVP

- reCAPTCHA / hCaptcha / Friendly Captcha (alternatives documentées seulement).
- Vérification email obligatoire (recommandé Phase 2 si spam continue).
- Turnstile sur login / OAuth Google-Apple (OAuth déjà désactivé côté UI).
- WAF Cloudflare complet (optionnel, hors scope code).
- Suppression en masse des comptes fictifs existants (ops manuelle / script admin séparé, hors change ou tâche ops optionnelle).

---

## 2. Architecture cible (à détailler dans `design.md`)

```
Browser Register.jsx
  → Turnstile widget (site key)
  → POST /api/auth/register { email, password, …, turnstile_token }
       → rate-limit IP
       → honeypot check
       → siteverify (Cloudflare) ──fail──→ 403
       → CreateUser (existant)
```

### 2.1 Surfaces à toucher (par dépôt)

| Dépôt | Rôle |
|-------|------|
| `essensys-support-site` | UI `Register.jsx` + éventuellement backend legacy si encore joinable |
| `essensys-user-portal-backend` | Handler `Register` consolidé OVH + middleware rate-limit + client siteverify |
| `essensys-ansible` | Vars SOPS cloud (`turnstile_secret_key`, site key) + template `cloud-backend.env` |
| `essensys-memory` | OpenSpec change + wiki/OKF + roadmap |

### 2.2 Contrat API (proposition)

Étendre le body register :

```json
{
  "email": "…",
  "password": "…",
  "first_name": "…",
  "last_name": "…",
  "turnstile_token": "<token widget>",
  "website": ""
}
```

Réponses :

| Code | Cas |
|------|-----|
| `201` | OK (inchangé) |
| `400` | body invalide / honeypot / token manquant |
| `403` | Turnstile invalide / expiré |
| `409` | email déjà existant (inchangé) |
| `429` | rate-limit |

### 2.3 Sécurité

- Timeout court sur siteverify (ex. 5 s) ; en cas d'erreur réseau Cloudflare → **fail-closed** (pas d'inscription).
- Ne jamais logger le token ni le secret.
- Secret uniquement serveur ; site key publique OK.
- Idempotence : un token Turnstile est **single-use** (comportement Cloudflare) — ne pas rejouer.

---

## 3. Décisions produit à trancher dans `proposal.md`

1. **Widget mode** : `managed` (checkbox légère) vs `invisible` — **recommandation : managed** (meilleure friction anti-bot UX acceptable).
2. **Repo handler prod** : confirmer que seul `user-portal-backend` (cloud-server) sert register en prod ; support-site backend = sync ou déprécié.
3. **Bypass CI** : clés test Cloudflare vs `TURNSTILE_DISABLED` — **recommandation : clés test Cloudflare en CI**, disable interdit en prod.
4. **Rate-limit** : valeurs exactes (ex. 5/h/IP, 20/jour/IP).
5. **Cleanup** : script admin pour purger comptes fictifs déjà créés — in/out of scope ?
6. **Phase 2** : email verification + Turnstile login.

---

## 4. Intégration OpenSpec — instructions à l'agent

- **Schema** : `spec-driven` (`essensys-memory/openspec/config.yaml`).
- **Repo hôte du change** : `essensys-memory` (roadmap) — ID proposé :
  **`essensys-turnstile-registration-2026-07-036`**
  (ajuster le numéro si collision avec un change déjà créé après `035`).
- **Commande** :
  ```bash
  cd /Users/nrineau/ESSENSYS/essensys-memory
  # puis /openspec-propose essensys-turnstile-registration
  # ou : openspec new change "essensys-turnstile-registration-2026-07-036"
  ```
- **Artefacts obligatoires** :
  - `proposal.md` — pourquoi (spam), impact legacy = **nul** (auth moderne uniquement), décisions §3, liens wiki auth/privacy.
  - `design.md` — sous-sections **backend Go** / **frontend React** / **infra secrets Ansible-SOPS** ; séquence siteverify ; fail-closed ; rate-limit.
  - `specs/turnstile-registration/spec.md` — exigences MUST (token requis, verify avant CreateUser, rate-limit, honeypot, admin create exempt, CI mock).
  - `tasks.md` — tâches par dépôt + **mettre à jour essensys-memory** + deploy OVH + tests.

### Contenu attendu de `tasks.md` (checklist)

- [ ] Créer site Turnstile Cloudflare + domaines
- [ ] Secrets SOPS / env cloud-backend
- [ ] Client Go `siteverify` + tests unitaires (HTTP mock)
- [ ] Brancher `Register` (portal-backend) fail-closed
- [ ] Rate-limit register
- [ ] Honeypot
- [ ] UI `Register.jsx` + site key
- [ ] Sync/support-site backend si encore dans le chemin
- [ ] Playwright / e2e stub Turnstile
- [ ] Deploy OVH + smoke register (token valide / invalide)
- [ ] Doc privacy / ops
- [ ] Ingest wiki `wiki/concepts/turnstile-registration.md` + OKF + `okf/log.md` + roadmap publique

### Definition of Done

- [ ] Sans token Turnstile valide → **aucun** user créé (preuve test unitaire + smoke prod/test).
- [ ] Rate-limit actif sur register.
- [ ] Admin create user **non** bloqué.
- [ ] Secrets absents du git ; SOPS/env OK.
- [ ] CI verte avec mock/clés test.
- [ ] `openspec validate <change> --strict` OK.
- [ ] `essensys-memory` mis à jour ; pas de secrets dans OKF/raw.
- [ ] Legacy IoT **non touché**.

---

## 5. Références code / docs

| Élément | Chemin |
|---------|--------|
| UI register | `essensys-support-site/site/src/pages/Register.jsx` |
| Handler legacy | `essensys-support-site/backend/internal/api/handlers_auth.go` |
| Handler consolidé | `essensys-user-portal-backend/internal/identity/` (`Register`) |
| Rate-limit existant | `essensys-user-portal-backend/internal/middleware/rate_limit.go` |
| Cookie consent | `essensys-support-site/site/src/components/CookieConsent.jsx` |
| Secrets cloud | `essensys-ansible/secrets/cloud/` (SOPS) |
| Doc auth | `essensys-support-site/docs/authentication.md` |
| Turnstile docs | https://developers.cloudflare.com/turnstile/ |

---

### Point de départ suggéré pour l'agent

> Lance `/openspec-propose` avec ce prompt comme contexte.  
> Change name : **`essensys-turnstile-registration-2026-07-036`**.  
> Commence par confirmer le handler prod réel (`cloud-backend` vs support-site), formalise les décisions §3 (recommandations par défaut sauf objection), puis `proposal.md` (impact legacy = nul), `design.md` (Go / React / SOPS), `specs/turnstile-registration/spec.md`, `tasks.md`.  
> N'implémente pas avant validation OpenSpec stricte. Ne commit aucun secret Turnstile.
