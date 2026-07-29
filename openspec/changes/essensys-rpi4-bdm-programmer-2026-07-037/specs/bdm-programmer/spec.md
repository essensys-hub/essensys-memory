## ADDED Requirements

### Requirement: Backup complet et vérifié avant toute écriture

Le système SHALL lire l'intégralité des 512 KB de flash interne (`0x0-0x7FFFF`) via BDM et produire un
fichier `backup-<serial>-<date>.bin` (et `.s19`) accompagné d'un hash `sha256`, **avant** d'autoriser
toute commande d'écriture (`erase-app`, `program`) sur la même cible. Le système SHALL refuser toute
commande d'écriture si aucun backup vérifié n'existe pour la session/cible en cours.

#### Scenario: Écriture refusée sans backup préalable

- **WHEN** un opérateur ou le pipeline invoque `erase-app` ou `program` sans backup vérifié préalable pour la cible
- **THEN** la commande échoue immédiatement, sans envoyer aucune commande WRITE/erase BDM à la cible

#### Scenario: Backup vérifié débloque l'écriture

- **WHEN** un `backup` complet 512 KB a été produit, relu, et son `sha256` calculé et stocké
- **THEN** les commandes `erase-app` et `program` deviennent autorisées pour cette cible

### Requirement: Backup relu et vérifié par relecture, pas seulement écrit sur disque

Le système SHALL relire le backup depuis le support de stockage après écriture et comparer son
`sha256` à celui calculé pendant la lecture BDM, avant de le considérer comme "vérifié".

#### Scenario: Divergence de hash après écriture disque

- **WHEN** le hash du fichier backup relu depuis le disque diffère du hash calculé pendant la lecture BDM
- **THEN** le backup est marqué non vérifié et aucune écriture flash n'est autorisée

### Requirement: Erase et program limités à la zone application

Le système SHALL restreindre les opérations `erase-app` et `program` à la plage d'adresses
`0x3000-0x7DFFF` (zone application). Le système SHALL refuser toute tentative d'effacement ou
d'écriture en dehors de cette plage via ces commandes.

#### Scenario: Tentative d'effacement du bootloader refusée

- **WHEN** une commande d'effacement cible une adresse dans `0x0-0x2FFF` (bootloader)
- **THEN** la commande échoue et aucun cycle d'effacement n'est envoyé à la cible

#### Scenario: Persistance préservée après flash

- **WHEN** un cycle complet `erase-app` puis `program` est exécuté
- **THEN** la zone `0x7E000-0x7EFFF` (`Tb_Echange[]`) reste bit-à-bit identique à son état avant le cycle, vérifié par relecture

### Requirement: Interdiction d'écriture dans le champ de sécurité flash CFM

Le système SHALL bloquer inconditionnellement toute écriture dans la plage `0x400-0x417` (CFM
Configuration Field complet, incluant le Security Word `0x414-0x417`), sauf procédure de déverrouillage
explicite, documentée séparément et hors périmètre MVP.

#### Scenario: Écriture dans le Security Word refusée

- **WHEN** une commande `program` ou toute opération d'écriture BDM cible une adresse dans `0x400-0x417`
- **THEN** l'opération est refusée avant tout envoi de commande WRITE BDM, quelle que soit la source de l'image

#### Scenario: Image chevauchant le CFM rejetée au chargement

- **WHEN** l'image `.s19` fournie en entrée de `program` contient des enregistrements S-record couvrant une adresse dans `0x400-0x417`
- **THEN** `program` échoue au chargement de l'image, avant toute communication BDM d'écriture

### Requirement: Verify par relecture octet-à-octet après programmation

Le système SHALL relire par BDM toute la zone programmée (`0x3000` jusqu'à la fin de l'image) après
`program` et comparer chaque octet à l'image source. Le système SHALL rapporter la programmation comme
échouée si une seule divergence est détectée.

#### Scenario: Divergence détectée en verify

- **WHEN** un octet relu après programmation diffère de l'octet correspondant dans l'image `.s19` source
- **THEN** le résultat de `verify` est FAIL, le pipeline/CLI rapporte l'adresse en divergence, et aucune conclusion de succès n'est émise

#### Scenario: Verify OK puis reset confirmé

- **WHEN** `verify` rapporte une correspondance octet-à-octet complète
- **THEN** le système déclenche `reset` et confirme, après reboot, que le bootloader valide le CRC applicatif (`.APP_CRC` @ `0x3000`) et démarre l'application

### Requirement: Refus de programmer une image sans CRC-16 injecté

Le système SHALL refuser d'exécuter `program` si l'image `.s19` fournie contient le CRC placeholder
connu (`0x0102`) à l'offset `.APP_CRC` (`0x3000`) plutôt qu'un CRC-16 calculé et injecté.

#### Scenario: Image avec CRC placeholder rejetée

- **WHEN** l'octet/mot CRC à `0x3000` de l'image fournie vaut le placeholder `0x0102`
- **THEN** `program` échoue avant toute écriture, avec un message explicite demandant l'injection CRC-16 préalable

### Requirement: Identification de la cible avant écriture

Le système SHALL lire une identité de la cible (a minima la version applicative à `0x3002` et le CRC
courant à `0x3000`, obtenus en mode halted post-BKPT) avant toute opération d'écriture, et SHALL
inclure cette identité dans le rapport avant/après.

#### Scenario: Rapport avant/après inclut les versions

- **WHEN** un cycle `program` + `verify` + `reset` se termine, succès ou échec
- **THEN** le rapport final inclut la version et le CRC lus avant écriture et, en cas de succès, après écriture

### Requirement: Portée hors périmètre documentée pour les mémoires SPI externes

Le système SHALL documenter explicitement que la flash SPI OTA (`SST25VF016B`) et l'EEPROM SPI
(`25AA02E48T`) ne sont pas couvertes par le backup/flash BDM interne, afin qu'un opérateur ne conclue
pas à tort qu'un backup complet de la carte a été réalisé.

#### Scenario: Documentation explicite de la limite de couverture

- **WHEN** un opérateur consulte la documentation du programmeur BDM
- **THEN** il trouve une mention explicite que le backup couvre uniquement la flash interne MCF52259 (512 KB), pas les mémoires SPI externes
