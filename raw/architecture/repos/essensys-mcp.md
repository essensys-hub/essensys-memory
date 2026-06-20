# essensys-mcp

> Dépôt destiné à héberger un serveur MCP (Model Context Protocol) pour Essensys, mais actuellement vide hormis un README d'une ligne.

**Catégorie :** Outillage / IA
**Stack :** Indéterminée (aucun code ni manifeste présent)
**Statut :** Stub — dépôt à l'état de squelette, non implémenté

## Rôle dans l'architecture Essensys

D'après son nom, ce dépôt est prévu pour exposer un **serveur MCP (Model Context Protocol)** permettant à des agents IA (assistants type Claude/LLM) d'interagir avec la plateforme domotique Essensys via un protocole standardisé : exposition d'outils, de ressources et de contexte. Il s'inscrit dans la famille « Outillage / IA » du projet, aux côtés de `essensys-memory`.

À ce jour, **rien ne permet de confirmer le périmètre fonctionnel réel** : aucune liste d'outils, aucune cible (Redis, Control Plane, firmware…) n'est documentée dans le dépôt.

## Stack technique & dépendances

Aucune information disponible. Le dépôt ne contient ni `package.json`, ni `pyproject.toml`, ni `go.mod`, ni Dockerfile, ni code source. La stack (TypeScript SDK MCP, Python, etc.) reste à décider.

## Structure du dépôt

```
.
├── .git/
└── README.md   # contenu : "# essensys-mcp" (une seule ligne)
```

L'historique Git se limite à un unique commit `Initial commit` (16fbe03).

## Build / Exécution / Déploiement

Néant. Aucun script de build, aucune CI (`.github/` absent), aucune cible de déploiement.

## Intégrations

Aucune intégration implémentée. Intégrations *attendues* (hypothèses à valider) : connexion au reste de l'écosystème Essensys (queue Redis `essensys:global:actions`, Control Plane, API backend) pour exposer des actions domotiques aux agents IA.

## Points d'attention

- **Dépôt stub** : ne contient qu'un titre. Toute description de ses capacités serait spéculative.
- Remote : `git@github.com:essensys-hub/essensys-mcp.git`.
- Avant tout développement, définir le SDK MCP retenu et le périmètre des outils exposés.
- Vérifier la cohérence de sécurité : un serveur MCP donnant accès aux actions domotiques doit être strictement contrôlé (cf. le bruteforce documenté dans `essensys-utils`).
