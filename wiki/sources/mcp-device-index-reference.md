---
tags: [source, protocol, backend, mcp]
sources: [mcp-device-index-reference.md]
created: 2026-06-20
updated: 2026-06-20
---

# MCP Device Index Reference

**Source:** `raw/protocol/mcp-device-index-reference.md` (from `essensys-server-backend/docs/`)  
**Type:** référence indices domotiques

## Summary

Mapping complet équipements → indices k/v pour le **Device MCP** (`essensys-server-backend/cmd/mcp-server`). Outil `find_device_index` par nom et catégorie.

## Key Claims

- Éclairage **allumer** : indices 611–616 (PDV, CHB, PDE + MSB variateurs)
- Éclairage **éteindre** : indices 605–610
- Volets : indices 617–622
- Valeurs = masques binaires (ex. chevet chambre 3 → index 613, valeur `64`)
- MCP `send_order` doit passer par expansion 590+605..622 comme le web

## Liens

- [[Table D Echange]]
- [[Essensys Server Backend]]
- [[Essensys MCP]] (brain) vs Device MCP (backend)

## Code pointers

- `essensys-server-backend/cmd/mcp-server/main.go` — `expandLegacyScenarioBlock`
- `essensys-server-backend/docs/MCP_DEVICE_INDEX_REFERENCE.md`
