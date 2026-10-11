## 1. Fusion des commandes — essensys-user-portal-backend (essensys-user-portal-backend#34)

- [ ] 1.1 Table d'appariement unique (lumières `605+i` ↔ `611+i`, volets `617/618/619` ↔ `620/621/622`, D2) dans `internal/domain` ; vérifier par un test que chaque index 605–622 a exactement un opposé
- [ ] 1.2 Fusion par intentions (D1) : OU bit à bit, retrait du bit opposé, `"0"` ignorés, valeur non numérique → la plus récente, bloc complet et 590 = `"1"` en sortie ; remplacer `TestMergeExchangeParams_lastWinsToggle` et vérifier `go test ./internal/domain/...` (Tout allumer avec les 21 lampes du portail, allumer→éteindre, deux bits sur un index, ouvrir→fermer)

## 2. Livraison à l'armoire — essensys-user-portal-backend (essensys-user-portal-backend#35)

- [ ] 2.1 `FetchPendingActionsForMachine` (D3) : actions bloc fusionnées en une action de 19 paramètres sous le GUID de la dernière, autres actions livrées telles quelles dans l'ordre ; vérifier par un test que bloc + scénario en attente donnent deux actions de 30 paramètres au plus, dans l'ordre
- [ ] 2.2 Acquittement groupé (D4) : vérifier par un test qu'un `done` sur la livraison passe en `done` toutes les actions regroupées et que `history/latest` renvoie la dernière commande « Exécutée »
- [ ] 2.3 Test `Test_NR_backend_9` (`NR-backend-9`, référence essensys-hub/essensys-user-portal-backend#33) : la séquence réelle du pilote (21 « allumer ») livre une commande qui allume les 21 lampes ; vérifier qu'il échoue sur l'ancien code et passe sur le nouveau

## 3. Livraison — essensys-user-portal-backend, essensys-memory (essensys-user-portal-backend#36)

- [ ] 3.1 Manifest `features/portal-action-merge-2026-10-007.json` (backend) ; vérifier `validate_feature_manifests.py` et `check_feature_gate.py --strict`
- [ ] 3.2 `/checkup portal-action-merge-2026-10-007` vert (build, `go test ./...`, `go vet`, NR, feature-gate, security-gate) et rapport posté sur #33
- [ ] 3.3 Déploiement du backend (`deploy-backend.yml`, lancé par le mainteneur) ; vérifier dans les journaux qu'un « Tout allumer » de test, fait par le mainteneur ou par l'utilisateur pilote, donne une livraison acquittée et les lampes allumées
- [ ] 3.4 Mettre à jour essensys-memory : [[Essensys User Portal Backend]] (fusion des commandes), [[Table D Echange]] (règle 3 appliquée au cloud, appariement des volets retenu), `wiki/log.md`
