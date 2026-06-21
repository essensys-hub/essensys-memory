---
tags: [synthesis, roadmap, product]
sources: [product-roadmap-rubric.md, platform-overview.md, migration-legacy-to-modern.md]
created: 2026-06-21
updated: 2026-06-21
era: modern
---

# Product Roadmap

Priorisation produit **vivante** — delta par rapport à [[Platform Overview]] et [[Migration Legacy To Modern]].

> **Rubrique** : [[Product Roadmap Rubric]]  
> **Dernière revue** : 2026-06-21 — file OpenSpec [[OpenSpec Queue 2026 06]] (`2026-06.001`…`023`)  
> **Gate Phase 0** : **levée** — [[Essensys Centralized Doc Maintenance]] completed ; [[Essensys Install Doc Platform]] completed (tâche ingest optionnelle 3.2 différée).

## Matrice gap

| Domaine | Existant | Partiel | Gap | OpenSpec / source | Risque si ignoré |
|---------|----------|---------|-----|-------------------|------------------|
| Brain / ingest | Vault, 40 entités, lint | qmd index | Ingest auto post-merge | [[Essensys Second Brain]] completed | Contexte agent stale |
| Doc centralisée | Rules + concept wiki | Adoption PR | Mesure conformité rules | [[Essensys Centralized Doc Maintenance]] completed | Doc divergente dépôts/brain |
| Doc install | Index brain + rules | Excerpt `wiki/sources/` | Ingest playbooks | [[Essensys Install Doc Platform]] completed | Wizard futur sans base |
| **Doc publique users** | MkDocs `essensys-doc`, CI, role Ansible | DNS `docs.essensys.fr` | Deploy prod + lien support-site | [[Essensys Doc Site]] active → archiver | Users sans URL doc unifiee |
| Cloud sync profils | Scheduler 3 h, 6 profils seed | UI admin Sync Cloud support-site | — | [[Essensys Cloud Sync Scheduler]] completed | Cache cloud obsolète |
| Scénarios domotique | UI jumeaux, API, sync, `test_chb3.py` | PG option 2.5 | Archiver change | [[Essensys Scenario Management]] active | Régression Mode A |
| Gateway ↔ cloud auth | HTTPS, token+MAC | [[Gateway PKI]] doc | mTLS enrollment, TPM | [[Essensys Gateway Mtls]] active | Token exfiltré |
| Dual-NIC CM5 | eth0 WAN / eth1 armoire doc | Prod Ansible vs NixOS | Décision prod | [[Essensys Gateway Dual Nic]], [[Essensys Gateway Nixos]] | Dette deploy |
| Portail distant | LinkGate, inject, `/portal/` | Parité jumeaux continue | — | [[Essensys Remote User Interface]] (prompt) | Régression miroir |
| IAM / sessions LAN | Basic Auth optionnelle | — | Comptes, RBAC LAN | > [!todo] `essensys-lan-iam` | Pas multi-utilisateur local |
| HTTPS local `.local` | Traefik LE + CA locale | Safari/iPad trust | Trusted devices | > [!todo] `essensys-trusted-devices` | UX iPad mural |
| Install particulier | Ansible `install-gateway.md` | — | Wizard UX | > [!todo] `essensys-install-wizard` | Non techniciens bloqués |
| Recovery gateway | API `gateways/register` | — | UX remplacement | Later (après install-wizard) | Support coûteux |
| Observabilité | New Relic partiel | Prometheus stub | Fleet health | Later | Pannes silencieuses |

## Now (0–3 mois)

| ID | Objectif | Change | DoD |
|----|----------|--------|-----|
| 2026-06.008 | DNS doc dediee | [[Essensys Doc Site Dns 2026 06.008]] | `docs.essensys.fr` 200 HTTPS |
| 2026-06.006 | Cloture scenarios | [[Essensys Scenario Management]] | archiver change |
| 2026-06.009 | mTLS phase 1 | [[Essensys Gateway Mtls]] | 2.1–2.3 enrollment |
| 2026-06.004 | Living roadmap | [[Essensys Product Roadmap]] | queue + revue trimestrielle |

> Phase 0 doc/install : **done** — rules `essensys-centralized-doc.mdc`, `essensys-install-doc.mdc` en vigueur.

## Next (3–9 mois)

| ID | Objectif | Change | Dépendances |
|----|----------|--------|-------------|
| 2026-06.009 | mTLS phase 2–3 | [[Essensys Gateway Mtls]] | phase 1 |
| 2026-06.013 | Trusted devices | [[Essensys Trusted Devices 2026 06.013]] | 009 |
| 2026-06.012 | Prod CM5 decision | [[Essensys Gateway Prod Decision 2026 06.012]] | 010, 011 |
| 2026-06.014 | Ingest install | [[Essensys Install Doc Ingest 2026 06.014]] | 002 |
| 2026-06.015 | Portail distant | [[Essensys Remote User Interface 2026 06.015]] | — |

## Later

| ID | Objectif | Change prévu |
|----|----------|--------------|
| 2026-06.016 | Wizard install | [[Essensys Install Wizard 2026 06.016]] |
| 2026-06.017 | IAM LAN | [[Essensys Lan Iam 2026 06.017]] |
| 2026-06.018 | Recovery gateway | [[Essensys Gateway Recovery 2026 06.018]] |
| 2026-06.019 | Fleet diagnostics | [[Essensys Gateway Fleet 2026 06.019]] |
| 2026-06.020 | PG scenarios | [[Essensys Scenario Pg Cache 2026 06.020]] |
| 2026-06.021 | Doc Docusaurus | [[Essensys Doc Docusaurus 2026 06.021]] |
| 2026-06.022 | Brain ingest auto | [[Essensys Brain Ingest Auto 2026 06.022]] |
| 2026-06.023 | CI doc conformance | [[Essensys Doc Ci Conformance 2026 06.023]] |
| RGPD / licensing / multi-foyer | > [!todo] non specifié vault |

## Décisions à trancher

> [!todo] **`docs.essensys.fr` vs `mon.essensys.fr/docs/`** — sous-domaine recommandé (évite collision API) ; trancher avant tâche 2.2 Ansible.
> [!todo] **Ansible vs NixOS** prod CM5 — critères : reproductibilité, TPM, équipe ops (cf. [[Essensys Gateway Nixos]]).
> [!todo] **Trusted device** — device-bound refresh token vs certificat client par iPad (impact [[Gateway PKI]]).
> [!todo] **nginx OVH consolidé** — fichier vhost exact pour mTLS `/api/gateway/` (cf. [[Gateway PKI]] todo).

## Angles morts (autocritique 2026-06-21)

1. **Jumeaux** : parité UI/back non mesurée automatiquement — risque régression silencieuse heating/scenarios.
2. **Firmware** : roadmap produit ignore migrations cartes SC944D — toute évolution 590–919 côté serveur sans firmware = OK, mais pas documenté ici pour les installateurs.
3. **Support-site** : consolidation backend faite ; reste cohérence JWT rotation (`Platform Overview` todo).
4. **Phase 0** : rules créées mais pas de CI vérifiant `[ ] Doc/brain` en PR.
5. **Doc fragmentée** : 4 dépôts MkDocs/gh-pages sans hub OVH — adressé par [[Essensys Doc Site]] en Next.
6. **Trusted devices** sans change OpenSpec — reste verbal jusqu'à création `essensys-trusted-devices`.
7. **Apps mobiles** reference-only — pas de stratégie produit (volontairement hors scope).

## Repoussé explicitement

- Réécriture firmware / MQTT WAN cloud — contraintes [[Gateway Exchange]].
- `scenario_definitions` PG (2.5) — MVP exchange cache suffit jusqu'à charge cloud prouvée.
- Ingest `wiki/sources/` install (3.2) — Later, non bloquant wizard design.
- **Docusaurus MVP** — MkDocs Material d'abord (stack existante) ; React doc site seulement si besoin UX unifiée.

## Voir aussi

- [[Roadmap OpenSpec]]
- [[OpenSpec Queue 2026 06]] — file ordonnée 2026-06.001…023
- [[Product Roadmap Rubric]]
- [[Centralized Documentation]]
- [[Install Documentation]]
- [[User Documentation Site]]
