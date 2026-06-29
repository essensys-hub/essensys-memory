# Tasks — essensys-trusted-devices-2026-06.013

> **Roadmap ID:** 2026-06.013 — **active** (spec/design affine le 2026-06-28)

## Phase 1 — Spec

- [x] 1.1 Affiner proposal depuis [[Product Roadmap]]
- [x] 1.2 Rediger design + specs `trusted-devices`
- [x] 1.3 Valider dependances 009 (HTTPS local / trust) + 017 (LAN IAM)

## Phase 2 — Backend (`essensys-server-backend`)

- [x] 2.1 Ajouter la persistance `trusted_devices` reliee a `lan_users`
- [x] 2.2 Resoudre l'adresse MAC cote gateway/backend (ARP/NDP ou source de confiance equivalente)
- [x] 2.3 Exposer les endpoints self-service `trusted-devices` pour `lan_user` / `lan_guest`
- [x] 2.4 Exposer les endpoints admin `trusted-devices` pour creation permanente / revocation
- [x] 2.5 Bloquer auto-login pour le compte usine `admin@essensys.local` uniquement
- [x] 2.6 Imposer l'expiration self-service a **60 jours** et la re-authentification login+mot de passe
- [x] 2.7 Gerer les cas ambigus (plusieurs comptes sur une MAC) sans auto-login silencieux
- [x] 2.8 Ajouter tests unitaires / integration backend sur expiration, revocation et exclusion admin

## Phase 3 — Frontend (`essensys-server-frontend`)

- [x] 3.1 Ajouter l'UI **Appareils de confiance** dans **Mon compte** pour `lan_user` / `lan_guest`
- [x] 3.2 Afficher les clients detectes par MAC avec libelle/derniere vue si disponible
- [x] 3.3 Permettre l'activation self-service d'un trusted device temporaire
- [x] 3.4 Afficher clairement la regle **2 mois puis re-login obligatoire**
- [x] 3.5 Ajouter l'UI admin de gestion / promotion permanente / revocation
- [x] 3.6 Masquer trusted device pour `admin@essensys.local` ; `lan_admin` locaux autorisés

## Phase 4 — Deploy / docs

- [x] 4.1 Documenter les prerequis reseau de resolution MAC sur gateway CM5
- [x] 4.2 Mettre a jour la doc install/utilisateur sur le comportement **2 mois**
- [x] 4.3 Documenter la procedure admin d'appairage permanent MAC + login
- [x] 4.4 Verifier l'absence d'impact sur les routes legacy IoT et sur l'acces WAN (scope LAN uniquement, pas de route trusted sur WAN)

## Verification

```bash
cd essensys-memory && openspec validate essensys-trusted-devices-2026-06.013 --strict
# Puis, lors de l'implementation :
# cd essensys-server-backend && go test ./...
# cd essensys-server-frontend && npm run build
# npm run lint  # actuellement bloque par des erreurs pre-existantes hors trusted-devices
```
