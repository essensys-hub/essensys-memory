---
tags: [concept, okf, memory, rule, skill, process]
sources: [.cursor/skills/essensys-okf-memory-sync/SKILL.md, .cursor/rules/essensys-okf-memory-sync.mdc]
created: 2026-06-28
updated: 2026-06-28
era: modern
---

# ESSENSYS OKF Memory Sync

ESSENSYS OKF Memory Sync est une discipline de livraison qui force la mise à jour de [[Essensys Memory]] et de sa base [[Open Knowledge Format]] dès qu'un dépôt `essensys-hub` est touché.

## Déclencheurs

- Modification, review, commit, merge ou PR sur un dépôt sous `/Users/nrineau/ESSENSYS`.
- Changement firmware, [[Table D Echange]], [[Dual Protocol]], protocole legacy HTTP, indices k/v, scénarios, alarmes, lumières ou volets.
- Changement des twins UI/backend : `essensys-server-*` et `essensys-user-portal-*`.
- Changement gateway, OVH/cloud, support, documentation, roadmap, install/deploy/Ansible.
- Changement OpenSpec ou lifecycle.

## Artefacts créés

- Skill Cursor : `.cursor/skills/essensys-okf-memory-sync/SKILL.md`.
- Skill Hermes local : `~/.hermes/skills/essensys-feature-lifecycle/essensys-okf-memory-sync/SKILL.md`.
- Rule Cursor : `.cursor/rules/essensys-okf-memory-sync.mdc`.
- Référence dans `.hermes.md`.

## Commande canonique

```bash
cd /Users/nrineau/ESSENSYS/essensys-memory
./scripts/sync-sources.sh
./scripts/extract-git-history.sh
./scripts/update-roadmap.sh
python3 scripts/okf/discover_repositories.py
python3 scripts/okf/generate_okf.py
python3 scripts/okf/report_coverage.py
python3 scripts/okf/validate_okf.py okf
```

## Liens

- [[Essensys Memory]]
- [[Open Knowledge Format]]
- [[Feature Lifecycle]]
- [[Table D Echange]]
- [[Dual Protocol]]
