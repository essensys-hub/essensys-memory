# Workflow OpenSpec + ESSENSYS-BRAIN

Guide pour les développeurs et agents IA : comment proposer, implémenter et documenter une évolution Essensys.

## Vue d'ensemble

```
Idée → OpenSpec change → Implémentation → Mise à jour brain → Archive OpenSpec
         (dépôt hôte)      (code + tests)    (essensys-memory)
```

## 1. Proposer un change OpenSpec

Dans le **dépôt concerné** (ex. `essensys-raspberry-gateway`) :

```bash
openspec new change "my-feature-name"
# ou skill Cursor: /openspec-propose
```

Artefacts générés : `proposal.md` → `design.md` → `specs/**` → `tasks.md`

Changes **brain** : uniquement dans `essensys-memory/openspec/changes/`.

## 2. Implémenter

```bash
openspec status --change "my-feature-name"
# Suivre tasks.md, cocher les tâches
go test ./...   # backends
npm run lint    # frontends
```

Règles jumeaux :
- UI : `essensys-server-frontend` ↔ `essensys-user-portal-frontend`
- Backend : `essensys-server-backend` ↔ `essensys-user-portal-backend`

## 3. Mettre à jour le brain (obligatoire si…)

| Déclencheur | Action |
|-------------|--------|
| Nouveau change OpenSpec | `refresh-all.sh` + page roadmap |
| Merge protocole legacy / table d'échange | Mettre à jour [[Dual Protocol]], [[Table D Echange]] |
| Nouveau dépôt | Ingest fiche → `wiki/entities/` |
| Décision architecture | Page `wiki/synthesis/` ou concept |

```bash
cd essensys-memory
ESSENSYS_ROOT=/Users/nrineau/ESSENSYS ./scripts/refresh-all.sh
# Ingest sémantique manuel si besoin :
# /second-brain-ingest
python3 scripts/lint-wiki.py
```

## 4. Archiver un change terminé

Quand `tasks.md` est entièrement coché :

```bash
openspec archive change "my-feature-name"   # selon version CLI
./scripts/update-roadmap.sh               # statut → completed
```

## 5. Interroger le brain (agents)

| Méthode | Usage |
|---------|-------|
| Obsidian | Ouvrir vault, naviguer wikilinks |
| `/second-brain-query` | Cursor skill |
| `qmd query -c essensys-brain "…"` | Recherche locale |
| `essensys-mcp` `brain_search` | MCP tool |
| `brain_get_page` | Page précise |

## 6. Automatisation

| Mécanisme | Quand |
|-----------|-------|
| `./scripts/install-git-hook.sh` | post-merge → timeline locale |
| `.github/workflows/brain-sync.yml` | push main + hebdo |
| `./scripts/refresh-all.sh` | refresh manuel complet |

## Checklist PR

```markdown
- [ ] Tests passent (dépôt(s) modifié(s))
- [ ] Jumeaux sync si UI/backend domotique
- [ ] Brain updated (essensys-memory) ou N/A
- [ ] OpenSpec tasks cochées si change en cours
```

## Références

- Change brain : `openspec/changes/essensys-second-brain/`
- Règle Cursor monorepo : `.cursor/rules/essensys-brain.mdc`
- Protocole legacy : `raw/protocol/http-legacy-protocol.md`
