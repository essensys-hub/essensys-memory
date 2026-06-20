---
tags: [entity, repo, legacy]
sources: [essensys-api-doc.md]
created: 2026-06-20
updated: 2026-06-20
era: legacy
repo: essensys-api-doc
---

# Essensys API DOC

> Documentation de l'API legacy Essensys (protocole HTTP du firmware ↔ serveur `mon.essensys.fr`), publiée sous forme de site MkDocs Material bilingue FR/EN.

| | |
|---|---|
| **Catégorie** | Documentation / Site |
| **Stack** | MkDocs + thème Material, plugins i18n (FR/EN) + Mermaid2, Python 3.9, GitHub Pages |
| **Statut** | Actif — publié sur `https://rhinosys.github.io/essensys-api-doc/` (remote `github.com/rhinosys/essensys-api-doc`, branche `main`) |
| **Era** | legacy |

## Rôle

Ce dépôt documente l'**API/protocole legacy** par lequel le contrôleur embarqué BP_MQX_ETH dialogue avec le serveur Essensys d'origine. Il sert de référence de rétro-ingénierie : c'est la spécification à partir de laquelle le backend moderne (gateway / Anti-Corruption Layer) doit reproduire une compatibilité 100 % avec le protocole legacy. Il documente aussi la **table de référence des indices** (clés/valeurs) pilotant les domaines fonctionnels (chauffage, cumulus, arrosage, prises de sécurité…).

## Intégrations

- Référence directe pour `essensys-server-backend` / gateway lors de l'implémentation de l'ACL (compatibilité protocole legacy).
- Le `reference.json` et la table d'indices sont cohérents avec la `exchange-table` documentée dans `essensys-doc` (mêmes indices, ex. cumulus, chauffage).
- Captures Wireshark exploitables pour rejouer/valider les échanges legacy.

## Structure

_Voir dépôt source._

## Points d'attention

- Hébergé sous l'organisation **`rhinosys`** et non `essensys-hub` (les autres dépôts doc/site sont sous `essensys-hub`) — incohérence d'organisation à surveiller.
- Documentation rédigée manuellement : pas de spec machine-readable type OpenAPI → risque de désynchronisation avec le code et pas de validation automatique de schéma.
- Plusieurs pages portent la mention « Keys inconnue » / « Undef » : rétro-ingénierie **incomplète**, certains indices restent non documentés.
- Petites incohérences de formatage dans les tables Markdown (séparateurs `|` manquants sur certaines lignes de `specification.fr.md`).
- Workflow CI épinglé sur des actions anciennes (`actions/checkout@v2`, `setup-python@v2`, Python 3.9).

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-api-doc.md`
