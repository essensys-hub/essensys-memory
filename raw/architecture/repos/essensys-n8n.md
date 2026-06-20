# essensys-n8n

> Dépôt destiné à héberger l'automatisation de workflows n8n de la plateforme Essensys, actuellement à l'état de squelette vide (réservation de nom).

**Catégorie :** Déploiement / Automatisation
**Stack :** n8n (prévu) — aucune dépendance ni configuration encore présente
**Statut :** Stub / placeholder — un seul commit (« Initial commit ») contenant uniquement un `README.md` d'une ligne

## Rôle dans l'architecture Essensys

Le dépôt est prévu pour porter l'**automatisation de workflows** via [n8n](https://n8n.io) (orchestration low-code de tâches : webhooks, intégrations, notifications, synchronisations entre services). Dans l'écosystème Essensys, ce rôle est typiquement tenu par un n8n connecté au broker MQTT, au backend, au cloud hub (`mon.essensys.fr`) et à des services externes (WhatsApp, e-mail, etc.).

**En l'état actuel, le dépôt ne contient aucune implémentation** : ni `docker-compose.yml`, ni définitions de workflows (`*.json`), ni variables d'environnement, ni README documenté. Il s'agit d'une réservation de nom de dépôt dont le contenu reste à créer.

## Structure du dépôt

```
essensys-n8n/
└── README.md     # Une seule ligne : "# essensys-n8n"
```

Vérification effectuée : aucun fichier caché, aucun sous-dossier (hors `.git`). Historique Git limité à un unique commit `54d84fe` (« Initial commit »).

## Ce qui est déployé / automatisé

Rien pour l'instant. Aucun workflow, aucun service défini.

À titre indicatif, le contenu attendu d'un tel dépôt comprendrait :
- un `docker-compose.yml` pour le service n8n (image `n8nio/n8n`, volume de persistance, base de données, variables `N8N_*`) ;
- un répertoire de workflows exportés (`workflows/*.json`) ;
- un fichier `.env` / `.env.example` pour les secrets et les URLs d'intégration.

## Build / Exécution

Aucune commande disponible à ce stade (pas de `docker-compose.yml`).

Mise en route typique une fois le dépôt rempli :

```bash
docker compose up -d        # démarrer le service n8n
# Import/export des workflows via l'UI n8n ou la CLI :
# docker compose exec n8n n8n export:workflow --all --output=/workflows
# docker compose exec n8n n8n import:workflow --input=/workflows
```

## Intégrations

Aucune intégration configurée. Les cibles d'intégration probables, par cohérence avec le reste de l'architecture Essensys, seraient : MQTT (Mosquitto), backend / cloud backend, cloud hub `mon.essensys.fr`, New Relic, et l'assistant OpenClaw / WhatsApp.

## Points d'attention

- **Dépôt vide / non fonctionnel :** il ne contient qu'un README d'une ligne. Toute documentation au-delà de ce constat serait spéculative.
- **À clarifier :** soit ce dépôt est abandonné/réservé, soit l'automatisation n8n est aujourd'hui hébergée ailleurs (par exemple en tant que conteneur géré directement par `essensys-ansible` ou un docker-compose externe). À confirmer auprès de l'équipe avant d'y investir.
- **Aucun secret ni configuration** présent — rien à sécuriser en l'état.
