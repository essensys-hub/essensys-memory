## Context

Change **2026-06.013** — trusted devices LAN sur `mon.essensys.local`.

Le change **017** a introduit l'IAM locale (`lan_users`, login/mot de passe, session cookie, roles `lan_admin` / `lan_user` / `lan_guest`). Ce change ajoute une couche **"appareil de confiance"** pour les clients LAN partages ou fixes : l'utilisateur choisit un client identifie par **adresse MAC** afin d'eviter le login manuel a chaque fois, tout en imposant une **re-authentification tous les 2 mois** pour les utilisateurs standard.

## Goals / Non-Goals

**Goals**

- Permettre a un utilisateur **non-admin** de marquer un client LAN comme **appareil de confiance** apres un login reussi.
- Utiliser un identifiant de client base sur l'**adresse MAC observee cote gateway**, pas sur une saisie manuelle fragile dans le navigateur.
- Expirer la confiance self-service apres **60 jours** puis redemander **login + mot de passe**.
- Permettre a un `lan_admin` de creer un appairage **permanent** `adresse MAC + login` pour un compte non-admin (mur tactile, tablette cuisine, etc.).
- Interdire tout auto-login pour les comptes `lan_admin`.

**Non-Goals**

- Lecture directe de l'adresse MAC depuis JavaScript/browser.
- Remplacement du login/mot de passe LAN ; le trusted device vient **apres** l'IAM locale.
- Auto-login WAN / cloud ; ce change ne concerne que `mon.essensys.local`.
- Authentification forte materielle type certificat client mutualise ou MDM.

## Decisions

### D1 — Source de verite de l'adresse MAC

Un navigateur web classique ne peut pas lire l'adresse MAC du client. Le systeme MUST donc resoudre l'adresse MAC **cote gateway / backend** a partir de la requete LAN (IP source -> cache ARP/NDP local, ou header injecte par un composant local de confiance). Le frontend ne fait qu'afficher les clients detectes que le backend lui expose.

Conséquence produit : l'UI ne demandera pas a l'utilisateur de taper sa MAC. Elle affichera une **liste des clients detectes** (label, MAC normalisee, derniere vue) afin qu'il choisisse le bon appareil.

### D2 — Modele de donnees `trusted_devices`

Le backend introduit une persistance dediee `trusted_devices` liee a `lan_users`.

Champs minimaux v1 :

- `id`
- `lan_user_id`
- `mac_address` (normalisee uppercase `AA:BB:CC:DD:EE:FF`)
- `device_label`
- `trust_mode` ∈ {`temporary`, `permanent`}
- `expires_at` (`NULL` si permanent)
- `created_by_user_id`
- `approved_by_admin_user_id` (`NULL` pour self-service temporaire)
- `last_seen_at`
- `revoked_at`
- `created_at`, `updated_at`

Contrainte v1 : unicite sur `(mac_address, lan_user_id, revoked_at IS NULL)` pour eviter les doublons actifs.

### D3 — Eligibilite des comptes

- `lan_user` : eligible trusted device.
- `lan_guest` : eligible trusted device si le compte est actif.
- `lan_admin` : eligible trusted device **sauf** le compte usine `admin@essensys.local` (`BootstrapLanAdminEmail`).

Rationale : le compte usine bootstrap ne doit jamais contourner la re-authentification sur un poste partage ; les administrateurs locaux (ex. installateur) peuvent utiliser l'auto-login comme les utilisateurs.

### D4 — Flux self-service utilisateur

1. L'utilisateur se connecte avec email + mot de passe via l'IAM LAN.
2. Le frontend appelle une route de type `GET /api/user/me/trusted-devices/candidates`.
3. Le backend renvoie les clients LAN observes pour cette session / source reseau avec MAC normalisee.
4. L'utilisateur choisit un client et active **Connexion automatique sur cet appareil**.
5. Le backend cree une entree `trusted_devices` en mode `temporary` avec `expires_at = now + 60 jours`.
6. Lors d'une visite future depuis cette meme MAC, le backend peut proposer ou declencher l'auto-login pour ce compte tant que l'entree est active et non expiree.

A l'expiration des 60 jours, l'utilisateur doit repasser par le login/mot de passe. Une nouvelle confiance peut ensuite etre recreee.

### D5 — Flux admin permanent

Un `lan_admin` peut gerer les trusted devices depuis l'UI/admin API :

- lister les appairages actifs ;
- creer un appairage **permanent** entre une MAC detectee et un compte `lan_user` ou `lan_guest` ;
- revoquer un appairage ;
- convertir un temporaire en permanent.

Le backend MUST refuser toute tentative de creation permanente vers un compte `lan_admin`.

### D6 — Decision d'auto-login

A l'arrivee sur `mon.essensys.local`, le backend evalue l'adresse MAC observee :

- **aucun match actif** -> login classique ;
- **un seul match actif non admin** -> auto-login autorise ;
- **plusieurs matches actifs** -> pas d'auto-login silencieux, l'UI demande un choix explicite ou retour au login ;
- **match expire / revoque** -> pas d'auto-login, login classique.

Pour limiter les erreurs sur clients partages, le backend garde `last_seen_at` et peut exposer un libelle d'appareil base sur hostname DHCP/ARP si disponible.

### D7 — Surface API v1

Surface indicative a implementer dans les depots cibles :

| Methode | Route | Auth |
|---------|-------|------|
| `GET` | `/api/user/me/trusted-devices/candidates` | session (`lan_user`, `lan_guest`) |
| `GET` | `/api/user/me/trusted-devices` | session (`lan_user`, `lan_guest`) |
| `POST` | `/api/user/me/trusted-devices` | session (`lan_user`, `lan_guest`) |
| `DELETE` | `/api/user/me/trusted-devices/{id}` | session (`lan_user`, `lan_guest`) |
| `GET` | `/api/admin/trusted-devices` | `lan_admin` |
| `POST` | `/api/admin/trusted-devices` | `lan_admin` |
| `POST` | `/api/admin/trusted-devices/{id}/promote-permanent` | `lan_admin` |
| `POST` | `/api/admin/trusted-devices/{id}/revoke` | `lan_admin` |

Le point d'entree d'auto-login peut etre integre au bootstrap auth existant (`/api/user/me`, `/health`, ou middleware dedie) tant qu'il reste scope LAN.

### D8 — UX / Frontend

Le frontend LAN ajoute :

- une section **Appareils de confiance** dans **Mon compte** pour `lan_user` / `lan_guest` ;
- un message clair sur l'expiration **dans 60 jours** ;
- une page / panneau admin pour gerer les appairages permanents ;
- aucune option trusted device pour un `lan_admin` authentifie.

Le vocabulaire doit rester non-technique cote utilisateur :

- "Cet appareil restera connecte pendant 2 mois"
- "Au bout de 2 mois, vous devrez ressaisir votre mot de passe"
- "Un administrateur peut rendre cet appareil permanent"

### D9 — Dependances et impacts

- **009** (`essensys-gateway-mtls`) : prerequis d'integrite de la surface locale HTTPS et de confiance reseau.
- **017** (`essensys-lan-iam-2026-06.017`) : prerequis fonctionnel, car trusted devices se branchent sur `lan_users` et le login local.
- Documentation : `essensys-raspberry-install` / `essensys-ansible` doivent documenter la decouverte MAC, les limites LAN et la revocation.

## Risks / Trade-offs

| Risque | Mitigation |
|--------|------------|
| MAC spoofable sur un LAN hostile | Limiter a `mon.essensys.local`, exclure `lan_admin`, journaliser/revoquer facilement |
| Browser incapable de lire la MAC | Resolution cote gateway uniquement |
| Ambiguite si plusieurs comptes associes a la meme MAC | Refus d'auto-login silencieux ; choix explicite requis |
| Client remplace / carte reseau changee | Revocation simple + recreation appairage |
| DHCP/ARP incomplet | UI affiche seulement les candidats observes recemment ; fallback login manuel |

## Migration Plan

1. Stabiliser IAM LAN (017) sur la gateway cible.
2. Ajouter persistance `trusted_devices` + resolution MAC cote backend.
3. Ajouter endpoints self-service et admin.
4. Ajouter UX frontend **Appareils de confiance**.
5. Documenter exploitation / revocation / duree 60 jours.
6. Verifier qu'aucun compte `lan_admin` ne peut activer l'auto-login.

## Open Questions

- La resolution MAC doit-elle vivre dans le backend Go, dans Traefik, ou dans un helper local dedie ?
- Faut-il afficher le hostname DHCP si disponible pour aider l'utilisateur a choisir le bon client ?
- En cas d'auto-login valide, souhaite-t-on une entree directe silencieuse ou un ecran de confirmation "Se connecter comme X" ?
