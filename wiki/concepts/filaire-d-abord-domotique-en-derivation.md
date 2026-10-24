---
tags: [concept, essensys, hardware, architecture, resilience, domotique, tbts, foudre]
sources: [analyses/2026-10-etudes-remplacement-armoire/analyse.md, analyses/2026-10-solutions-marche-armoire/analyse.md]
created: 2026-10-24
updated: 2026-10-24
---

# Filaire D Abord Domotique En Derivation

> Motif d'architecture pour une installation domotique dont les commandes locales doivent survivre à la perte de l'électronique : le bouton attaque directement un organe qui garde l'état, et la domotique s'ajoute en parallèle, sans jamais pouvoir retirer un ordre. Appliqué à l'armoire Essensys dans [[Reponse Resilience Armoire]].

## Le chemin du bouton

- **Organe bistable commandé par le bouton** : télérupteur électromécanique pour un éclairage, deux relais en chaîne de priorité pour un volet (jamais les deux sens), variateur à entrée locale. L'état vit dans l'organe, pas dans un logiciel ; il survit à une coupure du secteur.
- **Source et fusibles par zone** : une source TBTS de classe II par zone, homologuée EN 61558-2-16. F1 protège le commun des boutons, F2 (plus petit) celui des contacts domotiques : une domotique folle fait fondre F2, jamais F1.
- Aucun calculateur, aucun bus, aucun logiciel entre le bouton et sa charge.

## La domotique en dérivation

- **Contacts secs en parallèle** des poussoirs, par des relais de couplage isolés ; jamais sur une entrée prioritaire.
- **Relais de garde à chien de garde matériel**, un par zone : réarmé en permanence par un signal alterné couplé en capacitif, il retombe en moins d'une seconde si la domotique se tait ou se fige, et ne colle au démarrage qu'après plusieurs réarmements.
- **Borne sectionnable** par zone sur le commun domotique : retour arrière immédiat et parade au contact soudé.
- **Durées bornées dans le câblage** : un commun « impulsion » coupé au-delà d'une seconde pour les télérupteurs, un commun « maintien » coupé au-delà de la course pour les volets. Un ordre faux ou piraté reste borné.
- **Recopie d'état lue, jamais réimposée** : un second contact de l'organe, en 230 V, commande un relais de recopie ; seul son contact sec rejoint une entrée optocouplée. Un changement non commandé marque le circuit « repris à la main ».

## Isolement et foudre

- **Deux îlots TBTS** distincts, l'un pour les boutons, l'autre pour la domotique. Leurs 0 V ne se touchent jamais et ne touchent pas le PE (voir [[Ilots TBTS Et Equipotentialite]]).
- **Une barrière d'au moins 4 kV et 8 mm** à chaque passage d'îlot : bobine et contacts de l'organe, relais de couplage, relais de garde, optocoupleurs, isolateur Ethernet.
- Le motif coupe le chemin de l'onde au lieu de l'écrêter, contrairement à [[Protection Surtension Bus I2C]] ; les parafoudres restent au tableau et au bout des lignes extérieures.

## Replis choisis au câblage

Chaque fonction a un état de repli décidé à la conception et essayé à la recette (contrôleur coupé, réseau débranché, une sortie collée) : état gardé pour un éclairage, arrêt pour un volet, fil pilote en confort, cumulus sur le contact heures creuses.

## Limites

- Une bobine de télérupteur 24 V tire environ 230 mA : des ordres groupés doivent être séquencés, et la longueur des lignes de boutons est bornée par la chute de tension.
- Plus de place sur rail qu'une solution centralisée (second coffret probable).
- On renonce au double clic, à l'appui long et aux scénarios câblés dans les cartes.
- L'isolation renforcée des organes doit être attestée par écrit par le fabricant, sinon il faut un relais de couplage de plus par circuit.
- Ce qui n'a pas d'organe autonome (alarme, sirènes, délestage sans délesteur dédié) reste dépendant de la couche domotique.

## Quelle couche domotique en dérivation ?

Le motif ne fixe pas la technologie de la couche. Le [[Comparatif Solutions Marche Armoire]] (2026-10) l'a chiffrée pour onze solutions du marché : en dérivation, la couche n'a qu'à fermer des contacts secs, lire des recopies et battre le cœur du relais de garde, et les critères qui comptent deviennent le prix par voie, l'ouverture du protocole, la place et l'absence de logiciel du projet dans l'armoire. Les mieux placées sont un serveur d'E/S Modbus piloté par la passerelle (≈ 430 € HT en grand public, 3 000 à 3 900 € HT en industriel) et KNX TP (≈ 3 100 € HT) ; la Revolution Pi Connect 5 reste la troisième voie. Le même comparatif montre qu'aucune solution du marché ne tient la règle 1 seule : celles qui s'en approchent mettent un microcontrôleur par poussoir ou par zone. La grille est dans [[Grille Evaluation Resilience Domotique]].

## Voir aussi

- [[Analyse Etudes Remplacement Armoire 2026 10]]
- [[Incident Foudre Bus I2C 2026 08]]
- [[Comparatif Solutions Marche Armoire]]
