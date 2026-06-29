---
type: Process
title: ESSENSYS OKF Memory Sync
description: Gate obligatoire qui force la mise à jour wiki/OKF de essensys-memory après toute modification d'un dépôt essensys-hub.
tags: [essensys, okf, memory, process, rule, skill]
timestamp: 2026-06-28T06:52:22Z
resource: file:///Users/nrineau/ESSENSYS/.cursor/rules/essensys-okf-memory-sync.mdc
---

# Rôle

ESSENSYS OKF Memory Sync est le mécanisme de discipline documentaire qui rend `essensys-memory` obligatoire dès qu'un dépôt `essensys-hub` est touché. Il combine un skill agent et une rule Cursor pour empêcher qu'un changement code/protocole/UI/déploiement soit considéré comme terminé sans mise à jour de la mémoire.

# Déclencheurs

* Modification, review, commit, merge ou PR sur un dépôt sous `/Users/nrineau/ESSENSYS`.
* Changement firmware, SC944D, armoire, table d'échange, protocole legacy HTTP ou indices k/v.
* Changement des twins frontend/backend LAN/cloud.
* Changement gateway, OVH/cloud, support site, docs site, roadmap site, install/deploy/Ansible.
* Création, application ou archivage OpenSpec.

# Commandes de synchronisation

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

Si OpenSpec change :

```bash
openspec validate <change-name> --strict
```

# Artefacts

* Skill Cursor : `/.cursor/skills/essensys-okf-memory-sync/SKILL.md`.
* Skill Hermes local : `~/.hermes/skills/essensys-feature-lifecycle/essensys-okf-memory-sync/SKILL.md`.
* Rule Cursor : `/.cursor/rules/essensys-okf-memory-sync.mdc`.
* Référence workspace Hermes : `/.hermes.md`.

# Done criteria

Un travail ESSENSYS n'est terminé que si les tests pertinents sont traités, la mémoire est synchronisée, OKF valide, OpenSpec valide si applicable, et `git status --short` inspecté.

# Citations

[1] Cursor skill: `file:///Users/nrineau/ESSENSYS/.cursor/skills/essensys-okf-memory-sync/SKILL.md`
[2] Cursor rule: `file:///Users/nrineau/ESSENSYS/.cursor/rules/essensys-okf-memory-sync.mdc`
[3] Workspace Hermes context: `file:///Users/nrineau/ESSENSYS/.hermes.md`
