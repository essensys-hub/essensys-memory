---
type: Protocol Contract
title: Table D Echange
description: Contrat k/v armoire ↔ serveur au cœur du dialogue firmware, backend, écran et cloud.
tags: [essensys, protocol, firmware, legacy, armoire]
timestamp: 2026-06-28T19:07:32Z
era: migration
source_wiki: ../../wiki/concepts/table-d-echange.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

La Table d'Échange est le contrat central armoire ↔ serveur : paires `k` (indice) / `v` (valeur) partagées entre firmware, écran, backends et interfaces.

# Indices critiques

| Indice | Sémantique |
|---|---|
| `590` | Trigger scénario : `0` aucun, `1` serveur / Mode B, `2`-`8` slots mémorisés / Mode A |
| `591-919` | Scénarios mémorisés, 8 slots × 41 octets |
| `605-610` | Masques éteindre éclairage PDV / CHB / PDE |
| `611-616` | Masques allumer éclairage PDV / CHB / PDE |
| `617-622` | Ouvrir / fermer volets par zone |
| `409-411` | État et contrôle alarme |
| `566-589` | Temps de course volets propagés vers cloud/gateway |

# Règles d'action

* `_de67f` doit rester en premier dans la réponse `/api/myactions` pour l'alarme chiffrée AES ou `null`.
* Les actions lumière/volet doivent envoyer le bloc complet `605-622` avec `590="1"` pour préserver le comportement firmware.
* Les actions multiples sur un même index fusionnent par OR bitwise.
* Les chemins web/backend et cloud doivent rester cohérents avec firmware et écran IHM.

# Mappings multi-repos

* Firmware maître : `essensys-board-SC944D/.../TableEchange.h`.
* Client legacy : `client-essensys-legacy/H/TableEchange.h`.
* Écran IHM : `IHM_ECHANGES.INC` dans [SC945D](/firmware/sc945d.md) quand disponible.
* Backend LAN : `essensys-server-backend/pkg/protocol/constants.go`, `internal/core/action_service.go`.
* Cloud twin : `essensys-user-portal-backend/internal/domain/order_expansion.go`.

# Risques

* Toute renumérotation ou changement de sémantique doit être propagé firmware + écran + serveur + portail cloud.
* Les contradictions entre sources doivent être conservées dans le rapport de couverture, pas masquées.

# Citations

[1] [Wiki source](../../wiki/concepts/table-d-echange.md)
[2] [Dual Protocol](/protocols/dual-protocol.md)
<!-- END GENERATED CONTENT -->
