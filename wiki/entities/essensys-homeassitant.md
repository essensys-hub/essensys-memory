---
tags: [entity, repo, migration]
sources: [essensys-homeassitant.md]
created: 2026-06-20
updated: 2026-06-20
era: migration
repo: essensys-homeassitant
---

# Essensys Homeassitant

> Intégration personnalisée (custom component) Home Assistant qui expose les équipements domotiques Essensys (éclairages, volets, chauffage) en tant qu'entités HA, en pilotant le backend Essensys via son API d'injection d'actions.

| | |
|---|---|
| **Catégorie** | Home Assistant / HAL |
| **Stack** | Python (custom component Home Assistant), `requests`, `voluptuous` ; configuration YAML |
| **Statut** | Fonctionnel mais minimaliste (v1.2.0) — pilotage en aller simple, sans remontée d'état réelle |
| **Era** | migration |

## Rôle

Ce dépôt est le **pont entre Home Assistant et la plateforme Essensys**. Il permet à un utilisateur de Home Assistant de contrôler les équipements d'un site Essensys (maison domotisée) comme s'il s'agissait d'entités HA natives, et donc de bénéficier de l'écosystème HA : tableaux de bord, automatisations, assistants vocaux, scènes, etc.

Concrètement, l'intégration traduit les commandes Home Assistant (allumer une lumière, fermer un volet, changer un mode de chauffage) en **actions Essensys au format `{"k": index, "v": value}`** et les envoie au backend Essensys (`essensys-server-backend`) via l'endpoint d'injection `POST /api/admin/inject`. C'est exactement le même format clé/valeur (`k`/`v`) que celui utilisé dans le reste de l'écosystème Essensys pour piloter les boards/automates.

Le dépôt appartient à l'organisation GitHub `essensys-hub` (remote `git@github.com:essensys-hub/essensys-homeassitant.git`) : il fait donc partie du cœur Essensys, et non de la plateforme HAL (interphone vocal) qui est hébergée sous l'organisation `hal-home-assitant`.

## Intégrations

_Non documenté._

## Structure

_Voir dépôt source._

## Points d'attention

- **Pilotage en aller simple, aucune remontée d'état réelle.** Les entités supposent leur état après commande (`_is_on`, `_attr_is_closed`, `_attr_current_option` mis à jour localement). Il n'existe pas de polling ni de feedback depuis le backend : l'état affiché dans HA peut diverger de la réalité physique. Les volets et sélecteurs démarrent à l'état « inconnu ».
- **Configuration figée :** les entités sont construites au démarrage à partir de `table_reference.json`. Toute modification du parc d'équipements impose de mettre à jour ce fichier et de redémarrer HA. Pas de découverte dynamique.
- **Heuristiques fragiles dans `light.py`** : l'attribut `open` est détecté comme « ON » alors qu'il relève sémantiquement d'un volet (le code le commente lui-même). Un équipement peut donc apparaître à la fois côté Light et côté Cover selon sa catégorie/attribut.
- **Sécurité :** appel HTTP non authentifié vers `/api/admin/inject` (endpoint « admin »). À cantonner à un réseau de confiance ; pas de gestion de credentials/token côté intégration.
- **`config_flow: false`** : pas d'UI de configuration, tout passe par le YAML — moins ergonomique que les intégrations HA modernes.
- **README quasi vi

_… voir source complète dans raw/_

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-homeassitant.md`
