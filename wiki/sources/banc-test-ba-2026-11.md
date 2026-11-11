---
tags: [source, essensys, hardware, test, production, ba, i2c]
sources: [analyses/2026-11-banc-test-ba/synthese.md]
created: 2026-11-11
updated: 2026-11-11
era: legacy
---

# Banc Test BA 2026 11

**Source :** `raw/analyses/2026-11-banc-test-ba/synthese.md`
**Type :** synthèse anonymisée d'archives matérielles (2014-2017) et lecture du code de [[Essensys Board SC840B]]

## Métadonnées

| Champ | Valeur |
|---|---|
| Date | 2026-11-11 |
| Déclencheur | Archives du banc de test de production des BA retrouvées |
| Périmètre | Banc des cartes [[Essensys Board Sc940]], [[Essensys Board Sc941c]] et [[Essensys Board Sc942c]] : interface à lit de clous à trois plaques, carte de test SI840, console série |
| Méthode | Lecture des documents, puis du code source C du logiciel de test (aucune décompilation nécessaire) |
| Suivi | essensys-hub/essensys-doc#38 ; archives dans [[Essensys Test Banc BoitierSecondaire]] (dépôt privé) |

## Affirmations clés

- Un seul coffret, trois plaques interchangeables ; le banc reconnaît la carte par la plaque (code 0 = SI940, 2 = SI942, 4 = SI941).
- Points de test : 58 (SC940), 66 (SC941), 63 (SC942). Voies testées : 20, 22 et 21.
- Alimentation bonne entre 3325 et 4064 sur 12 bits. Variateurs : seuils 192 et 82 sur 10 bits.
- Bus I2C : le banc joue le BP, avec CRC16, aux adresses 0x11 (SC940), 0x12 (SC942), 0x13 (SC941).
- Résultat sur liaison série 9600 8N1, lu avec Tera Term ; lancement par la barre d'espace ou la fermeture du capot.
- Deux variantes du logiciel : V3 (variateurs avec point milieu) et V3 Fast (sans).

## Points ouverts

- Aucune photo : l'existence du banc physique reste à confirmer.
- Carte de test indice A (plan de cotes) ou B (dépôt public) : différence inconnue.
- Plans « pour nappe » de 2017 inexpliqués.

## Liens

- [[Essensys Test Banc BoitierSecondaire]]
- [[Essensys Board SC840B]]
- [[Banc Test BP 2026 11]]
- [[Essensys DOC]] — page « Banc de test des BA » (`debug/banc-de-test-ba`)
