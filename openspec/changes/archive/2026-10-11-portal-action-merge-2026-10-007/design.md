## Context

Voir proposal.md (section Why). État actuel dans [[Essensys User Portal Backend]] :

- `POST /api/portal/inject` développe chaque commande lumière ou volet en bloc complet : 590 = `"1"`, l'index visé porte son masque, les autres index 605–622 valent `"0"` (`ExpandLegacyScenarioBlock`). L'action est stockée dans `cloud_actions` (statut `pending`).
- `GET /api/myactions` (armoire, legacy) appelle `FetchPendingActionsForMachine` :
  - il lit jusqu'à 20 actions `pending` de la machine ;
  - il les fusionne **toutes** en une seule action avec `MergeExchangeParams` (dernière valeur par index), sous le GUID de la dernière ;
  - il passe les autres en `delivered`.
- `POST /api/done/{guid}` (`MarkActionDone`) passe déjà en `done` l'action acquittée **et toutes les actions `delivered` de la machine**. L'acquittement groupé est donc déjà correct.
- Le firmware ignore une action lumières/volets dont le bloc 605–622 est incomplet, et accepte au plus 30 paramètres par action (`MaxFirmwareParamsPerAction`). La réponse `myactions` peut contenir plusieurs actions.
- Référence legacy : `essensys-server-backend` `ActionService.BitwiseFusion` (OU bit à bit, 590 jamais fusionné, valeur non numérique → la plus récente).

## Goals / Non-Goals

**Goals**
- Une livraison groupée a le même effet que les commandes appliquées une à une.
- Rester compatible avec le firmware sans le modifier.

**Non-Goals**
- Pas de changement de l'API du portail ni de l'expansion à l'émission.
- Pas de limitation de débit ni d'envoi groupé côté portail : c'est le sujet de essensys-hub/essensys-user-portal-frontend#29.
- Pas de correction du tableau « volets » du wiki contre le firmware (voir D2).

## Decisions

**D1. Fusion par intentions, dans l'ordre.**
- Les actions sont rejouées dans l'ordre de création sur un état vide des index 605–622.
- Pour chaque paramètre d'un index du bloc dont la valeur est un entier non nul `m` :
  - `état[k] |= m` (OU bit à bit) ;
  - `état[opposé(k)] &^= m` : on retire le même bit de l'index opposé, pour que la dernière intention gagne.
- Les `"0"` venus de l'expansion ne portent aucune intention : ils sont ignorés.
- En sortie, on reconstitue le bloc complet (index absents à `"0"`) et 590 = `"1"`.
- *Alternative écartée : OU pur, comme le legacy.* Allumer puis éteindre la même lampe enverrait les deux bits à la fois, et le résultat dépendrait du firmware. Le test existant `lastWinsToggle` montre que la dernière intention est le comportement voulu.
- *Alternative écartée : ne plus fusionner du tout* et livrer une action par commande. 21 lampes prendraient alors 21 cycles de l'armoire, soit plusieurs dizaines de secondes.

**D2. Appariement des index opposés.**
- Lumières : éteindre `605+i` ↔ allumer `611+i` (i = 0…5). Cet appariement est confirmé par le wiki et par le portail.
- Volets : ouvrir `617/618/619` ↔ fermer `620/621/622`. C'est l'appariement du code du portail (`ShuttersPage.tsx`), vérifié par la console cuisine (619/622) et suivi par l'app Android v2.
- Le tableau du wiki ([[Table D Echange]]) indique un autre appariement, avec un écart noté le 2026-10-09 et non tranché. On suit le portail, parce que c'est lui qui émet les commandes. La table d'appariement est une constante unique, testée, facile à corriger si le firmware tranche autrement.

**D3. Séparer le bloc lumières/volets des autres commandes.**
- Une action est « bloc » si elle contient au moins un index 605–622. Son 590 sert alors de déclencheur et n'est pas fusionné (D1).
- Une action est « bloc pure » si elle ne contient que 590 et des index 605–622 (cas de `/inject`). Chaque **suite consécutive** d'actions bloc pures est fusionnée en **une** action de 19 paramètres (590 et 605–622), sous le GUID de la dernière action de la suite. Ne fusionner que des suites consécutives garantit l'ordre : une commande intercalée n'est jamais doublée.
- Une action bloc qui porte aussi d'autres index (morceau d'un `/inject/batch` mixte) est livrée telle quelle, comme les autres actions. Elle respecte déjà la limite de 30 paramètres.
- Les autres actions (lancement de scénario 590 = `"2"`…`"8"`, écriture de scénario, chauffage…) sont livrées **telles quelles, une par une, dans l'ordre**, sans fusion. C'est ainsi que se comporte le serveur legacy. Chacune respecte déjà la limite de 30 paramètres à l'émission (`ChunkExchangeParams`).
- *Alternative écartée : tout fusionner en « dernière valeur ».* On risque de dépasser 30 paramètres (scénarios de 41 octets) et de mêler un lancement de scénario au déclencheur des lumières.

**D4. Acquittement.** On garde `MarkActionDone` tel quel : il passe déjà en `done` toutes les actions `delivered` de la machine. Un test le vérifie pour une livraison de plusieurs actions.

### Tests et non-régression
- Unitaires (`internal/domain`) :
  - « Tout allumer » avec les 21 lampes réelles du portail (index partagés) → tous les bits ;
  - allumer puis éteindre → éteindre ;
  - deux bits sur un même index → OU ;
  - ouvrir puis fermer un volet → fermer ;
  - action non numérique → valeur la plus récente ;
  - bloc toujours complet, 590 = `"1"`.
- Store : bloc et scénario en attente → deux actions livrées, chacune de 30 paramètres au plus, ordre respecté ; acquittement → toutes `done`.
- `NR-backend-9` (référence #33) : la séquence réelle du pilote (21 « allumer ») donne une livraison qui allume les 21 lampes.
- Tous les tests tournent sans armoire (`no-armoire`). Le firmware n'est simulé que par le contrat `myactions`.

## Risks / Trade-offs

- [Appariement des volets incorrect par rapport au firmware (D2)] → constante unique et testée. L'effet n'apparaît que si un ouvrir et un fermer de même bit attendent ensemble. Validation sur l'armoire du pilote, faite par l'utilisateur lui-même.
- [Une armoire reçoit désormais plusieurs actions dans une même réponse `myactions`] → c'est le format legacy, déjà décrit par `LegacyActionsResponse`. Vérifier en production, dans les journaux, que les acquittements suivent.
- [Commandes déjà en attente au moment du déploiement] → elles sont fusionnées avec la nouvelle règle dès la première livraison qui suit. Aucune migration de données n'est nécessaire.

## Migration Plan

1. Fusionner la PR backend, puis déployer avec `deploy-backend.yml` (rôle `cloud_backend`). Aucune migration SQL.
2. Vérifier dans les journaux qu'après un « Tout allumer » de test, les lignes `coalesced N pending` sont suivies d'un `done`. Le test est fait par le mainteneur sur sa propre armoire ou par l'utilisateur pilote, jamais par Claude.
3. **Retour arrière** : redéployer la version précédente du backend. Les données ne changent pas.
