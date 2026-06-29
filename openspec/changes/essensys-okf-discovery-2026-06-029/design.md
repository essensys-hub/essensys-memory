## Context

`essensys-memory` contient déjà un wiki Obsidian riche et un premier bundle OKF minimal. La prochaine étape est de transformer la connaissance ESSENSYS en base OKF complète : fiches par dépôt, concepts transverses, architecture legacy, roadmap et portails. Le discovery doit être reproductible, sourcé et compatible avec les règles du brain : `raw/` immuable, wiki maintenu, OKF échangeable.

Le périmètre couvre les dépôts locaux Git ESSENSYS : firmware/cartes, gateways, backends, frontends, infra, legacy, documentation, outils, MCP et mémoire. Les savoirs existants du wiki doivent être réutilisés, mais le discovery doit aussi retourner aux sources Git quand le wiki est incomplet.

## Goals

- Constituer une base OKF complète du projet ESSENSYS, pas seulement un échantillon.
- Préserver la traçabilité source → wiki → OKF avec citations et code pointers.
- Mettre l'accent sur les zones de risque : armoire, [[Table D Echange]], [[Dual Protocol]], protocole legacy HTTP, portails 2025/2026 et roadmap.
- Rendre le résultat vérifiable par une validation OKF et un rapport de couverture.

## Non-goals

- Modifier le firmware, les backends, les frontends ou les endpoints legacy.
- Remplacer le wiki Obsidian : OKF est une couche de distribution/interopérabilité.
- Copier du code source complet dans OKF : utiliser des pointeurs de code, chemins et résumés.
- Inventer l'état d'un portail ou d'une roadmap quand la source n'est pas trouvée ; utiliser `TBD` ou signaler un gap.

## Architecture OKF cible

```text
okf/
├── index.md
├── log.md
├── systems/                 # fiches par dépôt/service/portail
├── firmware/                # cartes armoire, firmware, contraintes embarquées
├── protocols/               # table d'échange, legacy HTTP, dual protocol
├── roadmap/                 # changes OpenSpec, roadmap 2025/2026, horizons
├── portals/                 # local LAN, cloud, support, docs, roadmap site, admin/user
├── processes/               # lifecycle, security gates, install/deploy
├── synthesis/               # vues architecture et cartographies transverses
└── references/              # OKF spec et sources externes/format
```

Chaque concept OKF doit avoir :

- `type` non vide.
- `title`, `description`, `tags`, `timestamp` recommandés.
- `resource` quand un dépôt, URL, portail ou endpoint est canonique.
- Champs d'extension utiles : `repo`, `layer`, `era`, `source_wiki`, `code_pointers`, `status`, `owner` si connus.
- Corps markdown structuré avec sections stables : `# Rôle`, `# Interfaces`, `# Dépendances`, `# Code pointers`, `# Risques`, `# Citations`.

## Discovery strategy

1. Inventorier les dépôts Git sous `/Users/nrineau/ESSENSYS` et classer par couche : firmware, armoire, gateway/LAN, cloud, infra, documentation, tooling, legacy.
2. Lire les pages wiki existantes (`wiki/entities`, `wiki/concepts`, `wiki/synthesis`, `wiki/roadmap`) comme première source de synthèse.
3. Compléter depuis les sources Git quand nécessaire : README, docs, manifests, OpenSpec, fichiers constants/protocoles, packages Go, composants React, scripts Ansible.
4. Produire une fiche OKF par dépôt sous `okf/systems/` ou sous-dossier spécialisé si firmware/protocole/portail.
5. Produire des concepts transverses OKF pour les contrats critiques.
6. Générer un rapport de couverture listant : dépôts couverts, dépôts incomplets, sources manquantes, contradictions, questions ouvertes.

## Focus armoire et legacy

Le discovery doit créer ou enrichir au minimum :

- Architecture armoire complète : SC944D maître, SC940/SC941C/SC942C actionneurs, SC945D IHM, SC946D sirène, SC947-xB DFE, SC840/SC841 bancs test, SC843D gradateur.
- [[Table D Echange]] : indices critiques 590, 591–919, 605–622, 409–411, 566–589 ; règles de fusion OR ; expansion scénario ; ordre `_de67f`.
- Protocole legacy HTTP : endpoints `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}`, JSON non standard, content-type historique, Basic Auth, AES alarme, single-packet TCP.
- Mappings multi-repos : firmware `TableEchange.h`, écran `IHM_ECHANGES.INC`, backend Go `pkg/protocol/constants.go`, portail cloud `internal/domain/order_expansion.go`, frontend/API inject.

## Focus roadmap et portails 2025/2026

Le discovery doit intégrer :

- Roadmap OpenSpec active/completed/planned, dont changes 2025/2026 si présents dans sources.
- Portail LAN local gateway : backend/frontend serveur, IAM LAN, MCU panels, scénarios, install wizard.
- Portail cloud `mon.essensys.fr` : user portal backend/frontend, remote UI, cloud relay/sync.
- Support site et documentation publique : support, doc site, Docusaurus/MkDocs, roadmap site public.
- Portails admin/utilisateur : suppression interdite admin, trusted devices, security gates, dépendances déploiement OVH et local.

## Validation

Validation minimale :

- Parser tous les fichiers `okf/**/*.md` non réservés et vérifier frontmatter + `type`.
- Vérifier liens locaux OKF et citations wiki relatives quand elles pointent vers le dépôt.
- Vérifier que chaque dépôt Git ESSENSYS a au moins une fiche OKF ou une justification de non-couverture.
- Vérifier présence des concepts legacy obligatoires : armoire, table d'échange, dual protocol, legacy HTTP.
- Produire un rapport `output/okf-discovery-coverage-YYYY-MM-DD.md`.

## Risks and mitigations

- Risque : dérive entre wiki et code. Mitigation : citer source wiki et code pointer ; signaler les contradictions.
- Risque : volume important. Mitigation : discovery par lots, index de progression, rapport de couverture.
- Risque : endpoints legacy accidentellement interprétés comme à moderniser. Mitigation : marquer explicitement contrat gelé et non-goal de modification.
- Risque : secrets dans dépôts infra. Mitigation : ne jamais lire/imprimer `.env`, secrets SOPS déchiffrés ou credentials ; se limiter aux manifests, docs et chemins.
