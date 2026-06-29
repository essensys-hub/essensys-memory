---
type: Repository
title: Essensys Ansible
description: "Référentiel Ansible qui automatise l'intégralité du déploiement Essensys : passerelles Raspberry Pi / CM5 sur site (backend, frontend, MQTT, Redis, AdGuard, Traefik, monitoring, assistant IA) et infrastructure cloud OVH "
resource: file:///Users/nrineau/ESSENSYS/essensys-ansible
tags: [essensys, repository, infra, modern]
timestamp: 2026-06-28T19:07:32Z
repo: essensys-ansible
layer: infra
era: modern
source_wiki: ../../wiki/entities/essensys-ansible.md
---
<!-- BEGIN GENERATED CONTENT -->
# Rôle

Référentiel Ansible qui automatise l'intégralité du déploiement Essensys : passerelles Raspberry Pi / CM5 sur site (backend, frontend, MQTT, Redis, AdGuard, Traefik, monitoring, assistant IA) et infrastructure cloud OVH 

# Interfaces

* Couche : Infrastructure.
* Era : modern.
* Dépôt local : `essensys-ansible`.
* Interfaces détaillées à compléter lors d’un approfondissement ciblé.

# Dépendances

* TBD

# Code pointers

* `essensys-ansible/.venv-ansible/lib/python3.11/site-packages/ansible_collections/community/general/plugins/module_utils/oneandone.py`
* `essensys-ansible/.venv-ansible/lib/python3.11/site-packages/ansible_collections/community/general/plugins/modules/oneandone_firewall_policy.py`
* `essensys-ansible/.venv-ansible/lib/python3.11/site-packages/ansible_collections/community/general/plugins/modules/oneandone_load_balancer.py`
* `essensys-ansible/.venv-ansible/lib/python3.11/site-packages/ansible_collections/community/general/plugins/modules/oneandone_monitoring_policy.py`
* `essensys-ansible/.venv-ansible/lib/python3.11/site-packages/ansible_collections/community/general/plugins/modules/oneandone_private_network.py`
* `essensys-ansible/.venv-ansible/lib/python3.11/site-packages/ansible_collections/community/general/plugins/modules/oneandone_public_ip.py`
* `essensys-ansible/.venv-ansible/lib/python3.11/site-packages/ansible_collections/community/general/plugins/modules/oneandone_server.py`
* `essensys-ansible/README.md`

# Risques

* Ne pas inférer de changement fonctionnel depuis cette fiche : elle décrit l'état et les contrats connus.
* Toute zone legacy ou protocolaire doit être vérifiée contre firmware + backend avant modification.

# Citations

[1] [Inventory](../../output/okf-repository-inventory.json)
[2] [Wiki source](../../wiki/entities/essensys-ansible.md)
<!-- END GENERATED CONTENT -->
