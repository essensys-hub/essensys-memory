---
tags: [entity, repo, modern, infra]
sources: [essensys-prometheus.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-prometheus
---

# Essensys Prometheus

> Depot stub destine a la supervision Prometheus de la stack Essensys ; actuellement vide, le deploiement reel s'appuie sur l'image upstream `prom/prometheus` configuree par Ansible.

| | |
|---|---|
| **Catégorie** | Infrastructure |
| **Stack** | Prometheus (prevu) — depot actuellement non implemente |
| **Statut** | Stub / a completer |
| **Era** | modern |

## Rôle

Ce depot est cense porter la brique de monitoring (Prometheus) de la gateway Essensys : collecte des metriques (scraping) du backend, de Traefik, des node-exporters, etc. En l'etat, **le depot est un stub** : il ne contient qu'un `README.md` d'une seule ligne (`# essensys-prometheus`), sans Dockerfile, sans `prometheus.yml`, sans workflow CI.

Le monitoring est aujourd'hui assure non pas par une image custom issue de ce depot, mais par l'image officielle upstream `prom/prometheus` deployee directement via Ansible (cf. `essensys-ansible/roles/raspberry_prometheus`). Ce depot reste donc un emplacement reserve, en attente d'eventuelle personnalisation.

## Intégrations

_Non documenté._

## Structure

_Voir dépôt source._

## Points d'attention

- **Statut stub** : tant que ce depot ne contient pas de `Dockerfile`/`prometheus.yml`/CI, il ne produit aucune image. Le monitoring repose entierement sur l'image upstream et la config geree par Ansible.
- Incoherence a clarifier : la compose Ansible parle de l'image `prom/prometheus` alors que ce depot porte le nom `essensys-prometheus` — verifier l'intention (image custom future vs simple placeholder).
- A completer : config de scraping (`prometheus.yml`), regles d'alerting, et workflow de build si une image custom est souhaitee (sur le modele des autres depots infra : `FROM essensyshub/essensys-base`, push `essensyshub/essensys-prometheus`).

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-prometheus.md`
