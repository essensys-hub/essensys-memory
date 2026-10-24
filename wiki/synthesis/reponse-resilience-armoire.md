---
tags: [synthesis, essensys, hardware, armoire, resilience, foudre, tbts, migration]
sources: [analyses/2026-10-etudes-remplacement-armoire/analyse.md, incidents/2026-08-foudre-bus-i2c/rapport-analyse.md, analyses/2026-10-solutions-marche-armoire/analyse.md]
created: 2026-10-24
updated: 2026-10-24
era: legacy
---

# Reponse Resilience Armoire

> Après l'[[Incident Foudre Bus I2C 2026 08]], l'exploitant exige (2026-10-21) que les 63 boutons muraux pilotent toujours leurs lumières, volets et variateurs si le contrôleur, un automate ou un Raspberry Pi grille. La réponse retenue est une armoire « filaire d'abord, domotique en dérivation » : aucun calculateur sur le chemin d'un bouton, une domotique ajoutée qui peut tomber sans rien couper. Source : [[Analyse Etudes Remplacement Armoire 2026 10]].

Les chiffres viennent en grande partie d'un conseil d'autocritique de six agents d'IA dans des rôles d'expert : ce sont des estimations, à confirmer par un électricien, des devis, les fabricants et des essais.

## Critères vérifiables

- Contrôleur domotique coupé, réseau débranché ou une sortie collée : chaque bouton commande toujours sa charge.
- L'état de chaque circuit survit à l'arrêt de la domotique et à une coupure du secteur.
- Une domotique muette, figée, fausse ou piratée ne bloque aucun bouton.
- Une barrière d'au moins 4 kV et 8 mm sépare chaque îlot ; aucun 0 V n'est relié au PE.
- Chaque repli est essayé à la recette, zone par zone.

## Ce que la foudre a appris

- Un bus interne court reste un chemin de foudre : l'I2C a servi de pont entre des cartes flottantes (voir [[Ilots TBTS Et Equipotentialite]]).
- Un BA mort prive toute sa zone de boutons ; l'état des éclairages vivait dans le firmware, pas dans des relais monostables.
- La panne est restée silencieuse : commandes acquittées, état des BA relu seulement après un ordre (voir [[Analyse Demarrage BP BA 2026 10]]).
- Une seule ligne tenue basse fait taire les trois BA : le découpage en zones n'arrête pas une cause commune.

## Pourquoi les études V1 échouent

Les trois études V1 (Revolution Pi, Arduino Opta, Raspberry Pi et Ethernet), figées le 2026-10-21, placent toutes un calculateur entre le bouton et le relais. Une Revolution Pi morte prive 55 boutons sur 63 ; avec l'Opta ou la refonte Raspberry Pi, un cerveau mort est une zone morte. L'AMDEC compte les modes de panne qui privent toute la maison de ses boutons : 13 (Revolution Pi), 5 (Opta), 4 (Raspberry Pi), 0 (filaire autonome). La V2 garde leur câblage de migration (répartiteur, blocs de phase Wago, jonctions IDC) et quelques organes : relais de couplage 38.51, variateurs EUD12D, barrières de 4 kV.

## L'architecture retenue

Le motif est décrit dans [[Filaire D Abord Domotique En Derivation]]. Pour cette armoire :

- éclairages sur télérupteurs Finder 20.22, volets sur deux relais en chaîne de priorité, variateurs Eltako EUD12D à entrée locale ;
- une source 24 V de classe II par zone (pièces de vie, chambres, pièces d'eau), F1 pour les boutons, F2 pour la domotique ;
- domotique en parallèle par contacts secs, derrière un relais de garde à chien de garde matériel et une borne sectionnable par zone ;
- fil pilote en confort par défaut, cumulus sur le contact heures creuses, délesteur autonome si le bilan de puissance l'exige ; alarme et sirènes restent dans la couche domotique, sur batterie ;
- contrôleur domotique acheté en dernier : Revolution Pi Connect 5 ou serveur d'E/S léger piloté par la passerelle.

## Ce que garde la maison, panne par panne

| Panne | Ce qui reste |
| --- | --- |
| Contrôleur domotique, réseau ou passerelle | Les 63 boutons ; radiateurs en confort |
| Source de commande d'une zone | Les deux autres zones ; lumières de la zone dans leur état, au levier |
| Un télérupteur ou un relais de volet | Les autres circuits ; jamais les deux sens d'un volet à la fois |
| Coupure du secteur | Télérupteurs dans leur état au retour ; alarme sur batterie |
| La foudre | Bobines et contacts ; lumières dans leur état, au levier |

Restent deux défauts latents : la batterie de l'alarme et l'isolement qui se dégrade, à mesurer chaque année et après chaque orage proche.

## Coût estimé

- Matériel : 3 450 à 3 950 € HT pour la couche filaire, 4 300 à 4 900 € HT avec une domotique minimale, 6 450 à 7 850 € HT avec une domotique complète ; environ 1 000 € de plus sans attestations d'isolement.
- Main-d'œuvre : 6 à 8,5 jours d'électricien ; 1,6 à 2,1 m de rail, donc un second coffret.
- Logiciel : aucun sur le chemin d'un bouton, puis 5 à 11 semaines-personne de domotique (contre 11 à 28 avant bascule dans les V1).
- Renoncements : double clic, appui long, scénarios câblés dans les BA.

## Les preuves à apporter

1. Relevé d'une journée par l'électricien : volumes des salles d'eau, lignes de boutons (résistance de boucle, isolement), place loin du photovoltaïque, différentiels, bilan de puissance, parafoudre de tête et terre.
2. Attestations écrites d'isolation renforcée de Finder et d'Eltako.
3. Banc deux lumières : Finder 20.22 contre Eltako ES12Z-200-UC, Raspberry Pi 3 et 4 sur le 24 V de la domotique, huit essais.
4. Essai de choc de 2 puis 4 kV en mode commun sur une ligne de bouton, domotique branchée.
5. Recette de chaque zone, contrôleur coupé.

## Désaccords ouverts

- Éclairages : télérupteur électromécanique ou actionneurs Eltako (départagé par le banc et l'essai de choc).
- Volets : chaîne de deux relais ou Eltako EGS12Z (banc avec un vrai moteur).
- Source : 24 V continu ou transformateur 50 Hz (volumes des salles d'eau, norme).
- BA actuels : vérifier leur état sans les réparer, ou les réparer d'abord.
- Couche domotique : Revolution Pi Connect 5 ou serveur d'E/S léger.
- Calendrier : poser après les essais, ou dès novembre.

## Couche domotique : candidates chiffrées (2026-10-24)

L'étude [[Comparatif Solutions Marche Armoire]] a passé onze solutions du marché au crible de la [[Grille Evaluation Resilience Domotique]]. Aucune ne tient la règle 1 seule : la V2 reste la seule réponse qui la tient. En dérivation sur le filaire, deux candidates s'ajoutent au désaccord « Revolution Pi Connect 5 ou serveur d'E/S léger » :

| Candidate | Couche HT | Ce qu'elle apporte |
| --- | --- | --- |
| Serveur d'E/S Modbus piloté par la passerelle | ≈ 430 € en modules grand public ; ≈ 3 000 à 3 900 € en modules industriels | Aucune logique dans l'armoire, protocole ouvert ; chien de garde de communication sur les modules industriels seulement. À chiffrer en premier |
| KNX TP | ≈ 3 100 € | Norme à 500 fabricants, aucun Linux ni logiciel du projet sur le chemin des contacts ; ETS à acheter et apprendre |
| Revolution Pi Connect 5 | ≈ 581 € nue, modules d'E/S non chiffrés | La voie de la V1, candidate de trois conseillers |

Estimations d'octobre 2026 par des agents d'IA, à confirmer par un électricien, des devis, les fabricants et des essais. L'étude ne tranche pas et ne modifie pas la V2.

## Feuille de route (estimations)

| Quand | Étape |
| --- | --- |
| Novembre 2026 | Relevé, banc, attestations |
| Novembre-décembre 2026 | Chambres ([[Essensys Board Sc942c]]) et pièces d'eau ([[Essensys Board Sc941c]]) reviennent au bouton |
| Janvier 2027 | Pièces de vie ([[Essensys Board Sc940]]), fin du bus I2C |
| Février-avril 2027 | Couche domotique |
| Avant mai 2027 | Parafoudres |
| Printemps 2027 | Retrait du BP ([[Essensys Board Sc944d]]), fonction par fonction |

## Sept règles pour toutes les installations

1. Un bouton ne passe jamais par un calculateur pour atteindre sa charge.
2. L'état d'un circuit vit dans un organe bistable, pas dans un logiciel.
3. La domotique ajoute un ordre, elle n'en retire jamais.
4. Une source et un fusible par zone, et un fusible distinct pour la domotique.
5. Une barrière d'au moins 4 kV et 8 mm à chaque passage d'îlot ; le 0 V jamais au PE ; les parafoudres hors des coffrets.
6. Chaque repli se choisit au câblage et s'essaie à la recette.
7. L'isolement se mesure chaque année et après chaque orage proche.

## Pages publiques

Dans [[Essensys DOC]] :

- `essensys-doc/docs/etudes/resilience.md` : la réponse en une page
- `essensys-doc/docs/etudes/remplacement-armoire/v2/filaire-d-abord.md` : étude V2
- `essensys-doc/docs/etudes/remplacement-armoire/v2/conseil.md` : méthode et verdict du conseil
- `essensys-doc/docs/etudes/remplacement-armoire/v2/autocritique-v1.md` : autocritique des V1
- `essensys-doc/docs/etudes/remplacement-armoire/v2/sections-de-cables.md` : sections de câbles
- `essensys-doc/docs/etudes/banc-deux-lumieres.md` : banc deux lumières
- `essensys-doc/docs/etudes/remplacement-armoire/{revolution-pi,arduino-opta,raspberry-pi-ethernet}.md` : études V1 figées

## Voir aussi

- [[Incident Foudre Bus I2C 2026 08]]
- [[Protection Surtension Bus I2C]]
- [[Migration Legacy To Modern]]
- [[Product Roadmap]]
- [[Comparatif Solutions Marche Armoire]] : onze solutions du marché face à l'exigence, seules et en dérivation
