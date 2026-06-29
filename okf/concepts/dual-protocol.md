---
type: Concept
title: Dual Protocol
description: Coexistence de deux protocoles HTTP incompatibles dans les backends ESSENSYS.
tags: [essensys, protocol, legacy, backend, compatibility]
timestamp: 2026-06-28T06:11:17Z
source_wiki: ../../wiki/concepts/dual-protocol.md
---

# Définition

Le Dual Protocol désigne la coexistence, dans les backends ESSENSYS, d'un protocole HTTP legacy destiné aux clients embarqués et d'une API web moderne REST/JSON.

# Protocoles

| Protocole | Clients | Caractéristiques |
|---|---|---|
| Legacy IoT | Client Essensys Legacy, carte SC944D | Endpoints figés, JSON non standard à normaliser, réponse single-packet TCP, Basic Auth, alarmes AES |
| Web moderne | Frontends React, apps mobiles, Home Assistant | REST/JSON standard, sessions ou JWT, endpoints `/api/auth/*`, `/api/user/*`, `/api/admin/inject`, `/api/gateway/*` |

# Règle de compatibilité

Toute modification du protocole legacy doit préserver la compatibilité firmware et être accompagnée de tests de non-régression et d'une mise à jour de la mémoire.

# Liens

* [ESSENSYS Platform Overview](/synthesis/platform-overview.md)
* [Feature Lifecycle](/processes/feature-lifecycle.md)

# Citations

[1] [Wiki source: Dual Protocol](../../wiki/concepts/dual-protocol.md)
