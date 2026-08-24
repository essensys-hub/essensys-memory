## ADDED Requirements

### Requirement: Non-émission absolue sur le bus

Le sniffer SHALL configurer les broches reliées à SDA et SCL exclusivement en entrée, avec les
résistances de tirage internes désactivées, et SHALL n'exposer aucun chemin de code capable de piloter
ces broches en sortie ou d'activer un périphérique I2C matériel sur ces broches.

#### Scenario: Broches en entrée seule pendant tout le cycle de vie

- **WHEN** le firmware démarre, capture, est mis en pause, redémarre sa capture, ou entre en erreur
- **THEN** les broches SDA et SCL restent configurées en entrée avec tirages internes désactivés, à tout instant

#### Scenario: Aucun acquittement généré par le sniffer

- **WHEN** une adresse esclave correspondant à un BA (`0x11`, `0x12`, `0x13`) circule sur le bus
- **THEN** le sniffer se contente de l'enregistrer et ne tire jamais SDA à l'état bas pour acquitter

#### Scenario: Bus inchangé par la présence du sniffer

- **WHEN** le sniffer est connecté puis déconnecté d'un bus en fonctionnement
- **THEN** aucune erreur de dialogue BA supplémentaire n'est observée côté maître (compteurs d'erreurs I2C du SC944D inchangés) sur une fenêtre d'observation d'au moins 10 minutes

### Requirement: Détection des conditions START, repeated START et STOP

Le sniffer SHALL détecter une condition START (transition descendante de SDA pendant que SCL est haut),
une condition STOP (transition montante de SDA pendant que SCL est haut), et SHALL distinguer un START
survenant hors transaction d'un repeated START survenant à l'intérieur d'une transaction en cours.

#### Scenario: Repeated START identifié comme tel

- **WHEN** le maître émet `START + addr(W)` puis, sans STOP intermédiaire, un second START suivi de `addr(R)`
- **THEN** la capture marque le second START comme repeated START et rattache la phase de lecture à la même transaction que la phase d'écriture

#### Scenario: STOP clôt la transaction

- **WHEN** une condition STOP est détectée
- **THEN** la transaction en cours est clôturée et émise, et l'état interne repasse en attente de START

### Requirement: Capture de l'adresse, du bit R/W, des données et des bits d'acquittement

Le sniffer SHALL capturer, pour chaque phase de transaction, l'adresse 7 bits, le bit R/W, la totalité
des octets de données transférés, et l'état du bit d'acquittement (ACK ou NACK) suivant chaque octet, y
compris l'acquittement de l'octet d'adresse.

#### Scenario: NACK sur adresse enregistré

- **WHEN** le maître adresse un esclave absent du bus et reçoit un NACK sur l'octet d'adresse
- **THEN** la capture enregistre l'adresse ciblée, le NACK, et aucun octet de données pour cette transaction

#### Scenario: ACK par octet conservé

- **WHEN** une transaction d'écriture de N octets se déroule normalement
- **THEN** la capture contient les N octets et les N bits d'acquittement correspondants, individuellement adressables

### Requirement: Horodatage microseconde monotone

Le sniffer SHALL horodater chaque transaction avec une source monotone de résolution microseconde, et
SHALL horodater au minimum le START et le STOP de chaque transaction afin que la durée de la transaction
et l'écart entre transactions successives soient calculables.

#### Scenario: Écart entre deux forçages mesurable

- **WHEN** deux transactions successives sont capturées
- **THEN** l'écart temporel entre elles est calculable à partir des horodatages, avec une résolution d'au moins 1 µs

#### Scenario: Horodatage insensible aux pauses USB

- **WHEN** l'hôte cesse temporairement de lire le flux USB puis reprend
- **THEN** les horodatages des transactions capturées pendant cette période restent corrects et monotones

### Requirement: Signalement explicite des pertes et des trames incomplètes

Le sniffer SHALL détecter tout dépassement de capacité de capture ou de transport, et SHALL signaler
explicitement dans le flux de sortie le nombre d'événements perdus. Le sniffer SHALL marquer comme
incomplète toute transaction interrompue par un START inattendu, un silence anormal ou une remise à
zéro, plutôt que de l'émettre comme une transaction valide tronquée.

#### Scenario: Overrun signalé, jamais silencieux

- **WHEN** le tampon de capture déborde et que des événements sont perdus
- **THEN** un enregistrement d'anomalie est émis dans le flux, indiquant la perte et son ampleur, et le décodeur hôte le remonte à l'opérateur

#### Scenario: Transaction tronquée marquée

- **WHEN** une transaction commencée par un START ne se termine par aucun STOP ni repeated START avant un nouveau START
- **THEN** la transaction est émise avec un drapeau « incomplète » et n'est pas présentée comme une trame protocolaire valide

### Requirement: Capture indépendante du protocole applicatif

Le sniffer SHALL capturer et restituer toute transaction I2C présente sur le bus, y compris celles dont
l'adresse esclave, le code de trame ou la longueur ne correspondent à aucun élément connu du protocole
BP↔BA.

#### Scenario: Adresse inconnue capturée sans être écartée

- **WHEN** une transaction cible une adresse esclave hors de l'ensemble connu `0x11`-`0x13`
- **THEN** la transaction est capturée et restituée intégralement, marquée comme non reconnue au niveau protocolaire, et non supprimée du flux
