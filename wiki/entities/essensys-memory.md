---
tags: [entity, repo, modern, tooling]
sources: [essensys-memory.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-memory
---

# Essensys Memory

> Dépôt prévu pour fournir une mémoire persistante aux agents IA d'Essensys, actuellement réduit à un README d'une ligne.

| | |
|---|---|
| **Catégorie** | Outillage / IA |
| **Stack** | Indéterminée (aucun code ni manifeste présent) |
| **Statut** | Stub — dépôt à l'état de squelette, non implémenté |
| **Era** | modern |

## Rôle

D'après son nom, ce dépôt doit fournir une **couche de mémoire pour agents IA** : stockage et rappel de contexte, faits, historiques de conversation ou état long terme, en complément du serveur `essensys-mcp`. Il appartient à la famille « Outillage / IA » du projet.

Le périmètre exact (mémoire vectorielle, base clé/valeur, RAG, etc.) **n'est pas documenté** dans le dépôt.

## Intégrations

Aucune intégration implémentée. Couplage *attendu* (hypothèse) : fournir la mémoire consommée par le serveur `essensys-mcp` et les agents IA. La plateforme utilisant déjà Redis (cf. `essensys-utils`), Redis pourrait être un candidat naturel de backend, mais ce n'est pas confirmé.

## Structure

```
.
├── .git/
└── README.md   # contenu : "# essensys-memory" (une seule ligne)
```

Historique Git limité à un unique commit `first commit` (0f99f30).

## Points d'attention

- **Dépôt stub** : ne contient qu'un titre, aucune fonctionnalité.
- Remote : `git@github.com:essensys-hub/essensys-memory.git`.
- À cadrer conjointement avec `essensys-mcp` (le serveur MCP et sa mémoire forment vraisemblablement un couple).

## Liens

- [[Roadmap OpenSpec]]
- [[Essensys Second Brain]]

## Source

`raw/architecture/repos/essensys-memory.md`
