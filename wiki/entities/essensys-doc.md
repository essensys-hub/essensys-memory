---
tags: [entity, repo, modern]
sources: [essensys-doc.md, analyses/2026-10-etudes-remplacement-armoire/analyse.md, analyses/2026-10-solutions-marche-armoire/analyse.md]
created: 2026-06-20
updated: 2026-10-24
era: modern
repo: essensys-doc
---

# Essensys DOC

> Référentiel central de documentation technique de l'écosystème Essensys : architecture logicielle (modèle C4), spécifications matérielles, protocoles et guides de déploiement.

| | |
|---|---|
| **Catégorie** | Documentation / Site |
| **Stack** | Markdown, diagrammes Mermaid + PNG (modèle C4), skills Claude packagées (.zip) |
| **Statut** | Actif — dépôt de référence de l'organisation `essensys-hub` (branche `main`) |
| **Era** | modern |

## Rôle

`essensys-doc` est la **source de vérité documentaire** de tout l'écosystème. Il agrège dans un seul dépôt la description de l'architecture logicielle et matérielle, et joue le rôle de point d'entrée pour comprendre le projet (le README liste l'ensemble des dépôts de l'organisation et leur rôle).

Il couvre notamment :
- Le **client legacy** (firmware C du contrôleur BP_MQX_ETH sur Coldfire MCF52259 / MQX RTOS) et ses 8 contraintes firmware.
- La **table d'échange** (953 indices) qui constitue le modèle de données central partagé entre le firmware legacy et le backend moderne.
- Le **pattern Bridge / Anti-Corruption Layer** qui relie le backend Go moderne au protocole legacy.
- Le matériel : 4 cartes (SC944D boîtier principal, SC940D/SC941C/SC942C boîtiers auxiliaires).
- Les **études** (`docs/etudes/`, depuis octobre 2026) : la réponse à l'exigence de résilience (`resilience.md`), l'étude V2 « filaire d'abord », le verdict du conseil d'autocritique, l'autocritique des V1 et les sections de câbles (`remplacement-armoire/v2/`), le banc deux lumières (`banc-deux-lumieres.md`) et les trois études V1 figées le 2026-10-21 (Revolution Pi, Arduino Opta, Raspberry Pi et Ethernet). Voir [[Reponse Resilience Armoire]].
- Les **solutions du marché** (`docs/etudes/remplacement-armoire/marche/`, PR essensys-hub/essensys-doc#20, 2026-10-24) : `index.md` (grille, tableau comparatif, classement, recommandation) et onze dossiers au même gabarit (KNX TP, Loxone, Niko Home Control II, Domintell, Homematic IP Wired, Eltako Series 14, Siemens LOGO! 8, Wago PFC200, Shelly Pro, ESPHome sur rail DIN, Modbus et passerelle). Voir [[Comparatif Solutions Marche Armoire]].

## Intégrations

- Documente l'ensemble des dépôts `essensys-hub` (backend Go, frontend React, control-plane, Ansible, raspberry-install, images nginx/traefik/redis/mosquitto, support-site, client-essensys-legacy).
- Les `skills/` sont consommables par des agents Claude Code pour assister le développement firmware (MCF52259/MQX), électronique (Altium) et la gestion de projet GitHub.
- Les errata et les fiches `new_feature/` alimentent directement les évolutions du firmware et du backend.

## Structure

_Voir dépôt source._

## Points d'attention

- C'est de la documentation « living doc » non générée : la cohérence dépend de mises à jour manuelles (les errata montrent que la table d'échange a été corrigée de ~600 à 953 indices — risque de dérive entre doc et code).
- Mélange de niveaux d'abstraction (architecture C4, fiches matériel BOM, skills d'agent, newsletters) dans un seul dépôt.
- Les diagrammes existent en double format (sources Mermaid + PNG) : penser à régénérer les PNG quand le Mermaid change.
- Aucune CI ne valide les liens internes ni la fraîcheur des diagrammes.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-doc.md`
