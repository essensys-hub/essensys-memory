---
tags: [concept, security, gateway, lan, trusted-devices]
sources: [essensys-trusted-devices-2026-06.013, essensys-lan-iam-2026-06.017]
created: 2026-06-29
updated: 2026-06-29
---

# Trusted devices LAN (auto-login MAC)

> Connexion automatique sur **`https://mon.essensys.local`** pour les appareils de confiance identifiés par **adresse MAC**, au-dessus de l'IAM locale ([[LAN IAM]]).

## Périmètre

| In | Out |
|----|-----|
| Auto-login LAN après login/mot de passe ou appairage admin | Auto-login cloud `mon.essensys.fr` |
| Résolution MAC côté gateway (ARP / `ip neigh`) | Lecture MAC depuis le navigateur |
| Comptes `lan_user`, `lan_guest`, `lan_admin` (sauf usine) | Compte usine `admin@essensys.local` |

## Règles métier (v1 déployée 2026-06-29)

| Qui | Auto-login | Durée | Où configurer |
|-----|------------|-------|----------------|
| **Utilisateur / Invité** | Oui (self-service) | **60 jours** → re-login mot de passe obligatoire | `/settings/account` → Appareils de confiance |
| **Administrateur local** (`lan_admin`, ex. `nicolas@rineau.eu`) | Oui (self-service ou admin) | 60 jours ou **permanent** si appairé | Mon compte ou Comptes .local |
| **Compte usine** `admin@essensys.local` | **Non** | — | Mot de passe à chaque connexion |

Constante backend : `models.BootstrapLanAdminEmail` = `admin@essensys.local`. Seul ce compte est exclu via `LanUser.IsBootstrapLanAdmin()` / `CanUseTrustedDevices()`.

## Flux utilisateur (temporaire 60 jours)

1. Login email + mot de passe sur `/login`.
2. Backend enregistre la paire **user + MAC + IP** dans `lan_login_clients` (résolution MAC à la connexion).
3. **Mon compte** → liste des appareils depuis lesquels l'utilisateur s'est connecté → **Faire confiance — 60 jours**.
4. Visites suivantes : `GET /api/auth/auto-login` reconnaît la MAC → session cookie sans mot de passe.
5. Après `expires_at` : auto-login refusé → login manuel → l'utilisateur peut recréer la confiance.

## Flux administrateur (permanent)

1. L'utilisateur cible se connecte **une fois** depuis l'appareil (login + mot de passe).
2. Admin → **`/settings/users`** → section **Appairage auto-login** → **Rafraîchir** → **Appairer (permanent)** sur la ligne user + MAC.
3. `trusted_devices.trust_mode = permanent`, `expires_at = NULL`.

Promotion : un temporaire existant peut passer en permanent via **Promouvoir permanent** dans le tableau des appareils actifs.

## Données PostgreSQL (gateway)

| Table | Rôle |
|-------|------|
| `lan_users` | Comptes IAM (change 017) |
| `trusted_devices` | Appairages actifs (temporaire / permanent), migration `004` |
| `lan_login_clients` | Historique login → MAC pour listes UI, migration `005` |

Migrations Ansible : `essensys-ansible/roles/raspberry_backend/tasks/lan_iam_migrations.yml` (`003`, `004`, `005`).

## API (backend `internal/laniam`)

| Méthode | Route | Auth |
|---------|-------|------|
| `GET` | `/api/auth/auto-login` | public (MAC → session) |
| `GET` | `/api/user/me/trusted-devices/candidates` | session, `CanUseTrustedDevices` |
| `POST` | `/api/user/me/trusted-devices` | idem — crée temporaire 60 j |
| `GET` | `/api/admin/trusted-devices/candidates` | `lan_admin` — connexions récentes (hors `admin@essensys.local`) |
| `POST` | `/api/admin/trusted-devices` | `lan_admin` — permanent |
| `POST` | `/api/admin/trusted-devices/{id}/revoke` | révocation |

Candidats : **uniquement** les MAC observées lors d'un login enregistré dans `lan_login_clients` (plus de dump ARP complet).

## UI frontend (`essensys-server-frontend`)

| Page | Route | Rôle |
|------|-------|------|
| Mon compte | `/settings/account` | self-service 60 jours |
| Comptes .local | `/settings/users` | admin — appairage permanent, CRUD users |

Build gateway : `VITE_LAN_IAM=true`. Détection runtime : `/health` → `lan_iam_enabled`.

## Prérequis réseau (CM5)

- Backend en `network_mode: host` (Docker Compose) pour lire `/proc/net/arp` et `ip neigh`.
- Le client doit avoir **pingé** la gateway récemment ; un `ping -c 1` est déclenché côté backend avant lecture ARP.
- IP client transmise via `X-Real-IP` / `X-Forwarded-For` (nginx → backend).
- **Ne pas** lancer en parallèle `essensys-backend.service` (systemd host) et le conteneur Docker sur le port **7070** — conflit `address already in use`.

## Déploiement CM5 (rsync rapide)

```bash
# Backend
cd essensys-server-backend
GOOS=linux GOARCH=arm64 go build -o /tmp/server ./cmd/server
rsync -az /tmp/server essensys@<CM5>:/opt/essensys/backend/server
ssh essensys@<CM5> 'docker restart essensys-backend'

# Frontend
cd essensys-server-frontend
VITE_LAN_IAM=true npm run build
rsync -az --delete dist/ essensys@<CM5>:/opt/data/frontend/
```

Playbook complet : `ansible-playbook -i inventory.gateway update.raspberrypi.yml -e lan_iam_enabled=true`

## Cas limites

- **Ambiguïté** : deux comptes actifs sur la même MAC → pas d'auto-login silencieux (`409 ambiguous_trusted_device`).
- **IPv6 link-local** : ignorées pour la résolution MAC client.
- **MAC `00:00:00:00:00:00`** : filtrées (entrées ARP incomplètes).

## OpenSpec

- Change : `essensys-memory/openspec/changes/essensys-trusted-devices-2026-06.013/`
- Roadmap ID : **2026-06.013**
- Prérequis : [[LAN IAM]] (017), HTTPS local (009)

## Liens

- [[LAN IAM]]
- [[Deployment Perimeters]]
- [[Essensys Server Backend]]
- [[Essensys Server Frontend]]
- [[Essensys Ansible]]
