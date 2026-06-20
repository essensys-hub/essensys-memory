---
tags: [concept, firmware, protocol, legacy]
sources: [exchange-table.md, mcp-device-index-reference.md, TableEchange.h, constants.go]
created: 2026-06-20
updated: 2026-06-20
era: migration
---

# Table D Echange

Contrat central armoire ↔ serveur : paires **k** (indice) / **v** (valeur). Cœur du dialogue [[Essensys Board SC944D]] ↔ [[Essensys Server Backend]] ↔ [[Client Essensys Legacy]].

## Où elle vit

| Couche | Fichier |
|--------|---------|
| Firmware maître | `raw/protocol/TableEchange.h` (SC944D 099-37) |
| Écran IHM | `IHM_ECHANGES.INC` — [[Essensys Board SC945D]] |
| Backend Go | `pkg/protocol/constants.go` — [[Essensys Server Backend]] |
| Cloud jumeau | `internal/domain/order_expansion.go` — [[Essensys User Portal Backend]] |
| Pilotage web/HA | `POST /api/admin/inject` ou `/api/portal/inject` |

## Indices critiques (scénario / lumières / volets)

| Indice | Rôle |
|--------|------|
| **590** | Trigger scénario — `"0"` aucun ; `"1"` serveur (Mode B) ; `"2"`–`"8"` lancer slot mémorisé (Mode A) |
| **605–610** | Masques **éteindre** éclairage PDV / CHB / PDE (LSB+MSB par zone) |
| **611–616** | Masques **allumer** éclairage PDV / CHB / PDE |
| **617–622** | Ouvrir / fermer volets par zone (PDV, CHB, PDE) |
| **591–919** | Scénarios mémorisés (8×41 octets) — voir [[Scénarios domotique]] |
| **409–411** | État / contrôle alarme |
| **566–589** | Temps de course volets (push cloud, 2026-06) |

Constantes Go : `IndexScenario=590`, `IndexLightStart=605`, `IndexLightEnd=622`.

## Règles d'action (firmware BP_MQX_ETH)

1. **`_de67f` en premier** dans la réponse `/api/myactions` (ordre alarme chiffré AES ou `null`)
2. **Bloc complet 605–622 + 590=`"1"`** même si une seule lampe change — le serveur complète via `ActionService.AddAction()` / `ExpandLegacyScenarioBlock`
3. **Fusion OR bitwise** (`|`) si plusieurs actions sur le même index
4. Ordre MCP/Redis **sans** expansion → comportement différent du web (voir [[Dual Protocol]])

## Flux ordre valide

```
Web/MCP inject → Redis essensys:global:actions → GET /api/myactions → firmware → POST /api/done/{guid}
```

## Risque connu

Dérive d'indices corrigée (~600 → ~953). **Toute renumérotation doit être propagée** firmware + écran + serveur + portail cloud.

## Sources détaillées

- [[Exchange Table Protocol]] — `raw/protocol/exchange-table.md`
- [[MCP Device Index Reference]] — mapping équipements → indices 605–616
- `raw/protocol/constants.go`

## Code pointers

- `essensys-board-SC944D/SC944D/Prog/099-37/BP_MQX_ETH/H/TableEchange.h`
- `essensys-server-backend/internal/core/action_service.go`
- `client-essensys-legacy/H/TableEchange.h`
