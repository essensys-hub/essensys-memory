## ADDED Requirements

### Requirement: Runner self-hosted jamais exposé aux PR de forks

Le runner self-hosted `[self-hosted, rpi4, bdm, sc944d]` SHALL n'être déclenché que par des tags
protégés (`fw-v*`) ou des `workflow_dispatch` manuels sur des branches protégées. Le workflow de flash
SHALL NOT se déclencher sur un événement `pull_request` provenant d'un fork.

#### Scenario: PR de fork ne déclenche pas le job flash

- **WHEN** une pull request provenant d'un fork externe est ouverte ou mise à jour
- **THEN** le job `flash` (runner self-hosted rpi4) ne s'exécute pas, quel que soit le contenu de la PR

#### Scenario: Tag fw-v* déclenche le pipeline complet

- **WHEN** un tag correspondant au motif `fw-v*` est poussé sur une branche protégée
- **THEN** les jobs `build`, `crc-inject`, `flash`, `report` s'enchaînent selon le gate d'approbation défini ci-dessous

### Requirement: Gate reviewer humain obligatoire avant le job flash

Le job `flash` SHALL s'exécuter dans un environnement GitHub (`hardware-flash`) exigeant l'approbation
d'au moins un reviewer humain avant exécution.

#### Scenario: Job flash bloqué sans approbation

- **WHEN** le job `flash` est prêt à démarrer dans l'environnement `hardware-flash`
- **THEN** son exécution reste en attente tant qu'un reviewer désigné n'a pas explicitement approuvé le déploiement

### Requirement: Interlock CI — backup, CRC-16 et identité cible avant flash

Le job `flash` SHALL échouer avant toute opération d'écriture si l'une des conditions suivantes n'est
pas remplie : (1) un backup complet et vérifié de la cible existe pour cette exécution ; (2) l'image
`.s19` fournie porte un CRC-16 injecté (pas le placeholder `0x0102`) ; (3) l'identité lue sur la cible
(IDCODE/CSR ou signature équivalente) correspond au MCF52259 attendu.

#### Scenario: Flash refusé si CRC non injecté

- **WHEN** l'artefact `.s19` produit par le job `crc-inject` ne porte pas de CRC-16 valide à `0x3000`
- **THEN** le job `flash` échoue avant toute commande d'écriture BDM

#### Scenario: Flash refusé si identité cible inattendue

- **WHEN** l'identité lue sur la cible avant écriture ne correspond pas à un MCF52259 attendu
- **THEN** le job `flash` échoue et aucune commande erase/program n'est envoyée

### Requirement: Image flashée conforme à essensys-gcc avec CRC-16 injecté

Le pipeline SHALL flasher exclusivement une image `.s19` produite par `essensys-gcc` (`build.sh bp`)
et post-traitée par l'étape `crc-inject` (consommant l'outil issu de `essensys-gcc#14`) avant tout
passage au job `flash`.

#### Scenario: Chaîne build → crc-inject → flash respectée

- **WHEN** le pipeline s'exécute de bout en bout sur un tag `fw-v*`
- **THEN** l'artefact consommé par le job `flash` est celui produit par `crc-inject`, jamais l'artefact brut de `build`

### Requirement: Verify et rapport avant/après obligatoires dans le job flash

Le job `flash` SHALL exécuter une étape de vérification par relecture après programmation et produire,
dans le job `report`, un résumé incluant les versions/CRC avant et après flash, le résultat PASS/FAIL,
et les hashes de backup.

#### Scenario: Rapport final PASS avec hashes

- **WHEN** le cycle backup → erase-app → program → verify → reset se termine avec succès
- **THEN** le job `report` publie un résumé PASS incluant le hash sha256 du backup, les versions avant/après, et le résultat du verify

#### Scenario: Rapport final FAIL sans conclusion de succès

- **WHEN** verify échoue ou toute étape du job `flash` échoue
- **THEN** le job `report` publie un résumé FAIL détaillant l'étape en échec ; le pipeline ne prétend jamais à un succès partiel

### Requirement: Workflow de rollback disponible et testé

Le pipeline SHALL fournir un workflow `workflow_dispatch` de rollback distinct, capable de reflasher le
backup pré-flash correspondant à une cible donnée, suivi d'un `verify` et d'un `reset`.

#### Scenario: Rollback restaure l'image précédente

- **WHEN** un opérateur déclenche le workflow de rollback en désignant un backup pré-flash existant
- **THEN** le pipeline reflashe intégralement la zone application depuis ce backup, vérifie par relecture, et confirme le boot

### Requirement: Aucun secret ni contenu sensible loggé

Le pipeline SHALL NOT logger le contenu brut d'un backup de flash, ni tout secret réseau, dans les
sorties de job visibles. Seul le token d'enregistrement du runner self-hosted est un secret requis, géré
hors du contenu du workflow.

#### Scenario: Logs de job sans dump de flash en clair

- **WHEN** le job `flash` produit ses logs standard
- **THEN** aucun octet du contenu de la flash (backup ou image programmée) n'apparaît en clair dans les logs, seul le hash sha256 et les métadonnées (version, CRC, adresses) y figurent

### Requirement: Cible CI limitée à une carte de test dédiée

Le pipeline automatique (`fw-v*` tag ou `workflow_dispatch` standard) SHALL cibler exclusivement une
carte de test SC944D dédiée, jamais une carte de production, sans gate physique distinct et documenté
séparément.

#### Scenario: Pipeline standard ne cible que la carte de test

- **WHEN** le pipeline s'exécute via son déclencheur standard (tag ou workflow_dispatch documenté)
- **THEN** la cible physique flashée est la carte de test dédiée branchée en permanence au runner self-hosted, identifiée et confirmée par lecture d'identité avant écriture
