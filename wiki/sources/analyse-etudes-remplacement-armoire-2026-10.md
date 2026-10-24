---
tags: [source, essensys, hardware, armoire, resilience, foudre, tbts, sc944d, sc940d, sc941c, sc942c]
sources: [analyses/2026-10-etudes-remplacement-armoire/analyse.md]
created: 2026-10-24
updated: 2026-10-24
era: legacy
---

# Analyse Etudes Remplacement Armoire 2026 10

**Source :** `raw/analyses/2026-10-etudes-remplacement-armoire/analyse.md`
**Type :** analyse anonymisée (études V1, conseil d'autocritique, étude V2, banc deux lumières, recherche d'un appareil unique)

## Métadonnées

| Champ | Valeur |
|---|---|
| Date de la source | 2026-10-23 |
| Déclencheur | Après l'[[Incident Foudre Bus I2C 2026 08]], les BA chambres et pièces d'eau restent muets ; l'exploitant pose le 2026-10-21 une exigence : un calculateur grillé ne coupe aucun bouton |
| Périmètre | Remplacement de [[Essensys Board Sc944d]], [[Essensys Board Sc940]], [[Essensys Board Sc941c]], [[Essensys Board Sc942c]] : 63 boutons, 25 éclairages, 15 volets et un store, 8 variateurs, fil pilote, cumulus, alarme |
| Méthode | Trois études V1 (19-20 octobre, figées le 21) ; conseil d'autocritique de six agents d'IA dans des rôles d'expert, avec critique croisée anonyme et synthèse ; étude V2 relue par un relecteur indépendant (25 constats) ; banc deux lumières (22-23 octobre) |
| Pages publiques | [[Essensys DOC]], section `docs/etudes/` |
| Suivi | essensys-hub/essensys-board-SC944D#1 |

Les chiffres du conseil sont des estimations argumentées, pas des devis : ils restent à confirmer par un électricien, des devis, les fabricants et des essais. Les prix ont été relevés en octobre 2026.

## Affirmations clés

- **Aucune étude V1 ne tient l'exigence.** Toutes placent un calculateur entre le bouton et le relais (sauf pour les 8 variateurs).
  - Revolution Pi : 55 boutons sur 63 perdus si le Connect 5 meurt. Verdict : transformer.
  - Arduino Opta : un automate mort, c'est une zone morte ; le bloc 24 V commun éteint les trois. Verdict : abandonner.
  - Raspberry Pi et Ethernet : un nœud mort, c'est une zone morte ; cartes maison en 230 V sans marquage CE. Verdict : abandonner les cartes, garder le principe « plus une fonction est critique, moins elle dépend d'autres organes ».
  - AMDEC de la sûreté (modes de panne qui privent toute la maison de ses boutons) : 13, 5, 4, et 0 pour le filaire autonome.
- **Le câblage de migration des V1 est gardé** : répartiteur X1 (56 bornes Wago 2002-2201 à deux étages), blocs de phase X3 (Wago 2002-1401), jonctions IDC des nappes, plan de bornage.
- **La V2 « filaire d'abord, domotique en dérivation »** : chaque bouton attaque un organe qui garde l'état (télérupteur Finder 20.22, deux relais de volet en chaîne de priorité, Eltako EUD12D à entrée locale), sur une source 24 V de classe II par zone. La domotique ferme des contacts secs Finder 38.51 en parallèle, derrière un relais de garde tenu par un chien de garde matériel et une borne sectionnable. Voir [[Filaire D Abord Domotique En Derivation]].
- **Foudre** : deux îlots TBTS distincts, 0 V jamais au PE, une barrière d'au moins 4 kV et 8 mm à chaque passage, parafoudres au tableau et au bout des lignes extérieures, jamais dans les coffrets.
- **Coût estimé** : 3 450 à 3 950 € HT pour la couche filaire seule, 4 300 à 4 900 € HT avec une domotique minimale, 6 450 à 7 850 € HT avec une domotique complète ; environ 1 000 € de plus sans attestation d'isolement ; 6 à 8,5 jours d'électricien ; 1,6 à 2,1 m de rail. Renoncement au double clic, à l'appui long et aux scénarios câblés des BA.
- **Préalables à toute commande en série** : relevé de l'électricien, attestations d'isolation renforcée (Finder, Eltako), banc deux lumières, essai de choc à 2 puis 4 kV (1 000 à 1 800 € en laboratoire), recette de chaque zone contrôleur coupé.
- **Banc deux lumières** : lumière 1 sur Finder 20.22, lumière 2 sur Eltako ES12Z-200-UC ; Raspberry Pi 3 (E/S) et 4 (logique) sur le 24 V de la domotique ; 76 fils repérés, trois îlots sans fil commun ; 737,79 € TTC.
- **Aucun appareil unique** ne réunit en 24 V continu l'entrée du poussoir, une entrée domotique séparée et une sortie d'état en TBTS. Le plus proche est l'Eltako ES12Z-200-UC.
- **Désaccords ouverts** : télérupteur ou actionneurs Eltako, chaîne de relais ou Eltako EGS12Z pour les volets, 24 V continu ou transformateur 50 Hz, réparer ou non les BA actuels, Revolution Pi ou serveur d'E/S léger, calendrier.
- **Feuille de route estimée** : chambres et pièces d'eau en novembre-décembre 2026, pièces de vie et fin du bus I2C en janvier 2027, domotique de février à avril 2027, parafoudres avant mai 2027, retrait du BP au printemps 2027.

## Pages liées

- [[Reponse Resilience Armoire]] : la réponse à l'exigence, critères et preuves
- [[Filaire D Abord Domotique En Derivation]] : le motif d'architecture
- [[Ilots TBTS Et Equipotentialite]], [[Protection Surtension Bus I2C]] : les principes contre la foudre
- [[Analyse Demarrage BP BA 2026 10]] : pourquoi les BA chambres et pièces d'eau restent muets
