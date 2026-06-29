## Why

Sur `mon.essensys.local`, les utilisateurs ont besoin d'un **login automatique par appareil** pour les iPad muraux, tablettes cuisine et postes fixes du LAN, sans redemander le mot de passe a chaque ouverture. En meme temps, l'authentification locale ne doit pas devenir permanente sans controle : un utilisateur standard doit **reconfirmer son login/mot de passe tous les 2 mois**, et seul l'administrateur local peut rendre un couple **adresse MAC + login** permanent.

> **Roadmap ID:** 2026-06.013  
> **Horizon:** voir [[OpenSpec Queue 2026 06]]  
> **Depend de:** 009

## What Changes

- Epic **Trusted devices iPad mural HTTPS local** — voir [[Product Roadmap]].
- Definir un mecanisme de **trusted devices LAN** adosse a l'IAM locale (`lan_users`) : un utilisateur peut choisir un client detecte par **adresse MAC** pour activer la connexion automatique.
- La confiance self-service expire apres **2 mois (60 jours)** : a l'expiration, l'utilisateur doit ressaisir login + mot de passe avant de pouvoir reactiver la confiance.
- Un `lan_admin` peut creer un appairage **permanent** entre une **adresse MAC** et un **compte non-admin** pour les ecrans muraux / clients partages.
- Les comptes `lan_admin` sont explicitement **exclus** de toute connexion automatique.
- Depots cibles de l'implementation : `essensys-server-backend`, `essensys-server-frontend`, `essensys-raspberry-install` / `essensys-ansible` pour la doc et le deploiement.
- Depot hote OpenSpec : `essensys-memory`.

## Capabilities

### New Capabilities

- `trusted-devices` : spec dans `specs/trusted-devices/spec.md`.

## Impact

Composants : `essensys-server-backend`, `essensys-server-frontend`, `essensys-raspberry-gateway`, `essensys-raspberry-install`, `essensys-ansible`.

## Gate

- Ne pas demarrer l'implementation sans verifier que le socle HTTPS/local trust du change **009** est deployable sur la gateway cible.
- La livraison fonctionnelle depend aussi d'un login/mot de passe LAN stable issu du change **017** (`lan_users`, session cookie, roles LAN).
