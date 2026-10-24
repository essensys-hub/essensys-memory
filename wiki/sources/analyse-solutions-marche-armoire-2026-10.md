---
tags: [source, essensys, hardware, armoire, resilience, domotique, knx, modbus, comparatif]
sources: [analyses/2026-10-solutions-marche-armoire/analyse.md]
created: 2026-10-24
updated: 2026-10-24
era: legacy
---

# Analyse Solutions Marche Armoire 2026 10

**Source :** `raw/analyses/2026-10-solutions-marche-armoire/analyse.md`
**Type :** analyse anonymisée (étude comparative de onze solutions domotiques du marché, publiée dans [[Essensys DOC]] par la PR essensys-hub/essensys-doc#20)

## Métadonnées

| Champ | Valeur |
|---|---|
| Date de la source | 2026-10-24 |
| Déclencheur | La V2 ([[Reponse Resilience Armoire]]) laisse ouvert le choix de la couche domotique ; l'exploitant demande si une solution du marché, KNX en tête, peut remplacer l'armoire **sans toucher au câblage** (brief validé le 2026-10-24) |
| Périmètre | Les quatre cartes de l'armoire ([[Essensys Board Sc944d]], [[Essensys Board Sc940]], [[Essensys Board Sc941c]], [[Essensys Board Sc942c]]) : 63 poussoirs sur trois nappes, 25 éclairages, 15 volets et un store, 8 variateurs, fil pilote, cumulus, prises, arrosage, machines ; la passerelle CM5 doit pouvoir parler à la solution |
| Méthode | Onze dossiers au même gabarit ; deux lectures (seule, en dérivation) ; deux configurations (minimale, résiliente) ; grille décrite dans [[Grille Evaluation Resilience Domotique]] ; relecture par un agent d'IA en relecteur indépendant |
| Pages publiques | [[Essensys DOC]], `docs/etudes/remplacement-armoire/marche/` (index et onze dossiers) |
| Suivi | essensys-hub/essensys-doc#19 (étude), essensys-hub/essensys-memory#20 (ingestion) |

Les chiffres sont des estimations d'octobre 2026, relevées par des agents d'IA dans des fiches techniques, des boutiques en ligne et des retours d'utilisateurs : à confirmer par un électricien, des devis, les fabricants et des essais. Aucun comportement en panne n'a été essayé sur un banc.

## Affirmations clés

- **Aucune des onze solutions ne tient la règle 1** (un bouton ne passe jamais par un calculateur). Celles qui s'en approchent mettent un microcontrôleur par poussoir ou par zone, pas en le supprimant. La V2 reste la seule réponse qui tient.
- **Classement « seule »** (configuration résiliente, une alimentation et un segment par zone) : 1. Shelly Pro (« partielle, à confirmer », 0 cause commune, un module mort prive 4 circuits, isolement non publié, 63 relais d'interface) ; 2. KNX TP (bus le plus proche de l'exigence, 0 cause commune par zone, relais bistables, une zone de 20 à 22 boutons tombe avec son alimentation) ; 3. Eltako Series 14 ; 4. Siemens LOGO! 8 (version 230 V hors contrainte) ; 5. ESPHome sur rail DIN (micrologiciel du projet : non tenue) ; 6. Loxone ; 7. Niko Home Control II ; 8. Homematic IP Wired (hors contrainte sauf accord écrit du fabricant) ; 9. Modbus et passerelle (3 à 4 causes communes) ; 10. Wago PFC200 (5) ; 11. Domintell (hors contrainte, 6).
- **Hors contrainte** (recâblage exigé) : Domintell (entrées limitées à 10 m), Homematic IP Wired (câble blindé au-delà de 3 m), Siemens LOGO! 8 en version 230 V (secteur sur les nappes).
- **Coûts « armoire complète » HT** (résiliente / minimale) : KNX ≈ 5 200 / 2 950 € ; Loxone ≈ 6 700 / 3 900 € ; Niko ≈ 9 200 / 7 600 € ; Domintell ≈ 7 530 / 6 190 € ; Homematic ≈ 3 510 / 2 630 € ; Eltako ≈ 2 180 / 1 800 € ; LOGO! ≈ 1 900 / 1 600 € ; Wago ≈ 7 270 / 6 250 € (hors alimentation et relais) ; Shelly ≈ 2 270 € (hors 63 relais d'interface, ≈ 3 500 € au total) ; ESPHome ≈ 710 € (hors alimentation) ; Modbus ≈ 820 / 705 €. Repère V2 : ≈ 3 450 à 3 950 € HT filaire seul, 6 450 à 7 850 € HT avec domotique complète.
- **Recommandation « en dérivation »** : chiffrer en premier un **serveur d'entrées-sorties Modbus** piloté par la passerelle (≈ 430 € HT en modules grand public sans chien de garde ni isolement publié ; ≈ 3 000 à 3 900 € HT en modules industriels à chien de garde de communication), garder **KNX TP** (≈ 3 100 € HT) comme option normalisée sans Linux ni logiciel du projet sur le chemin des contacts, au prix d'ETS et de 1,6 m de rail. Suivent Eltako Series 14 (≈ 1 580 €), Homematic IP Wired (≈ 2 480 €), LOGO! (≈ 1 600 €), Shelly Pro (≈ 1 940 €), ESPHome (≈ 360 €). Loxone, Niko, Domintell et Wago (≈ 3 950 à 8 100 €) sont écartés.
- L'étude **ne tranche pas** le désaccord « Revolution Pi Connect 5 ou serveur d'E/S léger » de la V2 : elle lui donne un corps chiffré. La Revolution Pi Connect 5 (≈ 581 € HT nue, modules d'E/S non chiffrés) reste la troisième voie. Le choix revient à l'exploitant ; la V2 n'est pas modifiée.
- **Grille** : règle 1 lue à trois niveaux (tenue, partielle, non tenue) ; huit causes communes fermées comptées sur la configuration résiliente ; les 13/5/4/0 du conseil d'autocritique ne se comparent pas à ce décompte.
- **Écartés de l'étude** : Revolution Pi, Arduino Opta, Raspberry Pi et Ethernet (V1, repères) ; Zigbee et Z-Wave sur rail DIN ; Legrand MyHome et Hager coviva ; Beckhoff.

## Pages liées

- [[Comparatif Solutions Marche Armoire]] : la synthèse, tableau et recommandation
- [[Grille Evaluation Resilience Domotique]] : la grille réutilisable
- [[Reponse Resilience Armoire]] et [[Filaire D Abord Domotique En Derivation]] : l'exigence et la V2 sur lesquelles la lecture « en dérivation » s'appuie
- [[Analyse Etudes Remplacement Armoire 2026 10]] : la source précédente (V1, conseil, V2, banc)
