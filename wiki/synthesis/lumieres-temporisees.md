---
tags: [synthesis, feature, domotique, lumieres, table-echange]
sources: [TableEchange.h, essensys-board-SC942C.md]
created: 2026-11-07
updated: 2026-11-07
---

# Lumieres Temporisees

> Feature `lumieres-temporisees-2026-11-003` (ticket essensys-hub/essensys-feature-lifecycle#45) : régler depuis les portails et les apps le délai d'extinction automatique de six lumières, jusque-là réglable seulement sur l'écran de l'armoire.

## Constat

L'armoire éteint déjà certaines lumières après un délai : le BP le garde dans la [[Table D Echange]] (cases 518, 534, 550) et le boîtier en EEPROM ([[Essensys Board Sc942c]]). Seul l'écran tactile le règle (15 min, 30 min, 1 h, Jamais). La doc de maintenance ne citait que 555 à 557 et donnait PDV/CHB « non utilisé » ; elle est corrigée.

## Ce qui change

- **Six lumières** : Dressing 521, WC 1 555, WC 2 556, Service 557, Annexe 1 561, Annexe 2 562. Valeur : 0 à 255 minutes, 0 = jamais ; le boîtier applique `minutes × 60 × 0,994` secondes.
- **Routes dédiées**, validées et réservées à l'administrateur de l'armoire : cloud `GET /portal/lights/timers` et `PUT /portal/admin/lights/timers/{id}` ([[Essensys User Portal Backend]]), gateway `GET` et `PUT /api/admin/lights/timers/{id}` ([[Essensys Server Backend]]). `minutes` vaut `null` si la valeur n'a jamais été lue.
- **Clients** : menu « Temporisations » et réglage dans la fiche de chaque lumière sur le portail cloud ([[Essensys User Portal Frontend]]), le portail local ([[Essensys Server Frontend]]) et les apps ([[Essensys Android Phone Apps]], [[Essensys IOS Phone Apps]]). Raccourcis 15 min, 30 min, 1 h, Jamais, plus une valeur libre de 1 à 255.
- **Aucun changement** du firmware, de l'écran ni des endpoints legacy (`serverinfos`, `mystatus`, `myactions`, `done`). Le Pi 4 n'a rien à changer : les routes font partie du binaire du backend ([[Essensys Raspberry Install]]).

## Risques ouverts

- Une valeur libre (7 min) n'est cochée sur aucune case de l'écran, qui pourrait l'écraser à la validation : test banc obligatoire, jamais sur une armoire réelle.
- Les clés 561 et 562 et le bloc PDV sont marqués « non utilisé » dans le BP alors que le code du boîtier les applique : à confirmer au banc.
- Version du BP en production non comparée à la 099-37.

## Suivi

Process : [[Feature Lifecycle]]. Doc publique : page « Régler l'extinction automatique des lumières » ([[Essensys DOC]]).
