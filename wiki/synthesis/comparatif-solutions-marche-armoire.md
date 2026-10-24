---
tags: [synthesis, essensys, hardware, armoire, resilience, domotique, knx, modbus, comparatif]
sources: [analyses/2026-10-solutions-marche-armoire/analyse.md, analyses/2026-10-etudes-remplacement-armoire/analyse.md]
created: 2026-10-24
updated: 2026-10-24
era: legacy
---

# Comparatif Solutions Marche Armoire

> Onze solutions domotiques du marché (KNX TP, Loxone, Niko Home Control II, Domintell, Homematic IP Wired, Eltako Series 14, Siemens LOGO! 8, Wago PFC200, Shelly Pro, ESPHome sur rail DIN, modules Modbus et passerelle) évaluées pour remplacer l'armoire Essensys **sans toucher au câblage** : seules face à l'exigence de [[Reponse Resilience Armoire]], puis en couche domotique sur le filaire [[Filaire D Abord Domotique En Derivation]]. Source : [[Analyse Solutions Marche Armoire 2026 10]] ; grille : [[Grille Evaluation Resilience Domotique]].

Estimations d'octobre 2026, relevées par des agents d'IA et relues par un relecteur indépendant lui aussi agent d'IA ; aucun essai au banc. À confirmer par un électricien, des devis, les fabricants et des essais.

## La question

La V2 répond à l'exigence (un calculateur grillé ne coupe aucun bouton) avec des télérupteurs, des relais et des variateurs à entrée locale, et laisse ouvert le choix de la couche domotique entre une Revolution Pi Connect 5 et un serveur d'E/S léger piloté par la passerelle. Avant de s'engager : une solution du marché, KNX en tête, pourrait-elle remplacer les quatre cartes ([[Essensys Board Sc944d]], [[Essensys Board Sc940]], [[Essensys Board Sc941c]], [[Essensys Board Sc942c]]) sans changer un fil, et comment une dizaine de solutions se comparent-elles sur les mêmes critères ?

Ce qui ne change pas : 63 poussoirs en contacts secs sur trois nappes (pièces de vie 20, chambres 21, pièces d'eau 22), charges câblées sur l'armoire (25 éclairages, 15 volets dont le store, 8 variateurs, fil pilote, cumulus, prises, arrosage, machines), câblage de migration des V1, passerelle CM5 à backend Go qui doit parler à la solution.

## En bref

- **KNX peut remplacer l'armoire sans toucher un fil**, et découpé en une ligne par zone il ne laisse aucune défaillance unique priver toute la maison de ses boutons. Mais chaque bouton passe par le bus : la perte d'une alimentation de zone, panne la plus fréquente, coupe 20 à 22 boutons. **Il ne répond pas à l'exigence**, et aucune des onze solutions n'y répond.
- **Seule**, la plus proche est **Shelly Pro** : la liaison entrée → relais vit dans le micrologiciel du fabricant de chaque module, sans bus ni contrôleur ; « partielle, à confirmer » (isolement non publié, état et verrouillage des volets logiciels, un relais d'interface par poussoir).
- **En dérivation**, la couche la moins chère et la plus simple est un **serveur d'E/S Modbus piloté par la passerelle** (≈ 430 € HT en modules grand public, ≈ 3 000 à 3 900 € HT en industriel) ; **KNX** (≈ 3 100 € HT) est l'option normalisée et durable. Les deux donnent un corps au désaccord « Revolution Pi ou serveur d'E/S léger » de la V2 sans le trancher.

## Tableau comparatif (lecture « seule », configuration résiliente)

Coûts HT, matériel et licence compris, hors électricien. « Causes communes » = nombre des huit défaillances uniques qui privent toute la maison de ses boutons (résiliente / minimale).

| Solution | Règle 1 | Causes communes | Pire panne simple | Armoire complète | Couche en dérivation | Rail | Ouverture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KNX TP | Non tenue | 0 / 3 | Une zone ; éclairages gardent leur état | ≈ 5 200 / 2 950 € | ≈ 3 100 € | 2,1 m | Norme ouverte, 500 fabricants, ETS payant |
| Loxone | Non tenue | 0 / 6 | Une zone ; état des relais non documenté | ≈ 6 700 / 3 900 € | ≈ 3 950 € | ≈ 2 m | Propriétaire, logiciel gratuit, vente « Partner » |
| Niko Home Control II | Non tenue | 0 ou 1 / 6 ou 7 | Une zone ; Internet « requis » | ≈ 9 200 / 7 600 € | ≈ 8 100 € | ≈ 2,4 m | Propriétaire, API MQTT à jeton annuel |
| Domintell | Non tenue, **hors contrainte** | 6 / 6 | Toute la maison | ≈ 7 530 / 6 190 € | ≈ 5 570 € | ≈ 2,3 m | Propriétaire, Light Protocol documenté |
| Homematic IP Wired | Non tenue, **hors contrainte** sauf accord écrit | 4 (0 si liaisons directes) / 7 | Toute la maison ou une zone | ≈ 3 510 / 2 630 € | ≈ 2 480 € | 1,6 m | Propriétaire, centrale libre OpenCCU |
| Eltako Series 14 | Non tenue | 0 / 3 | Une zone ; éclairages s'éteignent | ≈ 2 180 / 1 800 € | ≈ 1 580 € | ≈ 1 m | Propriétaire, un fabricant |
| Siemens LOGO! 8 | Non tenue ; 230 V **hors contrainte** | 0 / 5 | Une zone ; relais retombent | ≈ 1 900 / 1 600 € | ≈ 1 600 € | 1,3 m | Propriétaire, Modbus TCP |
| Wago PFC200 | Non tenue | 5 / 6 | Toute la maison ; repli à zéro en 50 ms | ≈ 7 270 / 6 250 € (hors alim, relais) | ≈ 6 350 € | ≈ 0,9 m | Ouvert (Modbus, MQTT, CODESYS) |
| Shelly Pro | **Partielle**, à confirmer | 0 / 0 | Un module : 4 circuits | ≈ 2 270 € (hors 63 relais d'interface, ≈ 3 500 € au total) | ≈ 1 940 € | 1,1 m | API locale ouverte, cloud facultatif |
| ESPHome sur rail DIN | Non tenue (micrologiciel du projet) | 0 (2 sans réglages) / 2 | Une zone ; relais à zéro au redémarrage | ≈ 710 € (hors alim) | ≈ 360 € | 3 × 320 mm, hors rail | Open source, CE radio seulement |
| Modbus et passerelle | Non tenue | 3 RTU, 4 TCP / 6 | Toute la maison (passerelle) | ≈ 820 / 705 € | **≈ 430 €** ; 3 000 à 3 900 € en industriel | 1,9 m | Protocole ouvert, libre de droits |

Repères non comparables (méthode du conseil d'autocritique, voir [[Analyse Etudes Remplacement Armoire 2026 10]]) : V2 filaire d'abord, règle 1 **tenue**, 0 mode commun, ≈ 3 450 à 3 950 € HT filaire seul et 6 450 à 7 850 € HT avec domotique complète ; Revolution Pi (V1) 13 modes, ≈ 5 450 € ; Arduino Opta (V1) 5 modes, ≈ 5 600 € ; Raspberry Pi et Ethernet (V1) 4 modes, ≈ 3 160 €.

## Classement « seule »

1. **Shelly Pro** : partielle à confirmer, un module mort prive quatre circuits ; isolement non publié, volets verrouillés par logiciel, 63 relais d'interface pour garder les nappes en TBTS.
2. **KNX TP** : le bus le plus proche de l'exigence, relais bistables, manettes mécaniques chez certains fabricants ; une zone tombe avec son alimentation ; portée des entrées (100 m) à confirmer.
3. **Eltako Series 14** : compact et bon marché ; la perte du 12 V d'une zone éteint ses lumières ; fabricant unique.
4. **Siemens LOGO! 8** : relais qui retombent, entrées 230 V non isolées, pas de variateur ; version 230 V hors contrainte, version 24 V sans prix.
5. **ESPHome sur rail DIN** : logique locale par carte et prix le plus bas, mais micrologiciel du projet, relais à zéro au redémarrage, CE radio seulement : la refonte Raspberry Pi des V1 en moins cher et moins propre.
6. **Loxone** : un Miniserver par zone au prix fort, rien de manœuvrable à la main.
7. **Niko Home Control II** : à contre-emploi, dépendance à Internet affirmée.
8. **Homematic IP Wired** : entrées non isolées portant le 24 V du bus sur les nappes, câble blindé exigé : hors contrainte sauf accord écrit.
9. **Modbus et passerelle** : passerelle, Linux et logiciel sur le chemin de chaque appui.
10. **Wago PFC200** : contrôleur unique, repli à zéro en 50 ms, prix élevé.
11. **Domintell** : hors contrainte, maître unique.

Leçon : les solutions qui s'approchent de l'exigence mettent **un microcontrôleur par poussoir ou par zone**, elles ne le suppriment pas. La V2 reste la seule réponse qui tient la règle 1.

## Recommandation « en dérivation »

En dérivation, la couche domotique ferme des contacts secs en parallèle des poussoirs, lit des recopies, bat le cœur du relais de garde et parle à la passerelle : ≈ 85 sorties et ≈ 70 entrées. Le dispositif de la V2 (relais de couplage, relais de garde, fusible F2, durées bornées, barrières de 4 kV) s'impose à toutes et n'est pas recompté.

| Rang | Solution | Couche HT | Pour | Contre |
| --- | --- | --- | --- | --- |
| 1 | **Modbus et passerelle** | ≈ 430 € (grand public) ; ≈ 3 000 à 3 900 € (industriel) | Aucune logique dans l'armoire, protocole ouvert et libre, chien de garde de communication sur les modules industriels | Modules bon marché sans chien de garde ni isolement ni CE trouvés ; maître unique, acceptable pour une couche sacrifiable |
| 2 | **KNX TP** | ≈ 3 100 € | Norme, 500 fabricants, pièces à dix ans, aucun Linux ni logiciel du projet sur le chemin des contacts, minuterie d'actionneur en battement de cœur | ETS à acheter et apprendre, 88 modules, relais 16 A surdimensionnés |
| 3 | Eltako Series 14 | ≈ 1 580 € | Compact, sans licence, fabricant des variateurs de la V2 | Propriétaire, liaison série, pas de bibliothèque Go |
| 4 | Homematic IP Wired | ≈ 2 480 € | Peu de modules, centrale libre, sans cloud | Entrées non isolées, battement de cœur à travers centrale et réseau |
| 5 | Siemens LOGO! 8 | ≈ 1 600 € | Relais isolés ouverts à l'arrêt, Modbus TCP | Entrées 230 V non isolées, génération n−1 |
| 6 | Shelly Pro | ≈ 1 940 € | Bon marché, API locale | Relais sur la phase, 22 micrologiciels, isolement non publié |
| 7 | ESPHome sur rail DIN | ≈ 360 € | Le moins cher | Micrologiciel du projet, CE radio seulement, hors rail DIN |
| — | Loxone, Niko, Domintell, Wago | ≈ 3 950 à 8 100 € | | Trop chers, ou contrôleur propriétaire sur le chemin des contacts |

**Recommandation de l'étude** : chiffrer en premier le serveur d'E/S Modbus piloté par la passerelle, en modules industriels à chien de garde de communication et isolement attesté (demander un devis) ; garder KNX si l'on préfère une norme reprise par n'importe quel intégrateur à un logiciel maison. La Revolution Pi Connect 5 (≈ 581 € HT nue, modules d'E/S non chiffrés) reste la troisième voie, celle de la V1. Le choix revient à l'exploitant ; la V2 n'est pas modifiée.

## Ce que cela change pour la V2

- Le désaccord « Revolution Pi Connect 5 ou serveur d'E/S léger » ([[Reponse Resilience Armoire]]) a maintenant deux candidates chiffrées de plus : Modbus et passerelle (la forme concrète du serveur d'E/S léger) et KNX TP.
- Côté passerelle, Modbus RTU ou TCP et KNXnet/IP sont les deux protocoles à prévoir dans le backend Go ; le chien de garde de communication des modules industriels, ou la minuterie d'actionneur KNX, peut servir de battement de cœur au relais de garde.
- Rien n'est tranché : devis, attestations d'isolement et banc restent à faire, comme pour le reste de la V2.

## Pages publiques

Dans [[Essensys DOC]], `essensys-doc/docs/etudes/remplacement-armoire/marche/` : `index.md` (question, méthode, grille, tableau, classement, recommandation, réserves) et un dossier par solution (`knx.md`, `loxone.md`, `niko-home-control.md`, `domintell.md`, `homematic-ip-wired.md`, `eltako-series-14.md`, `siemens-logo.md`, `wago-pfc200.md`, `shelly-pro.md`, `esphome-rail-din.md`, `modbus-es.md`). PR essensys-hub/essensys-doc#20, ticket essensys-hub/essensys-doc#19.

## Voir aussi

- [[Grille Evaluation Resilience Domotique]]
- [[Filaire D Abord Domotique En Derivation]]
- [[Incident Foudre Bus I2C 2026 08]]
- [[Product Roadmap]]
