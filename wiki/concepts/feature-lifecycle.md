---
tags: [concept, process, jira, openspec, ci]
sources: [essensys-feature-lifecycle/AGENTS.md, essensys-feature-lifecycle/README.md]
created: 2026-06-26
updated: 2026-06-26
era: modern
---

# Feature Lifecycle

Process **Git-first** et orchestration IA pour les features Essensys. Canon : dépôt [[Essensys Feature Lifecycle]].

## Backlog & traçabilité

| Outil | Usage |
|-------|--------|
| **Jira SCRUM** | Backlog unique — <https://essensys-hub.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog> |
| **OpenSpec** | Specs par change (`openspec-propose` → design, specs, tasks) |
| **Git** | Code, PR, gates CI |
| **essensys-memory** | Brain persistant (ce vault) |

> GitHub Projects n'est plus utilisé pour le pilotage produit.

## Flux standard

1. Idée / epic → ticket Jira
2. Change OpenSpec dans le dépôt concerné (ou brain pour changes transverses)
3. Implémentation + tests (Playwright UI, `go test`, scripts `test/`)
4. **[[Security Gate]]** sur PR (bloquant)
5. Deploy **local** (gateway CM5 via [[Essensys Ansible]]) **et** **OVH** (`deploy-portal-stack.yml`, `support-site.yml`)
6. Mise à jour doc + [[Essensys Memory]]

## Manifest feature

Chaque feature versionnée :

```text
features/<id>.json   ← validé par features/schema/feature.schema.json
```

Consommé par `feature-gate.yml` (CI) et skill `feature-manifest-orchestrator`.

## Subagents & remediation

Le script `post_security_gate_to_jira.py` crée un ticket parent + sous-tâches Jira avec contexte complet (Trivy, gitleaks, commandes de fix) pour délégation à des subagents.

Exemple session 2026-06-26 : SCRUM-1…SCRUM-16 (security gate backend/frontend, deploy, infra Docker CM5).

## Liens

- [[Security Gate]]
- [[Centralized Documentation]]
- [[Product Roadmap Rubric]] — Phase 0 doc avant epics feature
