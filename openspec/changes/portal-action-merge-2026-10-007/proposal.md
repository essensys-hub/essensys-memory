> Ticket : [essensys-hub/essensys-user-portal-backend#33](https://github.com/essensys-hub/essensys-user-portal-backend/issues/33) — Feature ID `portal-action-merge-2026-10-007`
> Origine : premier utilisateur pilote, [essensys-hub/essensys-user-portal-frontend#29](https://github.com/essensys-hub/essensys-user-portal-frontend/issues/29)

## Why

Quand plusieurs commandes du portail attendent la même armoire, le hub cloud les fusionne en gardant la **dernière valeur par index**. Or les lampes et les volets d'une même zone partagent un index et ne se distinguent que par un bit, et chaque commande porte le bloc complet 605–622 rempli de `"0"`. Résultat en production (2026-10-07, utilisateur pilote) : « Tout allumer » livre une commande qui n'allume qu'une lampe. L'armoire l'acquitte, le portail affiche « Exécutée », et l'utilisateur constate que « rien ne marche ».

Le serveur local de référence ([[Essensys Server Backend]], `ActionService.BitwiseFusion`) fusionne par **OU bit à bit**, comme le prévoit la règle 3 de [[Table D Echange]]. Le hub cloud ([[Essensys User Portal Backend]]) s'en écarte.

## What Changes

- **Fusion des commandes en attente** (`GET /api/myactions` côté armoire) :
  - **OU bit à bit** sur les index lumières et volets (605–622) ;
  - pour une même lampe ou un même volet, **la dernière intention gagne** : allumer puis éteindre donne éteindre, et réciproquement ;
  - l'index 590 (déclencheur) n'est pas fusionné et reste à `"1"` pour un bloc lumières/volets ;
  - les autres index gardent la règle « dernière valeur ».
- **Respect de la limite firmware** : une commande livrée ne dépasse jamais 30 paramètres. Les commandes qui ne relèvent pas du bloc lumières/volets (scénarios, chauffage…) sont livrées à part, dans l'ordre.
- **Tests** : unitaires sur la fusion, plus un test de non-régression `NR-backend-9` qui référence #33.
- Aucun changement de l'API du portail (`/api/portal/inject`, `/inject/batch`) ni du protocole armoire. Seul le contenu de la commande fusionnée change, pour devenir conforme au comportement legacy.

## Capabilities

### New Capabilities
- `portal-command-delivery` : livraison à l'armoire des commandes en attente émises depuis le portail (fusion, limite de paramètres, acquittement).

### Modified Capabilities
<!-- Aucune : pas de spec existante sur ce sujet. -->

## Impact

- **essensys-user-portal-backend** :
  - `internal/domain/merge_params.go` et ses tests ;
  - `internal/data/store.go` (`FetchPendingActionsForMachine`) ;
  - test `NR-backend-9`.
- **Legacy IoT** : aucune modification du firmware BP_MQX_ETH ni du protocole `myactions`/`done`. La commande livrée redevient conforme à ce qu'attend l'armoire (bloc complet 605–622, OU bit à bit).
- **Table d'échange** : index 590 et 605–622 concernés. Les appariements allumer/éteindre et ouvrir/fermer suivent ceux du portail (voir design D2).
- **Toutes les armoires pilotées par le portail** sont concernées, pas seulement celle du pilote.
- Wiki : [[Essensys User Portal Backend]], [[Table D Echange]].
