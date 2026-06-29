---
type: Architecture Pattern
title: Dual Protocol
description: Coexistence du protocole HTTP legacy IoT et de l'API REST moderne.
tags: [essensys, protocol, backend, legacy, modern]
timestamp: 2026-06-28T19:07:32Z
source_wiki: ../../wiki/concepts/dual-protocol.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Le Dual Protocol impose aux backends ESSENSYS de servir simultanément le protocole legacy IoT et les APIs REST modernes.

# Contrats

* Legacy IoT : endpoints figés, wire quirks, compatibilité firmware et [Table D Echange](/protocols/table-d-echange.md).
* Moderne : REST/JSON, sessions/JWT, APIs utilisateur, admin et gateway.

# Risque

Tout changement backend doit vérifier les deux chemins. Une amélioration REST ne doit pas casser le firmware legacy.

# Citations

[1] [Wiki source](../../wiki/concepts/dual-protocol.md)
[2] [Legacy HTTP](/protocols/legacy-http.md)
<!-- END GENERATED CONTENT -->
