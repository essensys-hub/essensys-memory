## Why

La base OKF `okf/` ne contient aujourd'hui qu'un noyau minimal alors que le projet ESSENSYS porte déjà un savoir critique réparti entre ~40 dépôts, le wiki, la roadmap OpenSpec, les protocoles legacy et les portails 2025/2026. Il faut lancer un discovery structuré de tous les dépôts ESSENSYS pour produire une mémoire OKF complète, fiable, interopérable et exploitable par les agents.

Le besoin est prioritaire car les zones les plus risquées — architecture armoire, [[Table D Echange]], protocole legacy HTTP `/api/serverinfos` / `/api/mystatus` / `/api/myactions` / `/api/done/{guid}`, roadmap, portails local/cloud/support/admin — conditionnent la compatibilité firmware et la migration moderne.

## What Changes

- Ajouter une campagne de discovery tous dépôts ESSENSYS vers la base OKF `okf/`.
- Générer un inventaire OKF de chaque dépôt Git ESSENSYS : rôle, couche, stack, statut, interfaces, liens avec les autres dépôts, code pointers et sources.
- Enrichir fortement les concepts OKF de l'architecture armoire : cartes SC840/SC841/SC940/SC941C/SC942C/SC944D/SC945D/SC946D/SC947-xB, firmware, bus/échanges et contraintes temps réel.
- Produire une représentation OKF détaillée de la [[Table D Echange]] : indices critiques, zones, scénarios, alarmes, volets, mappings frontend/backend/firmware/cloud.
- Documenter le protocole legacy HTTP comme contrat gelé : endpoints, formats non standard, Basic Auth, AES alarme, single-packet TCP, ordre `_de67f`, flux `/api/myactions` → `/api/done/{guid}`.
- Intégrer la roadmap et les portails déployés ou prévus en 2025/2026 : LAN local, portail cloud `mon.essensys.fr`, support site, roadmap site, documentation Docusaurus/MkDocs, interfaces admin/utilisateur, gateway CM5.
- Ajouter des scripts de discovery/validation OKF pour rendre la base régénérable et vérifiable.
- Mettre à jour `wiki/index.md`, `wiki/log.md`, `okf/index.md`, les index de sous-dossiers OKF et le log OKF.

## Capabilities

### New Capabilities

- `okf-repository-discovery`: discovery systématique des dépôts ESSENSYS et publication de fiches OKF par dépôt, couche et dépendance.
- `okf-legacy-architecture`: documentation OKF approfondie de l'architecture armoire, table d'échange et protocole legacy HTTP.
- `okf-roadmap-portals`: intégration OKF de la roadmap produit et des portails ESSENSYS déployés/prévus en 2025/2026.
- `okf-validation-pipeline`: génération, indexation et validation automatique de la base OKF.

### Modified Capabilities

- Aucun spec OpenSpec existant n'est modifié directement ; le changement complète la base OKF et référence les pages wiki existantes.

## Impact

- Dépôt hôte : `essensys-memory`.
- Données produites : `okf/**`, `wiki/concepts/**`, `wiki/synthesis/**`, `wiki/entities/**`, `wiki/index.md`, `wiki/log.md`.
- Sources lues : tous les dépôts Git sous `/Users/nrineau/ESSENSYS`, `raw/architecture/**`, `raw/protocol/**`, `wiki/**`, `openspec/changes/**`, `content/roadmap/site/**`.
- Scripts probables : `scripts/sync-sources.sh`, `scripts/extract-git-history.sh`, `scripts/update-roadmap.sh`, nouveaux scripts `scripts/okf/*`.
- Contrat sécurité/legacy : aucune modification du firmware ou des endpoints legacy ; seulement discovery et documentation. Toute contradiction détectée entre firmware, backend et portail doit être signalée explicitement, pas lissée.
