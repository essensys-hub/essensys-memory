---
type: Protocol Contract
title: Legacy HTTP
description: Contrat HTTP historique entre firmware/client embarqué ESSENSYS et backend compatible.
tags: [essensys, legacy, http, firmware, compatibility]
timestamp: 2026-06-28T19:07:32Z
era: legacy
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Legacy HTTP est le protocole historique figé utilisé par les clients embarqués ESSENSYS, notamment BP_MQX_ETH / SC944D, pour dialoguer avec le serveur.

# Endpoints gelés

| Endpoint | Rôle |
|---|---|
| `/api/serverinfos` | Informations serveur nécessaires au client embarqué |
| `/api/mystatus` | Remontée état armoire / client |
| `/api/myactions` | Récupération des actions pending côté firmware |
| `/api/done/{guid}` | Acquittement d'une action traitée |

# Particularités wire

* JSON non standard pouvant nécessiter normalisation.
* `Content-Type` historique avec forme non canonique.
* Basic Auth côté legacy.
* Payload alarme chiffré AES via `_de67f`.
* Réponse single-packet TCP à préserver.
* Flux critique : injection web/MCP/cloud → pending actions → `/api/myactions` → firmware → `/api/done/{guid}`.

# Compatibilité

Ces endpoints sont compatibility-critical. Ils ne doivent pas être modernisés, renommés ou reformattés sans campagne explicite de tests firmware et régression legacy.

# Liens

* [Table D Echange](/protocols/table-d-echange.md)
* [Dual Protocol](/protocols/dual-protocol.md)
* [Client Essensys Legacy](/systems/client-essensys-legacy.md)
* [Essensys Server Backend](/systems/essensys-server-backend.md)

# Citations

[1] [Dual Protocol wiki](../../wiki/concepts/dual-protocol.md)
[2] [Table D Echange wiki](../../wiki/concepts/table-d-echange.md)
<!-- END GENERATED CONTENT -->
