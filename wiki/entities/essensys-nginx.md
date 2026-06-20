---
tags: [entity, repo, modern, infra]
sources: [essensys-nginx.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-nginx
---

# Essensys Nginx

> Serveur web et reverse-proxy interne de la gateway Essensys : sert le frontend React (SPA) et proxifie l'API, le MCP et le control-plane sur le LAN.

| | |
|---|---|
| **Catégorie** | Infrastructure |
| **Stack** | Nginx (Alpine `apk`), Docker (multi-arch arm64/amd64), image de base `essensyshub/essensys-base` |
| **Statut** | Actif |
| **Era** | modern |

## Rôle

Nginx est le serveur HTTP local (port 80) de la gateway. Il remplit deux fonctions :
1. servir les fichiers statiques du frontend React avec routage SPA (`try_files ... /index.html`) ;
2. agir comme reverse-proxy vers les services backend internes (API, MCP, control-plane).

Dans la chaine de bordure, Nginx ecoute le trafic LAN sur `:80` tandis que Traefik gere la terminaison TLS et le filtrage WAN sur `:443`. Traefik route d'ailleurs le frontend vers ce Nginx (`http://127.0.0.1:80`).

## Intégrations

_Non documenté._

## Structure

_Voir dépôt source._

## Points d'attention

- `server_name _;` (catch-all) : tout host est accepte ; le filtrage par domaine est delegue a Traefik en amont.
- Pas de TLS au niveau Nginx : il ne doit ecouter que sur le LAN ; l'exposition WAN passe obligatoirement par Traefik. En profil gateway, le LAN n'expose que HTTPS (le `:80` direct sur eth0 renvoie 444 selon la doc Ansible).
- Les cibles de proxy sont en `127.0.0.1` : cela suppose `network_mode: host` (tous les conteneurs partagent la pile reseau de l'hote) — coherent avec la compose Ansible.
- `worker_connections 256` : volontairement modeste (cible Raspberry Pi).

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-nginx.md`
