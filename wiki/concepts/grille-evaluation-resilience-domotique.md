---
tags: [concept, essensys, hardware, resilience, domotique, evaluation, methode]
sources: [analyses/2026-10-solutions-marche-armoire/analyse.md]
created: 2026-10-24
updated: 2026-10-24
---

# Grille Evaluation Resilience Domotique

> Grille pour juger une solution domotique face à l'exigence de résilience de [[Reponse Resilience Armoire]] : un calculateur grillé ne coupe aucun bouton. Construite pour l'étude [[Comparatif Solutions Marche Armoire]] (source : [[Analyse Solutions Marche Armoire 2026 10]]), elle est réutilisable pour toute candidate future, seule ou en couche domotique sur un filaire [[Filaire D Abord Domotique En Derivation]].

## Deux lectures

- **Seule** : la solution remplace l'armoire ; ses modules d'entrées reçoivent les poussoirs, ses actionneurs commandent les charges. On mesure ce qui reste quand son cerveau, son bus, son alimentation, son logiciel ou sa licence tombe.
- **En dérivation** : la solution n'est que la couche domotique posée sur le filaire. Elle ferme des contacts secs en parallèle des poussoirs, derrière le relais de garde et la borne sectionnable, lit l'état par des recopies et bat le cœur du chien de garde. Les critères qui comptent deviennent le prix par voie, l'ouverture du protocole, la place et l'absence de logiciel du projet dans l'armoire.

## Deux configurations

- **Minimale** : conforme au fabricant, un bus, une alimentation, un contrôleur. Chiffrée pour montrer l'écart.
- **Résiliente** : alignée sur la V2, un segment, une alimentation et, s'il existe, un contrôleur **par zone**. Le classement, le décompte des causes communes et le coût « armoire complète » portent sur elle.

## Règle 1 à trois niveaux

La règle 1, « un bouton ne passe jamais par un calculateur pour atteindre sa charge », décide de la lecture « seule ». La définition tolère le microcontrôleur du commerce d'un variateur à entrée locale.

| Niveau | Ce que fait le poussoir | Exemple |
| --- | --- | --- |
| **Tenue** | Il attaque directement un organe qui garde l'état, sans bus ni logiciel du projet | Télérupteur, variateur à entrée locale |
| **Partielle** | Il attaque un module du commerce, à micrologiciel fixé par le fabricant, qui lie lui-même son entrée à sa sortie, sans bus ni contrôleur ; une panne ne prive que les circuits de ce module | Module à entrée locale et relais intégré (Shelly Pro) |
| **Non tenue** | L'ordre passe par un bus ou par un contrôleur programmable ; la perte du bus, de son alimentation ou du contrôleur coupe le bouton | Bus de terrain (KNX, même sans contrôleur central), automate, serveur domotique, carte à micrologiciel du projet (ESPHome) |

Pour une solution « non tenue », on dit combien de boutons une panne de ligne ou de zone prive, et quelles parades le fabricant propose (relais bistables, manettes mécaniques, repli réglable).

## Huit causes communes

Liste fermée de défaillances uniques, passée sur la configuration résiliente ; on compte celles qui privent **toute la maison** de ses boutons :

1. l'alimentation du système ou du bus ;
2. un court-circuit ou une ligne collée sur un bus ;
3. le contrôleur central ;
4. le logiciel figé (plantage sans redémarrage) ;
5. une mise à jour ratée ;
6. une licence, un compte ou un cloud indisponible ;
7. le commutateur ou le routeur du réseau local ;
8. la foudre sur le chemin du bus.

Ce décompte ne se compare pas aux modes communs du conseil d'autocritique de la V2 (13, 5, 4 et 0 pour les trois V1 et le filaire, voir [[Analyse Etudes Remplacement Armoire 2026 10]]), dont la méthode n'est pas publiée.

## Hors contrainte

Une solution qui exige de changer les fils des poussoirs ou des charges est marquée **hors contrainte**, quel que soit son rang par ailleurs : longueur d'entrée limitée (10 m), câble blindé exigé, secteur porté sur les nappes de poussoirs. Les boutons tactiles, écrans et poussoirs connectés d'une gamme ne comptent pas.

## Autres critères

| Critère | Ce qu'on regarde |
| --- | --- |
| Foudre et isolement | Bus dans l'armoire ou à travers la maison ; isolement annoncé entre entrées, bus et contacts 230 V ; barrières de 4 kV et 8 mm et deux îlots TBTS tenables ([[Ilots TBTS Et Equipotentialite]]) ; parafoudres dédiés |
| Coût matériel HT | Armoire complète (seule) et couche seule (en dérivation), prix datés et sourcés, TTC convertis en HT au taux du pays ; prix non public marqué « estimé », « dérivé », « prix conseillé » ou « TVA non précisée » |
| Charge de travail | Jours d'électricien ; semaines-personne de logiciel et de paramétrage ; outil, licence, formation |
| Place | Mètres de rail, nombre de coffrets |
| Ouverture et pérennité | Protocole ouvert ou propriétaire, norme, nombre de fabricants, cloud ou licence, pièces à dix ans, communauté |
| Passerelle | Protocole exposé (KNXnet/IP, Modbus, MQTT, REST, API locale) et travail côté passerelle |
| Fonctions | Double appui, appui long, scénarios, délestage, alarme, écran : perdus, gardés ou reportés |

Le périmètre du coût est celui des totaux de la V2 (poussoirs, éclairages, volets, variateurs, fil pilote, cumulus, prises, arrosage, machines) ; alarme, sirène, détecteurs de fuite, écran et délestage sont des fonctions à reporter, hors total. En dérivation, le dispositif de la V2 s'impose à toutes et son coût n'est pas recompté.

## Limites

- Les comportements en panne viennent de la documentation et de retours d'utilisateurs, pas d'un banc : chaque verdict « à confirmer » appelle un essai.
- Les prix sont des relevés datés par des agents d'IA, pas des devis.
- La grille juge la résilience ; elle ne note ni l'ergonomie ni la richesse fonctionnelle, reportées en « fonctions perdues, gardées ou reportées ».

## Voir aussi

- [[Comparatif Solutions Marche Armoire]]
- [[Reponse Resilience Armoire]]
- [[Filaire D Abord Domotique En Derivation]]
