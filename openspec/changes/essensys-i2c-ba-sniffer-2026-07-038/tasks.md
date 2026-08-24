## 1. Préconditions matérielles — gates bloquants

- [ ] 1.1 **[À LEVER, bloquant]** Identifier le point de piquage physique SDA / SCL / GND (connecteur ou bornier) sur le SC944D ou sur un BA, sur carte assemblée — photographier et documenter, ne pas deviner depuis le code
- [ ] 1.2 **[À LEVER, bloquant]** Mesurer au multimètre la tension de repos SDA et SCL, armoire sous tension, masse de référence = masse armoire — consigner la valeur dans `docs/`
- [ ] 1.3 Si le bus est en 5 V : approvisionner et câbler un buffer 5 V-tolérant alimenté en 3,3 V (74LVC2G17 ou équivalent), une voie par ligne — **aucune connexion directe au Pico**
- [ ] 1.4 Relever la valeur des résistances de tirage et la longueur de bus en armoire, pour documenter la marge de charge disponible
- [ ] 1.5 Rédiger et valider la procédure de branchement **armoire hors tension**, avec la conduite à tenir en cas de doute
- [ ] 1.6 Approvisionner le matériel : Pico (RP2040 ou RP2350), analyseur logique USB bas coût pour l'oracle, isolateur USB pour les interventions sur installation en service

## 2. Amorçage du dépôt

- [ ] 2.1 Créer le dépôt `essensys-i2c-ba-sniffer` avec l'arborescence `firmware/ host/ captures/ docs/ tests/`
- [ ] 2.2 README d'accueil énonçant **les limites intrinsèques en tête** : pas d'état réel des relais, pas d'appuis locaux BA, pas de chauffage, trafic événementiel
- [ ] 2.3 Documenter dans `docs/protocol.md` le protocole BP↔BA en citant les fichiers et lignes sources (`ba.c`, `ba_i2c.c`, `global.h`, `application.h`, `slavenode.c`, `crc.c`) — pointeurs de code, pas copie de code
- [ ] 2.4 Mettre en place la CI hôte : lint, tests unitaires du décodeur, exécution sur les captures de référence — aucune dépendance matérielle

## 3. Firmware Pico — capture passive

- [ ] 3.1 Squelette firmware SDK Pico, broches SDA/SCL en entrée seule, tirages internes désactivés, aucun périphérique I2C matériel instancié
- [ ] 3.2 Écrire le test de non-émission : vérification statique qu'aucun chemin de code ne configure ces broches en sortie (revue + assertion au démarrage)
- [ ] 3.3 Programme PIO `SM_DATA` : échantillonnage de SDA sur front montant de SCL
- [ ] 3.4 Programme PIO `SM_EVENT` : détection START / STOP (transition de SDA pendant SCL haut)
- [ ] 3.5 Machine à états cœur 0 : `IDLE → START → ADDR+RW → ACK → DATA*+ACK* → reSTART | STOP`, avec distinction START / repeated START
- [ ] 3.6 Horodatage µs monotone sur START et STOP de chaque transaction
- [ ] 3.7 Tampon circulaire + détection d'overrun, avec émission d'un enregistrement d'anomalie explicite en cas de perte
- [ ] 3.8 Marquage des transactions incomplètes (START sans STOP ni repeated START avant un nouveau START)
- [ ] 3.9 Sortie USB CDC au format ligne brute auto-descriptive + mode `--pretty` minimal (code de trame et BA en clair)
- [ ] 3.10 Sortie UART de repli véhiculant le même format
- [ ] 3.11 **Si 3.3-3.5 s'avèrent instables** : basculer sur le repli documenté (une seule SM poussant l'état `(SCL, SDA)` à chaque transition, décodage complet en C) et consigner la décision dans `design.md`

## 4. Validation par oracle indépendant

- [ ] 4.1 Monter un banc reproduisant le dialogue BP↔BA (armoire de test, ou maître I2C de substitution rejouant les trames connues) — **jamais une armoire de production pour la mise au point**
- [ ] 4.2 Capturer le même trafic simultanément avec le Pico et l'analyseur logique sous sigrok/PulseView
- [ ] 4.3 Comparer trame à trame ; tout écart est un défaut du décodeur Pico jusqu'à preuve du contraire
- [ ] 4.4 Vérifier par la mesure que la connexion du sniffer ne dégrade pas le bus : compteurs d'erreurs I2C du SC944D inchangés sur au moins 10 minutes, sniffer connecté puis déconnecté
- [ ] 4.5 **[À LEVER]** Confirmer par recalcul sur trames réellement capturées que le CRC est bien un CRC-16/MODBUS (init `0xFFFF`, polynôme `0xA001`, little-endian) conformément à `crc.c`
- [ ] 4.6 **[À LEVER]** Confirmer par capture les adresses des BA réellement présents sur l'installation observée (le code dérive `0x11 + n`, une installation peut n'en avoir qu'un ou deux)
- [ ] 4.7 **[À LEVER]** Confirmer par capture l'ordre des bits de la trame `ACTIONS` (hypothèse : bit 0 secouru/sauvegarde, bit 1 blocage volets, bit 2 forçage allumage), les deux firmwares déclarant ce champ avec des conventions de bitfield opposées

## 5. Décodeur hôte — protocole

- [ ] 5.1 Parseur du format de ligne firmware, tolérant aux lignes tronquées et aux enregistrements d'anomalie
- [ ] 5.2 Reconstruction des transactions write + repeated START + read ; cas « écriture sans réponse » traité explicitement
- [ ] 5.3 Résolution adresse → identité BA (`0x11` pièces de vie, `0x12` chambres, `0x13` pièces d'eau), adresse brute conservée
- [ ] 5.4 Validation des longueurs attendues par code de trame (11 / 11 / 19 / 11 / 4 octets)
- [ ] 5.5 Vérification indépendante du CRC-16 de la requête, avec restitution attendu/reçu en cas d'écart
- [ ] 5.6 Décodage de la réponse 5 octets : écho de code, écho de CRC, CRC de réponse ; qualification explicite « reçue et validée CRC », jamais « sortie commutée »
- [ ] 5.7 Détection des répétitions et des abandons après épuisement des tentatives
- [ ] 5.8 Garantir l'égalité stricte entre décodage temps réel et rejeu hors ligne

## 6. Décodeur hôte — sémantique domotique

- [ ] 6.1 Décodage `FORCAGE_SORTIES` : lampes 16 bits OFF/ON, variateurs OFF/ON, volets sens 1 / sens 2
- [ ] 6.2 Application des priorités du firmware BA : extinction prioritaire, montée prioritaire ; conflits signalés
- [ ] 6.3 Décodage `ACTIONS` : secouru/sauvegarde, blocage volets, forçage allumage ; mise en évidence des transitions ; bits réservés signalés
- [ ] 6.4 Décodage `CONF_SORTIES`, `TPS_EXTINCTION`, `TPS_ACTION` en champs nommés, avec mention de l'écriture EEPROM côté BA
- [ ] 6.5 Profils de boîtier configurables (défauts SC942C : 13 relais lampes, 4 variateurs, 6 volets) et signalement des index hors plage
- [ ] 6.6 Restitution des octets excédentaires en brut, sans interprétation inventée
- [ ] 6.7 Résumé d'état **commandé** cumulé, avec marquage explicite des sorties « inconnues » quand la capture n'a pas démarré à la mise sous tension

## 7. Restitution et outillage

- [ ] 7.1 Sortie NDJSON complète (horodatages source et mural, adresse, BA, code, octets bruts, ACK, CRC, anomalies, événements)
- [ ] 7.2 Sortie texte compacte temps réel avec écart depuis la transaction précédente
- [ ] 7.3 Enregistrement de capture et rejeu hors ligne sans matériel
- [ ] 7.4 Filtrage d'affichage (BA, code de trame, anomalies) sans altération du fichier de capture
- [ ] 7.5 Résumé de session : volumétrie par BA et par code, erreurs CRC, NACK, répétitions, pertes, plus long silence
- [ ] 7.6 Ancre horloge murale ↔ compteur Pico avec mesure de dérive périodique

## 8. Corrélation backend

- [ ] 8.1 Définir le format d'entrée du relevé d'actions backend (actions distribuées via les endpoints legacy IoT, indices k/v de la table d'échange)
- [ ] 8.2 Implémenter la mise en correspondance temporelle capture ↔ actions backend, avec fenêtre de tolérance paramétrable
- [ ] 8.3 Restituer les deux asymétries : « demandée, non émise sur le bus » et « émise sans demande portail connue »
- [ ] 8.4 Valider la corrélation sur un scénario domotique de bout en bout (commande portail → trame observée)

## 9. Corpus de référence et tests

- [ ] 9.1 Constituer le corpus versionné : capture nominale, erreur CRC, NACK d'adresse, répétitions avec abandon, transaction tronquée
- [ ] 9.2 Figer les résultats de décodage attendus pour chaque capture
- [ ] 9.3 Brancher le corpus en CI (échec en cas de divergence, avec diff attendu/obtenu)
- [ ] 9.4 Tests unitaires du CRC-16 sur vecteurs extraits de trames réellement capturées

## 10. Documentation et mémoire projet

- [ ] 10.1 `docs/wiring.md` : point de piquage, procédure de mesure préalable, schéma de câblage, variante buffer 5 V, isolation USB
- [ ] 10.2 `docs/limits.md` : limites intrinsèques et modes d'échec du bus, formulés sans ambiguïté
- [ ] 10.3 Page protocole I2C BP↔BA dans `essensys-doc`, sourcée à la fois par le code et par la mesure
- [ ] 10.4 Page `essensys-memory/okf/protocols/` dédiée au bus I2C interne, avec pointeurs de code (aucune copie de source)
- [ ] 10.5 Exécuter la chaîne de synchronisation mémoire OKF et joindre le rapport de couverture
- [ ] 10.6 `openspec validate essensys-i2c-ba-sniffer-2026-07-038 --strict`

## 11. Décision de fin d'exploration

- [ ] 11.1 Rédiger une note de conclusion : ce que le sniffer a réellement permis de diagnostiquer, ce qu'il n'a pas permis, et le coût d'usage en intervention
- [ ] 11.2 Trancher explicitement la suite : arrêt de l'exploration, ou Phase 2 (décodeur `libsigrokdecode` ESSENSYS, capture longue durée autonome, intégration en banc de test) — un change distinct sera requis pour toute capacité d'émission sur le bus
