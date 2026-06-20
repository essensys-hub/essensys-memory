---
tags: [entity, repo, modern, infra]
sources: [essensys-traefik.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-traefik
---

# Essensys Traefik

> Reverse-proxy de bordure de la gateway Essensys, terminaison TLS (Let's Encrypt + CA locale) et filtrage des routes exposees sur le WAN.

| | |
|---|---|
| **Catégorie** | Infrastructure |
| **Stack** | Traefik v2.11.3, Docker (multi-arch arm64/amd64), image de base `essensyshub/essensys-base` |
| **Statut** | Actif |
| **Era** | modern |

## Rôle

Traefik est le point d'entree HTTPS de la gateway (Raspberry Pi). Il assure la terminaison TLS et controle finement ce qui est accessible depuis l'exterieur (WAN), par opposition a Nginx qui sert le trafic LAN interne. Dans la stack Docker il tourne en `network_mode: host` aux cotes de Nginx, du backend, de Redis et de Mosquitto.

Sa fonction principale cote securite est de n'exposer sur Internet qu'un sous-ensemble strictement controle de l'application :
- le frontend (protege par BasicAuth) ;
- une unique route d'API autorisee (`/api/admin/inject`, egalement protegee par BasicAuth) ;
- toutes les autres routes `/api/` sont volontairement bloquees (renvoyees vers un service de blocage).

## Intégrations

_Non documenté._

## Structure

_Voir dépôt source._

## Points d'attention

- `api.insecure: true` et `dashboard.insecure: true` : le dashboard est servi sans TLS sur l'entryPoint dashboard/traefik — a n'exposer que sur le LAN.
- `certificatesResolvers.letsencrypt.acme.email: admin@acme.com` est une valeur placeholder a personnaliser.
- `DOMAIN_PLACEHOLDER` dans `wan-routes.yml` doit imperativement etre substitue au deploiement (gere par Ansible), sinon les routers ne matchent rien.
- La securite du WAN repose sur `users.htpasswd` (BasicAuth) : ce fichier doit etre provisionne, sinon `auth-wan` echoue.
- Le `tlsChallenge` ACME requiert que le port 443 soit accessible publiquement pour l'emission Let's Encrypt ; en local on s'appuie plutot sur la CA locale.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-traefik.md`
