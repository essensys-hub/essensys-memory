---
tags: [source, protocol, legacy, firmware]
sources: [exchange-table.md]
created: 2026-06-20
updated: 2026-06-20
---

# Exchange Table Protocol

**Source:** `raw/protocol/exchange-table.md` (from `client-essensys-legacy/docs/protocol/`)  
**Type:** protocole firmware legacy

## Summary

Spécification de la table d'échange ~600 index entre boîtier BP_MQX_ETH et serveur. État partagé en octets 0–255 (état, masques, consignes).

## Key Claims

- Index **590** = trigger scénario obligatoire dans chaque action
- **605–622** = blocs éclairage/volets (paires LSB/MSB par zone PDV/CHB/PDE)
- **613–624** dans doc legacy = même plage scénario (numérotation base 600 + offset enum)
- Fusion **OR bitwise** des valeurs sur un même index
- Action `/api/myactions` : `_de67f` first, bloc complet requis

## Concepts

- [[Table D Echange]]
- [[Dual Protocol]]
- [[Client Essensys Legacy]]

## Entities

- [[Essensys Board SC944D]]
- [[Essensys Server Backend]]
