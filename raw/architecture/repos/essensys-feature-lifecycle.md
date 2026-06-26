# essensys-feature-lifecycle

Dépôt source de vérité du **cycle de vie feature Git-first** Essensys : skills Cursor, rules, workflows CI (feature-gate, security-gate), hooks pre-commit, schéma JSON des manifestes `features/<id>.json`, scripts Python (validation, Trivy/gitleaks summary, publication Jira).

## Rôle

- Centralise le **process produit** : Jira SCRUM → OpenSpec → code → tests → gate sécurité (open source) → deploy local + OVH → mémoire `essensys-memory`.
- Skill **`feature-lifecycle-bootstrap`** : déploie gates, scripts et rules dans les dépôts applicatifs (`essensys-server-*`, `essensys-user-portal-*`).
- **`scripts/install-skills.sh`** : installation open source des skills dans `~/.cursor/skills` ou `.cursor/skills`.

## Stack

- GitHub Actions : `feature-gate.yml`, `security-gate.yml` (gitleaks + Trivy CVE/IaC + Dependabot)
- Python 3.11+ : `summarize_security_gate.py`, `post_security_gate_to_jira.py`, `validate_feature_manifests.py`
- Pas d'outil propriétaire bloquant ; GitGuardian optionnel (dashboard secrets, token SOPS `gitguardian_token`)

## Intégrations

- **Jira** projet SCRUM (`JIRA_SECRET` dans SOPS) — backlog, sous-tâches remediation security-gate
- **essensys-memory** — doc continue, brain ingest
- Dépôts bootstrappés (2026-06-26) : server-backend/frontend `V.1.3.0`, portal-backend/frontend `main`

## Liens

- Repo : `github.com/essensys-hub/essensys-feature-lifecycle`
- Doc : `docs/feature-lifecycle/`, `AGENTS.md`
