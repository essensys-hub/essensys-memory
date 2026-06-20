## Why

Les scénarios domotiques (Je sors, vacances, Personnalisé 1/2, etc.) sont **implémentés dans le firmware** BP_MQX_ETH (8 slots × 41 paramètres, indices **590–919**) et éditables depuis l'écran IHM legacy, mais **absents des UIs modernes** Go/React. Aujourd'hui :

- seul le **bloc partiel 605–622 + trigger 590=1** est géré par `ActionService` / `ExpandLegacyScenarioBlock` (actions lumières/volets immédiates) ;
- le **lancement par bouton** (`590=2..8`) existe dans le MCP mais pas dans les frontends ;
- il n'existe **aucun CRUD** de définitions scénario ni **sync cloud** des slots Scenario1–8, alors que `essensys-cloud-sync-scheduler` fournit déjà l'infrastructure pull/push par profils.

Les utilisateurs ne peuvent pas reproduire depuis le portail ou l'UI locale ce que l'IHM armoire propose depuis des années. La doc raw [[Table D Echange]] mélange encore offsets enum et indices absolus (base 600 vs **592** réelle) — risque d'erreurs à l'implémentation.

## What Changes

- **Cartographie protocole validée** : table indices **590–919** alignée firmware SC944D 099-37 ; correction `essensys-memory/raw/protocol/exchange-table.md` et wiki associé.
- **Deux modes d'exécution documentés et implémentés** :
  - **Mode A** — lancer un scénario mémorisé : inject `{590: "2"}` … `{590: "8"}` sans bloc 605–622 ;
  - **Mode B** — action serveur / slot 1 : `590=1` + expansion backend (605–622 aujourd'hui ; extension opt-in 592–632).
- **API scénarios** (local + portail cloud) : liste slots, lecture/écriture définition 41 paramètres, lancement, métadonnées bitmasks pour l'UI.
- **Page UI « Scénarios »** : grille de boutons (Je sors, vacances, …) + éditeur multi-onglets (alarme, lumières, volets, chauffage, cumulus, réveil) en **jumeaux** `essensys-server-frontend` ↔ `essensys-user-portal-frontend`.
- **Profil sync cloud `scenarios`** : pull/push plages **592–919** (et métadonnées 590–591) via `ExchangePullScheduler` existant ; exclusion du trigger 590 des push continus (reset firmware à 0).
- **Modèle persistant cloud** : `scenario_definitions` (slot, libellé, params JSON) par gateway, aligné sur le cache exchange.

## Capabilities

### New Capabilities

- `scenario-protocol-map` : indices 590–919, offsets `enumScenario`, errata doc raw ; source de vérité firmware 099-37.
- `scenario-launch-modes` : règles Mode A (590=N) vs Mode B (590=1 + bloc) ; intégration `ActionService` / inject portail.
- `scenario-definition-model` : entité 41 paramètres par slot, validation bitmasks, restore preset firmware (`Scenario_Efface`).
- `scenario-crud-api` : routes GET/PUT/POST launch côté server-backend et user-portal-backend.
- `scenario-ui-dashboard` : boutons lancement, dernier scénario lancé (591), états gateway.
- `scenario-ui-editor` : formulaire structuré par domaine fonctionnel ; parité jumeaux frontends.
- `scenario-cloud-sync` : profil sync dédié, push/pull CM5↔OVH, option Settings.
- `scenario-memory-wiki` : mise à jour wiki essensys-memory et changelog versions gateway.

### Modified Capabilities

- `sync-profile-config` (change `essensys-cloud-sync-scheduler`) : profil par défaut **scenarios** (592–919) et règles d'exclusion index 590.
- `gateway-exchange-push` (change `essensys-cloud-sync-scheduler`) : compléter le fallback hardcodé 590+605–622 par les plages scénarios configurées.

## Impact

| Composant | Impact |
|-----------|--------|
| [[Essensys Server Backend]] | Package `scenario` (domain), handlers API, extension `GenerateCompleteBlock` ou `ExpandFullScenario1Block` |
| [[Essensys User Portal Backend]] | CRUD `scenario_definitions`, handlers portail, expansion lancement |
| [[Essensys Server Frontend]] | Nouvelle page Scénarios (dashboard + éditeur) |
| [[Essensys User Portal Frontend]] | Parité UI portail cloud |
| [[Essensys Cloud Sync Scheduler]] | Profil sync `scenarios`, exclusion trigger 590 |
| Firmware BP_MQX_ETH | **Aucune modification** — lecture/écriture via table d'échange existante |
| Protocole legacy | **Aucune modification** des routes `/api/mystatus`, `/api/myactions`, `/api/done`, `/api/serverinfos` |
| [[Table D Echange]] | Correction doc raw (+8 errata), wiki concepts scénarios |

## Liens wiki

- [[Table D Echange]]
- [[Gateway Exchange]]
- [[Essensys Server Backend]]
- [[Essensys User Portal Backend]]
- [[Essensys Cloud Sync Scheduler]]
- [[Client Essensys Legacy]]
