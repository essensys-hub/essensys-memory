---
tags: [concept, essensys, hardware, firmware, i2c, cem, foudre, protection]
sources: [incidents/2026-08-foudre-bus-i2c/rapport-analyse.md, analyses/2026-10-etudes-remplacement-armoire/analyse.md]
created: 2026-10-11
updated: 2026-10-24
---

# Protection Surtension Bus I2C

Ce sont les règles pour protéger une interface de bus (SDA, SCL, alimentation) entre deux cartes contre les surtensions et les courants d'équilibrage. Elles viennent de l'[[Incident Foudre Bus I2C 2026 08]] sur le bus BP ↔ BA de l'armoire Essensys ([[Essensys Board Sc944d]] et BA [[Essensys Board Sc940]], [[Essensys Board Sc941c]], [[Essensys Board Sc942c]]). Source : [[Rapport Analyse Foudre Bus I2C 2026 08]].

Ces règles protègent les **circuits intégrés** une fois que le courant est entré. Elles ne remplacent pas la réduction du courant lui-même, qui relève de l'équipotentialité ou de l'isolement : voir [[Ilots TBTS Et Equipotentialite]]. L'idée à retenir : écrêter plus fort ne supprime pas le chemin.

## Principes

### 1. Limiter le courant vers chaque circuit intégré (résistance série)

- Une diode d'écrêtage seule ne protège pas un circuit intégré si rien ne limite le courant entre elle et lui.
  - Exemple : la diode interne d'un PIC conduit vers 5,5 V, alors qu'une TVS 5 V ne claque qu'à partir de 6,4 V.
  - Avec 0 Ω entre les deux, le PIC devient l'écrêteur principal.
- Pour placer la résistance série, on fait un **budget de niveau bas**, avec une marge visée d'au moins 0,3 V sous le seuil du lecteur. Les valeurs ci-dessous sont celles du bus Essensys, avec des pull-ups de 1 kΩ :

  | Résistance série côté BA | Niveau bas lu au BP (ΔVg = 0 / 0,1 V) | Verdict |
  |---|---|---|
  | 0 Ω (actuel) | 0,46 / 0,55 V | Courant non limité |
  | 33 Ω | 0,63 / 0,72 V | Si ΔVg > 0,12 V et pas de liaison équipotentielle (N2/N1) |
  | 47 Ω | 0,70 / 0,78 V | Retenu si ΔVg ≤ 0,12 V (de 0,1 à 0,12 V : contrôle du niveau bas au MCF, < 0,85 V) |
  | 100 Ω | 0,94 / 1,02 V | Refusé (marge de 0,22 V, puis 0,13 V) |

- Règle retenue, selon ΔVg mesuré au BA en bout de chaîne : jusqu'à 0,1 V, 47 Ω ; de 0,1 à 0,12 V, 47 Ω avec contrôle du niveau bas au MCF (< 0,85 V) ; au-delà de 0,12 V, poser d'abord N2 ou N1 (voir [[Ilots TBTS Et Equipotentialite]]), sinon 33 Ω. Le critère générique « 33 Ω si ΔVg > 0,1 V » du v1 est remplacé.

- La résistance doit être **anti-impulsion** (0805 ou 0603 de la gamme « pulse-proof »).
- Elle borne le courant (19 à 34 mA au seuil de la TVS, environ 140 mA à 12 V pour 47 Ω), mais ne le ramène pas sous le maximum absolu du circuit (±20 mA). C'est le rôle de l'écrêteur secondaire.

### 2. Écrêtage coordonné (primaire, puis secondaire)

- **Primaire** côté connecteur : une TVS prend l'essentiel du courant de choc.
- **Secondaire** côté circuit intégré, après la résistance série : une Schottky double (BAT54S) vers le rail et la masse locale.
  - Elle ramène la ligne vers 5,8 V au lieu de 9 à 14 V.
  - Avec 47 Ω, elle reçoit environ 135 mA en positif ((12 − 5,7) / 47, pour VC ≈ 12 V) et environ 40 mA en négatif ((2,5 − 0,6) / 47), pour une tenue d'environ 600 mA en surcharge brève [DS?].
  - Il reste une injection d'environ −0,5 V sur les broches 28/29 du MCF (limite −0,3 V). Elle n'est levée qu'en rév. E.
- Le rail doit pouvoir absorber le courant renvoyé. Un régulateur n'absorbe pas de courant entrant, c'est la consommation et le découplage qui le font. Une impulsion de 0,15 A pendant 20 µs dans 10 µF fait monter le rail d'environ 0,3 V.

### 3. Un ordre fixe sur chaque ligne

**Connecteur → TVS (à 10 mm au plus de la broche) → résistance série → écrêteur → circuit intégré.**

- Le retour de la TVS rejoint par une piste de 5 mm au plus, ou par des vias, un petit plan GND_BUS relié à la broche 0 V du connecteur.
- **Le courant de surtension ne traverse jamais le plan logique.**
- La protection du microcontrôleur se place **au pied du microcontrôleur**. Sur le SC944D, la piste vers le MCF fait aujourd'hui 55 mm sans aucune protection.

### 4. L'alimentation du bus : PTC en amont, puis TVS propre au nœud

- Une TVS d'alimentation finit en court-circuit. Elle doit donc toujours se trouver **en aval** d'un élément qui l'isole quand elle claque, une PTC par exemple, et cet élément doit être **propre au nœud** qu'elle protège.
- Ne jamais poser une TVS sur un nœud de chaînage partagé (par exemple +VBUS en amont de R79 sur un BA) : une TVS morte y couperait tous les nœuds.
- Pas de résistance série sur une ligne de puissance. On découple par une inductance ou une PTC, ou on utilise un parafoudre DIN coordonné.
- La PTC se dimensionne sur le courant de maintien **à la température du tableau** : il doit valoir au moins 1,5 fois le courant mesuré, relais collés.
- Les composants derrière la TVS doivent tenir sa tension d'écrêtage. Une SMAJ16A remonte à environ 26 V au courant crête, d'où C2 en 35 V et D6 en 40 V sur les BA, et U16 (LD1117, 15 V) remplacé par un LM317 au BP.
- **Limite assumée.** Sur un BA retouché, U1 (LMR12010, 24 V) reste exposé (≈ 25 V après D3, BOOST à la limite de ses 30 V) et FI1 (25 V) est frôlé : la protection reste partielle, seule la défaillance est confinée par la PTC propre au BA. La correction complète vient en rév. E (LMR16006 4-60 V, à valider au banc : VFB, fréquence, 0,6 A maximum).

### 5. Les marges en régime nominal d'abord

Un composant hors marge en fonctionnement normal cède au premier transitoire. Deux exemples sur les cartes actuelles :
- C2 en 16 V sous 14,3 V ;
- U16 (LD1117, entrée 15 V maximum) sous 15,2 V.

### 6. La capacité et le temps de montée

- Une TVS 5 V de forte puissance a une capacité d'environ 1 nF : c'est elle, et non le câble, qui fixe le temps de montée du bus. Sur le bus actuel, il va de 1,4 à 3,2 µs entre 0 et 3,45 V, pour un critère de moins de 4 µs à 50 kHz.
- Avec des isolateurs (ISO1640 : C ≤ 400 pF côté bus, C ≤ 80 pF côté nœud), il faut des TVS de 50 pF au plus.

## Pièges

| Piège | Pourquoi |
|---|---|
| **Résistance série de 0 Ω** (R1/R2 des BA) | Le circuit intégré écrête seul, sans limite : 1 à 2 A dans la broche dès environ 30 A d'équilibrage |
| **TVS 5 V « plus puissantes »** (SMBJ5.0A, SMF4L5.0A) | Leur fuite atteint 800 µA, soit environ 2,5 V perdus sur le niveau haut avec les pull-ups du bus. Le niveau haut I2C du PIC exige au moins 3,45 V |
| **TVS dont l'écrêtage dépasse la tenue du circuit** | Une SMF5V0A écrête à 9,2 V en onde 10/1000, et vers 12 à 14 V en 8/20, alors que le PCA9306 tient 7 V. Le circuit partage alors le courant avec la TVS |
| **Éclateur à gaz (GDT) entre le 0 V et la terre** | En fin de vie, il passe en court-circuit et relie la TBTS à la terre, ce qui la fait passer en TBTP (NF C 15-100 §414, et §701 pour les salles de bains). Il s'amorce à plusieurs centaines de volts, sans protéger les ports I2C. Il crée une boucle avec la terre. Avec une résistance de 1 MΩ en parallèle, la liaison devient galvanique |
| **Condensateurs sur les lignes** (C23/C25) | Avec 47 à 100 Ω, la constante de temps n'est que de 1 à 2 ns, sans effet contre la foudre. Ces empreintes servent mieux à la BAT54S |
| **Self de mode commun seule** (L3, sans isolement) | Environ 314 Ω à 50 kHz dans le retour : la masse rebondit et le mode commun est poussé dans les TVS de ligne |
| **PTC ou fusible en série avec une TVS de ligne de données** | Le courant des pull-ups (2 à 6 mA) ne le fera jamais déclencher, et une TVS en court-circuit bloque toujours le bus. Le confinement passe par l'isolement et un superviseur |
| **Varistance nue sur une sortie 230 V** | Ce n'est pas un parafoudre au sens de la NF EN 61643-11 : ni déconnecteur thermique, ni protection de secours. En fin de vie, elle passe en court-circuit avec un risque d'incendie. Utiliser un parafoudre de type 3 conforme, au départ dans le tableau |
| **Parafoudre RJ45 relié au PE sur un îlot TBTS** | Si le PE voisin monte, il injecte le choc dans le 0 V de l'îlot. Il faut isoler (fibre, isolateur) plutôt que parafoudrer |
| **Une ferrite comme protection** | Elle n'agit que sur les fronts rapides et ne fait presque rien contre la foudre |

## Application à l'armoire Essensys

| Point | État actuel | Cible court terme | Cible rév. E |
|---|---|---|---|
| Série SDA/SCL des BA (R1/R2, R1/R3 sur SC941C) | 0 Ω | 47 Ω anti-impulsion (33 Ω selon ΔVg) | 47 à 100 Ω montées |
| Écrêteur secondaire | Aucun | BAT54S sur les empreintes C79/C80 (BP) et C23/C25 (BA), en option | Prévu au schéma |
| Pull-ups du BP (R155/R156) | 1 kΩ | 2,2 kΩ, selon le temps de montée mesuré | 2,2 kΩ |
| +15 V du bus (BA_ALIM) | Ni TVS, ni PTC | PTC puis SMAJ16A au BP, PTC puis TVS après R79 sur chaque BA | eFuse avec démarrage progressif et SMCJ16A |
| Rail « +12V » des BA | C2 en 16 V, D6 en 20 V | C2 en 35 V, D6 en 40 V ; protection partielle, U1 (24 V) reste exposé | LMR16006 (60 V), C2 en 50 V |

Ces retouches sont suivies dans le change OpenSpec `i2c-surge-protection-2026-10-007`, capacité `i2c-bus-surge-protection`, du dépôt essensys-board-SC944D.

> [!note] Remplacement des cartes (2026-10)
> L'architecture V2 étudiée pour remplacer les cartes ([[Reponse Resilience Armoire]]) coupe le chemin de l'onde au lieu de l'écrêter : îlots TBTS séparés par des barrières de 4 kV. Elle met fin au bus I2C à la bascule des pièces de vie (estimée en janvier 2027). D'ici là, les protections de cette page restent valables pour l'armoire en service.

## Voir aussi

- [[Ilots TBTS Et Equipotentialite]]
- [[Incident Foudre Bus I2C 2026 08]]
- [[Rapport Analyse Foudre Bus I2C 2026 08]]
