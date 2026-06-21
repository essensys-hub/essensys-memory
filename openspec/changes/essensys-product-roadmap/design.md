## Context

Trois niveaux de roadmap coexistent :

| Niveau | Fichier | Rôle |
|--------|---------|------|
| Technique OpenSpec | `wiki/roadmap/index.md` | Index des changes (auto sync) |
| Rubrique produit | `wiki/roadmap/product-roadmap-rubric.md` | **Comment** découper et ordonner |
| Priorités vivantes | `wiki/synthesis/product-roadmap.md` | **Quoi** Now / Next / Later |

## Décisions

1. **Phase 0 bloquante** : doc centralisée + doc install (rules) avant epics feature.
2. **1 epic produit = 1 change OpenSpec** (≤ ~2 semaines dev idéal) ; pas de méga-change.
3. **Hôte du change** : dépôt concerné ; changes **cadre** dans `essensys-memory`.
4. **Revues roadmap** : mettre à jour `product-roadmap.md` quand un change passe active → completed.

## Découpage type d’un epic feature

```
proposal.md   → pourquoi + lien product-roadmap Now/Next
design.md     → décisions + contraintes legacy/jumeaux
specs/*.md    → exigences testables
tasks.md      → checklist dev + tâche brain obligatoire
```

## Phases rubrique

| Phase | Changes | Statut gate |
|-------|---------|-------------|
| **0** | centralized-doc-maintenance, install-doc-platform | Obligatoire |
| **1** | product-roadmap (ce change) | Rubrique + living doc |
| **2+** | mTLS, trusted-devices, wizard, IAM LAN, … | Un change par ligne matrice gap |

## Risques

- Rubrique ignorée si non liée dans `AGENTS.md` et prompt — mitiger par rules Phase 0.
