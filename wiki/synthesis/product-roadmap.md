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
> **Dernière revue** : 2026-06-21 (exécution `prompts/roadmap-product.md`)  
> **Gate Phase 0** : **levée** — [[Essensys Centralized Doc Maintenance]] completed ; [[Essensys Install Doc Platform]] completed (tâche ingest optionnelle 3.2 différée).

## Matrice gap

| Domaine | Existant | Partiel | Gap | OpenSpec / source | Risque si ignoré |
|---------|----------|---------|-----|-------------------|------------------|
| Brain / ingest | Vault, 40 entités, lint | qmd index | Ingest auto post-merge | [[Essensys Second Brain]] completed | Contexte agent stale |
| Doc centralisée | Rules + concept wiki | Adoption PR | Mesure conformité rules | [[Essensys Centralized Doc Maintenance]] completed | Doc divergente dépôts/brain |
| Doc install | Index brain + rules | Excerpt `wiki/sources/` | Ingest playbooks | [[Essensys Install Doc Platform]] completed | Wizard futur sans base |
| Cloud sync profils | Scheduler 3 h, 6 profils seed | UI admin Sync Cloud support-site | — | [[Essensys Cloud Sync Scheduler]] completed | Cache cloud obsolète |
| Scénarios domotique | UI jumeaux, API, sync 591–919 | `test_chb3.py` 1.5, PG option 2.5 | Clôture change | [[Essensys Scenario Management]] active | Régression Mode A |
| Gateway ↔ cloud auth | HTTPS, token+MAC | [[Gateway PKI]] doc | mTLS enrollment, TPM | [[Essensys Gateway Mtls]] active | Token exfiltré |
| Dual-NIC CM5 | eth0 WAN / eth1 armoire doc | Prod Ansible vs NixOS | Décision prod | [[Essensys Gateway Dual Nic]], [[Essensys Gateway Nixos]] | Dette deploy |
| Portail distant | LinkGate, inject, `/portal/` | Parité jumeaux continue | — | [[Essensys Remote User Interface]] (prompt) | Régression miroir |
| IAM / sessions LAN | Basic Auth optionnelle | — | Comptes, RBAC LAN | > [!todo] `essensys-lan-iam` | Pas multi-utilisateur local |
| HTTPS local `.local` | Traefik LE + CA locale | Safari/iPad trust | Trusted devices | > [!todo] `essensys-trusted-devices` | UX iPad mural |
| Install particulier | Ansible `install-gateway.md` | — | Wizard UX | > [!todo] `essensys-install-wizard` | Non techniciens bloqués |
| Recovery gateway | API `gateways/register` | — | UX remplacement | Later (après install-wizard) | Support coûteux |
| Observabilité | New Relic partiel | Prometheus stub | Fleet health | Later | Pannes silencieuses |

## Now (0–3 mois)

| Objectif | Change | DoD |
|----------|--------|-----|
| Clôture scénarios | [[Essensys Scenario Management]] | 1.5 `test_chb3.py` vert ; change archivable |
| mTLS phase 1 (enrollment) | [[Essensys Gateway Mtls]] | 2.1–2.3 : PG fingerprint + CSR admin + Ansible cert |
| Living roadmap | [[Essensys Product Roadmap]] | Cette page + revue trimestrielle process |

> Phase 0 doc/install : **done** — rules `essensys-centralized-doc.mdc`, `essensys-install-doc.mdc` en vigueur.

## Next (3–9 mois)

| Objectif | Change | Dépendances |
|----------|--------|-------------|
| mTLS phase 2–3 | [[Essensys Gateway Mtls]] | Phase 1 + nginx OVH |
| Trusted devices (iPad mural) | `essensys-trusted-devices` (à créer) | HTTPS local strategy |
| Prod CM5 : Ansible vs NixOS | [[Essensys Gateway Nixos]] ou clôture dual-nic | Matériel + ops |
| Ingest install excerpts | [[Essensys Install Doc Platform]] tâche 3.2 | Optionnel |

## Later

| Objectif | Change prévu |
|----------|--------------|
| Wizard install grand public | `essensys-install-wizard` |
| IAM LAN complet | `essensys-lan-iam` |
| Fleet / remote diagnostics | `essensys-gateway-fleet` (à définir) |
| Migration PG scénarios cache | [[Essensys Scenario Management]] 2.5 optionnel |
| RGPD / licensing / multi-foyer | > [!todo] non specifié vault |

## Décisions à trancher

> [!todo] **Ansible vs NixOS** prod CM5 — critères : reproductibilité, TPM, équipe ops (cf. [[Essensys Gateway Nixos]]).
> [!todo] **Trusted device** — device-bound refresh token vs certificat client par iPad (impact [[Gateway PKI]]).
> [!todo] **nginx OVH consolidé** — fichier vhost exact pour mTLS `/api/gateway/` (cf. [[Gateway PKI]] todo).

## Angles morts (autocritique 2026-06-21)

1. **Jumeaux** : parité UI/back non mesurée automatiquement — risque régression silencieuse heating/scenarios.
2. **Firmware** : roadmap produit ignore migrations cartes SC944D — toute évolution 590–919 côté serveur sans firmware = OK, mais pas documenté ici pour les installateurs.
3. **Support-site** : consolidation backend faite ; reste cohérence JWT rotation (`Platform Overview` todo).
4. **Phase 0** : rules créées mais pas de CI vérifiant `[ ] Doc/brain` en PR.
5. **Trusted devices** sans change OpenSpec — reste verbal jusqu'à création `essensys-trusted-devices`.
6. **Scénarios** quasi finis mais change encore **active** — priorité Now correcte, pas de promotion mTLS avant 1.5 si régression protocol.
7. **Apps mobiles** reference-only — pas de stratégie produit (volontairement hors scope).

## Repoussé explicitement

- Réécriture firmware / MQTT WAN cloud — contraintes [[Gateway Exchange]].
- `scenario_definitions` PG (2.5) — MVP exchange cache suffit jusqu'à charge cloud prouvée.
- Ingest `wiki/sources/` install (3.2) — Later, non bloquant wizard design.

## Voir aussi

- [[Roadmap OpenSpec]]
- [[Product Roadmap Rubric]]
- [[Centralized Documentation]]
- [[Install Documentation]]
