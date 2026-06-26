---
tags: [concept, security, ci, trivy, gitleaks]
sources: [essensys-feature-lifecycle/.cursor/rules/security-gate.mdc, essensys-feature-lifecycle/AGENTS.md]
created: 2026-06-26
updated: 2026-06-26
era: modern
---

# Security Gate

Politique **bloquante** sur les PR des dépôts Essensys bootstrappés via [[Essensys Feature Lifecycle]].

## Stack open source (obligatoire)

| Outil | Rôle | Bloquant |
|-------|------|----------|
| **gitleaks** | Secrets dans le code | Oui — jamais muter ; rotation + allowlist documentée |
| **Trivy** | CVE deps (Go, npm, pip) + misconfig Dockerfile/IaC | Oui — Critical/High |
| **Dependabot** | Alertes dépendances GitHub | Intégré au résumé gate |

**Pas de scanner propriétaire bloquant.** GitGuardian (`gitguardian_token` SOPS) = dashboard secrets optionnel, `ggshield` usage local non bloquant.

## Workflow CI

Fichier : `.github/workflows/security-gate.yml`  
Artifacts : `.artifacts/security-gate/{gitleaks,trivy,summary}.json`  
Script agrégateur : `scripts/feature_lifecycle/summarize_security_gate.py`

Publication Jira : `post_security_gate_to_jira.py` (`JIRA_SECRET` SOPS).

## Remédiation CVE — session 2026-06-26

### [[Essensys Server Backend]] `V.1.3.0`

| PR | Contenu |
|----|---------|
| #2 | Bump dépendances Go (CVE Trivy) |
| #3 | axios / form-data `simulation/ui` |
| #4 | Dockerfile non-root (Trivy DS-0002) |
| #5 | `.gitleaks.toml` allowlist doc (SCRUM-8) |
| #6 | npm résiduel `simulation/ui` (10→0 vulns) |
| #7 | Compilation tests Go (SCRUM-9) |

### [[Essensys Server Frontend]] `V.1.3.0`

| PR | Contenu |
|----|---------|
| #2 | `react-router` 7.11 → 7.18 (6 CVE HIGH) |
| #3 | Dockerfile runtime non-root (DS-0002) |
| #4 | gitleaks allowlist artefacts design-system (`.design-sync/`, `ds-bundle/`) |

### Portail

[[Essensys User Portal Backend]] et [[Essensys User Portal Frontend]] : gate **vert** au premier scan (bootstrap `main`, 2026-06-26).

## Allowlist gitleaks

Faux positifs uniquement, path-scoped, commentaire + ticket Jira. Exemples :

- Doc backend : `test/README_TEST_CLIENT.md`, `.kiro/specs/.../design.md`
- Frontend : hash `sourceKey` dans artefacts générés design-system

## Liens

- [[Feature Lifecycle]]
- [[Secrets Management]]
