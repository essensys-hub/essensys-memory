---
tags: [source, architecture, index]
sources: [README.md]
created: 2026-06-20
updated: 2026-06-20
---

# Architecture README

**Source:** `raw/architecture/README.md`  
**Date ingested:** 2026-06-20  
**Type:** documentation architecture

## Summary

Documentation générée le 2026-06-16 couvrant les **40 dépôts** Essensys : vue C4, dual-protocol, table d'échange, index par couche (firmware, LAN, cloud, infra).

## Key Claims

- Essensys = domotique résidentielle (alarme, chauffage, éclairage, volets, arrosage, cumulus, fuites)
- Migration active : ASP.NET/MQX → Go/React/Raspberry, **compatibilité legacy IoT 100 %**
- Deux flux fondamentaux : dual-protocol backend + relay cloud NAT traversal
- 40 fiches détaillées dans `repos/` — ingestées en [[Platform Overview]] et `wiki/entities/`

## Entities Mentioned

Toutes les entités `wiki/entities/essensys-*` et cartes SC* — voir section Entities de [[Index]].

## Concepts Covered

- [[Dual Protocol]]
- [[Table D Echange]]
- [[Cloud Relay]]
- [[Migration Legacy To Modern]]
