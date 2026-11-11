---
title: Banc de test du BP SC944 — synthèse des archives (corrigée)
date: 2026-11-11
origine: dépôt privé essensys-hub/essensys-test-banc-SC944D et dépôt public essensys-board-SC841A, synthèse anonymisée
suivi: essensys-hub/essensys-doc#36, corrigé par #38
---

# Banc de test du boîtier principal (BP)

Le banc de test de production du BP (carte SC944) a été retrouvé en novembre 2026 avec ses archives d'étude. Cette page en donne la synthèse.

!!! info "Où trouver les documents"
    - **Carte d'interface et logiciel** : dépôt public [`essensys-board-SC841A`](https://github.com/essensys-hub/essensys-board-SC841A) (projet Altium, Gerber, nomenclature, code source et binaire du logiciel de test).
    - **Archives d'étude** (spécification, plans des points de test, mécanique, croquis, photos) : dépôt privé `essensys-hub/essensys-test-banc-SC944D`. Il reste privé parce qu'il contient des plans du fabricant de l'interface mécanique et des documents de fabricants.
    - Suivi : [essensys-doc#36](https://github.com/essensys-hub/essensys-doc/issues/36), corrigé par [#38](https://github.com/essensys-hub/essensys-doc/issues/38).


## À quoi il sert

Le banc contrôle une carte BP à la sortie de fabrication. L'opérateur pose la carte sur un lit de clous et ferme la presse. Le banc :

1. alimente la carte en 24 V (« secteur »), puis en 12 V (« secouru ») ;
2. mesure les tensions internes et allume un voyant vert ou rouge par tension ;
3. vérifie que la carte coupe et rétablit le +15VSP, la tension qui alimente les boîtiers auxiliaires (BA) ;
4. vérifie les alimentations des détecteurs de présence, des sirènes et du bus BA ;
5. répond aux trames I2C du bus BA, pour que la carte valide elle-même la communication ;
6. offre des boutons, des voyants et des borniers pour tester à la main les autres entrées et sorties.

## De quoi il est fait

| Élément | Description |
|---|---|
| Interface mécanique | Coffret à presse et lit de clous, réalisé sur mesure par un fabricant d'interfaces de test ; plaque porte-carte « 944-BP » |
| Carte d'interface SI841A | Carte de façade : écran, boutons, voyants bicolores, microcontrôleur dsPIC33FJ256GP710A. Schéma de 19 folios |
| Points de test | 74 clous sur la carte, plus la prise Ethernet et 10 perçages de réserve pour la programmation |
| Alimentations | Trois alimentations rail DIN : 24 V, 12 V et 5 V |
| Réseau | Un routeur, relié directement à la prise Ethernet de la carte |
| Téléinformation | Un compteur électrique sert de source |

L'étude date de juillet 2014 à février 2015.

Le banc des boîtiers auxiliaires est décrit sur la page [Banc de test des BA](banc-de-test-ba.md).

## Séquence automatique

Le microcontrôleur du banc reste en reset tant que la presse est ouverte. La fermer avec une carte en place lance le test ; l'ouvrir l'arrête.

| # | Étape | Ce que fait le banc | Voyant |
|---|---|---|---|
| 1 | Lancement | Attend que l'opérateur ait mis le strap de forçage du +15VSP | TEST FINI clignote rouge tant qu'il manque |
| 2 | Démarrage | Alimente la carte en 24 V seul et attend 21 s | – |
| 3 | Tensions sous secteur | Mesure 15V, 15VS, 5VS, 3V3S, +15VSP, +12VSP | Un voyant par tension |
| 4 | Pilotage 1/2 | Le +15VSP doit être présent | – |
| 5 | Tensions sous secouru | Applique le 12 V puis coupe le 24 V ; mesure 15VS, 5VS, 3V3S | Un voyant par tension |
| 6 | Pilotage 2/2 | Attend 6,5 s que la carte coupe le +15VSP, qui doit tomber à 0 V | **P** |
| 7 | Forçage | Le +15VSP doit être à 0 V ; l'opérateur retire le strap ; le +15VSP doit revenir | **F** clignote, puis donne le résultat |
| 8 | Alimentations d'alarme | Applique le 24 V puis coupe le 12 V ; mesure les alimentations des deux détecteurs de présence et des deux sirènes | Un voyant par alimentation |
| 9 | Bus BA | Mesure l'alimentation du bus, puis répond en permanence aux trames du BA « pièces de vie » | Voyant BA ; résultat de la communication sur l'écran de la carte |

Vert : mesure bonne. Rouge : mesure mauvaise.

Lors d'un changement d'alimentation, le banc applique toujours la nouvelle tension avant de couper l'ancienne.

Les seuils de chaque mesure sont dans le fichier `Banc_BP.h` du logiciel. D'après ses notes de version, le logiciel publié (`Banc_BP_V2_FAST`) suit la spécification v4 et demande un BP en version 091-30 ou plus récente.

Les autres fonctions se testent ensuite à la main depuis la façade : détecteur d'ouverture, signal et fraude des détecteurs et des sirènes, fuite d'eau, pluie, vent, bouton magique, arrosage, fil pilote (zones jour et nuit, deux salles de bain), machines à laver, prises de sécurité, cumulus.

## Sécurité

- Le banc applique du 230 V sur la partie fil pilote. D'après les croquis d'étude, ce 230 V passe par deux relais (phase et neutre) qui ne collent que presse fermée. **Ce point reste à vérifier sur le banc avant toute remise sous tension.**
- Le banc n'a pas été mis sous tension depuis des années.

## Ce qui manque

| Manque | Conséquence |
|---|---|
| Notice d'utilisation | Le mode opératoire est déduit de la spécification et du code |
| Plan de câblage lit de clous → carte d'interface | La correspondance clou → connecteur n'est pas documentée |

## Points ouverts

- Vérifier que le logiciel chargé dans le banc est bien celui du dépôt `essensys-board-SC841A`.
- Les plans des points de test portent l'indice C de la carte. Leur validité pour l'indice D n'est pas établie.

!!! note "Correction du 11 novembre 2026"
    La première version de cette page disait que la SI841A n'était pas la SC841A et que le logiciel du banc était perdu. C'était faux : tout est dans `essensys-board-SC841A`.
