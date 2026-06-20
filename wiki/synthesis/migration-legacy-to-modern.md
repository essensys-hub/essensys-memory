---
tags: [synthesis, migration, legacy, roadmap]
sources: [MIGRATION_PLAN.md, README.md, essensys-server-backend.md]
created: 2026-06-20
updated: 2026-06-20
era: migration
---

# Migration Legacy To Modern

Phase de migration active : remplacement .NET/SQL Server + boîtier C/MQX par **Go + React + PostgreSQL + passerelle Raspberry**.

## Projets legacy (référence)

| Dépôt | Rôle | Stack |
|-------|------|-------|
| [[Essensys Web Legacy]] | Serveur + portail historiques | ASP.NET MVC 4, NHibernate, SQL Server |
| [[Client Essensys Legacy]] | Boîtier BP_MQX_ETH (carte+passerelle historique) | C, MQX RTOS, ColdFire MCF52259 |

## Cibles modernes

| Dépôt | Fait ✅ | Reste ❌ |
|-------|---------|----------|
| [[Essensys Server Backend]] | Protocole legacy IoT, inject, Redis, cloudsync | Users, machines, services métier complets, AES |
| [[Essensys Server Frontend]] | UI domotique complète | Auth, compte, sessions |
| [[Essensys User Portal Backend]] | Hub cloud CONSOLIDATED_MODE | Consolidation support-site backend |
| [[Essensys User Portal Frontend]] | Portail `/portal/` | Parité jumeau avec server-frontend |
| [[Essensys Raspberry Gateway]] | HW CM5, OpenSpec dual-NIC/NixOS | Production NixOS vs Ansible à trancher |

## Règle absolue

**NE JAMAIS MODIFIER** les endpoints legacy IoT : `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}`.

Contraintes client imposées par [[Client Essensys Legacy]] :
- Single-packet TCP
- JSON clés non quotées
- `Content-Type: application/json ;charset=UTF-8` (espace avant `;`)
- POST → `201 Created`

→ Détails : [[Dual Protocol]]

## Firmware armoire (hors migration serveur)

Les cartes [[Essensys Board SC944D]] (maîtresse) et esclaves PIC restent en production ; la passerelle Raspberry remplace le rôle **réseau** du boîtier legacy, pas les cartes I²C.

## Cloud

[[Cloud Relay]] + [[Gateway Exchange]] remplacent le couplage WAN historique. Backend support-site **déprécié** (juin 2026).

## Roadmap OpenSpec liée

- [[Essensys Gateway Dual Nic]]
- [[Essensys Gateway Nixos]]
- [[Essensys Second Brain]]
- Consolidation cloud (prompt `CloudBackendConsolidation.md`)

## Sources

- [[Migration Plan Source]] — `raw/plans/MIGRATION_PLAN.md`
- [[Architecture README]]
