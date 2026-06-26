# essensys-doc

> Référentiel central de documentation technique de l'écosystème Essensys : architecture logicielle (modèle C4), spécifications matérielles, protocoles et guides de déploiement.

**Catégorie :** Documentation / Site
**Stack :** Markdown, diagrammes Mermaid + PNG (modèle C4), skills Claude packagées (.zip)
**Statut :** Actif — dépôt de référence de l'organisation `essensys-hub` (branche `main`)

## Rôle dans l'architecture Essensys
`essensys-doc` est la **source de vérité documentaire** de tout l'écosystème. Il agrège dans un seul dépôt la description de l'architecture logicielle et matérielle, et joue le rôle de point d'entrée pour comprendre le projet (le README liste l'ensemble des dépôts de l'organisation et leur rôle).

Il couvre notamment :
- Le **client legacy** (firmware C du contrôleur BP_MQX_ETH sur Coldfire MCF52259 / MQX RTOS) et ses 8 contraintes firmware.
- La **table d'échange** (953 indices) qui constitue le modèle de données central partagé entre le firmware legacy et le backend moderne.
- Le **pattern Bridge / Anti-Corruption Layer** qui relie le backend Go moderne au protocole legacy.
- Le matériel : 4 cartes (SC944D boîtier principal, SC940D/SC941C/SC942C boîtiers auxiliaires).

## Contenu / structure
- `README.md` — vue d'ensemble, index complet de la documentation, cartographie des composants physiques et de l'écosystème de dépôts.
- `archi/` — documentation d'architecture suivant le **modèle C4** :
  - `index.md` (contexte C4), `containers.md` (14 services Docker), `legacy-client*.md` (client embarqué : sécurité, build/toolchain CodeWarrior, protocoles I2C/UART/SPI, config GPIO, OTA, debug).
  - `exchange-table.md` (cartographie des 953 indices, droits d'accès, bitmasks), `domaines-fonctionnels.md` (alarme, chauffage, volets, cumulus, fuites, vent, arrosage).
  - `bridge-pattern.md` (ACL, 4 points d'entrée), `deployment.md` (Ansible, Docker Compose, CI/CD), `critique_ddd.md` (autocritique DDD).
  - `hardware-overview.md` + `hardware-sc94*.md` (4 fiches cartes, BOM, bus I2C).
  - `archi/img/` — diagrammes PNG (architecture globale, flux bouton→relais, flux alerte→WhatsApp, pattern bridge, déploiement infra).
- `new_feature/` — propositions de nouvelles fonctionnalités firmware (firmware v2 local + full status, intégration Home Assistant, modernisation HTTP/mDNS/SSDP) et **errata** sur la table d'échange.
- `skills/` — skills Claude packagées (`mcf52259-mqx-expert`, `altium-electronics-expert`, `plan-to-github-tasks`, `execute-github-project`, `essensys-raspberry-doc`, `essensys-backend-reference-orders`) + références (.md, .zip).
- `newsletters/` — contenu de newsletters (ex. `2026-06-volets`).

## Build / Publication (générateur, hébergement)
**Aucun générateur de site statique** : le dépôt est un ensemble de fichiers Markdown destinés à être lus directement sur GitHub (rendu Mermaid natif + images PNG pré-générées dans `archi/img/`). Pas de `mkdocs.yml`, de workflow GitHub Actions ni de configuration Docusaurus/Astro. La publication se fait par simple consultation du dépôt `github.com/essensys-hub/essensys-doc`.

## Intégrations
- Documente l'ensemble des dépôts `essensys-hub` (backend Go, frontend React, control-plane, Ansible, raspberry-install, images nginx/traefik/redis/mosquitto, support-site, client-essensys-legacy).
- Les `skills/` sont consommables par des agents Claude Code pour assister le développement firmware (MCF52259/MQX), électronique (Altium) et la gestion de projet GitHub.
- Les errata et les fiches `new_feature/` alimentent directement les évolutions du firmware et du backend.

## Points d'attention
- C'est de la documentation « living doc » non générée : la cohérence dépend de mises à jour manuelles (les errata montrent que la table d'échange a été corrigée de ~600 à 953 indices — risque de dérive entre doc et code).
- Mélange de niveaux d'abstraction (architecture C4, fiches matériel BOM, skills d'agent, newsletters) dans un seul dépôt.
- Les diagrammes existent en double format (sources Mermaid + PNG) : penser à régénérer les PNG quand le Mermaid change.
- Aucune CI ne valide les liens internes ni la fraîcheur des diagrammes.
