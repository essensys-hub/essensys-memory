## ADDED Requirements

### Requirement: Dépôt dédié avec séparation firmware / hôte / captures

Le projet SHALL vivre dans un dépôt `essensys-i2c-ba-sniffer` distinct, séparant le firmware Pico, le
décodeur hôte, les captures de référence versionnées, les tests et la documentation. Le projet SHALL
n'introduire aucune modification dans `essensys-board-SC944D`, `essensys-board-SC942C`,
`essensys-server-backend` ou `essensys-user-portal-backend`.

#### Scenario: Aucune dépendance d'écriture sur les dépôts firmware

- **WHEN** le sniffer est construit, testé et utilisé
- **THEN** aucun fichier des dépôts `essensys-board-*` n'est modifié, ceux-ci restant des sources de référence en lecture seule

### Requirement: Sortie machine-lisible NDJSON

Le sniffer SHALL produire, pour chaque transaction décodée, un enregistrement JSON sur une ligne
contenant au minimum : horodatage source microseconde, horodatage horloge murale reconstruit, adresse
brute, identité BA résolue, code de trame, octets bruts en hexadécimal, bits d'acquittement, résultat de
vérification CRC de la requête et de la réponse, drapeaux d'anomalie, et événements sémantiques dérivés.

#### Scenario: Enregistrement exploitable sans le décodeur

- **WHEN** un enregistrement NDJSON est produit
- **THEN** il contient les octets bruts de la transaction, permettant un re-décodage complet ultérieur sans la capture d'origine

#### Scenario: Capture rejouable par une version ultérieure du décodeur

- **WHEN** une capture enregistrée est traitée par une version plus récente du décodeur
- **THEN** le re-décodage produit les champs sémantiques de la nouvelle version, à partir des octets bruts conservés

### Requirement: Sortie texte lisible en temps réel

Le sniffer SHALL proposer une sortie texte compacte, une ligne par transaction, lisible directement dans
un terminal, indiquant l'écart temporel depuis la transaction précédente, le BA, le type de trame, les
événements dérivés et le statut d'acquittement.

#### Scenario: Lecture directe sans outil hôte

- **WHEN** un opérateur ouvre le port série USB du Pico avec un terminal standard, sans installer le décodeur hôte
- **THEN** il voit au minimum l'horodatage, l'adresse BA et le code de trame de chaque transaction en clair

### Requirement: Enregistrement et rejeu de captures

Le sniffer SHALL permettre d'enregistrer une session dans un fichier de capture et de rejouer ce fichier
dans le décodeur hors ligne, sans matériel connecté.

#### Scenario: Analyse hors ligne d'un incident

- **WHEN** une capture réalisée en intervention est rejouée sur un poste sans Pico ni armoire
- **THEN** le décodeur produit le même diagnostic que sur site, sans accès matériel

### Requirement: Filtrage sans perte d'information

Le sniffer SHALL permettre de filtrer l'affichage par BA, par code de trame ou par présence d'anomalie,
et SHALL garantir que le filtrage n'affecte que l'affichage, jamais le contenu de la capture
enregistrée.

#### Scenario: Capture complète malgré un affichage filtré

- **WHEN** l'opérateur filtre l'affichage sur un seul BA pendant l'enregistrement
- **THEN** le fichier de capture contient l'intégralité du trafic observé, tous BA confondus

### Requirement: Statistiques de session

Le sniffer SHALL produire, à la demande ou en fin de session, un résumé comportant : nombre de
transactions par BA, répartition par code de trame, nombre d'erreurs CRC de requête et de réponse,
nombre de NACK, nombre de répétitions détectées, nombre d'événements perdus, et durée du silence le plus
long observé sur le bus.

#### Scenario: Comparaison avant/après d'une intervention

- **WHEN** deux sessions sont capturées dans les mêmes conditions, avant et après une modification
- **THEN** leurs résumés sont comparables et permettent de quantifier une variation du taux d'erreur

#### Scenario: Silence prolongé rapporté comme un fait, pas comme une panne

- **WHEN** aucune transaction n'est observée pendant une longue période
- **THEN** le résumé rapporte la durée de silence sans la qualifier de défaillance, le trafic étant événementiel par conception

### Requirement: Corrélation avec les traces backend

Le sniffer SHALL fournir une commande de corrélation prenant en entrée une capture et un relevé
d'actions côté backend (actions distribuées via les endpoints legacy IoT et indices de la table
d'échange), et produisant une mise en correspondance temporelle indiquant les actions demandées sans
trame I2C observée et les trames I2C observées sans action correspondante.

#### Scenario: Action demandée sans trame observée

- **WHEN** une action est enregistrée côté backend et qu'aucune trame I2C correspondante n'apparaît dans la fenêtre temporelle attendue
- **THEN** la corrélation la signale comme « demandée, non émise sur le bus », isolant le défaut en amont du bus

#### Scenario: Trame observée sans action backend

- **WHEN** une trame de forçage est observée sans action backend correspondante
- **THEN** la corrélation la signale comme « émise sans demande portail connue », piste d'une commande locale ou automatique

### Requirement: Décodeur testé sur des captures de référence versionnées

Le projet SHALL versionner un corpus de captures de référence accompagnées de leurs résultats de
décodage attendus, et SHALL exécuter le décodeur contre ce corpus en intégration continue, sans
matériel.

#### Scenario: Régression de décodage détectée en CI

- **WHEN** une modification du décodeur change le résultat produit sur une capture de référence
- **THEN** la CI échoue en exposant la différence entre attendu et obtenu

#### Scenario: Corpus couvrant les cas dégradés

- **WHEN** le corpus de référence est constitué
- **THEN** il contient au minimum une capture nominale, une capture avec erreur CRC, une capture avec NACK d'adresse, une capture avec répétitions et abandon, et une capture avec transaction tronquée

### Requirement: Procédure de connexion documentée avec vérification électrique préalable

La documentation SHALL décrire la procédure de branchement, imposer la mesure du niveau logique du bus
avant toute connexion du Pico, imposer le branchement armoire hors tension, et préciser la conduite à
tenir si le bus n'est pas en 3,3 V.

#### Scenario: Opérateur bloqué avant une connexion risquée

- **WHEN** un opérateur suit la procédure et mesure un niveau logique de bus incompatible avec les entrées du microcontrôleur
- **THEN** la procédure lui impose l'interposition d'un étage d'adaptation avant connexion, plutôt qu'un branchement direct

#### Scenario: Limites de l'outil énoncées d'emblée

- **WHEN** un opérateur consulte la documentation d'accueil du dépôt
- **THEN** il y trouve, avant tout mode d'emploi, l'énoncé des limites : aucune visibilité sur l'état réel des relais, sur les appuis locaux des boîtiers, ni sur le chauffage
