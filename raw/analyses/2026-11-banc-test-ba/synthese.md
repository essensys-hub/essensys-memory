---
title: Banc de test des BA SC940/SC941/SC942 — synthèse
date: 2026-11-11
origine: dépôt privé essensys-hub/essensys-test-banc-BoitierSecondaire et dépôt public essensys-board-SC840B, synthèse anonymisée
suivi: essensys-hub/essensys-doc#38
---

# Banc de test des boîtiers auxiliaires (BA)

Le banc de test de production des BA contrôle les trois cartes de la gamme : SC940 (pièces de vie), SC941 (pièces d'eau) et SC942 (chambres). Ses archives d'étude ont été retrouvées en novembre 2026.

!!! info "Où trouver les documents"
    - **Carte de test et logiciel** : dépôt public [`essensys-board-SC840B`](https://github.com/essensys-hub/essensys-board-SC840B) (projet Altium, Gerber, nomenclature, code source, binaires, spécification).
    - **Archives d'étude** (plans des points de test, mécanique, notice de la console) : dépôt privé `essensys-hub/essensys-test-banc-BoitierSecondaire`. Il reste privé parce qu'il contient des plans du fabricant de l'interface mécanique.
    - Suivi : [essensys-doc#38](https://github.com/essensys-hub/essensys-doc/issues/38).

Le banc du boîtier principal est décrit sur la page [Banc de test du BP](banc-de-test-bp.md).

## De quoi il est fait

| Élément | Description |
|---|---|
| Interface mécanique | Un coffret à presse et lit de clous, avec **trois plaques interchangeables**, une par carte |
| Carte de test SI840 | Microcontrôleur dsPIC33FJ256GP710A |
| Points de test | 58 sur la SC940, 66 sur la SC941, 63 sur la SC942 |
| Console | Un PC relié par un cordon USB-série, avec le logiciel Tera Term |

Ce banc n'a ni voyants ni écran : le résultat s'affiche ligne par ligne dans la console.

## Ce qu'il teste

| Test | Méthode | Critère |
|---|---|---|
| Alimentation | Moyenne de 8 mesures sur 12 bits | Entre 3325 et 4064 |
| Relais | Lecture de l'état, impulsion de 0,1 s, lecture, impulsion, lecture | L'état change, puis revient |
| Variateurs | Double appui (maximum), appui long de 3,1 s (moitié), appui (minimum) ; moyenne de 100 mesures sur 10 bits | Maximum ≥ 192 ; moitié entre 82 et 192 ; minimum ≤ 82 |
| Bus I2C | Le banc joue le rôle du BP : commande avec CRC16, puis lecture de la réponse | Le CRC de la réponse est juste |

La carte est déclarée `OK` seulement si tous les tests sont bons.

Le banc reconnaît la carte grâce à la plaque en place. Il lui parle à son adresse I2C : 0x11 pour la SC940, 0x12 pour la SC942, 0x13 pour la SC941.

| Carte | Voies testées | Dont variateurs |
|---|---|---|
| SC940 | 20 | 3 |
| SC941 | 22 | 1 |
| SC942 | 21 | 4 |

## Deux variantes du logiciel

| Variante | Test des variateurs |
|---|---|
| V3 | Avec le point milieu à 50 % |
| V3 Fast | Sans le point milieu, plus rapide |

La console affiche la version au démarrage.

## Utilisation

1. Relier le PC à la carte de test, ouvrir Tera Term, puis mettre le banc sous tension.
2. Régler le port série : **9600 bauds, 8 bits, sans parité, 1 bit de stop, sans contrôle de flux**.
3. Monter la plaque de la carte à tester et poser la carte.
4. Fermer le capot ou appuyer sur la barre d'espace.
5. Lire le rapport : une ligne par voie, `OK` ou `HS`, puis la ligne `Carte`.
6. Pour relancer : barre d'espace, ou ouvrir puis refermer le capot.

Si la console affiche `Erreur`, le banc n'a pas reconnu la plaque.

## Points ouverts

- Les archives ne contiennent aucune photo : l'existence et l'état du banc physique restent à confirmer.
- Le plan de cotes archivé porte l'indice A de la carte de test, le dépôt public l'indice B. La différence n'est pas documentée.
- Des plans de points de test « pour nappe » ont été faits en 2017 pour l'indice suivant de chaque carte. Leur raison d'être n'est pas expliquée.
- La variante du logiciel chargée dans le banc est inconnue.
