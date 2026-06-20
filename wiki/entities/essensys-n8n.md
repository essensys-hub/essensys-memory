---
tags: [entity, repo, modern]
sources: [essensys-n8n.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-n8n
---

# Essensys N8n

> Dépôt destiné à héberger l'automatisation de workflows n8n de la plateforme Essensys, actuellement à l'état de squelette vide (réservation de nom).

| | |
|---|---|
| **Catégorie** | Déploiement / Automatisation |
| **Stack** | n8n (prévu) — aucune dépendance ni configuration encore présente |
| **Statut** | Stub / placeholder — un seul commit (« Initial commit ») contenant uniquement un `README.md` d'une ligne |
| **Era** | modern |

## Rôle

Le dépôt est prévu pour porter l'**automatisation de workflows** via [n8n](https://n8n.io) (orchestration low-code de tâches : webhooks, intégrations, notifications, synchronisations entre services). Dans l'écosystème Essensys, ce rôle est typiquement tenu par un n8n connecté au broker MQTT, au backend, au cloud hub (`mon.essensys.fr`) et à des services externes (WhatsApp, e-mail, etc.).

**En l'état actuel, le dépôt ne contient aucune implémentation** : ni `docker-compose.yml`, ni définitions de workflows (`*.json`), ni variables d'environnement, ni README documenté. Il s'agit d'une réservation de nom de dépôt dont le contenu reste à créer.

## Intégrations

Aucune intégration configurée. Les cibles d'intégration probables, par cohérence avec le reste de l'architecture Essensys, seraient : MQTT (Mosquitto), backend / cloud backend, cloud hub `mon.essensys.fr`, New Relic, et l'assistant OpenClaw / WhatsApp.

## Structure

```
essensys-n8n/
└── README.md     # Une seule ligne : "# essensys-n8n"
```

Vérification effectuée : aucun fichier caché, aucun sous-dossier (hors `.git`). Historique Git limité à un unique commit `54d84fe` (« Initial commit »).

## Points d'attention

- **Dépôt vide / non fonctionnel :** il ne contient qu'un README d'une ligne. Toute documentation au-delà de ce constat serait spéculative.
- **À clarifier :** soit ce dépôt est abandonné/réservé, soit l'automatisation n8n est aujourd'hui hébergée ailleurs (par exemple en tant que conteneur géré directement par `essensys-ansible` ou un docker-compose externe). À confirmer auprès de l'équipe avant d'y investir.
- **Aucun secret ni configuration** présent — rien à sécuriser en l'état.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-n8n.md`
