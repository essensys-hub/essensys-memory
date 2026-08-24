## Why

Le bus I2C interne de l'armoire ESSENSYS est aujourd'hui une **boîte noire d'exploitation**. Le SC944D
(BP, maître) pilote les boîtiers auxiliaires SC940 / SC942C / SC941C (BA, esclaves) par un protocole
propriétaire, mais aucun outil ne permet de **voir ce qui circule réellement sur le bus** :

- quand un scénario ou une commande portail n'aboutit pas à un relais qui claque, on ne sait pas
  distinguer « la trame I2C n'a jamais été émise » de « la trame a été émise mais rejetée CRC » ou
  « la trame est passée mais le BA n'a pas actionné la sortie » ;
- les erreurs de dialogue BA (`Erreur cheksum recue`, `Blocage`, `REINIT START`) ne sont observables
  que via l'espion série interne du SC944D, donc **seulement du point de vue du maître**, sans preuve
  indépendante de ce qui a été électriquement transmis ;
- toute évolution firmware BP ou BA se valide aujourd'hui « à l'œil » (le relais a claqué ou non), sans
  trace horodatée réutilisable en test de non-régression ;
- le mapping entre les indices k/v de la table d'échange, les endpoints legacy
  (`/api/myactions`, `/api/done/{guid}`) et les octets réellement poussés sur le bus n'est validé par
  aucune mesure — uniquement par lecture de code.

Ce change spécifie un **sniffer I2C passif** sur Raspberry Pi Pico, dans un nouveau dépôt exploratoire
`essensys-i2c-ba-sniffer`, capable de capturer, décoder et horodater le dialogue BP↔BA **sans jamais
émettre sur le bus**, et de restituer les trames sous forme d'événements domotiques exploitables.

### Ce que le code firmware nous garantit déjà (faits sourcés)

Ces éléments sont **relevés dans le code**, pas supposés — ils rendent le décodage déterministe :

| Fait | Source |
|------|--------|
| Bus `i2c0:`, **50 kHz**, mode polled, maître = SC944D | `SC944D/.../H/application.h:3`, `C/ba_i2c.c:106-118` |
| Adresse station BP `0x10` ; esclaves BA = `0x11 + numéro BA` → `0x11`, `0x12`, `0x13` | `application.h:8-9`, `ba_i2c.c:126,178` |
| Transaction = `START + addr(W)` → N octets → `repeated START + addr(R)` → **5 octets** → `STOP` | `ba_i2c.c:206-371` |
| Trame écrite = `[code trame][payload…][CRC16 LE sur code+payload]` | `ba.c:179-181,245-247`, `slavenode.c:245-247` |
| Réponse 5 octets = `[écho code][CRC reçu LO][CRC reçu HI][CRC16 LO][CRC16 HI]` | `slavenode.c:305-340`, `ba_i2c.c:382-432` |
| 5 codes de trame : `1 FORCAGE_SORTIES`, `2 CONF_SORTIES`, `3 TPS_EXTINCTION`, `4 TPS_ACTION`, `5 ACTIONS` | `global.h:518-522`, `slavenode.c:119-126` |
| Longueur **déterminée par le code de trame** (11, 11, 19, 11, 4 octets sur le fil) | `slavenode.c:201-224` |
| `FORCAGE_SORTIES` : lampes OFF/ON (16 bits), variateurs OFF/ON (8 bits), volets sens1/sens2 (8 bits) | `slavenode.c:443-486`, `ba.c:235-247` |
| Émission **sur changement** uniquement, avec répétitions bornées en cas d'erreur | `ba.c:171-211` |
| **100 ms de temporisation** imposée après chaque transaction (`_time_delay(100)`) | `ba_i2c.c:508` |

Conséquence directe : à 50 kHz et ≤ 10 transactions/s en pic, le débit à capturer est **très faible**
(quelques centaines d'octets/s au maximum). La difficulté n'est pas la performance, c'est la
**non-intrusivité électrique** et la **fidélité du décodage**.

## What Changes

- Nouveau dépôt **`essensys-i2c-ba-sniffer`** : firmware Pico (capture PIO), décodeur hôte (CLI Python),
  documentation de câblage, et jeux de captures de référence versionnés.
- **Capture bas niveau passive** (`i2c-bus-capture`) : détection START / repeated START / STOP,
  adresse 7 bits + bit R/W, octets de données, **bit ACK/NACK de chaque octet**, horodatage
  microseconde, détection d'overrun et de trames tronquées. Le firmware **n'entraîne jamais** SDA/SCL :
  broches configurées en entrée seule, aucune pull-up ajoutée, aucun mode maître/esclave I2C activé.
- **Décodage protocole ESSENSYS** (`i2c-frame-decode`) : reconstruction des transactions write+read,
  résolution adresse → identité BA, validation de la longueur attendue par code de trame, **vérification
  indépendante du CRC-16** (même polynôme que `us_CalculerCRCSurTrame`), corrélation requête/réponse et
  contrôle de l'écho CRC renvoyé par le BA.
- **Sémantique domotique** (`ba-event-semantics`) : transformation d'une trame `FORCAGE_SORTIES` en
  événements lisibles (`BA2 lampe 5 → ON`, `BA1 volet 3 → montée`, `BA3 variateur 2 → OFF`), avec
  détection des cas particuliers documentés dans le firmware BA (extinction prioritaire sur allumage,
  montée prioritaire sur descente), et décodage du champ `ACTIONS` (secouru, blocage volets, forçage
  allumage, sauvegarde).
- **Outillage et restitution** (`sniffer-tooling`) : sortie temps réel USB CDC lisible, format
  **NDJSON machine-lisible** pour rejeu et diff, enregistrement de captures `.ndjson` versionnables,
  repli UART si USB indisponible, et commande de **corrélation avec le backend** (comparer une capture
  bus avec les actions vues côté `/api/myactions` / table d'échange) pour valider bout-en-bout.
- Documentation matérielle : point de piquage SDA/SCL/GND sur l'armoire, **procédure de mesure du niveau
  logique du bus avant connexion** (gate bloquant), schémas de câblage, et procédure de branchement
  hors tension.

## Non-Goals (MVP exploratoire)

- **Aucune émission sur le bus.** Pas de mode maître, pas d'injection de trame, pas de spoofing de BA,
  pas de « rejeu actif ». Le sniffer est strictement en lecture. Toute capacité d'émission est hors
  périmètre et devra faire l'objet d'un change distinct avec analyse de risque armoire.
- Pas de modification du firmware SC944D ni des firmwares BA.
- Pas de déploiement en parc : outil de banc et d'intervention ponctuelle, pas un équipement permanent
  d'armoire de production.
- Pas d'analyse électrique fine (temps de montée, glitches, qualité des pull-ups) — un sniffer
  logique ne remplace pas un oscilloscope ; documenté comme limite.
- Pas de capture des **appuis locaux sur les boutons BA** ni de l'**état réel des relais** : ces
  informations ne transitent pas sur le bus (voir « Limites intrinsèques » ci-dessous).
- Pas de capture du chauffage : les commandes de chauffage passent par des GPIO du SC944D, pas par I2C.
- Pas d'intégration CI matérielle (pas de runner self-hosted branché en permanence) — Phase 2 si
  l'exploration est concluante.

## Limites intrinsèques du bus (à documenter, pas à contourner)

Le sniffer est **borné par ce que le protocole expose réellement**. Il faut l'écrire noir sur blanc pour
éviter une attente irréaliste :

1. **Pas de retour d'état des sorties.** La réponse du BA fait 5 octets et ne contient qu'un écho du
   code de trame et des CRC (`slavenode.c:305-340`). Elle prouve que la trame a été **reçue et validée
   CRC**, pas que le relais a physiquement commuté.
2. **Pas de visibilité sur les entrées locales BA.** Les appuis boutons traités localement par le BA ne
   génèrent aucun trafic I2C.
3. **Trafic événementiel, pas périodique.** Le BP n'émet que sur changement (`ba.c:171`). Un bus
   silencieux signifie « rien n'a changé », pas « le bus est mort ». Le sniffer doit rendre cette
   distinction explicite plutôt que de la masquer.
4. **Les répétitions sur erreur sont bornées** et le BP finit par acquitter localement pour arrêter la
   répétition (`ba.c:202-209`) : une commande peut donc être « abandonnée » sans que le BA l'ait jamais
   reçue. C'est précisément un des défauts que le sniffer doit rendre visible.

## Impact legacy

**NUL sur le fonctionnement.** Le sniffer est un observateur passif : il ne modifie ni le firmware BP,
ni les firmwares BA, ni la table d'échange `Tb_Echange[]`, ni les endpoints legacy IoT
(`/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}`), ni les backends
`essensys-server-backend` / `essensys-user-portal-backend`.

**Risque résiduel matériel non nul** : brancher un fil sur un bus I2C actif d'une armoire en service
peut provoquer un court-circuit transitoire ou une perturbation du bus. D'où l'exigence de branchement
hors tension et de mesure préalable du niveau logique (voir `design.md` §Sécurité).

## Capabilities

### New Capabilities

- `i2c-bus-capture` : capture passive niveau bit/octet du bus I2C (START/STOP/repeated START, adresse,
  R/W, données, ACK/NACK, horodatage µs), garantie de non-émission.
- `i2c-frame-decode` : reconstruction et validation des trames du protocole BP↔BA (codes, longueurs,
  CRC-16, corrélation requête/réponse).
- `ba-event-semantics` : traduction des trames en événements domotiques (lampes, variateurs, volets,
  actions globales) et identification des BA.
- `sniffer-tooling` : dépôt, firmware Pico, CLI hôte, formats de sortie NDJSON, captures de référence,
  corrélation avec les traces backend, documentation de câblage.

### Modified Capabilities

- _(aucune — aucune capability OpenSpec existante ne couvre l'observation du bus I2C interne)_

## Impact

| Zone | Impact |
|------|--------|
| `essensys-i2c-ba-sniffer` (nouveau repo) | Firmware Pico PIO, CLI hôte de décodage, captures de référence, doc câblage |
| `essensys-board-SC944D` | Lecture seule (source de vérité du protocole maître) — aucune modification |
| `essensys-board-SC942C` | Lecture seule (source de vérité du protocole esclave) — aucune modification |
| `essensys-server-backend` | Aucune modification ; utilisé en lecture pour la corrélation capture ↔ actions |
| `essensys-doc` | Page protocole I2C BP↔BA consolidée et sourcée par la mesure |
| `essensys-memory` | Ce change OpenSpec ; `okf/protocols/` à enrichir d'une page bus I2C interne |
| Matériel | 1 Pico (RP2040 ou RP2350), fils de piquage SDA/SCL/GND, multimètre pour le gate de niveau logique |
| Sécurité armoire | Branchement hors tension obligatoire ; aucune émission possible par conception |
