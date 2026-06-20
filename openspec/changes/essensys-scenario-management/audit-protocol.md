# Audit protocole scénarios — Phase 0

**Date** : 2026-06-16  
**Référence firmware** : `essensys-board-SC944D/SC944D/Prog/099-37/BP_MQX_ETH`  
**Change** : `essensys-scenario-management`

## Synthèse

| Source | État avant audit | Action |
|--------|------------------|--------|
| Firmware `TableEchange.h` + `Scenario.c` | Source de vérité | Référence |
| `essensys-doc/archi/exchange-table.md` | Corrigé (errata juin 2026) | Aligné firmware |
| `essensys-memory/raw/protocol/exchange-table.md` | **Décalage +8**, 590=1 uniquement, pas de slots 2–8 | **Corrigé Phase 0** |
| `essensys-server-backend` | 605–622 + 590=1 (Mode B partiel) | Package `internal/scenario/` |
| `test_chb3.py` | Index 613 Allumer CHB LSB | **Confirmé** |
| HA `table_reference.json` | Clés 605–622 pour lumières/volets | **Confirmé** |

## Cartographie firmware (099-37)

| Indice absolu | Mnemonique | Rôle |
|---------------|------------|------|
| 590 | `Scenario` | Numéro scénario à lancer (0=aucun, 1=serveur, 2–8=slots) |
| 591 | `Scenario_DernierLance` | Dernier scénario lancé (lecture) |
| 592–632 | `Scenario1` | Scénario serveur / inject Internet (41 param.) |
| 633–673 | `Scenario2` | Je sors |
| 674–714 | `Scenario3` | Je pars en vacances |
| 715–755 | `Scenario4` | Je rentre |
| 756–796 | `Scenario5` | Je vais me coucher |
| 797–837 | `Scenario6` | Je me lève |
| 838–878 | `Scenario7` | Personnalisé 1 |
| 879–919 | `Scenario8` | Personnalisé 2 |

**Formule** : indice absolu = `592 + (slot-1)*41 + offset` où `slot ∈ [1,8]`, `offset ∈ [0,40]`.

`Scenario_NB_VALEURS` = **41** (633 − 592).

## Paramètres Scenario1 (offsets → indices absolus)

| Offset | Indice | Paramètre |
|--------|--------|-----------|
| 0 | 592 | Confirme_Scenario |
| 1 | 593 | Alarme_ON |
| 2–12 | 594–604 | AlarmeConfig (11) |
| 13–18 | 605–610 | Eteindre lumières |
| 19–24 | 611–616 | Allumer lumières |
| 25–27 | 617–619 | Ouvrir volets |
| 28–30 | 620–622 | Fermer volets |
| 31 | 623 | Securite |
| 32 | 624 | Machines |
| 33–36 | 625–628 | Chauffage zj/zn/zsb1/zsb2 |
| 37 | 629 | Cumulus |
| 38 | 629 | Reveil_Reglage → **630** |
| 39 | 631 | Reveil_ON |
| 40 | 632 | Efface |

Correction ligne Reveil : offset 38 = **630**, offset 39 = **631**, offset 40 = **632**.

## Écarts doc raw vs firmware

| Sujet | Doc raw (avant) | Réel | Statut |
|-------|-----------------|------|--------|
| Base enumScenario | « commence à 600 » | Scenario1 = **592** | Corrigé |
| Index 590 | Toujours `"1"` | 0–8 ; `"1"` = serveur, `"2"`–`"8"` = lancer slot | Corrigé |
| Table 600–622 | Nomme alarme/lumières | Confond offset+600 et indices **605–622** réels | Corrigé |
| Indices 623–639 | Allumer PDE, volets, chauff | **623–632** dans Scenario1 ; 633+ = slot suivant | Corrigé |
| Slots Scenario2–8 | Absents | 633–919 | Ajouté |
| Exemple Je Sors | Inject 601, 628–631 | **`{590:"2"}`** suffit (Mode A) | Corrigé |
| Exemple alarme 607 | « 602+5=607 » | AlarmeConfig offset 5 = **599** (592+7) | Corrigé |
| C comment « 13 → 613 » | Offset 13 = 613 | Offset 13 = **605** (Eteindre PDV LSB) | Corrigé |

## Écarts backend vs firmware

| Comportement | Backend actuel | Attendu | Package scenario |
|--------------|----------------|---------|------------------|
| Lancer Je sors | MCP seulement `{590:2}` | Idem | `LaunchParams(2)` |
| Toggle lampe | `GenerateCompleteBlock` 605–622 + 590=1 | Mode B | `ExpandModeB` |
| Écriture slot 41 params | Non implémenté | 2 actions × 30 max | `WriteDefinitionChunks` |
| Fusion 590 | Jamais OR | Idem firmware | Inchangé |
| Sync cloud | 590 + 605–622 hardcodé | 592–919 profil dédié | Phase 5 |

## Vérifications croisées indépendantes

| Paramètre | Firmware | test_chb3 | HA table_reference | MCP |
|-----------|----------|-----------|-------------------|-----|
| Allumer CHB LSB | offset 21 → 613 | INDEX_ON=613 | keys 613 | k=613 v=64 chevet |
| Eteindre CHB LSB | offset 15 → 607 | INDEX_OFF=607 | keys 607 | — |
| OuvrirVolets PDV | offset 25 → 617 | — | keys 617 | — |
| FermerVolets PDE | offset 30 → 622 | — | keys 622 | — |
| Lancer Je sors | Tb_Echange[590]=2 | — | — | 590=2 |

## Mapping lancement (enum SCENARIOS)

| Valeur 590 | Libellé | Slot table |
|------------|---------|------------|
| 1 | uc_SCENARIO_SERVEUR | Scenario1 |
| 2 | uc_SCENARIO_JE_SORS | Scenario2 |
| 3 | uc_SCENARIO_JE_PARS_EN_VACANCES | Scenario3 |
| 4 | uc_SCENARIO_JE_RENTRE | Scenario4 |
| 5 | uc_SCENARIO_JE_ME_COUCHE | Scenario5 |
| 6 | uc_SCENARIO_JE_ME_LEVE | Scenario6 |
| 7 | uc_SCENARIO_PERSO | Scenario7 |
| 8 | uc_SCENARIO_LIBRE | Scenario8 |

Firmware remet `Tb_Echange[590]` à 0 après prise en compte (`vd_GestionScenario`).

## Bitmasks UI (HA table_reference.json)

Les entrées lumières/volets utilisent les indices **605–622** (Scenario1) pour les commandes Mode B inject. Exemples confirmés :

- 613 / bit 64 : petite chambre 3 allumer
- 607 / bit 64 : petite chambre 3 éteindre
- 617 / 620 : volets ouvrir/fermer PDV

## Conclusion Phase 0

- **0 écart non expliqué** restant pour SC944D 099-37.
- Variantes firmware (SC945D, autres prog) : recalculer `Scenario1` depuis `TableEchange.h` local si différent de 592.
- Implémentation backend : `essensys-server-backend/internal/scenario/` avec constantes et fonctions Mode A/B.
