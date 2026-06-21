---
tags: [concept, cloud, protocol, modern]
sources: [README.md, essensys-user-portal-backend.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
---

# Cloud Relay

Pilotage domotique **à distance** quand l'armoire n'est pas joignable depuis Internet (NAT).

## Flux

1. Utilisateur sur [[Essensys User Portal Frontend]] (`mon.essensys.fr/portal/`)
2. [[Essensys User Portal Backend]] enregistre une `cloud_action` (PostgreSQL)
3. [[Essensys Raspberry Gateway]] / [[Essensys Server Backend]] **poll en sortie** le hub cloud
4. La passerelle traduit l'action en commande armoire (bus legacy ou [[Table D Echange]] via inject)

## Endpoints clés

Voir [[Gateway Exchange]] pour le détail des routes `/api/gateway/*`.

## Prérequis

- Liaison armoire validée par admin (`link_requests`)
- Identité gateway (MAC, token) — cf. `cloudsync` dans [[Essensys Server Backend]] ; renforcement cible : [[Gateway PKI]]

## OpenSpec liés

- [[Essensys Cloud Backend Consolidation]] (prompt `prompts/CloudBackendConsolidation.md`)
- [[Essensys Remote User Interface]]

## Contraste legacy

Historiquement le WAN passait par [[Essensys Web Legacy]] (SQL Server). La cible est le hub consolidé [[Essensys User Portal Backend]] en `CONSOLIDATED_MODE`.
