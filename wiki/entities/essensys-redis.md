---
tags: [entity, repo, modern, infra]
sources: [essensys-redis.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-redis
---

# Essensys Redis

> Cache et store cle-valeur en memoire de la gateway Essensys, partage par le backend et le serveur MCP.

| | |
|---|---|
| **Catégorie** | Infrastructure |
| **Stack** | Redis (Alpine `apk`), Docker (multi-arch arm64/amd64), image de base `essensyshub/essensys-base` |
| **Statut** | Actif |
| **Era** | modern |

## Rôle

Redis fournit le stockage cle-valeur rapide en memoire de la gateway : cache, etat partage et donnees ephemeres. Dans la stack Docker il est demarre tot car plusieurs services en dependent (`depends_on: essensys-redis` pour le backend et le serveur MCP). Il tourne en `network_mode: host` sur le port 6379.

## Intégrations

_Non documenté._

## Structure

_Voir dépôt source._

## Points d'attention

- `protected-mode no` + `bind 0.0.0.0` sans `requirepass` : Redis accepte les connexions sans authentification. Acceptable uniquement parce que l'acces est limite a la boucle locale de la gateway (`network_mode: host`, non expose au WAN) — a ne jamais exposer hors du LAN.
- `maxmemory 128mb` avec eviction `allkeys-lru` : dimensionnement Raspberry Pi ; les cles peuvent etre evincees sous pression memoire (ne pas l'utiliser comme stockage durable critique).
- Persistance RDB uniquement (pas d'AOF) : risque de perte des dernieres ecritures en cas d'arret brutal.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-redis.md`
