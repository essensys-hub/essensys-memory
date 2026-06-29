---
type: Reference
title: Open Knowledge Format
description: Spécification OKF v0.1 utilisée pour structurer la mémoire ESSENSYS en markdown + frontmatter YAML.
resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
tags: [okf, knowledge-format, markdown, yaml, interoperability]
timestamp: 2026-06-28T06:11:17Z
---

# Objet

Open Knowledge Format (OKF) est un format ouvert, lisible par humains et agents, pour représenter de la connaissance sous forme d'un répertoire de fichiers markdown avec frontmatter YAML.

# Règles appliquées dans ce bundle

* Le bundle est un arbre de fichiers markdown sous `/okf/`.
* Les fichiers réservés `index.md` et `log.md` servent respectivement à la découverte progressive et à l'historique.
* Chaque document concept non réservé a un frontmatter YAML parseable.
* Chaque frontmatter contient un champ `type` non vide.
* Les liens internes entre concepts utilisent des liens markdown standards, préférentiellement bundle-relative.
* Les citations externes sont listées sous une section `# Citations`.

# Conformance visée

Ce bundle cible OKF v0.1 et déclare `okf_version: "0.1"` dans l'index racine, qui est l'unique `index.md` autorisé à porter ce frontmatter de version selon la spécification.

# Citations

[1] [Open Knowledge Format v0.1 draft](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
