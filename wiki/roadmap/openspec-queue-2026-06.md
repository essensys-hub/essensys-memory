---
tags: [roadmap, openspec, queue]
sources: [product-roadmap.md, product-roadmap-rubric.md]
created: 2026-06-21
updated: 2026-06-21
era: modern
---

# OpenSpec Queue 2026 06

File d'exécution **ordonnée** des changes OpenSpec produit. Chaque epic a un identifiant **`2026-06.NNN`**.

> Registre canonique : `openspec/changes/essensys-roadmap-queue-2026-06/`  
> Prompt revue : `prompts/roadmap-product.md`

## Légende statut

| Statut | Signification |
|--------|---------------|
| **completed** | `tasks.md` entièrement coché — archivable |
| **active** | En cours d'implémentation |
| **planned** | Scaffold créé — pas encore Now |

## Ordre d'exécution

| ID | Change | Dépôt hôte | Horizon | Statut | Dépend de |
|----|--------|------------|---------|--------|-----------|
| **2026-06.001** | [[Essensys Centralized Doc Maintenance]] | essensys-memory | Phase 0 | completed | — |
| **2026-06.002** | [[Essensys Install Doc Platform]] | essensys-memory | Phase 0 | completed | 001 |
| **2026-06.003** | [[Essensys Second Brain]] | essensys-memory | Fondation | completed | — |
| **2026-06.004** | [[Essensys Product Roadmap]] | essensys-memory | Living | active | 001, 002 |
| **2026-06.005** | [[Essensys Roadmap Site 2026 06.005]] | essensys-memory | Now | planned | 004 |
| **2026-06.006** | [[Essensys Scenario Management]] | essensys-memory | Now | active | 001 |
| **2026-06.007** | [[Essensys Doc Site]] | essensys-memory | Now | completed | 001, 002 |
| **2026-06.008** | [[Essensys Doc Site Dns 2026 06.008]] | essensys-memory | Now | planned | 007 |
| **2026-06.009** | [[Essensys Gateway Mtls]] | essensys-memory | Now → Next | active | 001 |
| **2026-06.010** | [[Essensys Gateway Dual Nic]] | essensys-raspberry-gateway | Next | active | — |
| **2026-06.011** | [[Essensys Gateway Nixos]] | essensys-raspberry-gateway | Next | active | 010 |
| **2026-06.012** | [[Essensys Gateway Prod Decision 2026 06.012]] | essensys-memory | Next | planned | 010, 011 |
| **2026-06.013** | [[Essensys Trusted Devices 2026 06.013]] | essensys-memory | Next | planned | 009 |
| **2026-06.014** | [[Essensys Install Doc Ingest 2026 06.014]] | essensys-memory | Next | planned | 002 |
| **2026-06.015** | [[Essensys Remote User Interface 2026 06.015]] | essensys-memory | Next | planned | — |
| **2026-06.016** | [[Essensys Install Wizard 2026 06.016]] | essensys-memory | Later | planned | 002, 014 |
| **2026-06.017** | [[Essensys Lan Iam 2026 06.017]] | essensys-server-backend | Later | planned | — |
| **2026-06.018** | [[Essensys Gateway Recovery 2026 06.018]] | essensys-memory | Later | planned | 016 |
| **2026-06.019** | [[Essensys Gateway Fleet 2026 06.019]] | essensys-memory | Later | planned | 009, 018 |
| **2026-06.020** | [[Essensys Scenario Pg Cache 2026 06.020]] | essensys-memory | Later | planned | 006 |
| **2026-06.021** | [[Essensys Doc Docusaurus 2026 06.021]] | essensys-doc | Later | planned | 007, 008 |
| **2026-06.022** | [[Essensys Brain Ingest Auto 2026 06.022]] | essensys-memory | Later | planned | 003 |
| **2026-06.023** | [[Essensys Doc Ci Conformance 2026 06.023]] | essensys-memory | Later | planned | 001 |
| **2026-06.024** | [[Essensys Cloud Sync Scheduler]] | essensys-memory | — | completed | — |
| **2026-06.025** | [[Essensys Lan Mcu Panels 2026 06.025]] | essensys-memory | Next | planned | 013 |
| **2026-06.026** | [[Essensys Ui E2e Playwright 2026 06.026]] | essensys-memory | Now → Next | active | 006 |

## Règles

1. **Un ID = un epic** — ne pas dupliquer un change actif sous un autre numéro.
2. Les changes **001–004, 006–011, 024** existaient avant la queue ou ont un dossier legacy ; l'ID est dans `roadmap_id` du `.openspec.yaml`.
3. Promouvoir **planned → active** uniquement quand le change **précédent bloquant** est completed ou N/A.
4. Mettre à jour cette page + [[Product Roadmap]] à chaque promotion.

## Voir aussi

- [[Product Roadmap]]
- [[Product Roadmap Rubric]]
- [[Roadmap OpenSpec]]
