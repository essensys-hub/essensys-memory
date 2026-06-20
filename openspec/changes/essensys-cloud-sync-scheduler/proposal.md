## Why

La table d'échange domotique (indices **13–348** planning chauffage, **566–589** volets, **349–352** modes immédiats, etc.) n'est **pas remontée automatiquement** par le cycle firmware `serverinfos → mystatus` : le BP_MQX_ETH limite à **30 indices** par requête. Aujourd'hui :

- le cache Redis gateway et le cache cloud `gateway_exchange_cache` ne contiennent que les indices déjà injectés ou listés dans `serverinfos` ;
- la **sync manuelle** (bouton « Sync armoire » chauffage) fonctionne mais n'est pas planifiée ;
- `cloudsync` pousse une liste **hardcodée** (`exchangePushIndices()` dans [[Essensys Server Backend]]) toutes les ~5 s sans **pull armoire** préalable pour les plages 13–348.

Résultat : sur `mon.essensys.fr/portal/heating`, **SDB1** affichait du Confort alors que l'armoire était en OFF — données cloud obsolées ou absentes.

Il faut une **planification configurable** (défaut **toutes les 3 h**) et un **menu admin Sync Cloud** pour déclarer quelles plages de la table de ref synchroniser, à quelle fréquence, avec journalisation.

## What Changes

- **Modèle de configuration** `SyncProfile` : plages d'indices (k min–max ou liste), intervalle (cron ou heures), options `pull_from_armoire`, `push_to_cloud`, activation.
- **Scheduler gateway** : cron / ticker intégré à `cloudsync` (défaut **3 h**) exécutant pour chaque profil actif :
  1. **Pull** — rotation `serverinfos` (réutilise `HeatingSyncManager` généralisé) jusqu'à couverture complète de la plage ;
  2. **Push** — `POST /api/gateway/exchange` vers OVH avec merge (comportement actuel `UpsertGatewayExchange`).
- **API cloud admin** : CRUD profils sync par gateway / machine, historique des exécutions, déclenchement manuel « Sync now ».
- **Menu admin « Sync Cloud »** (`essensys-support-site` → onglet Admin, rôle `admin_global`) : liste des profils, éditeur de plages, intervalle, statut dernière sync, console/logs.
- **Valeur par défaut** : profils pré-remplis pour les 4 zones chauffage (13–96, 97–180, 181–264, 265–348) + volets (566–585) + modes 349–352, intervalle **3 h**.
- **Documentation** : mise à jour [[Gateway Exchange]], fiches backend, `essensys-memory` roadmap.

## Capabilities

### New Capabilities

- `sync-profile-config` : modèle, validation (≤30 indices/cycle firmware), persistance cloud + réplication vers gateway.
- `sync-scheduler-gateway` : exécution planifiée pull→push sur la CM5, logs structurés, idempotence.
- `sync-cloud-admin-ui` : écran admin Sync Cloud (CRUD profils, intervalle, sync manuelle, console).
- `sync-execution-history` : journal des runs (succès/partiel/échec, octets reçus, durée, prochaine exécution).

### Modified Capabilities

- `gateway-exchange-push` : indices poussés lus depuis profils actifs au lieu de liste hardcodée uniquement (fallback legacy conservé).
- `heating-sync-manual` : aligné sur le même moteur de pull que le scheduler (pas de duplication).

## Impact

| Composant | Impact |
|-----------|--------|
| [[Essensys Server Backend]] | Scheduler, generalisation `HeatingSyncManager` → `ExchangePullScheduler`, config locale |
| [[Essensys User Portal Backend]] | Tables `sync_profiles`, `sync_runs`, API admin + push config vers gateway |
| [[Essensys Support Site]] | Nouvel onglet **Sync Cloud** dans Admin |
| [[Essensys Server Frontend]] / [[Essensys User Portal Frontend]] | Consommation cache à jour ; pas de menu admin (LAN user) |
| [[Essensys Ansible]] | Variables déploiement, timer systemd optionnel |
| Protocole legacy | **Aucune modification** des routes `/api/mystatus`, `/api/myactions`, `/api/done` — seul le contenu temporaire de `GET /api/serverinfos` en mode pull planifié (déjà le cas pour sync chauffage manuelle) |

## Liens wiki

- [[Table D Echange]]
- [[Gateway Exchange]]
- [[Cloud Relay]]
- [[Essensys Server Backend]]
- [[Essensys User Portal Backend]]
