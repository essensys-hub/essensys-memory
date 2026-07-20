## Why

Chaque nouvelle intégration (un onduleur solaire, une sonde, un service tiers) oblige aujourd'hui à modifier à la main les **quatre applications modernes** jumelles ([[Essensys Server Backend]], [[Essensys User Portal Backend]], [[Essensys Server Frontend]], [[Essensys User Portal Frontend]]), avec un risque permanent de dérive entre jumeaux LAN/cloud et de collision avec le protocole legacy gelé. Le déclencheur concret est l'intégration d'une **centrale solaire Sungrow SH6.0RS + batterie SBR064** (collecteur local WiNet-S déjà écrit) : on veut ajouter cette **option** sans forker les 4 apps, et disposer d'un mécanisme réutilisable pour toutes les intégrations futures.

## What Changes

- Introduction d'un **framework de plugins** permettant de déclarer une option/intégration **une seule fois** et de la surfacer dans les 4 apps modernes.
- **Contrat de plugin déclaratif** : `plugin.manifest.json`, **extension** de `features/schema/feature.schema.json` (pas un système de manifest parallèle) — déclare `capabilities`, `perimeters`, `surfaces`, `visibility` (RBAC), `secrets` (références SOPS), `metrics`.
- **SDK Go** avec un **registre compilé** (pas de chargement dynamique `plugin.Open`) intégré aux deux backends ; expose `/api/plugins/<id>/*` côté moderne, s'abonne au bus, publie Prometheus.
- **Package TS partagé** : un **renderer générique** (server-driven UI) rendu **identiquement** par les deux frontends → supprime la dérive des jumeaux par construction.
- **Contrat collecteur** langage-agnostique : topics **Mosquitto** + schéma de payload + heartbeat.
- **Persistance réutilisant l'infra existante** : séries → **Prometheus**, last-value → **Redis**, transport → **Mosquitto** ; secrets → **SOPS**.
- **Plugin de référence `sungrow-solar`** validant le framework end-to-end (production PV, conso maison, injection/soutirage réseau, SoC/santé/température batterie).
- **Gates** : reconnaissance des plugins par `check_feature_gate.py`, [[ESSENSYS UX Matrix Gate]] sur le renderer, security-gate (secrets, no-armoire), **diff-guard legacy**.
- **Impact legacy = NUL** : aucun endpoint `/api/serverinfos`, `mystatus`, `myactions`, `done` ni la [[Table D Echange]] n'est touché. Les plugins vivent **exclusivement** côté [[Dual Protocol]] moderne (REST/JSON). C'est une garantie **vérifiée en CI**, pas une intention.
- Décisions à trancher (formalisées ci-dessous, non implicites) : dépôt hôte, runtime backend, modèle UI, persistance, transport, portée MVP.

## Capabilities

### New Capabilities
- `plugin-framework`: contrat de manifest, SDK Go (registre compilé + routes `/api/plugins/*`), package TS renderer générique server-driven, contrat collecteur MQTT, RBAC déclaratif, respect des 3 périmètres de déploiement, gates (UX/feature/security/legacy diff-guard).
- `sungrow-solar`: plugin de référence — collecteur MQTT dérivé de `sungrow_winet_collector.py`, adaptateur Go, descripteur UI (tuile flux instantané + page détail historique), lecture seule, zéro mutation armoire.

### Modified Capabilities
<!-- Aucune : openspec/specs/ est vide, aucun contrat de spec existant modifié. -->

## Impact

- **Nouveau dépôt** (décision par défaut, à confirmer) : `essensys-plugin-framework` — SDK Go (`/go`), package TS (`/ts`), schéma manifest, plugin exemple. Alternative : rattacher à [[Essensys Feature Lifecycle]].
- **4 apps modernes** : ajout du registre compilé (backends Go), du renderer partagé (frontends TS) — **changes-satellites** liés à ce change primaire.
- **Infra** : topics [[Essensys Mosquitto]] `essensys/plugins/<id>/<machine_id>/…`, clés [[Essensys Redis]], séries [[Essensys Prometheus]], secrets SOPS, déploiement via [[Essensys Ansible]] par périmètre.
- **Périmètres** ([[Deployment Perimeters]]) : plugin device-LAN (Sungrow) → collecteur sur CM5 ; cloud via cloudsync ; indisponible en « armoire seule WAN ».
- **Legacy / firmware** : hors périmètre, **aucun impact** (diff-guard bloquant).
- **Mémoire** : ingest `wiki/concepts/plugin-framework.md`, fiche `okf/systems/essensys-plugin-framework.md`, `okf/log.md`, roadmap publique.
- **Décisions §0-ter du prompt** : repo hôte / runtime backend (registre compilé MVP, gRPC Phase 2) / server-driven UI / Prometheus / Mosquitto / MVP avec Sungrow — tranchées dans [[design.md]] avec conséquences.
