---
tags: [entity, repo, process, security, ci]
sources: [essensys-feature-lifecycle.md, essensys-feature-lifecycle/README.md]
created: 2026-06-26
updated: 2026-06-26
era: modern
repo: essensys-feature-lifecycle
---

# Essensys Feature Lifecycle

> Dépôt **source de vérité** du cycle de vie feature Git-first Essensys : skills, rules Cursor, gates CI, manifestes `features/*.json`, orchestration IA/subagents et intégration **Jira SCRUM**.

| | |
|---|---|
| **Catégorie** | Outillage process / CI / agents |
| **Stack** | GitHub Actions, gitleaks, Trivy, Dependabot, Python 3.11, JSON Schema, OpenSpec |
| **Statut** | Actif — bootstrap déployé sur les 4 dépôts domotique (2026-06-26) |
| **Era** | modern |

## Rôle

Modélise le process Essensys de bout en bout :

```
Idée → Jira (SCRUM) → OpenSpec → tasks Jira → Code → Tests → Gate sécurité → Deploy (local + OVH)
```

Trois exigences non négociables : **sécurité** (bloquant), **open source** (toolchain gates), **traçabilité** (Git + Jira + brain).

## Artefacts clés

| Artefact | Chemin |
|----------|--------|
| Manifest feature | `features/<id>.json` (JSON Schema) |
| Gate feature | `.github/workflows/feature-gate.yml` |
| Gate sécurité | `.github/workflows/security-gate.yml` |
| Bootstrap skill | `.cursor/skills/feature-lifecycle-bootstrap/` |
| Post Jira scan | `scripts/feature_lifecycle/post_security_gate_to_jira.py` |
| Install skills | `scripts/install-skills.sh` |

## Gate sécurité (open source, bloquant)

- **gitleaks** — secrets (jamais mutés ; rotation + scrub)
- **Trivy** — CVE dépendances + misconfig Dockerfile/IaC
- **Dependabot** — alertes GitHub natives
- GitGuardian : optionnel (`gitguardian_token` SOPS), non bloquant dans le gate

## Bootstrap (2026-06-26)

| Dépôt | Branche | Notes |
|-------|---------|-------|
| [[Essensys Server Backend]] | `V.1.3.0` | PR #5–#7 : gitleaks, npm, tests Go |
| [[Essensys Server Frontend]] | `V.1.3.0` | PR #2–#4 : react-router, Dockerfile, gitleaks |
| [[Essensys User Portal Backend]] | `main` | bootstrap gates + scripts |
| [[Essensys User Portal Frontend]] | `main` | bootstrap gates + scripts |

## Liens

- [[Feature Lifecycle]] — concept process
- [[Security Gate]] — politique CVE/secrets
- [[Secrets Management]] — `JIRA_SECRET`, `gitguardian_token`
- [[Essensys Memory]] — mise à jour continue du brain
- [[Roadmap OpenSpec]] — changes produit

## Source

`raw/architecture/repos/essensys-feature-lifecycle.md`
