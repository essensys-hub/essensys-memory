---
tags: [concept, documentation, governance]
sources: [essensys-second-brain, AGENTS.md, WORKFLOW.md]
created: 2026-06-21
updated: 2026-06-21
era: modern
---

# Centralized Documentation

Gouvernance de la **documentation centralisée** : le brain (`essensys-memory`) synthétise ; les dépôts gardent la doc opérationnelle.

## Principe

| Couche | Rôle | Exemple |
|--------|------|---------|
| **Dépôt** | How-to run, API locale, README | `essensys-server-backend/docs/` |
| **raw/** (brain) | Copie sync immuable | `raw/architecture/`, `raw/protocol/` |
| **wiki/** (brain) | Entités, concepts, synthèses | [[Platform Overview]], [[Gateway Exchange]] |
| **OpenSpec** | Roadmap exécutable | `openspec/changes/` |

## Règle agent

Fichier monorepo : `.cursor/rules/essensys-centralized-doc.mdc`

## Cartographie (extrait)

| Changement | Dépôt(s) | Mettre à jour |
|------------|----------|---------------|
| API / protocole domotique | server-backend, portal-backend | [[Gateway Exchange]], [[Dual Protocol]] si contrat ; rules jumeaux |
| Indices k/v | idem + firmware ref | [[Table D Echange]], `raw/protocol/` via sync |
| UI domotique | server-frontend, portal-frontend | rules jumeaux ; wiki si nouveau concept UX |
| Nouveau OpenSpec | hôte + memory | `update-roadmap.sh`, page `wiki/roadmap/changes/` |
| Architecture dépôt | `docs/architecture/` | sync-sources + entité `wiki/entities/` |
| Doc publique users | `essensys-doc`, ansible install | [[User Documentation Site]], change [[Essensys Doc Site]] |
| Sécurité gateway cloud | backend + ansible | [[Gateway PKI]], concept concerné |

## Triggers obligatoires

1. Nouveau change OpenSpec → sync roadmap + log  
2. Merge protocole legacy / table d'échange → concepts + raw  
3. Décision architecture → `wiki/synthesis/` ou `wiki/concepts/`  
4. Nouveau dépôt → entité wiki + architecture README  

## Checklist PR

```markdown
- [ ] Doc/brain updated per essensys-centralized-doc.mdc (or N/A)
```

## Voir aussi

- [[Product Roadmap Rubric]] — Phase 0a
- [[Essensys Centralized Doc Maintenance]]
- `essensys-memory/docs/WORKFLOW.md`
