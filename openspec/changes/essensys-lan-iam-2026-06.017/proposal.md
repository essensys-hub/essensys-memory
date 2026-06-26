## Why

Aujourd'hui, l'accès au dashboard sur **`https://mon.essensys.local`** repose sur une **Basic Auth optionnelle en mode passif** (capture seulement, pas de 401) ou sur des identifiants statiques en bordure Traefik. Il n'existe **pas** de gestion multi-utilisateur LAN : pas de création de comptes, pas de reset mot de passe, pas de rôles locaux, pas d'UI d'administration.

Le backend Go embarque déjà une **ébauche legacy** (`UserService`, `/api/auth/login`, hash SHA1) héritée de la migration ASP.NET, mais **sans middleware session**, **sans frontend**, et **sans mode strict**.

Ce change formalise l'**IAM LAN** : comptes email/mot de passe locaux à la gateway, sessions sécurisées, RBAC installateur/propriétaire/invité, sans confondre avec l'IAM cloud (`mon.essensys.fr`).

> **Roadmap ID:** 2026-06.017  
> **Horizon:** Later → promotion **active** après validation autocritique  
> **Depend de:** 013 (recommandée — sessions longues iPad), 016 (bootstrap UX installateur)  
> **Autocritique:** [`autocritique.md`](autocritique.md)

## What Changes

- Epic **IAM sessions LAN multi-utilisateur** — voir [[Product Roadmap]].
- **Gestion user + mot de passe** sur `.local` : CRUD admin, login/logout, changement mot de passe, désactivation compte.
- Durcissement auth : fin du Basic Auth passif ; table **`lan_users`** dédiée ; sessions **7 jours** ; rôles `lan_admin` / `lan_user` / `lan_guest` (guest = pilotage LAN comme user, sans admin).
- UI React (`essensys-server-frontend`) : Login, profil, admin utilisateurs LAN.
- Bootstrap premier `lan_admin` (CLI/Ansible, puis wizard 016).
- Dépôt hôte principal : `essensys-server-backend` ; jumeau UI : `essensys-server-frontend`.

## Capabilities

### New Capabilities

- `lan-iam` : spec dans `specs/lan-iam/spec.md`.

## Impact

| Composant | Changement |
|-----------|------------|
| `essensys-server-backend` | Middleware session, CRUD users LAN, hash policy, retrait capture Basic Auth |
| `essensys-server-frontend` | Pages auth + admin users |
| `essensys-ansible` | Bootstrap mot de passe initial, doc install |
| `essensys-raspberry-install` | Prompt / doc alignés wizard 016 |

**Hors scope :** `essensys-user-portal-backend` (IAM cloud JWT/OAuth inchangé).

## Gate

Ne pas démarrer l'implémentation tant que :

1. L'**autocritique** est validée (decisions D1–D8).
2. PostgreSQL gateway confirmé disponible sur cible prod CM5.
3. (Recommandé) Change **013** trusted-devices au moins en design pour sessions iPad longues.
