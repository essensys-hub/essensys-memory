---
type: Architecture Overview
title: Armoire Architecture
description: "Vue OKF de l'architecture armoire ESSENSYS : cartes, firmware, table d'échange et protocoles."
tags: [essensys, architecture, armoire, firmware, legacy]
timestamp: 2026-06-28T19:07:32Z
---
<!-- BEGIN GENERATED CONTENT -->
# Vue d'ensemble

L'armoire ESSENSYS combine une carte maître, des cartes actionneurs, une IHM, des modules alarme/détection et des bancs de test. Elle dialogue avec les couches serveur par [Legacy HTTP](/protocols/legacy-http.md) et partage son état via [Table D Echange](/protocols/table-d-echange.md).

# Cartes

* [SC944D](/firmware/sc944d.md)
* [SC940](/firmware/sc940.md)
* [SC941C](/firmware/sc941c.md)
* [SC942C](/firmware/sc942c.md)
* [SC945D](/firmware/sc945d.md)
* [SC946D](/firmware/sc946d.md)
* [SC947-xB](/firmware/sc947-xb.md)
* [SC840B](/firmware/sc840b.md)
* [SC841A](/firmware/sc841a.md)
* [SC843D](/firmware/sc843d.md)

# Flux architecture

```text
Utilisateur / portail → backend LAN/cloud → pending actions → Legacy HTTP → SC944D / armoire → Table d'Échange → cartes + IHM
```

# Contraintes

* Préserver les endpoints legacy et le format attendu par firmware.
* Vérifier les index table d'échange avant changement métier.
* Synchroniser les backends twins et UI twins pour éviter les dérives LAN/cloud.

# Citations

[1] [Platform Overview wiki](../../wiki/synthesis/platform-overview.md)
[2] [Table D Echange wiki](../../wiki/concepts/table-d-echange.md)
<!-- END GENERATED CONTENT -->
