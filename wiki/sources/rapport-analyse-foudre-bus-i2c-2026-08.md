---
tags: [source, essensys, domotique, firmware, hardware, incident, foudre, i2c, cem]
sources: [incidents/2026-08-foudre-bus-i2c/rapport-analyse.md]
created: 2026-10-11
updated: 2026-10-11
era: legacy
---

# Rapport Analyse Foudre Bus I2C 2026 08

**Source :** `raw/incidents/2026-08-foudre-bus-i2c/rapport-analyse.md` (présenté par le `README.md` du même dossier)
**Type :** rapport d'incident technique, anonymisé

## Métadonnées

| Champ | Valeur |
|---|---|
| Événement | 9 août 2026, vers 16 h 20 (fenêtre déduite : 16 h 15 à 16 h 25) |
| Analyse | 2026-10-11. Version v2, qui intègre et corrige le v1 écrit le même jour |
| Statut | Analyse terminée, diagnostic sur site en cours |
| Cartes | [[Essensys Board Sc944d]] (BP, maître I2C), [[Essensys Board Sc940]] (SC940D), [[Essensys Board Sc941c]], [[Essensys Board Sc942c]] |
| Firmware | BP 099-37 ([[Client Essensys Legacy]]), BA v1.7 |
| Méthode | Relectures croisées adversariales. v1 : cinq analyses spécialisées en parallèle, puis deux vérificateurs par volet (calculs, puis terrain et sécurité). v2 : audit de 8 photos du site, analyse CEM recoupée par un script indépendant, analyse de l'installation photovoltaïque, deux relectures |
| Périmètre | Dépôts lus sans modification. Les essais sont des mesures manuelles. Aucun test automatisé ne pilote l'armoire réelle |
| Suivi | Ticket `essensys-hub/essensys-board-SC944D#1`, change OpenSpec `i2c-surge-protection-2026-10-007` (dépôt essensys-board-SC944D) |
| Anonymisation | Les équipements du site, le réseau, le lieu, les personnes et l'installateur sont remplacés par une désignation fonctionnelle. Les caractéristiques techniques (Uc, Up, In, Imax, tensions, distances) sont conservées |
| Immuabilité | Source figée. Les résultats du diagnostic sur site arriveront dans de nouveaux fichiers datés |

**Marquage des affirmations dans la source :**
- [VU] : lu sur un schéma, une BOM ou dans le code ;
- [DS] : lu sur une fiche technique, et [DS?] : valeur citée de mémoire, à vérifier ;
- [DÉDUIT] : calcul à confirmer par une mesure ;
- [HYP] : hypothèse sur l'installation ;
- [EST] : prix estimé ;
- [VU ph. n] : constaté sur une photo du site (photos non publiées).

## Résumé

Le coup de foudre a fait déclencher le disjoncteur de branchement et arrêté l'installation photovoltaïque. Depuis, le BP SC944D ne reçoit plus de réponse d'aucun des trois BA. Un BA est présumé mort, mais il n'est pas encore identifié.

Le rapport constate (schémas, BOM, code) que les quatre cartes sont des îlots TBT flottants reliés par le seul câble de bus, et que ni les interfaces I2C ni le +15 V du bus ne limitent le courant. Il en déduit, à confirmer par la mesure, que ce câble a servi de pont aux courants d'équilibrage.

Il propose :
- un diagnostic sûr ;
- des retouches sans nouveau circuit imprimé ;
- une étoile 0 V et l'isolement de l'Ethernet du BP ;
- à long terme, une carte d'interconnexion équipotentielle et une révision E des cartes.

L'origine exacte de la surtension n'est pas établie.

## Affirmations clés

1. **Topologie.**
   - Un seul coffret domotique, avec les cartes empilées [VU ph.].
   - Chaîne du bus, ordre le plus probable : BP-J31 → SC942C → SC941C → SC940D. Le J1 du SC940D est libre [VU ph. ; continuité derrière les goulottes : DÉDUIT].
   - Trois tronçons d'environ 33 cm de câble cat. 5e, probablement AWG26 [VU ph.].
   - Bus I2C à 50 kHz [VU code, `ba_i2c.c:106`] sur 4 fils : SDA, SCL, GND et +15 V (BA_ALIM).
2. **Îlots flottants [VU].** Aucune carte n'a de liaison au PE. Le câble 4 fils est le seul lien galvanique entre elles.
3. **Modèle R + (L − M) [DÉDUIT].**
   - Entre une ligne et son 0 V, un tronçon présente R ≈ 0,09 Ω et L − M ≈ 0,09 à 0,16 µH.
   - Dans R, les contacts pèsent autant que le fil.
   - L'inductance propre (0,46 µH) ne s'applique pas ici.
4. **Seuil d'équilibrage [DÉDUIT].**
   - Les écrêteurs I2C conduisent quand l'écart entre le 0 V du SC940D et celui du BP dépasse 6,3 à 7,8 V.
   - Il faut pour cela un courant d'équilibrage d'environ 20 A en onde 8/20, d'environ 11 A sur un front rapide et d'environ 4 A sur un front très rapide.
5. **Bout de chaîne.**
   - C'est le SC940D, et non le SC941C qu'avait supposé le v1.
   - Son seuil est environ 3 fois plus bas que celui du SC942C.
   - Cette position ne le désigne pas pour autant comme la carte défaillante.
6. **Destruction par les broches I2C [DÉDUIT].**
   - Avec R1/R2 = 0 Ω, la diode du PIC reçoit 1 à 2 A dès environ 30 A d'équilibrage, soit 50 à 100 fois son maximum de 20 mA.
   - Côté BP, la ligne monte à 9-10 V alors que U19 est limité à 7 V.
7. **Destruction par le fil +15 V [DÉDUIT, ajout v2].**
   - Quand le 0 V d'un BA descend sous celui du BP, le +15 V charge sans seuil C2 (10 µF/16 V) et le rail « +12V » du BA.
   - C2 est dépassé dès un écart ΔV d'environ 2 V.
   - U1 (LMR12010, 24 V) est atteint vers ΔV ≈ 10 V, soit environ 28 A en 8/20 au SC940D.
   - Ce mécanisme suffit à expliquer un « BA mort non alimenté ».
8. **Un BA mort bloque tout [DÉDUIT].**
   - Le bus est partagé, sans tampon.
   - Une seule ligne tenue basse ou à mi-niveau fait taire les trois adresses : TVS en court-circuit, broche claquée, ou PIC non alimenté qui se réalimente par ses diodes.
9. **Origine non établie.**
   - Quatre hypothèses restent concurrentes : H-PV, H-RÉS, H-TOV et H-IND.
   - H-IND recule, car la coupure du branchement et l'arrêt du PV sont simultanés.
10. **Constats annexes.**
    - Le parafoudre AC du coffret photovoltaïque a ses deux fenêtres noires [VU ph.].
    - Les parafoudres DC n'ont aucune fenêtre rouge [VU ph.].
    - Le parafoudre de type 2 du tableau a un voyant vert [VU ph.].
    - Le dongle de supervision de l'onduleur, branché sur le même switch réseau que le BP, ne répondait plus lors de la mesure réseau du 2026-10-11 [VU, mesure réseau]. La date à laquelle il a cessé de répondre n'est pas connue.
11. **R1/R2 en 47 Ω.**
    - Cette valeur transforme une destruction quasi certaine du PIC en survie probable, sans respecter son maximum absolu.
    - Elle ne relève pas le seuil d'équilibrage du système.
12. **Étoile 0 V doublée (N2).**
    - Elle relève le seuil d'équilibrage de 20 à 173 A en onde 8/20, et de 11 à 79 A sur un front rapide.
    - C'est la seule mesure de court terme qui garde son efficacité quand le front raidit. Le gain du renfort 0 V (N1) tombe de ×5 à moins de ×2.
13. **Ethernet du BP.** Il faut l'isoler par une fibre ou un isolateur de 4 à 6 kV au moins. Aucun parafoudre RJ45 relié au PE ne doit être posé côté BP.
14. **Firmware du BP [VU].**
    - Il ne récupère pas un bus bloqué.
    - Au-delà de 21 échecs, il abandonne la commande et la marque comme acquittée.
    - Il ne renvoie jamais les trames de configuration perdues.
    - L'index 12 n'est mis à jour qu'après l'envoi d'une commande.

## Résumé structuré

### Système et implantation (fiche de synthèse, §0.2)

- BP **SC944D** : MCF52259, Ethernet, maître I2C.
- Trois BA :
  - **SC940D**, pièces de vie (PDV), adresse 0x11 ;
  - **SC941C**, pièces d'eau (PDE), adresse 0x13 ;
  - **SC942C**, chambres (CHB), adresse 0x12.
- Coffret domotique IP40, accolé à gauche au tableau électrique (parafoudre de type 2 en tête) et, à droite, à quelques centimètres, au coffret photovoltaïque. L'onduleur hybride et des câbles DC passent au-dessus.
- Les câbles de bus descendent à 1 à 5 cm des bornes de phase, sans goulotte séparée.
- Le BP est relié en Ethernet à un switch réseau, sur lequel est aussi câblé le dongle de supervision de l'onduleur.

### Événement et chronologie (§0.1 bis)

- Le disjoncteur de branchement (AGCP) a déclenché, et l'installation PV s'est arrêtée au même moment.
- Sur la supervision de l'onduleur, toutes les puissances sont à zéro à 16 h 25, d'où la fenêtre de 16 h 15 à 16 h 25.
- Deux mois ont passé entre l'événement et l'analyse :
  - le côté AC du PV est resté sans parafoudre local en saison orageuse ;
  - les historiques courts (48 h) sont perdus.
- Restent exploitables :
  - le dernier « seen » du dongle dans le contrôleur réseau ;
  - le `ts` des messages MQTT retenus ;
  - le journal de l'onduleur ;
  - l'historique du compteur communicant ;
  - les données d'un réseau de détection de la foudre.

### Mécanisme (§0.3, §1)

Le câble de bus n'est pas une antenne, c'est un **pont** entre quatre îlots TBT qui ont chacun leur câblage de terrain :
- nappes J3 vers les boutons ;
- sorties 230 V ;
- côté BP : Ethernet, téléinformation, électrovanne et fils pilotes.

Un événement extérieur porte ces îlots à des potentiels différents. Au-delà du seuil, SDA et SCL deviennent des chemins parallèles au fil GND. Le courant passe alors par les TVS SMF5V0A (D33/D34 au BP, D1/D2 sur chaque BA), U19 et les broches RC6/RC7 des PIC. Il passe aussi par le fil +15 V, qui fait monter le rail du BA.

L'ordre de grandeur « ≈ 1 kV sur 10 m » du v1 ne vaut que pour un câble long dont la boucle est fermée, comme les nappes J3.

Le tableau ci-dessous donne le seuil d'équilibrage entre le SC940D et le BP selon la configuration [DÉDUIT] :

| Configuration | Onde 8/20 | Front rapide (1 Ipk/µs) | Front très rapide (4 Ipk/µs) |
|---|---|---|---|
| Actuelle (3 tronçons AWG26) | ≈ 20 A | ≈ 11 A | ≈ 4 A |
| N1 : 0 V de 4 mm² plaqué, soudé sur chaque carte | ≈ 97 A | ≈ 25 A | ≈ 7 A |
| N1 sans retouche (J1 libre vers le moins de la batterie du BP) | ≈ 73 A | ≈ 22 A | ≈ 6 A |
| N2 : étoile, chaque BA par J1 et J2 (AWG20, ≤ 15 cm) | ≈ 173 A | ≈ 79 A | ≈ 26 A |
| Fond de panier avec plot 0 V (BA rév. E) | ≈ 875 A | ≈ 292 A | ≈ 83 A |

### Hypothèses sur l'origine (§0.3.3)

| Hypothèse | Contenu | Test qui départage |
|---|---|---|
| H-PV | Foudre côté PV, puis entrée par l'Ethernet (dongle → switch → J32 du BP → 0 V du BP). Avant amorçage, les capacités en série ne laissent passer que 0,3 à 1,7 A : il faut l'amorçage de plusieurs barrières | Journal des ports du switch, résistance entre les broches 1 et 3 de J32 (≈ 150 Ω), isolement de J32 et C63 à 500 V, journal de l'onduleur |
| H-RÉS | Foudre côté réseau, en mode commun (régime TT). L'éclateur N-PE du parafoudre de tête n'a pas de voyant | Traces d'amorçage dans la zone J1/J2–K1, isolement 230 V / TBT, TVS d'entrée de J3, données de détection de la foudre |
| H-TOV | Surtension temporaire d'origine HTA, ou défaut de l'onduleur | Notice du parafoudre AC du coffret PV, historique du compteur communicant, journal de l'onduleur |
| H-IND | Événements indépendants | Date à laquelle le parafoudre AC a été vu vert pour la dernière fois, état de l'onduleur |

Chemins secondaires à garder en vue :
- nappes J3, si la boucle se ferme à l'autre bout ;
- départs 230 V extérieurs, quand le contact du relais est ouvert ;
- boucle entre l'écran IHM et les boutons, seulement si J3 du BP est câblé ;
- induction par les câbles PV sur le côté 230 V du SC940D. Elle ne désigne pas le port I2C, car la boucle SDA/GND ne fait qu'environ 1 mm.

### Faiblesses relevées sur les schémas (§2)

**BP SC944D (B1 à B6).**
- B1 : les TVS SMF5V0A écrêtent à 9,2 V en onde 10/1000, et vers 12 à 14 V en onde 8/20, au-dessus des 7 V de U19 (PCA9306).
- B2 : en polarité négative, l'impulsion traverse U19 jusqu'au MCF, qui tolère −0,3 V.
- B3 : la piste vers les broches 28/29 du MCF fait 55 mm sans aucune protection. Le MCF n'est pas tolérant au 5 V (4,0 V maximum).
- B4 : BA_ALIM n'a ni TVS, ni fusible, ni PTC. U16 (LD1117, entrée 15 V maximum) est déjà hors spécification sous 15,17 V nominaux.
- B5 : le Bob Smith et le blindage de J32 sont couplés au 0 V par environ 1 nF/2 kV. J32 n'est isolé qu'à 1,5 kV et se trouve à 18 mm de J31.
- B6 : EN ≈ 5 V sur U19 signifie « passant sans limitation de niveau », et non « ouvert ».

**BA SC940D, SC941C et SC942C (A1 à A8).**
- A1 : avec R1/R2 = 0 Ω, la diode interne du PIC16F946 conduit vers 5,5 V, avant que la TVS ne claque à 6,4 V.
- A2 : le seuil haut I2C du PIC est de 3,45 V. Une TVS qui fuit se voit donc vite.
- A3 : le rail « +12V » est à 14,3 V, sans TVS. C2 tient 16 V, D6 20 V, le LMR12010 24 V et FI1 25 V. La carte a été conçue pour 12 V.
- A4 : depuis la modification DM de janvier 2017, R79/R80 (0 Ω) relient directement la masse du bus au 0 V local, et L3/C40 sont retirées.
- A5 : 20 à 22 entrées TOR, sans optocoupleur, étendent le 0 V du BA dans tout le bâtiment.
- A6 : J1/J2 sont estimés à 2-3 mm du relais K1 (230 V), alors que le BP impose 5,5 mm.
- A7 : un BA non alimenté tire SDA et SCL entre 0,6 et ≈ 3 V.
- A8 : le BA n'a pas de chien de garde (`WDTDIS`) ni de traitement d'erreur SSP.

**Bus.**
- Pull-ups : 769 Ω, soit environ 6,5 mA à l'état bas, contre 3 mA prévus par la norme.
- Capacité : 2 à 3 nF, fixée par les TVS (1120 pF chacune), et non par le câble.
- Écart de masse statique ΔVg attendu au SC940D : 0,06 à 0,16 V.
- La marge de niveau bas dans le sens BP → BA n'est pas déterminée : il faut la mesurer.

### Diagnostic et réparation (§3)

- **E-1, sécurité.**
  - Mesurer la tension 0 V TBT–PE en mode basse impédance (LoZ).
  - Consigner selon la NF C 18-510, installation PV comprise : l'onduleur peut avoir une sortie de secours.
  - Seul l'installateur PV touche au coffret PV : les chaînes sont à plusieurs centaines de volts continus.
  - Faire les essais d'isolement à 500 V continu sur **les trois BA et le BP**, en commençant par le SC941C. En dessous de 10 MΩ, la carte n'est pas remise en service.
  - Ne pas sonder J31/J1 à pointe nue : la broche 4 (+15 V) est voisine de SCL.
  - Débrancher le câble Ethernet du dongle côté switch.
- **Mode de travail pour E0 à E2.** Tout le 230 V consigné. Le BP est alimenté par une alimentation de laboratoire flottante de 22 à 24 V continu, limitée à 1,5-2 A, sur J56-1/J56-2. En dessous d'environ 20 V, le BP pourrait se croire sur batterie et couper le +15VSP au bout de 12 s [HYP].
- **E0, observation.**
  - Filmer 10 s les LED ÉTAT des BA et la LED de téléinformation du BP.
  - Relire l'index 12 après une commande vers chaque BA.
  - Horodater l'événement avant que les historiques expirent.
- **E1/E2, isolement de la carte fautive.**
  - Retirer entièrement le câble du BA mort, puis rebrancher un BA à la fois.
  - Critère de repos relatif : ΔV ≤ 40 mV par rapport au +5 V local.
- **Console « Espion » du BP.** Elle est compilée dans le firmware 099-37. Il faut souder R109/R110 et J102 sur l'UART2 pour y accéder. Elle départage un NACK d'un bus bloqué.
- **Établi.**
  - BP : U19, puis D33/D34, puis J32/C63.
  - BA : l'alimentation (U1, D3, C2, D6, FI1) **avant** RC6/RC7. Un maître I2C 5 V autonome permet de tester l'acquittement de l'adresse.
  - Avant de remplacer un PIC qui répond encore, lire son EEPROM (bit CPD à vérifier).
- **Pièces.** TVS à commander en SMF5V0A-E3-08 (le suffixe GS08 n'est plus au tableau de commande). PIC16F946 en approvisionnement tendu : passer par Microchip en direct et constituer un stock.
- **Firmware à flasher.**
  - BP : uniquement l'image de production `.S19` 099-37, après une sauvegarde BDM. **Jamais un nouveau build.**
  - BA : les `.hex` v1.7 par type de carte. **Jamais le build essensys-gcc.**
- **Remise en service.**
  - Renvoyer les configurations de **tous** les BA. Après un changement de PIC, les variateurs repartent en mode gradateur par défaut : à corriger pour les charges qu'on ne peut pas graduer.
  - Les BA sont relancés sans ouvrir l'armoire en coupant le secteur du BP au moins 13 s (20 s par marge). Prérequis : batterie présente, cavalier J58 fermé, `Mode_Test` = 0. Effet de bord : les relais monostables retombent.

### Protection à court terme (§4)

| Prio | Mesure |
|---|---|
| P0 | Sécurité et isolement sur les 4 cartes. Remplacement de D33/D34 et des D1/D2 du BA mort. Débranchement de l'Ethernet du dongle. Horodatage. Conservation des preuves |
| Parallèle | L'installateur PV remplace le parafoudre AC et lit le journal de l'onduleur. Non bloquant pour Essensys |
| P1 | R1/R2 de 0 à 47 Ω anti-impulsion (33 Ω si ΔVg > 0,12 V sans N2/N1) |
| P1 | BA_ALIM : PTC en amont, puis TVS. U16 remplacé par un LM317. Sur chaque BA déposé : C2 en 35 V, D6 en 40 V, TVS après R79 |
| P1 | Isolement de l'Ethernet du BP (fibre alimentée depuis l'îlot TBTS, ou isolateur ≥ 4-6 kV) |
| P1 | N2, étoile 0 V doublée (30 à 60 €), ou à défaut N1, renfort 0 V (10 à 30 €) |
| P1 | Contrôle du parafoudre de tête par l'électricien. Câbles PV à 30-50 cm au moins du coffret |
| P2 | Option renforcée : R155/R156 en 2,2 kΩ, L30/L32 remplacées par 47 Ω, BAT54S au BP et aux BA |
| P1/P2 | Parafoudre de type 3 conforme au départ des lignes 230 V extérieures, dans le tableau |
| P2 | Alerte serveur quand `comm_faults` n'est pas vide |

### À ne pas faire (§4.5)

- Monter L3 seule, ou retirer R79/R80.
- Mettre 100 Ω côté BA avec les pull-ups de 1 kΩ.
- Monter des TVS 5 V « plus puissantes » : leur fuite atteint 800 µA.
- Monter C23/C25 en condensateurs.
- Poser un éclateur à gaz (GDT) entre le 0 V et la terre.
- Reflasher avec un build non qualifié.
- Poser un parafoudre RJ45 relié au PE au BP.
- Amener un PE dans le coffret domotique.
- Poser une varistance nue sur une sortie 230 V.
- Faire passer un renfort 0 V par un autre chemin que le bus.

### Long terme (§5)

- **Principe.** Couper la boucle galvanique en isolant les données ET l'alimentation ensemble, ou rendre les 0 V équipotentiels. La TBTS est toujours conservée.
- **Coffret unique.**
  - Carte d'interconnexion équipotentielle (fond de panier, 60 à 100 €).
  - Bus en étoile.
  - Par port : 47 Ω et TVS ≤ 50 pF, PTC et SMCJ16A sur le +15 V, cavalier de déconnexion.
  - Isolement des ports qui sortent du coffret.
- **BA déporté.** Module d'isolement par BA (MIB) :
  - isolateur ISO1640DW, alimenté côté BA pour libérer le bus quand le BA meurt ;
  - convertisseur DC/DC renforcé de 4 à 5 kVAC ;
  - superviseur de nœud ;
  - J2 du BA neutralisé.
- **Écartés.**
  - TCA4307 par nœud (architecture à nœud commun déconseillée par TI).
  - PCA9615 et LTC4331.
  - GDT.
  - CAN isolé (le PIC16F946 n'a pas de contrôleur CAN).
- **Génération 3.** RS-485 isolé, avec une adresse sur 9 bits. Le signal DE est absent sur le SC941C. La décision sera prise dans un ADR.
- **Règles de placement (rév. E).**
  - Zonage bus / TBTS locale / 230 V, avec au moins 8 mm sans cuivre, et 6 à 8 mm plus une fente côté 230 V.
  - Ordre fixe : connecteur → TVS → résistance série → écrêteur → circuit intégré.
  - Le courant de surtension ne traverse jamais le plan logique.
- **Phasage.**
  - 0 : installation.
  - 1 : réparation, Ethernet isolé et N2.
  - 2 : carte d'interconnexion et banc, pilote I2C du BP.
  - 3 : BP et BA rév. E.
  - 4 : RS-485 isolé.

### Plan de test (§5.9)

- Sur banc uniquement, jamais sur l'armoire réelle.
- Critère B redéfini : reprise automatique en moins de 10 s avec resynchronisation, et aucune sortie qui change d'état sans commande.
- Essais IEC 61000-4-2, -4-4 et -4-5, dont le mode commun entre îlots.
- Injection de courant d'équilibrage : onde 8/20 de 100 A puis 1 kA, et front rapide.
- Couplage par l'Ethernet.
- Tests `NR-*` : BA hors tension, ligne forcée basse, branchement à chaud, cycle de TE2, endurance de 72 h.

### Firmware (§5.10)

- **BP.**
  - Préalable : pilote I2C MQX à attentes bornées en temps dans [[Essensys GCC]].
  - Récupération de bus par 9 coups d'horloge.
  - Commandes conservées, resynchronisation, état de santé par BA, sonde de présence toutes les 30 à 60 s.
- **BA 1.8.** Chien de garde, état d'erreur du SSP, NACK quand `CmdBuf` est occupé, `comm_stat` dans un 6ᵉ octet.
- **Serveur.** Alerte sur `system.comm_faults` ([[Essensys Server Backend]]).

### Écarts de documentation (annexe E)

- `essensys-doc/archi/hardware-sc944d.md` et `hardware-overview.md` : la liaison BA passe par J31.
- `hardware-sc94{0d,1c,2c}.md` :
  - J3 porte les entrées TOR, et le bus passe par J1/J2 ;
  - la logique est en 5 V ;
  - L3 n'est pas montée ;
  - les quantités de TVS et de VDR du SC940D sont fausses.
- `essensys-board-SC944D/docs/i2c.md` : le bus tourne à 50 kHz, et non 100 kHz ; le code ACTIONS vaut 5 ; les adresses vont de 0x11 à 0x13.
- `essensys-board-SC940/docs/Architecture_Overview.md` : le SC943 est un variateur à IGBT, et non un module RF.

### Points ouverts (§0.5, annexe C)

- Identité du BA défaillant.
- Chronologie croisée.
- État de l'onduleur et du dongle.
- Notice du parafoudre AC du coffret PV.
- Alimentation du switch (avec ou sans terre).
- Contenu de J3 du BP.
- Nombre de fils par contact.
- Consommation réelle d'un BA.
- ΔVg mesuré.
- Temps de montée.
- Distances 230 V / TBT sur les Gerber.

### Ce que le v1 affirmait (annexe G)

Le v1 supposait des boîtiers distants, reliés par plusieurs mètres de câble. Ses affirmations remplacées en v2 :
- « 1 kV sur 10 m » ;
- SC941C en bout de chaîne ;
- parafoudre de tête à installer ;
- parafoudre RJ45 relié au PE ;
- MIB par BA pour tous les cas ;
- parafoudre de type 3 ou varistance 275 V sur les départs extérieurs (formule résumée au §0.4 du v2).

## Code pointers

- `client-essensys-legacy/C/ba_i2c.c` : initialisation I2C0 à 50 kHz (ligne 106) et pointeur de fichier périmé (lignes 86, 98, 180).
- `client-essensys-legacy/C/ba.c` (lignes 202-209 et 313-316) : trames abandonnées et marquées acquittées.
- `client-essensys-legacy/C/Hard.c` (lignes 879-945) et `H/global.h` : coupure du +15VSP sur batterie au bout d'environ 12 s.
- `client-essensys-legacy/C/EspionRS.c` : console Espion.
- `essensys-board-SC940/SC940D/Prog/code_ba (fichiers sources 1.7)/source/` : `main.c:17` (watchdog désactivé), `slavenode.c:361` (`else;`) et `gestionsorties.c` (LED DL1).
- `essensys-gcc/ba/source/hard.h` : trois macros `TYPE_*` définies ensemble.
- `essensys-server-backend/internal/armoire/decode.go` : décodage de `system.comm_faults`.
- `essensys-board-SC944D/SC944D/Prog/099-37/` : image de production `.S19` du BP.

## Concepts

- [[Ilots TBTS Et Equipotentialite]]
- [[Protection Surtension Bus I2C]]
- [[Table D Echange]] (index 12 `comm_faults`)

## Entités

- [[Essensys Board Sc944d]]
- [[Essensys Board Sc940]]
- [[Essensys Board Sc941c]]
- [[Essensys Board Sc942c]]
- [[Client Essensys Legacy]]
- [[Essensys GCC]]
- [[Essensys Server Backend]]

## Synthèse

- [[Incident Foudre Bus I2C 2026 08]]
