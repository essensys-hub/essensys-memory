# Remplacement des cartes de l'armoire : répondre à l'exigence de résilience (analyse du 2026-10-23)

Version anonymisée : pas d'adresse ni de lieu, pas de plan de la maison, pas de nom de prestataire ni de lien privé. Les pages publiques correspondantes sont dans `essensys-doc/docs/etudes/` (section « Études » du site).

## Contexte

Après la foudre du 9 août 2026, deux des trois boîtiers auxiliaires (BA) de l'armoire ne répondent plus sur le bus I2C. Le boîtier principal (BP SC944D) et le BA pièces de vie (SC940D) ont été remplacés ; les BA chambres (SC942C) et pièces d'eau (SC941C) restent muets. Les composants d'origine (PIC16F946) sont en approvisionnement tendu.

L'armoire commande 63 boutons muraux (contacts secs en 5 V sur trois nappes J3), 25 éclairages sur relais monostables, 15 volets et un store sur relais bistables, 8 variateurs, le fil pilote, le cumulus, des prises de sécurité, l'arrosage et la coupure des machines. Le BP porte aussi l'alarme, le délestage par la TIC et l'écran.

Trois zones : pièces de vie (PDV, 20 poussoirs, 5 éclairages, 6 volets, 3 variateurs), chambres (CHB, 21 poussoirs, 7 éclairages, 5 volets, 4 variateurs), pièces d'eau (PDE, 22 poussoirs, 13 éclairages, 4 volets dont le store, 1 variateur).

## Question

Après la foudre, l'exploitant a posé une exigence nouvelle (21 octobre 2026) :

> Si le contrôleur, un automate ou un Raspberry Pi grille, les interrupteurs muraux pilotent toujours les relais, en filaire. La domotique devient une couche ajoutée, qui peut tomber sans rien couper.

Comment l'armoire de remplacement peut-elle tenir cette exigence, et que deviennent les trois études V1 ?

## Méthode et versions

- **Études V1 (19 et 20 octobre 2026, figées le 21 octobre)** : trois études de remplacement complètes, avec architecture, câblage de migration, repiquage des phases, simulation 3D, nomenclature, risques et feuille de route.
- **Conseil d'autocritique (21 octobre 2026)** : six agents d'IA (Claude), chacun dans un rôle d'expert (électricien tableautier, automaticien, sûreté de fonctionnement, spécialiste foudre et CEM, mainteneur seul, avocat du diable), ont jugé les trois études sur l'exigence. Chacun a travaillé seul avec recherche web, puis a critiqué les cinq autres avis rendus anonymes ; un président de séance a fait la synthèse. Leurs chiffres sont des estimations argumentées, pas des devis.
- **Étude V2 « filaire d'abord, domotique en dérivation » (21 octobre 2026)** : rédigée d'après le verdict, relue par un relecteur indépendant (25 constats), puis corrigée.
- **Banc deux lumières (22 et 23 octobre 2026)** : banc de développement de la V2 sur rail DIN, avec liste d'achats et liste des fils ; lumière 2 passée sur un Eltako ES12Z-200-UC le 23 octobre.

## Réponse courte

1. **Aucune étude V1 ne tient l'exigence.** Toutes mettent un calculateur entre le bouton et le relais, sauf pour les 8 variateurs. Une Revolution Pi morte prive 55 boutons sur 63 ; avec l'Opta ou la refonte Raspberry Pi, un cerveau mort, c'est une zone morte. L'AMDEC de la sûreté compte les modes de panne qui privent toute la maison de ses boutons : 13 pour la Revolution Pi, 5 pour l'Opta, 4 pour la refonte Raspberry Pi, 0 pour le filaire autonome.
2. **La réponse est une armoire « filaire d'abord, domotique en dérivation ».** Chaque bouton attaque directement un organe qui garde l'état : télérupteur électromécanique pour les éclairages, deux relais en chaîne de priorité pour les volets, variateur Eltako à entrée locale. Une source de commande 24 V par zone l'alimente. La domotique s'ajoute en parallèle par des contacts secs, derrière un relais de garde tenu par un chien de garde matériel : elle peut mourir, se figer ou se tromper sans bloquer un bouton.
3. **Le prix** : environ 3 450 à 3 950 € HT de matériel pour la couche filaire seule, 4 300 à 4 900 € HT avec une couche domotique minimale, 6 450 à 7 850 € HT avec une couche complète ; environ 1 000 € de plus sans attestation d'isolement ; 6 à 8,5 jours d'électricien ; 1,6 à 2,1 m de rail, donc un second coffret. Aucun logiciel sur le chemin d'un bouton, puis 5 à 11 semaines-personne de domotique, contre 11 à 28 semaines avant la bascule dans les V1. On renonce au double clic, à l'appui long et aux scénarios câblés dans les BA.
4. **La preuve se fait avant toute commande en série** : relevé de l'électricien, attestations écrites d'isolement (Finder, Eltako), banc deux lumières, huit essais au banc, essai de choc de 2 puis 4 kV, recette de chaque zone contrôleur coupé.

## Ce que la foudre a appris

- Le bus I2C, seul lien galvanique entre des cartes flottantes, a servi de pont aux courants d'équilibrage : un bus interne court reste un chemin de foudre.
- Chaque BA bascule lui-même ses relais : un BP planté laisse les boutons actifs, mais un BA mort prive toute sa zone. Muet sur le bus ne veut pas dire sans boutons : l'état réel des BA chambres et pièces d'eau reste à vérifier (appui, LED DL1).
- Les relais monostables des éclairages ne retiennent rien : l'état vivait dans le firmware.
- La panne est restée silencieuse : commandes marquées acquittées, état des BA relu seulement après un ordre.
- Une seule ligne tenue basse fait taire les trois adresses : le découpage en zones n'arrête pas une cause commune.

## Les études V1 et leur verdict

| Étude V1 | Principe | Matériel HT | Logiciel avant bascule | Si le calculateur meurt | Verdict du conseil | Ce que la V2 garde |
| --- | --- | --- | --- | --- | --- | --- |
| Revolution Pi | Connect 5, 7 DIO, 1 AIO, 68 relais d'interface, 8 Eltako EUD12D | ≈ 5 450 € | 13 à 16 semaines | 55 boutons sur 63 perdus | Transformer | Connect 5 candidate pour la couche domotique, achetée en dernier ; relais 38.51 en couplage ; variateurs EUD12D ; barrières de 4 kV |
| Arduino Opta | 4 automates (un « BP », un par zone), 12 extensions | ≈ 5 600 € | 11 à 16 semaines | Sa zone perdue ; le bloc 24 V commun éteint les trois | Abandonner | Fusible par zone ; liaisons isolées entre coffrets |
| Raspberry Pi et Ethernet | Cartes nœuds maison (Pico 2, relais soudés, 230 V), Pi de gestion CM4 | ≈ 3 160 € | 19 à 28 semaines | Sa zone perdue, lumières éteintes | Abandonner les cartes | Isolement des entrées (à 4 kV au lieu de 3) ; monostable devenu relais de garde ; battement de cœur |

Les trois partagent le câblage de migration, que la V2 garde : répartiteur X1 (56 bornes Wago 2002-2201 à deux étages, 112 circuits), blocs de phase X3 (Wago 2002-1401 et contact de pontage, un bloc par disjoncteur), jonctions IDC des nappes (RS PRO 403-320), plan de bornage.

Reproches principaux du conseil :
- Revolution Pi : contrôleur unique ; service figé, boutons morts jusqu'au chien de garde logé dans le même Linux ; repli qui éteint les lumières ; isolement des DIO annulé par un bus 24 V commun ; frontières qui oublient les 63 lignes de boutons ; coffret ajouté contre le coffret photovoltaïque.
- Arduino Opta : « pas de panne unique » contredit par le bloc 24 V commun ; même code dans les quatre automates ; entrées non isolées sur un 0 V commun, la topologie du 9 août ; bus I2C des extensions sans signal de vie ; plateforme logicielle en transition.
- Raspberry Pi et Ethernet : nœud mort, zone morte ; cartes maison portant du 230 V sans marquage CE ; relais soudés ; entrées isolées à 3 kV seulement ; charge de 19 à 28 semaines (23 à 35 selon le mainteneur) pour une seule personne. C'est pourtant l'étude la mieux conçue contre la foudre, et son principe (« plus une fonction est critique, moins elle dépend d'autres organes ») devient celui de la V2.

## L'architecture V2 « filaire d'abord, domotique en dérivation »

### Le chemin du bouton

| Fonction | Organe retenu | Sans contrôleur | Repli si tout s'arrête |
| --- | --- | --- | --- |
| Éclairages (25) | Télérupteur Finder 20.22 à levier, bobine 24 V continu (230 mA, 21,6 à 26,4 V), 2 NO qui basculent ensemble | Le poussoir attaque la bobine | État gardé, levier |
| Volets et store (15) | Deux relais en chaîne de priorité : Finder 19.91 en montée, 48.P6 (ou second 19.91) en descente ; diodes d'aiguillage et de roue libre | Commande maintenue | Arrêt ; jamais les deux sens ; store rentré au vent par un automatisme autonome |
| Variateurs (8) | Eltako EUD12D-UC en PRI 1 ou 5 | Entrée locale sur la source de zone | Niveau gardé |
| Fil pilote | Relais au repos, commutateur Auto/Confort/Hors-gel par zone | Commutateur | Confort, sans délestage ; aucun ordre « arrêt » possible |
| Cumulus | Contacteur jour/nuit manuel | Contact heures creuses du compteur | Heures creuses, si l'abonnement en a |
| Délestage | Délesteur autonome si le bilan de puissance l'exige (≈ 250 €) | Délesteur | Rien ne déleste sans lui |
| Alarme, sirènes | Couche domotique sur batterie | Aucune | Perdues si la couche tombe |

Le Finder 20.28 (inverseur à quatre séquences) ne convient pas : son second contact ne recopie pas le premier. Le Schneider iTLs A9C32211 limite l'impulsion à 1 s et à 5 manœuvres par minute : retenu seulement avec une réponse écrite du fabricant.

### La source de commande par zone

- Un 24 V continu de classe II par zone, homologué EN 61558-2-16 (exemple : Mean Well HDR-30-24, 4 kV entre entrée et sortie), séparé de celui de la domotique, plus une rechange au coffret.
- F1 de 1 A pour le commun des boutons (calé sur la jonction IDC, donnée pour 1 A) ; F2 de 0,5 A au plus pour le commun des contacts domotiques. Une domotique folle fait fondre F2, jamais F1.
- Un disjoncteur de 2 A par source, sous un différentiel distinct pour chacune ; aucune sous le différentiel du lave-linge ou d'une salle d'eau.
- 25 bobines ensemble tireraient 5,75 A : la domotique séquence ses ordres groupés, et F2 protège la zone si elle ne le fait pas.

### La domotique en dérivation

- Contacts secs Finder 38.51 (6 kV et 8 mm entre bobine et contact) en parallèle des poussoirs ; jamais sur une entrée prioritaire.
- Relais de garde par zone, tenu par un chien de garde matériel réarmé toutes les 200 ms environ par un signal alterné couplé en capacitif ; retombée en moins d'une seconde ; il ne colle au démarrage qu'après plusieurs réarmements.
- Borne sectionnable par zone sur le même commun : retour arrière et parade au contact soudé.
- Deux communs domotiques par zone : impulsion (coupé au-delà d'une seconde) pour les télérupteurs, maintien (coupé au-delà de la course) pour les volets.
- Un quatrième relais de garde coupe le fil pilote, qui retombe en confort.
- Lecture d'état : le second contact du télérupteur, en 230 V, commande un relais de recopie 38.51 à bobine 230 V ; seul son contact sec rejoint une entrée optocouplée isolée à 4 kV. Aucun contact de télérupteur n'est relié à la TBTS : deux contacts voisins d'un Finder 20 ne tiennent que 2 000 V CA. L'état est lu, jamais réimposé ; un changement non commandé marque le circuit « repris à la main ».
- Contrôleur acheté en dernier, après les zones filaires et le banc : environ 85 sorties et 68 entrées. Revolution Pi Connect 5 (candidate de trois conseillers) ou serveur d'E/S léger piloté par la passerelle (proposition du mainteneur).

| Si la domotique | Ce que fait le matériel | Ce que garde la maison |
| --- | --- | --- |
| Se tait | Relais de garde ouvert en moins d'une seconde | Tous les boutons ; fil pilote en confort |
| Se fige | Chien de garde privé de signal, relais de garde ouvert | Idem |
| Envoie un ordre faux | Durées et ordres bornés par le câblage | Les boutons, sauf contre un volet tenu en montée : borne sectionnable |
| Est piratée | Mêmes bornes câblées | Les boutons ; chauffage au pire en hors-gel ; alarme et sirènes exposées |

### La foudre

- La V2 coupe le chemin de l'onde au lieu de l'écrêter : deux îlots TBTS distincts (filaire et domotique), dont les 0 V ne se touchent jamais et ne touchent pas le PE (ni liaison, ni varistance, ni TVS, ni éclateur).
- Chaque passage d'îlot est une barrière d'au moins 4 kV efficaces et 8 mm : télérupteur (4 000 V CA et 4 kV en onde 1,2/50 µs entre bobine et contacts ; isolation renforcée à faire attester), 38.51 (6 kV), relais de garde, optocoupleurs, isolateur Ethernet vers la passerelle.
- Onde induite en mode commun sur une boucle de 10 m², selon l'avis foudre : 1 à 9,5 kV pour un impact à 20 m, 0,4 à 3,9 kV à 50 m, 0,1 à 1 kV à 200 m (pentes de 10 à 100 kA/µs).
- Parafoudres au tableau et au bout des lignes extérieures, jamais dans les coffrets ; contrôle du parafoudre de tête, de la cartouche et de la terre avant mai 2027 ; type 1 si un paratonnerre est à moins de 30 m.
- Coffrets à 30 à 50 cm des câbles photovoltaïques, ou goulotte métallique reliée au PE aux deux bouts.

### Ce que garde la maison, panne par panne

| Panne | Ce qui reste |
| --- | --- |
| Contrôleur domotique arrêté | Les 63 boutons ; volets en commande maintenue ; radiateurs en confort |
| Réseau ou passerelle | Tout le local |
| Source de commande d'une zone | Les deux autres zones ; lumières de la zone dans leur état, au levier ; rechange en 30 minutes environ |
| Un télérupteur | Les autres circuits ; levier si la bobine seule est morte ; échange en 5 à 15 minutes |
| Un relais de volet | Les autres volets ; jamais les deux sens à la fois |
| Coupure du secteur | Télérupteurs dans leur état au retour ; alarme sur batterie |
| La foudre | Bobines et contacts ; lumières dans leur état, au levier |

Deux défauts restent latents : la batterie de l'alarme (essai de capacité annuel, remplacement vers 4 ans) et l'isolement qui se dégrade (mesure chaque année et après chaque orage proche).

## Désaccords ouverts

| Désaccord | Choix provisoire du verdict | Autre option | Départagé par |
| --- | --- | --- | --- |
| Éclairages | Télérupteur électromécanique (électricien, sûreté, spécialiste foudre) | Actionneurs Eltako, ≈ 0,9 m de rail (automaticien, avocat du diable) | Courant des lignes, place, essai de choc, banc |
| Volets | Chaîne de deux relais | Eltako EGS12Z, appui court sans contrôleur | Banc avec un vrai moteur |
| Source de commande | 24 V continu par zone (cinq conseillers) | Transformateur 50 Hz (spécialiste foudre) | Volumes des salles d'eau, norme |
| BA actuels | Ne pas réparer, mais vérifier leur état | Réparer d'abord (avocat du diable) | LED DL1, expertise éventuelle |
| Couche domotique | Revolution Pi Connect 5, achetée en dernier | Serveur d'E/S léger (mainteneur) | Fonctions utilisées, devis |
| Calendrier | Poser après les essais | Poser dès novembre | État des BA, attestations |

Angles morts relevés par la critique croisée : le délestage quand le contrôleur est mort ; la garde des BA déposés, intacts, tant qu'une expertise est possible ; le coffret photovoltaïque à quelques centimètres ; la prémisse des zones mortes, non mesurée ; un contrôleur faux ou piraté.

## Préalables avant toute commande

- Relevé d'une journée par l'électricien : volumes des salles d'eau (en volumes 1 et 2, seul un interrupteur TBTS 12 V est admis ; le 24 V continu y reste à confirmer), section, résistance de boucle et isolement de chaque ligne de bouton (bobine entre 21,6 et 26,4 V, soit 11,7 Ω au plus sous 24 V), place loin du photovoltaïque, différentiels, bilan de puissance, parafoudre de tête et terre, température du coffret (Finder 20 limité à 40 °C).
- Attestations écrites d'isolation renforcée : Finder (20.22, 48.P6) et Eltako. Sans elles, un 38.51 devant chaque télérupteur, alors à bobine 230 V (≈ 1 000 €), et un relais de couplage par variateur (≈ 150 €).
- Essai de choc au banc : onde 1,2/50 µs de 2 puis 4 kV en mode commun sur une ligne de bouton, domotique branchée ; 1 000 à 1 800 € en laboratoire.
- Isolement : 250 V continu entre lignes, 500 V continu entre TBTS et 230 V, plus de 100 MΩ visés.

## Le banc deux lumières (23 octobre 2026)

- **But** : prouver la chaîne V2 sur deux lumières avant l'armoire, et départager « électromécanique ou Eltako ».
- **Lumière 1** : télérupteur Finder 20.22.9.024.4000 (23,15 € TTC), relais de couplage KC1 en parallèle du poussoir derrière le relais de garde KG et la borne sectionnable XS, recopie KR1 (38.51 à bobine 230 V) ; limiteur KL d'une seconde posé mais pas câblé.
- **Lumière 2** : Eltako ES12Z-200-UC (52,39 € TTC), relais bistable électronique 2 NO 16 A, 1 module. Entrée locale +B1 et alimentation +A1/−A2 sur le 24 V des boutons (d'après le marquage, à confirmer avec la notice) ; entrées centrales Marche (+E1) et Arrêt (+F1), commun −E2 au 0 V de la domotique, alimentées par le +24 V gardé (contact du chien de garde puis borne sectionnable XSD) ; recopie KR2 sur le contact 3-4 ; réglages ZE+ZA sans retard et priorité 1. Il remplace télérupteur, relais de couplage et limiteur ; isolements entre entrées et contacts à faire attester.
- **Domotique** : Raspberry Pi 3 en nœud d'entrées-sorties (rôle du serveur d'E/S léger), Raspberry Pi 4 en logique (rôle de la passerelle), tous deux sur le 24 V de la domotique par un convertisseur isolé Mean Well DDR-30G-5 réglé à 5,1 V. Carte d'interface sur plaque à pastilles : ULN2803A (couplage et chien de garde), BC547 et BC327 par ordre de l'ES12Z (GPIO 27 Marche, GPIO 23 Arrêt), PC817 pour les recopies (GPIO 25 et 24), chien de garde sur GPIO 22, couplage sur GPIO 17. Chien de garde : Finder 80.01 en fonction BE réarmé par couplage capacitif.
- **Implantation** : coffret de 3 rangées de 13 modules (230 V et sources G1 HDR-30-24 et G2 HDR-60-24), platine ouverte en très basse tension (rails P1 et P2, cartes), mur de deux poussoirs relié par une nappe IDC de 3 m.
- **Fils** : 76 fils et câbles repérés à leurs deux bouts (1 à 30 en 230 V, 101 à 119 boutons, 201 à 223 domotique, 301 à 304 en 5 V et réseau) ; trois îlots sans fil commun.
- **Coût** : 737,79 € TTC à acheter (230 V 302,85 € ; boutons 214,31 € ; domotique 128,90 € ; montage 91,73 €), dont 608,89 € pour la couche filaire seule ; ≈ 1 586 € avec une Revolution Pi, ≈ 962 € avec un Pico 2 Ethernet et un CM5.
- **Points ouverts** : montage du limiteur, valeurs du chien de garde, repérage réel des bornes, notice de l'ES12Z, attestation d'Eltako, jonction IDC en voie de retrait chez son distributeur.

## Recherche du 23 octobre 2026 : un appareil unique ?

Aucun appareil modulaire de 10 ou 16 A ne réunit, en 24 V continu, l'entrée du poussoir, une entrée domotique séparée et une sortie d'état utilisable en TBTS. Le plus proche est l'Eltako ES12Z-200-UC (entrée locale 12 à 230 V UC, entrées centrales Marche et Arrêt 8 à 230 V UC séparées galvaniquement de l'entrée locale, 2 NO 16 A), d'où son essai sur la lumière 2 du banc. Le Schneider iTLs A9C32211 réunit télérupteur et contact d'état, mais limite l'impulsion à 1 s. Les commandes centralisées des grands fabricants n'existent qu'en alternatif.

## Feuille de route (estimations, sauf mai 2027)

| Quand | Étape | La maison |
| --- | --- | --- |
| Novembre 2026 | Relevé, banc, attestations | Inchangée |
| Novembre et décembre 2026 | Chambres et pièces d'eau (≈ 2 000 € HT, 3 à 4 jours d'électricien) | 20 éclairages, 8 volets, le store et 5 variateurs reviennent au bouton |
| Janvier 2027 | Pièces de vie, fin du bus I2C | Les 63 boutons commandent leur charge sans calculateur |
| Février à avril 2027 | Couche domotique | Commande à distance revenue ; sa panne ne touche aucun bouton |
| Avant mai 2027 | Parafoudres | Prête pour l'été |
| Printemps 2027 | Retrait du BP, fonction par fonction | Utilisable tout du long |

## Règles pour toutes les installations

1. Un bouton ne passe jamais par un calculateur pour atteindre sa charge.
2. L'état d'un circuit vit dans un organe bistable, pas dans un logiciel.
3. La domotique ajoute un ordre, elle n'en retire jamais : contacts en parallèle, relais de garde, borne sectionnable.
4. Une source et un fusible par zone, et un fusible distinct pour la domotique.
5. Une barrière d'au moins 4 kV et 8 mm à chaque passage d'îlot ; le 0 V jamais au PE ; les parafoudres hors des coffrets.
6. Chaque repli se choisit au câblage et s'essaie à la recette : contrôleur coupé, réseau débranché, une sortie collée.
7. L'isolement se mesure chaque année et après chaque orage proche.

## Pages publiques (essensys-doc)

- `docs/etudes/resilience.md` : répondre à l'exigence de résilience.
- `docs/etudes/remplacement-armoire/v2/filaire-d-abord.md` : étude V2.
- `docs/etudes/remplacement-armoire/v2/conseil.md` : question, méthode et verdict du conseil.
- `docs/etudes/remplacement-armoire/v2/autocritique-v1.md` : autocritique des trois études V1.
- `docs/etudes/remplacement-armoire/v2/sections-de-cables.md` : sections de câbles.
- `docs/etudes/banc-deux-lumieres.md` : banc deux lumières.
- `docs/etudes/remplacement-armoire/{revolution-pi,arduino-opta,raspberry-pi-ethernet}.md` : études V1 figées.
- Renvois depuis `docs/retex/index.md` et `docs/retex/foudre-2026/synthese.md`.

Chiffres à confirmer par un électricien, des devis, les fabricants et des essais. Les prix ont été relevés en octobre 2026.
