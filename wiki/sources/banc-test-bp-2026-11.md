---
tags: [source, essensys, hardware, test, production, bp, i2c]
sources: [analyses/2026-11-banc-test-bp/synthese.md]
created: 2026-11-11
updated: 2026-11-11
era: legacy
---

# Banc Test BP 2026 11

**Source :** `raw/analyses/2026-11-banc-test-bp/synthese.md`
**Type :** synthèse anonymisée d'archives matérielles (2014-2015)

## Métadonnées

| Champ | Valeur |
|---|---|
| Date | 2026-11-11 |
| Déclencheur | Le banc de test de production du BP et ses archives d'étude ont été retrouvés |
| Périmètre | Banc de test de la carte BP ([[Essensys Board Sc944d]]) : interface à lit de clous, carte d'interface SI841A, spécification du logiciel de test v4 |
| Méthode | Lecture des documents et extraction du texte des PDF ; aucun binaire à analyser |
| Suivi | essensys-hub/essensys-doc#36 ; archives dans [[Essensys Test Banc SC944D]] (dépôt privé) |

## Affirmations clés

- Le banc alimente la carte en 24 V (« secteur ») puis en 12 V (« secouru »), et applique toujours la nouvelle tension avant de couper l'ancienne.
- Il mesure 15V, 15VS, 5VS, 3V3S, +15VSP et +12VSP, avec un voyant vert ou rouge par tension.
- Il vérifie le pilotage du +15VSP (coupure en secouru, attendue en 6,5 s avec le firmware 092-31 en mode test) et son forçage par un strap que l'opérateur met puis retire.
- Il vérifie les alimentations des deux détecteurs de présence, des deux sirènes et du bus BA, puis répond aux trames I2C du BA « pièces de vie » : c'est le BP qui juge la communication et l'affiche.
- 74 points de test, plus l'Ethernet et 10 perçages de réserve pour la programmation.
- La carte d'interface SI841A porte un dsPIC33FJ256GP710 ; elle reste en reset tant que la presse est ouverte.
- **Le code du logiciel de test n'est pas dans les archives**, ni les fichiers de conception de la SI841A, ni une notice, ni le plan de câblage du lit de clous.

## Points ouverts

- Vérifier sur le banc que le 230 V du test fil pilote est bien coupé presse ouverte.
- Les plans des points de test portent l'indice C ; validité pour l'indice D non établie.
- Tableau manuscrit des seuils de mesure à retranscrire.

## Liens

- [[Essensys Test Banc SC944D]]
- [[Essensys Board Sc944d]]
- [[Essensys DOC]] — page « Banc de test du BP » (`debug/banc-de-test-bp`)
