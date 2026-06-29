# Tasks — essensys-okf-discovery-2026-06-029

> Objectif : lancer un discovery complet des savoirs ESSENSYS et les publier dans la base OKF `okf/`, avec priorité sur armoire, table d'échange, protocole legacy HTTP, roadmap et portails 2025/2026.

## Phase 0 — Préparation et garde-fous

- [x] 0.1 Exécuter `scripts/sync-sources.sh`, `scripts/extract-git-history.sh`, et `scripts/update-roadmap.sh` si l'état de travail permet de ne pas écraser de modifications humaines.
- [x] 0.2 Capturer l'inventaire initial des dépôts Git sous `/Users/nrineau/ESSENSYS`.
- [x] 0.3 Définir les règles anti-secrets : ne pas lire/imprimer `.env`, secrets SOPS déchiffrés, tokens ou credentials.
- [x] 0.4 Définir la taxonomie OKF : `systems`, `firmware`, `protocols`, `roadmap`, `portals`, `processes`, `synthesis`, `references`.

## Phase 1 — Scripts discovery et validation

- [x] 1.1 Créer `scripts/okf/discover_repositories.py` pour inventorier les dépôts, README, docs, manifests, OpenSpec et fichiers de protocole connus.
- [x] 1.2 Créer `scripts/okf/generate_okf.py` ou équivalent pour générer/mettre à jour les concepts OKF à partir du wiki et des sources Git.
- [x] 1.3 Créer `scripts/okf/validate_okf.py` pour vérifier frontmatter, champ `type`, index/log, liens locaux et citations relatives.
- [x] 1.4 Créer `scripts/okf/report_coverage.py` pour produire `output/okf-discovery-coverage-YYYY-MM-DD.md`.
- [x] 1.5 Ajouter une règle de régénération sûre : préserver les champs inconnus et sections curées autant que possible.

## Phase 2 — Discovery tous dépôts ESSENSYS

- [x] 2.1 Générer une fiche OKF par dépôt ESSENSYS local ou documenter explicitement les exceptions.
- [x] 2.2 Classer chaque dépôt par couche : firmware/armoire, gateway-LAN, cloud, infra, documentation, tooling, MCP, memory, legacy.
- [x] 2.3 Ajouter les relations critiques : UI twins, backend twins, gateway ↔ cloud, firmware ↔ backend, portail ↔ API.
- [x] 2.4 Ajouter `# Code pointers` sans dupliquer de code source complet.
- [x] 2.5 Vérifier que tous les dépôts listés dans l'inventaire apparaissent dans le rapport de couverture.

## Phase 3 — Focus armoire ESSENSYS

- [x] 3.1 Générer les concepts OKF firmware/cartes : SC944D, SC940, SC941C, SC942C, SC945D, SC946D, SC947-xB, SC840, SC841, SC843D.
- [x] 3.2 Créer une synthèse `okf/synthesis/armoire-architecture.md` reliant cartes, firmware, passerelle et backends.
- [x] 3.3 Ajouter les contraintes embarquées et legacy : temps réel, compatibilité firmware, écran IHM, actionneurs, alarmes.
- [x] 3.4 Citer les sources wiki et code pointers firmware pertinents.

## Phase 4 — Table d'échange et protocole legacy HTTP

- [x] 4.1 Générer/enrichir `okf/protocols/table-d-echange.md` avec indices 590, 591-919, 605-622, 409-411, 566-589.
- [x] 4.2 Documenter règles d'action : `_de67f` en premier, bloc complet 605-622 + 590=`"1"`, fusion OR bitwise, expansion scénario.
- [x] 4.3 Générer `okf/protocols/legacy-http.md` avec `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}`.
- [x] 4.4 Documenter JSON non standard, Content-Type historique, Basic Auth, AES alarm payload, single-packet TCP.
- [x] 4.5 Croiser firmware, écran, backend Go, portail cloud et frontends ; lister toute contradiction dans le rapport de couverture.

## Phase 5 — Roadmap et portails 2025/2026

- [x] 5.1 Générer les concepts OKF roadmap depuis `wiki/roadmap/index.md`, `openspec/changes/**` et `content/roadmap/site/**`.
- [x] 5.2 Identifier explicitement les éléments 2025 et 2026 ; marquer `TBD` quand la date n'est pas sourcée.
- [x] 5.3 Générer le catalogue OKF des portails : LAN local, cloud `mon.essensys.fr`, support site, documentation, roadmap site, admin/utilisateur, gateway install/control.
- [x] 5.4 Relier chaque portail aux dépôts, APIs, auth/security gates, déploiements local/OVH et roadmap items.
- [x] 5.5 Vérifier que les portails déployés/prévus ne sont pas décrits sans citation.

## Phase 6 — Indexation, logs, wiki et rapport

- [x] 6.1 Mettre à jour `okf/index.md` et tous les index de sous-dossiers.
- [x] 6.2 Ajouter une entrée datée dans `okf/log.md`.
- [x] 6.3 Créer/mettre à jour les pages wiki nécessaires et maintenir `wiki/index.md` + `wiki/log.md`.
- [x] 6.4 Générer `output/okf-discovery-coverage-YYYY-MM-DD.md` avec couverture, gaps, contradictions et next steps.
- [x] 6.5 Exécuter validation OKF et corriger tous les échecs.

## Phase 7 — Vérification finale

- [x] 7.1 `python3 scripts/okf/validate_okf.py okf`
- [x] 7.2 `openspec validate essensys-okf-discovery-2026-06-029 --strict`
- [x] 7.3 `git status --short` pour isoler les fichiers modifiés par la change.
- [x] 7.4 Résumer le coverage : nombre de dépôts couverts, concepts OKF créés/mis à jour, gaps restants.
