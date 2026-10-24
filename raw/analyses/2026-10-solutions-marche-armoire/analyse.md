# Solutions du marché pour remplacer l'armoire sans recâblage : étude comparative (analyse du 2026-10-24)

Version anonymisée : pas d'adresse ni de lieu, pas de plan de la maison, pas de nom de prestataire ni de lien privé. Les pages publiques correspondantes sont dans `essensys-doc/docs/etudes/remplacement-armoire/marche/` (section « Études » du site), publiées par la PR essensys-hub/essensys-doc#20 (ticket essensys-hub/essensys-doc#19).

## Contexte

L'étude V2 « filaire d'abord, domotique en dérivation » (analyse du 2026-10-23) répond à l'exigence de résilience posée après la foudre du 9 août 2026 : un calculateur grillé ne coupe aucun bouton. Elle retient des télérupteurs, des relais et des variateurs à entrée locale, et laisse ouvert le choix de la couche domotique, entre une Revolution Pi Connect 5 et un serveur d'entrées-sorties léger piloté par la passerelle.

Avant de s'engager, l'exploitant a posé une question (brief validé le 2026-10-24) : une solution domotique du marché, KNX en tête, pourrait-elle remplacer les quatre cartes de l'armoire **sans toucher au câblage existant** ? Et comment une dizaine de solutions, ouvertes, payantes ou issues de l'automatisme, se comparent-elles sur les mêmes critères ?

## Méthode

- **Onze dossiers au même gabarit** : synthèse, principe et gamme, dans l'armoire sans recâblage, seule face à l'exigence, en dérivation sur le filaire V2, foudre et isolement, logiciel et passerelle, nomenclature et coût, ouverture et pérennité, verdict, sources. Un tableau comparatif dans la page d'index.
- **Deux lectures par solution.** *Seule* : elle remplace les quatre cartes, ses modules d'entrées reçoivent les 63 poussoirs, ses actionneurs commandent les charges ; on mesure ce qui reste quand son cerveau, son bus, son alimentation, son logiciel ou sa licence tombe. *En dérivation* : elle n'est que la couche domotique posée sur le filaire de la V2 ; elle ferme des contacts secs en parallèle des poussoirs, derrière le relais de garde et la borne sectionnable, et lit l'état par des recopies ; on la compare à la Revolution Pi Connect 5 et au serveur d'E/S léger.
- **Deux configurations par solution** : une *minimale*, conforme au fabricant (un bus, une alimentation, un contrôleur), et une *résiliente*, alignée sur la V2 (un segment, une alimentation et, s'il existe, un contrôleur par zone). Le classement, le décompte des causes communes et le coût « armoire complète » portent sur la résiliente.
- **Relecture** par un agent d'IA dans un rôle de relecteur indépendant ; constats repris.
- **Chiffres** : fiches techniques, boutiques en ligne et retours d'utilisateurs consultés en octobre 2026, TTC convertis en HT au taux du pays de la boutique (19 % Allemagne, 20 % France, 21 % Pays-Bas). Ce sont des estimations produites par des agents d'IA, à confirmer par un électricien, des devis, les fabricants et des essais. Aucun comportement en panne n'a été essayé sur un banc.

## Ce qui ne change pas

- 63 poussoirs muraux, contacts secs à impulsion, ramenés à l'armoire sur trois nappes, une par zone (pièces de vie 20, chambres 21, pièces d'eau 22), par des jonctions IDC données pour 1 A.
- Les charges restent câblées sur l'armoire : 25 éclairages, 15 volets dont le store (30 relais, deux sens verrouillés), 8 variateurs, fil pilote, cumulus, prises de sécurité, arrosage, coupure des machines.
- Le câblage de migration des V1, gardé par la V2 : répartiteur X1, blocs de phase X3, jonctions des nappes, plan de bornage.
- La passerelle (Raspberry Pi CM5, backend Go) continue d'exposer l'application : elle doit pouvoir parler à la solution retenue.

Toute solution doit fournir, sur rail DIN : des entrées binaires pour 63 contacts secs, des sorties relais 230 V, des sorties variateur, et des contacts pour le fil pilote, le cumulus et les prises. Les boutons tactiles, écrans ou poussoirs connectés d'une gamme ne comptent pas. Une solution qui exige un recâblage est marquée **hors contrainte**.

## La grille d'évaluation

### Règle 1 à trois niveaux

Les sept règles de la réponse de résilience sont reprises règle par règle (tenue, partielle, non tenue). La règle 1, « un bouton ne passe jamais par un calculateur pour atteindre sa charge », décide de la lecture « seule », avec la définition de la V2 qui tolère le microcontrôleur du commerce d'un variateur Eltako :

| Niveau | Ce que fait le poussoir | Exemple |
| --- | --- | --- |
| Tenue | Il attaque directement un organe qui garde l'état, sans bus ni logiciel du projet | Télérupteur, variateur à entrée locale |
| Partielle | Il attaque un module du commerce, à micrologiciel fixé par le fabricant, qui lie lui-même son entrée à sa sortie, sans bus ni contrôleur ; une panne ne prive que les circuits de ce module | Module à entrée locale et relais intégré |
| Non tenue | L'ordre passe par un bus ou par un contrôleur programmable ; la perte du bus, de son alimentation ou du contrôleur coupe le bouton | Bus de terrain, automate, serveur domotique |

Un bus sans contrôleur central, comme KNX, est donc « non tenue » : le dossier dit alors combien de boutons une panne de ligne prive.

### Huit causes communes

Pour chaque solution, en configuration résiliente, on passe la même liste fermée de défaillances uniques et on compte celles qui privent **toute la maison** de ses boutons :

1. l'alimentation du système ou du bus ;
2. un court-circuit ou une ligne collée sur un bus ;
3. le contrôleur central ;
4. le logiciel figé (plantage sans redémarrage) ;
5. une mise à jour ratée ;
6. une licence, un compte ou un cloud indisponible ;
7. le commutateur ou le routeur du réseau local ;
8. la foudre sur le chemin du bus.

Le conseil d'autocritique de la V2 avait compté 13, 5, 4 et 0 modes communs pour les trois V1 et le filaire avec sa propre méthode : ces chiffres sont rappelés à part et ne se comparent pas directement au décompte de cette étude.

### Autres critères

Foudre et isolement (bus dans l'armoire ou à travers la maison, isolement annoncé, barrières de 4 kV et 8 mm, deux îlots TBTS, parafoudres) ; coût matériel HT (armoire complète et couche en dérivation) ; charge de travail (jours d'électricien, semaines-personne de logiciel, outil, licence, formation) ; place (mètres de rail, coffrets) ; ouverture et pérennité (protocole, norme, nombre de fabricants, cloud ou licence, pièces à dix ans, communauté) ; passerelle (protocole exposé : KNXnet/IP, Modbus, MQTT, REST, API locale ; travail côté passerelle) ; fonctions (double appui, appui long, scénarios, délestage, alarme, écran : perdus, gardés ou reportés).

Périmètre du coût : le même que les totaux de la V2 (poussoirs, éclairages, volets, variateurs, fil pilote, cumulus, prises, arrosage, coupure des machines). Alarme, sirène, détecteurs de fuite, écran et délestage sont des fonctions à reporter, hors du total. En dérivation, le dispositif de la V2 (relais de couplage, relais de garde à chien de garde matériel, fusible F2, durées bornées, recopie d'état, barrières de 4 kV) s'impose à toutes les solutions et son coût est déjà dans la V2 ; le coût « en plus » ne compte que contrôleur, modules d'E/S, logiciel et licence.

## Les onze solutions

| Solution | Famille | Pourquoi elle est là |
| --- | --- | --- |
| KNX TP | Bus normalisé, multi-fabricants | La question de départ ; dossier le plus détaillé |
| Loxone | Propriétaire, centralisé | Très répandu en rénovation ; entrées pour poussoirs classiques |
| Niko Home Control II | Propriétaire, bus | Modules rail DIN, interface pour contacts secs |
| Domintell | Propriétaire, bus | Modules d'entrées dédiés aux poussoirs classiques |
| Homematic IP Wired | Propriétaire, bus filaire, logiciel de centrale libre | Bus bon marché ; communauté open source |
| Eltako Series 14 | Propriétaire, bus RS-485 | Même fabricant que les variateurs de la V2 |
| Siemens LOGO! 8 | Automate | Automate d'entrée de gamme très répandu en domotique |
| Wago PFC200 + bornes 750 | Automate, ouvert | Automate industriel ouvert ; des Wago déjà dans la V2 |
| Shelly Pro | Modules LAN et Wi-Fi sur rail DIN, API ouverte | Entrées locales par module, fonctionne sans contrôleur |
| ESPHome sur rail DIN + Home Assistant | Open source, matériel et logiciel | La voie « maison » la moins chère |
| Modbus et passerelle | Modules d'E/S Modbus RTU ou TCP pilotés par la passerelle | La forme concrète du « serveur d'E/S léger » de la V2 |

Écartés : Revolution Pi, Arduino Opta et Raspberry Pi et Ethernet (déjà étudiés en V1, rappelés comme repères) ; Zigbee et Z-Wave sur rail DIN (variante de Shelly) ; Legrand MyHome et Hager coviva (gammes en transition) ; Beckhoff (proche de Wago, non chiffré).

## Tableau comparatif

Lecture « seule », configuration résiliente, puis coût de la couche en dérivation. Coûts HT, matériel et licence compris, hors électricien.

| Solution | Règle 1 | Causes communes (résiliente / minimale) | Pire panne simple | Armoire complète (résiliente / minimale) | Couche en dérivation | Rail | Ouverture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KNX TP | Non tenue ; portée 100 m des entrées à confirmer | 0 / 3 | Une zone ; éclairages gardent leur état | ≈ 5 200 / 2 950 € | ≈ 3 100 € | 2,1 m | Norme ouverte, 500 fabricants, ETS payant |
| Loxone | Non tenue | 0 / 6 | Une zone ; état des relais non documenté | ≈ 6 700 / 3 900 € | ≈ 3 950 € | ≈ 2 m | Propriétaire, logiciel gratuit, vente « Partner » |
| Niko Home Control II | Non tenue | 0 ou 1 / 6 ou 7 | Une zone ; Internet « requis » selon la doc | ≈ 9 200 / 7 600 € | ≈ 8 100 € | ≈ 2,4 m | Propriétaire, API MQTT locale à jeton annuel |
| Domintell | Non tenue, hors contrainte (entrées à 10 m) | 6 / 6 | Toute la maison | ≈ 7 530 / 6 190 € | ≈ 5 570 € | ≈ 2,3 m | Propriétaire, Light Protocol documenté |
| Homematic IP Wired | Non tenue, hors contrainte sauf accord écrit du fabricant (câble blindé exigé au-delà de 3 m) | 4 (0 si liaisons directes sans centrale) / 7 | Toute la maison ou une zone | ≈ 3 510 / 2 630 € | ≈ 2 480 € | 1,6 m | Propriétaire, centrale libre OpenCCU |
| Eltako Series 14 | Non tenue | 0 / 3 | Une zone ; ses éclairages s'éteignent | ≈ 2 180 / 1 800 € | ≈ 1 580 € | ≈ 1 m | Propriétaire, un fabricant, outil gratuit |
| Siemens LOGO! 8 | Non tenue ; version 230 V chiffrée hors contrainte (secteur sur les nappes), version 24 V non chiffrable | 0 / 5 | Une zone ; relais retombent | ≈ 1 900 / 1 600 € | ≈ 1 600 € | 1,3 m | Propriétaire, Modbus TCP |
| Wago PFC200 | Non tenue | 5 / 6 | Toute la maison ; repli à zéro en 50 ms | ≈ 7 270 / 6 250 €, hors alim et relais | ≈ 6 350 € | ≈ 0,9 m, hors alimentations | Ouvert (Modbus, MQTT, CODESYS) |
| Shelly Pro | Partielle, à confirmer ; 63 relais d'interface | 0 / 0 | Un module : 4 circuits | ≈ 2 270 € les deux, hors relais d'interface | ≈ 1 940 € | 1,1 m | API locale ouverte, cloud facultatif |
| ESPHome sur rail DIN | Non tenue ; logique locale par carte, micrologiciel du projet | 0 (2 sans réglages) / 2 | Une zone ; relais à zéro au redémarrage | ≈ 710 € les deux, hors alim | ≈ 360 € | 3 × 320 mm, hors rail | Open source, CE radio seulement |
| Modbus et passerelle | Non tenue | 3 en RTU, 4 en TCP / 6 | Toute la maison (passerelle) | ≈ 820 / 705 € | ≈ 430 € (modules grand public) ; ≈ 3 000 à 3 900 € en industriel | 1,9 m | Protocole ouvert, libre de droits |

Postes exclus des totaux : Wago, l'alimentation 24 V, la fin de bus, les modules d'alimentation du bus et les relais d'interface 230 V ; Shelly, les 63 relais d'interface des poussoirs (≈ 1 200 à 1 350 € HT d'après la V2, soit ≈ 3 500 € HT au total), le commutateur et la passerelle ; ESPHome, l'alimentation 12 V, le commutateur et l'import ; LOGO!, le commutateur ; Eltako, l'alimentation 24 V des boucles de poussoirs. Les six autres lignes sont complètes.

Repères (chiffres du conseil d'autocritique, non comparables au décompte ci-dessus) : V2 filaire d'abord, règle 1 tenue, 0 mode commun, ≈ 3 450 à 3 950 € HT (filaire seul) et 6 450 à 7 850 € HT (avec domotique complète) ; Revolution Pi (V1) non tenue, 13 modes, ≈ 5 450 € ; Arduino Opta (V1) non tenue, 5 modes, ≈ 5 600 € ; Raspberry Pi et Ethernet (V1) non tenue, 4 modes, ≈ 3 160 €. Revolution Pi Connect 5 : ≈ 581 € HT nue, modules d'E/S non chiffrés dans cette étude.

## Classement : seule face à l'exigence

Aucune des onze solutions ne tient la règle 1. Le classement mesure la distance qui reste : ce qu'il faut pour priver la maison de ses boutons, et ce que garde un circuit quand sa commande meurt.

1. **Shelly Pro** : la liaison entrée → relais vit dans le micrologiciel, fixé par le fabricant, de chaque module ; aucune défaillance unique ne touche toute la maison, un module mort prive quatre circuits. Mais l'état et le verrouillage des volets sont logiciels, l'isolement n'est pas publié, et il faut un relais d'interface par poussoir pour garder les nappes en TBTS. « Partielle, à confirmer ».
2. **KNX TP** : l'architecture à bus la plus proche de l'exigence. Zéro cause commune par zone, relais bistables qui gardent l'état, manettes mécaniques sur certains actionneurs, norme à 500 fabricants. Une zone tombe avec son alimentation (20 à 22 boutons, panne la plus fréquente) ; portée des entrées (100 m) à confirmer.
3. **Eltako Series 14** : zéro cause commune par zone, compact et bon marché, mais la perte du 12 V d'une zone éteint ses lumières ; fabricant unique.
4. **Siemens LOGO! 8** : zéro cause commune avec cinq unités autonomes, mais relais qui retombent à l'arrêt, entrées 230 V non isolées, ni variateur ni verrouillage natif ; la version 230 V chiffrée met le secteur sur les nappes : hors contrainte, la version 24 V n'ayant pas de prix.
5. **ESPHome sur rail DIN** : logique locale par carte, une carte par zone, zéro cause commune une fois paramétrée, le prix le plus bas ; mais le lien du bouton à sa charge est un micrologiciel du projet : « non tenue ». Relais à zéro au redémarrage, CE radio seulement, aucun isolement publié. C'est la refonte Raspberry Pi des V1 en moins cher et moins propre.
6. **Loxone** : zéro cause commune avec un Miniserver par zone, au prix fort ; état des relais à la perte du Link non documenté, rien de manœuvrable à la main.
7. **Niko Home Control II** : à contre-emploi (trois entrées par module, un contrôleur par installation) et dépendance à Internet affirmée par sa documentation.
8. **Homematic IP Wired** : zéro ou quatre causes communes selon que les liaisons directes filaires tiennent sans centrale, ce que le terrain contredit ; entrées non isolées qui portent le 24 V du bus sur les nappes, câble blindé exigé au-delà de 3 m : hors contrainte sauf accord écrit du fabricant.
9. **Modbus et passerelle** : la passerelle, son Linux et son logiciel sont sur le chemin de chaque appui : 3 à 4 causes communes.
10. **Wago PFC200** : contrôleur unique, coupleurs sans logique, repli à zéro en 50 ms : 5 causes communes, prix élevé, postes non chiffrés.
11. **Domintell** : hors contrainte (entrées limitées à 10 m), maître unique, 6 causes communes.

Ce que dit ce classement : les solutions qui s'approchent de l'exigence le font en mettant **un microcontrôleur par poussoir ou par zone**, pas en le supprimant. La V2 reste la seule réponse qui tient la règle 1.

## Recommandation : en dérivation sur le filaire V2

En dérivation, la couche domotique n'a plus qu'à fermer des contacts secs en parallèle des poussoirs, lire des recopies, battre le cœur du relais de garde et parler à la passerelle. Les critères qui comptent changent : prix pour ≈ 85 sorties et ≈ 70 entrées, ouverture du protocole, place, et rien du projet qui tourne dans l'armoire.

| Rang | Solution | Couche HT | Pour | Contre |
| --- | --- | --- | --- | --- |
| 1 | Modbus et passerelle (serveur d'E/S léger) | ≈ 430 € en modules grand public ; ≈ 3 000 à 3 900 € en modules industriels | Aucune logique dans l'armoire, protocole ouvert et libre, chien de garde de communication sur les modules industriels, la passerelle fait tout | Isolement et CE des modules bon marché non trouvés, et pas de chien de garde ; un maître unique, acceptable pour une couche sacrifiable |
| 2 | KNX TP | ≈ 3 100 € | Norme, 500 fabricants, pièces à dix ans, aucun Linux ni logiciel du projet sur le chemin des contacts, minuterie d'actionneur en battement de cœur | ETS à acheter et apprendre ; 88 modules ; relais 16 A surdimensionnés |
| 3 | Eltako Series 14 | ≈ 1 580 € | Compact (0,75 m), sans licence, fabricant des variateurs de la V2 | Propriétaire, un seul fabricant, liaison série, pas de bibliothèque Go |
| 4 | Homematic IP Wired | ≈ 2 480 € | Peu de modules, centrale libre, sans cloud | Entrées non isolées, battement de cœur à travers centrale et réseau |
| 5 | Siemens LOGO! 8 | ≈ 1 600 € | Relais isolés qui s'ouvrent à l'arrêt, Modbus TCP | Entrées non isolées en 230 V, version 24 V sans prix, génération n−1 |
| 6 | Shelly Pro | ≈ 1 940 € | Bon marché, API locale | Relais qui commutent la phase, 22 micrologiciels, isolement non publié |
| 7 | ESPHome sur rail DIN | ≈ 360 € | Le moins cher | Micrologiciel du projet, CE radio seulement, hors rail DIN |
| — | Loxone, Niko, Domintell, Wago | ≈ 3 950 à 8 100 € | | Trop chers pour le service rendu, ou contrôleur propriétaire sur le chemin des contacts |

**Recommandation** : pour la couche domotique de la V2, chiffrer en premier le **serveur d'entrées-sorties Modbus** piloté par la passerelle, avec des modules à chien de garde de communication et un isolement attesté, en demandant un devis en modules industriels ; garder **KNX** comme option si l'on préfère une norme reprise par n'importe quel intégrateur à un logiciel maison, au prix d'ETS et de 1,6 m de rail. La Revolution Pi Connect 5 reste la troisième voie, celle de la V1. Le choix revient à l'exploitant ; l'étude ne modifie pas la V2 et ne tranche pas le désaccord « Revolution Pi ou serveur d'E/S léger » : elle lui donne un corps chiffré.

## Réserves

- Les chiffres viennent de fiches techniques, de boutiques en ligne et de retours d'utilisateurs consultés en octobre 2026, relevés par des agents d'IA. Ce sont des estimations, à confirmer par un électricien, des devis, les fabricants et des essais.
- Les comportements en panne sont ceux que la documentation des fabricants décrit ou que des utilisateurs rapportent ; aucun n'a été essayé sur un banc.
- Les études V1 et la V2 ne sont pas modifiées par cette étude.

## Pages publiques (essensys-doc)

- `docs/etudes/remplacement-armoire/marche/index.md` : question, méthode, grille, tableau comparatif, classement, recommandation, réserves.
- `docs/etudes/remplacement-armoire/marche/{knx,loxone,niko-home-control,domintell,homematic-ip-wired,eltako-series-14,siemens-logo,wago-pfc200,shelly-pro,esphome-rail-din,modbus-es}.md` : un dossier par solution.
- Entrée « Solutions du marché » dans la navigation et sous-section dans `docs/etudes/index.md`.
