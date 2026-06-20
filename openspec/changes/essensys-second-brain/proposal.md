## Why

Essensys repose sur **40 dépôts Git**, du firmware legacy (ColdFire/MQX, PIC) à la stack Go/React cloud, avec une migration en cours documentée de façon fragmentée. Les agents IA et les développeurs perdent du contexte entre sessions : roadmaps, décisions OpenSpec, historique de commits et contrats protocolaires (table d'échange, dual-protocol) ne sont pas centralisés. `essensys-memory` doit devenir la **mémoire persistante** du projet — lisible par humains (Obsidian) et par LLM (Cursor, Claude Code, Codex) — pour piloter les roadmaps et accélérer les développements.

## What Changes

- **Vault Obsidian LLM Wiki** dans `essensys-memory` : structure `raw/` (sources immuables) + `wiki/` (connaissances structurées) + `output/` (rapports).
- **OpenSpec comme moteur de roadmap** : chaque évolution significative = change OpenSpec ; le wiki reflète l'état `proposal → design → specs → tasks → done`.
- **Pipeline d'ingestion** : scripts pour synchroniser `docs/architecture/`, les changes OpenSpec dispersés, et extraire l'historique Git daté de chaque dépôt ESSENSYS.
- **Pages wiki initiales** : plateforme, 40 dépôts, concepts clés (dual-protocol, table d'échange, migration), timeline par repo.
- **Règles de maintenance** : obligation de mettre à jour le brain à chaque change OpenSpec, merge significatif ou décision d'architecture ; règles Cursor/AGENTS dans le monorepo ESSENSYS.
- **Intégration MCP future** : préparation du couplage avec `essensys-mcp` (hors scope implémentation immédiate).

## Capabilities

### New Capabilities

- `wiki-vault-structure`: Arborescence, conventions de nommage, frontmatter et wikilinks pour le vault ESSENSYS-BRAIN.
- `source-sync`: Synchronisation automatique des docs d'architecture et des sources OpenSpec vers `raw/`.
- `git-timeline`: Extraction et publication de l'historique Git (auteur, date, message, hash) par dépôt dans `wiki/timeline/`.
- `openspec-roadmap`: Index wiki des changes OpenSpec (statut, dates, liens vers specs) et procédure de mise à jour.
- `ingest-workflow`: Workflow agent `/second-brain-ingest` adapté ESSENSYS (code + doc → pages entities/concepts/sources).
- `dev-maintainability`: Règles obligatoires pour les développeurs et agents IA de tenir le brain à jour.

### Modified Capabilities

*(aucune — premier change OpenSpec dans ce dépôt)*

## Impact

- **Dépôt `essensys-memory`** : passe de stub à vault actif (Obsidian + OpenSpec + scripts).
- **Monorepo ESSENSYS** : nouvelle règle Cursor à la racine ; les devs doivent référencer le brain dans les PR/changes.
- **Dépôts avec OpenSpec existants** : `essensys-raspberry-gateway/openspec/changes/*` référencés par le brain (pas déplacés).
- **Agents IA** : `essensys-mcp` consommera ce vault à terme ; pas de modification MCP dans ce change.
- **CI** : option future — hook post-merge pour regénérer timeline (hors scope Phase 1).
