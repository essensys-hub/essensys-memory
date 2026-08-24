# Design — Sniffer I2C passif BP↔BA

## Contexte technique mesuré

Le bus à observer est **lent et peu chargé**, ce qui simplifie radicalement le problème :

- 50 kHz → 1 bit = 20 µs, 1 octet + ACK = 180 µs, transaction complète (write 11 + read 5 octets,
  2 adresses, START/reSTART/STOP) ≈ **3,5 ms** ;
- temporisation imposée de **100 ms** entre deux transactions (`ba_i2c.c:508`) → au plus ~10
  transactions/s, soit **< 200 octets/s** ;
- trafic **événementiel** : en régime nominal (aucune action utilisateur), le bus est quasi silencieux.

Un RP2040 à 125 MHz dispose donc de ~2 500 cycles CPU par bit I2C. Le budget n'est pas un problème ; les
vrais risques sont ailleurs : **fidélité de la détection START/STOP**, **compatibilité électrique**, et
**non-intrusivité**.

## Décisions

### D1 — Plateforme : Raspberry Pi Pico (PIO), pas Arduino

**Choix** : Raspberry Pi Pico (RP2040 ; RP2350/Pico 2 accepté) avec capture par **PIO**.

**Pourquoi** :

- Le PIO échantillonne SDA/SCL de façon **déterministe**, indépendamment de l'ordonnancement CPU, de
  l'USB et des interruptions — c'est exactement le point faible d'une capture par interruption GPIO.
- FIFO + DMA côté PIO : aucun échantillon perdu même pendant l'émission USB.
- USB CDC natif : pas d'adaptateur série externe (contrairement à un Arduino Uno/Nano).
- 264 KB de RAM : buffer circulaire de plusieurs milliers de transactions décodées.
- Deux cœurs : cœur 0 = capture/décodage bas niveau, cœur 1 = sérialisation et USB.

**Alternatives écartées** :

| Option | Pourquoi écartée |
|--------|------------------|
| Arduino Uno / Nano (AVR 16 MHz) | Capture par interruption uniquement ; latence d'ISR de plusieurs µs et jitter non borné ; 2 KB de RAM ; pas d'USB CDC natif. Techniquement faisable à 50 kHz, mais fragile et non extensible. |
| Arduino en mode esclave I2C (`Wire.onReceive`) | **Rédhibitoire** : le contrôleur matériel devrait acquitter les adresses écoutées → le sniffer deviendrait un participant actif du bus. Viole l'exigence de non-émission. |
| Raspberry Pi + `i2c-dev` | Pas de mode moniteur passif exposé par le contrôleur ; Linux non temps réel. |

### D2 — Analyseur logique USB comme **oracle**, Pico comme **livrable**

**Choix** : lors de la Phase 1, capturer le même trafic en parallèle avec un analyseur logique USB bas
coût (clone Saleae 8 voies) sous **sigrok/PulseView** et son décodeur I2C intégré, et **comparer trame à
trame** avec la sortie du Pico.

**Pourquoi** : sigrok fournit une référence indépendante et éprouvée pour valider le décodeur PIO. Sans
cet oracle, un bug de capture est indiscernable d'une anomalie réelle du bus — le pire mode d'échec pour
un outil de diagnostic.

**Pourquoi ne pas s'arrêter à sigrok** : il décode l'I2C générique mais ignore le protocole ESSENSYS
(codes de trame, longueurs, CRC-16, sémantique lampes/volets), exige un PC attaché en permanence, et
ne permet ni capture longue durée autonome ni corrélation avec les traces backend. Un décodeur
`libsigrokdecode` ESSENSYS est un **bonus optionnel** (Phase 2), pas le livrable principal.

### D3 — Architecture de capture PIO

Deux programmes PIO sur deux state machines, partageant les mêmes broches en entrée :

1. **SM_DATA** : attend un front montant de SCL, échantillonne SDA, pousse le bit. C'est le chemin de
   données : à front montant de SCL, la donnée est stable par définition du protocole I2C.
2. **SM_EVENT** : détecte une transition de SDA **pendant que SCL est haut** → START (SDA ↓) ou
   STOP (SDA ↑), et pousse un marqueur distinct.

Le cœur 0 consomme les deux FIFO, horodate (compteur µs matériel), et reconstruit la machine à états :
`IDLE → START → ADDR(7b)+RW → ACK → DATA*+ACK* → (reSTART | STOP)`.

**Repli documenté** si la synchronisation inter-SM s'avère délicate : une seule SM poussant l'état
`(SCL, SDA)` à **chaque transition de l'une ou l'autre broche**, le décodage complet étant fait en C sur
le cœur 0. À ~200 k transitions/s maximum, ce repli reste très confortable et il est plus simple à
raisonner. Le choix définitif est tranché par la mesure en Phase 1, pas a priori.

### D4 — Sécurité électrique : gate de mesure bloquant + buffer 5 V-tolérant

**Le RP2040 n'est pas 5 V-tolérant.** Le SC944D (MCF52259) travaille en 3,3 V, mais les BA sont des PIC
qui peuvent être alimentés en 5 V ; la tension effective du bus dépend de l'endroit où sont les
résistances de tirage et de leur rail d'alimentation. **Cette valeur n'est pas établie par la lecture du
code et doit être mesurée.**

**Règle** : aucune connexion du Pico au bus tant que la tension de repos SDA/SCL n'a pas été mesurée au
multimètre, armoire sous tension, sonde de masse sur la masse de l'armoire, et consignée dans la doc.

- Si **3,3 V** mesuré : connexion directe possible (GPIO en entrée, aucune pull-up interne activée).
- Si **5 V** mesuré : interposer un **buffer non-inverseur 5 V-tolérant alimenté en 3,3 V**
  (type 74LVC2G17, entrées Schmitt), une voie par ligne. Charge ajoutée sur le bus : quelques pF et
  quelques µA — négligeable devant les pull-ups existantes.
- **Pont diviseur résistif écarté** comme solution par défaut : il charge le bus en permanence et
  dégrade les fronts, ce qui est précisément ce qu'un outil de diagnostic ne doit pas faire.

**Non-intrusivité par conception** — quatre garde-fous cumulés :

1. broches SDA/SCL initialisées en **entrée seule**, jamais en sortie, à aucun moment du cycle de vie ;
2. pull-up/pull-down internes du RP2040 **explicitement désactivées** ;
3. aucun périphérique I2C matériel du RP2040 activé ni relié à ces broches ;
4. aucune API d'écriture bus exposée dans le firmware — l'absence d'émission est une propriété
   structurelle du code, pas une consigne d'usage.

### D5 — Masse commune et isolation

La capture exige une **masse commune** entre le Pico et l'armoire. Sur une installation en service,
relier la masse d'un portable secteur à la masse de l'armoire peut créer une boucle de masse.

**Choix** : brancher/débrancher le piquage **armoire hors tension** ; pour toute intervention sur une
installation en service, utiliser un **isolateur USB** (type ADuM3160) entre le Pico et le poste, ou
alimenter le Pico sur batterie et enregistrer en local.

### D6 — Répartition firmware / hôte : le firmware transporte, l'hôte interprète

**Choix** : le firmware Pico émet une **ligne brute auto-descriptive par transaction** (horodatage µs,
adresse, R/W, octets en hexadécimal, bits ACK, drapeaux d'anomalie). Toute la sémantique ESSENSYS —
CRC-16, longueurs attendues, mapping lampes/variateurs/volets — est faite par le **décodeur hôte**.

**Pourquoi** :

- une capture ancienne peut être **re-décodée** par une version ultérieure du décodeur (les captures de
  référence gardent leur valeur dans le temps) ;
- le décodeur est testable unitairement sur des captures figées, sans matériel — condition nécessaire
  pour une CI sans banc ;
- le firmware reste petit, auditables, et donc plus facile à garantir non-émetteur ;
- une régression de sémantique ne nécessite pas de reflasher un Pico en intervention.

**Concession** : un mode `--pretty` minimal dans le firmware (code de trame + identité BA en clair) pour
qu'un simple `screen /dev/tty.usbmodem*` reste exploitable sans installer le décodeur.

### D7 — Transport : USB CDC en principal, UART en repli

USB CDC par défaut (débit confortable, pas de câblage supplémentaire). Sortie UART sur broches dédiées
conservée comme repli pour les cas où l'USB n'est pas disponible ou pas souhaitable (isolation, capture
autonome vers un enregistreur tiers). Les deux transports véhiculent **le même format de ligne**.

### D8 — Horodatage

Le Pico horodate avec son compteur µs matériel (monotone, non ajustable). L'hôte pose une **ancre**
horloge murale ↔ compteur Pico à l'ouverture de session, et la réévalue périodiquement pour mesurer la
dérive. Chaque enregistrement NDJSON porte **les deux** : `t_us` (source Pico, faisant foi pour les
écarts entre trames) et `ts` (horloge murale reconstruite, pour la corrélation avec les logs backend).

### D9 — Nouveau dépôt dédié

`essensys-i2c-ba-sniffer`, hors des dépôts `essensys-board-*` qui restent des archives fournisseur en
lecture seule, et hors de `essensys-server-backend` dont le cycle de vie n'a rien à voir avec un outil
de banc.

Structure cible :

```
essensys-i2c-ba-sniffer/
  firmware/            # C/C++ SDK Pico : programmes PIO, décodeur bas niveau, USB CDC
  host/                # CLI Python : décodage protocole, sémantique, NDJSON, corrélation backend
  captures/            # captures de référence versionnées (.ndjson) + attendus
  docs/                # câblage, procédure de mesure, protocole BP↔BA sourcé
  tests/               # tests du décodeur hôte sur captures figées
```

## Risques

| # | Risque | Gravité | Mitigation |
|---|--------|---------|------------|
| R1 | Bus en 5 V → destruction d'un GPIO du Pico | Moyenne | Gate de mesure bloquant (D4) ; buffer 74LVC2G17 |
| R2 | Court-circuit SDA/SCL au piquage sur armoire en service | **Haute** (perte de pilotage domotique) | Branchement hors tension obligatoire ; piquage sur point identifié et documenté |
| R3 | Décodeur PIO subtilement faux → diagnostic erroné | Haute (outil de diagnostic qui ment) | Oracle sigrok en Phase 1 (D2) ; corpus de captures de référence en CI |
| R4 | Boucle de masse portable ↔ armoire | Moyenne | Isolateur USB ou alimentation sur batterie (D5) |
| R5 | Le firmware dérive vers une capacité d'émission | Moyenne | Non-émission structurelle (D4) ; revue explicite à chaque PR touchant `firmware/` |
| R6 | Attente irréaliste : « le sniffer dira si le relais a claqué » | Moyenne | Limites intrinsèques documentées en tête du README, pas enfouies |

## Questions ouvertes [À LEVER en Phase 1]

1. **Tension du bus** (3,3 V ou 5 V) — bloquant, à mesurer avant toute connexion.
2. **Point de piquage physique** : connecteur ou bornier exposant SDA/SCL/GND sur SC944D ou sur un BA,
   à identifier sur carte assemblée et à photographier.
3. **Valeur des pull-ups et longueur de bus réelle** en armoire, pour juger de la marge avant d'ajouter
   une charge (même faible).
4. **Adresse effective des BA installés** : le code dérive `0x11 + numéro BA`, à confirmer par la
   capture sur une armoire réelle (une installation peut ne pas avoir les trois BA).
5. Le CRC est identifié comme **CRC-16/MODBUS** (init `0xFFFF`, polynôme réfléchi `0xA001`, pas de XOR
   final, transmis en little-endian) d'après `SC944D/.../C/crc.c:4-36`. Reste à **confirmer par recalcul
   sur trames réellement capturées** : c'est la lecture de code qui doit être validée par la mesure, pas
   l'inverse.
