# Systems

* [Client Essensys Legacy](client-essensys-legacy.md) - Client embarqué legacy BP_MQX_ETH compatible protocole HTTP historique.
* [Essensys Android Phone Apps](essensys-android-phone-apps.md) - Application Android native (Kotlin / Jetpack Compose) « Mon Essensys » permettant de piloter une installation domotique Essensys (éclairage, volets, scénarios) en local Wi-Fi ou à distance.
* [Essensys Ansible](essensys-ansible.md) - Référentiel Ansible qui automatise l'intégralité du déploiement Essensys : passerelles Raspberry Pi / CM5 sur site (backend, frontend, MQTT, Redis, AdGuard, Traefik, monitoring, assistant IA) et infrastructure cloud OVH 
* [Essensys Api Doc](essensys-api-doc.md) - Documentation de l'API legacy Essensys (protocole HTTP du firmware ↔ serveur `mon.essensys.fr`), publiée sous forme de site MkDocs Material bilingue FR/EN.
* [Essensys Base](essensys-base.md) - Image Docker de base commune (Alpine 3.19) partagée par tous les services Essensys déployés sur Raspberry Pi.
* [Essensys Board Sc840b](essensys-board-SC840B.md) - Carte **banc de test usine** « Banc BA » : teste automatiquement les cartes d'actionneurs (type BA / SC940-SC942) — alimentation, relais et variateurs.
* [Essensys Board Sc841a](essensys-board-SC841A.md) - Carte **banc de test usine** « Banc BP » : teste automatiquement les cartes de type BP (alimentations, alarmes, téléinfo, façade) en production.
* [Essensys Board Sc843d](essensys-board-SC843D.md) - Module **gradateur** (variateur d'éclairage / dimmer) Essensys SC943D, à base d'un petit PIC 8 broches.
* [Essensys Board Sc940](essensys-board-SC940.md) - Carte « Boîtier Pièce de Vie » : contrôleur d'actionneurs domotiques (éclairage, variateurs, volets) piloté sur bus I2C par le concentrateur central.
* [Essensys Board Sc941c](essensys-board-SC941C.md) - Variante « Boîtier Pièce d'Eau » du contrôleur d'actionneurs domotique : commute lampes, variateurs et volets sur ordre du concentrateur via bus I2C.
* [Essensys Board Sc942c](essensys-board-SC942C.md) - Carte auxiliaire « Chambres » de la box domotique Essensys : relais, lampes, volets et variateurs d'éclairage, pilotée en esclave I²C par le contrôleur central.
* [Essensys Board Sc944d](essensys-board-SC944D.md) - Carte contrôleur central (« client ») de la box domotique Essensys : cerveau Ethernet sous RTOS MQX qui agrège les boîtiers auxiliaires, dialogue avec le serveur Essensys et distribue les firmwares aux autres cartes.
* [Essensys Board Sc945d](essensys-board-SC945D.md) - Carte IHM tactile murale de la box domotique Essensys : écran couleur 2,8\" piloté par un contrôleur graphique 4D Systems PICASO-GFX2, interface utilisateur de l'installation.
* [Essensys Board Sc946d](essensys-board-SC946D.md) - Carte sirène d'alarme de la box domotique Essensys : génère et amplifie les signaux sonores d'alerte via un PIC24 et un amplificateur audio classe D 25 W.
* [Essensys Board Sc947 Xb](essensys-board-SC947-xB.md) - Carte détecteur de fuite d'eau (DFE) de la box domotique Essensys : petit capteur autonome à sonde résistive qui remonte une alerte de présence d'eau au système.
* [Essensys Control Plane](essensys-control-plane.md) - Plan de contrôle de la passerelle Essensys : service Go (UI React embarquée) qui orchestre la **flotte de conteneurs Docker** locaux (état, restart, update, rollback, versions), expose le **registre d'échange Redis** des
* [Essensys Doc](essensys-doc.md) - Référentiel central de documentation technique de l'écosystème Essensys : architecture logicielle (modèle C4), spécifications matérielles, protocoles et guides de déploiement.
* [Essensys Feature Lifecycle](essensys-feature-lifecycle.md) - Dépôt **source de vérité** du cycle de vie feature Git-first Essensys : skills, rules Cursor, gates CI, manifestes `features/*.json`, orchestration IA/subagents et intégration **Jira SCRUM**.
* [Essensys Gateway](essensys-gateway.md) - Dépôt « ombrelle » / réservé de la passerelle Essensys, aujourd'hui réduit à un README stub — le contenu réel (matériel CM5 + déploiement) vit dans `essensys-raspberry-gateway`.
* [Essensys Gcc](essensys-gcc.md) - Chaîne de compilation (toolchain) libre et reproductible migrant le firmware Essensys de CodeWarrior/MPLAB vers GCC, avec build cross-compile sous Docker, tests host et CI GitHub Actions.
* [Essensys Homeassitant](essensys-homeassitant.md) - Intégration personnalisée (custom component) Home Assistant qui expose les équipements domotiques Essensys (éclairages, volets, chauffage) en tant qu'entités HA, en pilotant le backend Essensys via son API d'injection d'
* [Essensys Ios Phone Apps](essensys-ios-phone-apps.md) - Application iOS native (Swift / SwiftUI) « Essensys » permettant de piloter une installation domotique Essensys (éclairage, volets, scénarios, chauffage…) depuis un iPhone, en local Wi-Fi ou à distance via WAN.
* [Essensys Mcp](essensys-mcp.md) - Dépôt destiné à héberger un serveur MCP (Model Context Protocol) pour Essensys, mais actuellement vide hormis un README d'une ligne.
* [Essensys Memory](essensys-memory.md) - Mémoire persistante ESSENSYS, wiki Obsidian et bundle OKF agent-friendly.
* [Essensys Mosquitto](essensys-mosquitto.md) - Broker MQTT (Eclipse Mosquitto) de la gateway Essensys, point d'echange temps reel entre les objets domotiques IoT et le backend.
* [Essensys N8n](essensys-n8n.md) - Dépôt destiné à héberger l'automatisation de workflows n8n de la plateforme Essensys, actuellement à l'état de squelette vide (réservation de nom).
* [Essensys Nginx](essensys-nginx.md) - Serveur web et reverse-proxy interne de la gateway Essensys : sert le frontend React (SPA) et proxifie l'API, le MCP et le control-plane sur le LAN.
* [Essensys Prometheus](essensys-prometheus.md) - Depot stub destine a la supervision Prometheus de la stack Essensys ; actuellement vide, le deploiement reel s'appuie sur l'image upstream `prom/prometheus` configuree par Ansible.
* [Essensys Raspberry Gateway](essensys-raspberry-gateway.md) - Passerelle Essensys « CM5 Edition » : conception matérielle de la carte (Raspberry Pi Compute Module 5, stack 3 PCB, rail DIN) **et** déploiement déclaratif NixOS de la pile applicative Essensys sur cette passerelle.
* [Essensys Raspberry Install](essensys-raspberry-install.md) - Provisioning / bootstrap d'installation de la passerelle Essensys sur Raspberry Pi : un script `install.sh` minimal qui pose les prérequis (git, Ansible) puis **délègue tout le déploiement au dépôt `essensys-ansible`** (
* [Essensys Redis](essensys-redis.md) - Cache et store cle-valeur en memoire de la gateway Essensys, partage par le backend et le serveur MCP.
* [Essensys Server Backend](essensys-server-backend.md) - Backend Go LAN qui expose l'API moderne et maintient la compatibilité legacy IoT.
* [Essensys Server Frontend](essensys-server-frontend.md) - Interface web LAN React/TypeScript pour piloter la domotique via le backend local.
* [Essensys Support Site](essensys-support-site.md) - Portail de support communautaire d'Essensys : SPA React (vitrine + espace utilisateur/admin) doublée d'une documentation MkDocs, autour d'un backend Go aujourd'hui déprécié au profit du hub cloud unifié.
* [Essensys Traefik](essensys-traefik.md) - Reverse-proxy de bordure de la gateway Essensys, terminaison TLS (Let's Encrypt + CA locale) et filtrage des routes exposees sur le WAN.
* [Essensys User Portal Backend](essensys-user-portal-backend.md) - Backend Go cloud/OVH pour portail distant, relais gateway et expansion d'ordres.
* [Essensys User Portal Frontend](essensys-user-portal-frontend.md) - Portail cloud React/TypeScript pour l'accès distant utilisateur sur mon.essensys.fr.
* [Essensys Utils](essensys-utils.md) - Boîte à outils de scripts de maintenance pour Essensys ; à ce jour, contient principalement un script Go de bruteforce du code de configuration à 4 chiffres du panneau SC944D via la queue Redis.
* [Essensys Web Legacy](essensys-web-legacy.md) - Application web legacy ASP.NET MVC/Web API de la plateforme historique.
