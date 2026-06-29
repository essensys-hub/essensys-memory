---
tags: [concept, okf, knowledge-format, markdown, interoperability]
sources: [https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md]
created: 2026-06-28
updated: 2026-06-28
era: modern
---

# Open Knowledge Format

Open Knowledge Format (OKF) est un format ouvert pour représenter une mémoire de connaissance lisible par humains et agents : un répertoire de fichiers Markdown UTF-8 avec frontmatter YAML.

## Règles essentielles

- Un bundle OKF est une arborescence de fichiers `.md`.
- Chaque document concept non réservé doit contenir un frontmatter YAML parseable.
- Le champ `type` est obligatoire dans chaque concept.
- `index.md` est réservé à la découverte progressive.
- `log.md` est réservé à l'historique chronologique des mises à jour.
- Les liens internes sont des liens Markdown standard, de préférence relatifs à la racine du bundle.
- Les citations sont listées sous `# Citations` quand un concept s'appuie sur des sources externes.

## Application ESSENSYS

Le bundle OKF initial est créé dans `okf/` et référence les concepts structurants du brain : [[Essensys Memory]], [[Platform Overview]], [[Feature Lifecycle]] et [[Dual Protocol]].

L'objectif est de garder une couche échangeable et agent-friendly sans remplacer le wiki existant : le wiki reste l'espace de travail Obsidian, tandis que `okf/` devient le format de distribution et d'interopérabilité.

## Liens

- [[Essensys Memory]]
- [[Platform Overview]]
- [[Feature Lifecycle]]
- [[Dual Protocol]]

## Source

- <https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md>
