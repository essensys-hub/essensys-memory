---
tags: [concept, essensys, hardware, installation, cem, foudre, tbts, equipotentialite]
sources: [incidents/2026-08-foudre-bus-i2c/rapport-analyse.md]
created: 2026-10-11
updated: 2026-10-11
---

# Ilots TBTS Et Equipotentialite

Ce concept décrit comment les cartes d'une armoire Essensys se comportent, électriquement, les unes par rapport aux autres pendant un transitoire (foudre, surtension), et quelle réponse apporter selon leur implantation. Il vient de l'[[Incident Foudre Bus I2C 2026 08]]. Source : [[Rapport Analyse Foudre Bus I2C 2026 08]]. La protection des interfaces elles-mêmes est traitée dans [[Protection Surtension Bus I2C]].

## Les cartes sont des îlots flottants

- Le BP ([[Essensys Board Sc944d]]) et chaque BA ([[Essensys Board Sc940]], [[Essensys Board Sc941c]], [[Essensys Board Sc942c]]) forment chacun un **îlot TBT flottant**, sans aucune liaison au PE.
- Chaque îlot a son propre câblage de terrain, qui le couple au reste du bâtiment :
  - BA : nappe J3 vers 20 à 22 boutons muraux à contact sec, sans optocoupleur, et sorties 230 V ;
  - BP : Ethernet, téléinformation, électrovanne, fils pilotes et capteurs extérieurs.
- Pendant un transitoire, chaque îlot suit le potentiel de ses câbles. Deux îlots voisins peuvent donc se retrouver à des potentiels différents.

## Le câble de bus est un pont, pas une antenne

- Le câble 4 fils (SDA, SCL, 0 V, +15 V) est le **seul lien galvanique** entre les îlots. C'est par lui que passe le **courant d'équilibrage** entre les îlots.
- **Modèle R + (L − M).**
  - Un courant de mode commun induit presque la même tension sur tous les conducteurs du câble.
  - Entre une ligne et son 0 V, seuls apparaissent la résistance R et la différence L − M entre l'inductance propre et l'inductance mutuelle.
  - Pour 33 cm d'AWG26 : R ≈ 0,09 Ω (les deux contacts de 20 mΩ pèsent autant que le fil) et L − M ≈ 0,09 à 0,16 µH. Le calcul en inductance propre (0,46 µH, ou « 1 µH/m ») surestime fortement la tension.
- **Seuil d'équilibrage** = tension d'écrêtage des lignes ÷ impédance du chemin 0 V.
  - Au-delà, SDA et SCL deviennent des chemins parallèles au fil 0 V, et le courant traverse les TVS et les circuits intégrés.
  - Sur le site de l'incident : environ 20 A en onde 8/20 et environ 11 A sur un front rapide.
  - Le seuil baisse quand le front raidit.
- **Position dans la chaîne.** Le nœud en bout de chaîne cumule l'impédance de tous les tronçons. Son seuil est environ 3 fois plus bas que celui du premier nœud. Cela ne suffit pas à le désigner comme le plus endommagé.
- **Le fil d'alimentation est aussi un pont.**
  - Quand le 0 V d'un nœud descend sous celui du maître, le +15 V, qui ne porte pas le courant d'équilibrage, arrive au nœud à 15 V + ΔV.
  - Il charge alors le rail d'entrée sans aucun seuil.
  - Sur un BA, C2 (16 V) est dépassé dès ΔV ≈ 2 V, et U1 (24 V) vers ΔV ≈ 10 V.
- **Ce qui reste valable pour un câble long.** L'ordre de grandeur « ≈ 1 kV sur 10 m à 100 A/µs » ne vaut que pour un câble long qui longe un conducteur parcouru par un choc, **et dont la boucle se ferme** à l'autre bout. Les nappes J3 qui longent le 230 V en sont un exemple.

## Écart de masse statique (ΔVg)

- Le courant d'alimentation des BA revient par le fil 0 V du bus. Il décale les masses en régime permanent : ΔVg = 6 × R_tronçon × I_BA au BA en bout de chaîne (trois tronçons), soit 0,06 à 0,16 V sur le site de l'incident.
- Cet écart réduit la marge de niveau bas I2C. Il conditionne le choix de la résistance série (47 ou 33 Ω).
- Une étoile ou un renfort 0 V le ramène sous 0,02 V.

## La réponse dépend de la géométrie

| Implantation | Réponse | Pourquoi |
|---|---|---|
| **Même coffret** (cartes accolées, liaisons ≤ 0,5 m) | **Équipotentialité** : rendre l'écart de 0 V entre cartes négligeable devant les seuils I2C et d'alimentation | Des piquages courts à 50 kHz ne posent aucun problème de ligne. Il suffit d'abaisser l'impédance 0 V |
| **Frontière du coffret** (Ethernet, lignes TBT extérieures, départs 230 V extérieurs) | **Isoler ou protéger chaque port qui sort.** Le port à traiter en premier est celui qui a une liaison métallique directe vers des équipements potentiellement reliés au PE | Ce sont les portes d'entrée de l'énergie |
| **BA déporté** (autre coffret, plus de 2-3 m de câble, autre bâtiment) | **Isolement**, des données ET de l'alimentation ensemble : module d'isolement par BA (MIB) | L'équipotentialité n'est plus atteignable. Isoler les données sans l'alimentation ne sert à rien, car le courant passe par le 0 V et le +15 V |

### Dans un coffret unique : abaisser l'impédance 0 V

| Mesure | Description | Seuil (8/20, puis front rapide) |
|---|---|---|
| Actuel | 3 tronçons d'AWG26 en chaîne | ≈ 20 A, puis ≈ 11 A |
| **N1**, renfort 0 V | Conducteur souple de 2,5 à 4 mm², **plaqué** le long de chaque tronçon et soudé sur la broche traversante J1/J2-3. Un renfort qui suit un autre chemin crée une boucle et aggrave la situation | ≈ 97 A, puis ≈ 25 A |
| **N2**, étoile 0 V doublée | Petite carte passive sur rail DIN. Chaque BA y est relié par J1 et J2 (AWG20, 15 cm au plus). Elle loge aussi la PTC et la TVS du +15 V de chaque port, et un cavalier pour retirer un BA | ≈ 173 A, puis ≈ 79 A |
| **Fond de panier** | Carte d'interconnexion équipotentielle, avec un plot 0 V sur les BA rév. E | ≈ 875 A, puis ≈ 292 A |

N2 est la seule mesure de court terme qui garde son efficacité sur un front raide : le gain de N1 tombe de ×5 à moins de ×2. Au-delà du seuil, les TVS conduisent encore : la [[Protection Surtension Bus I2C]] des circuits intégrés reste nécessaire.

### Entre bâtiments ou coffrets distincts : isoler

- Une barrière **renforcée** sur les données et sur l'alimentation : isolateur I2C ISO1640DW et convertisseur DC/DC isolé de 4 à 5 kVAC, avec une tenue en onde de choc spécifiée.
- Le côté BA de l'isolateur est alimenté par le BA lui-même. Un BA mort met ainsi l'isolateur en haute impédance et **libère le bus**.
- Le courant résiduel vaut C·dV/dt, soit environ 0,2 A pour 200 pF à 1 kV/µs. La tension qui n'est plus court-circuitée se reporte sur la barrière la plus faible. D'où une distance d'au moins 8 mm entre les zones.
- Pour un écran de câble : repris à 360° sur la barrette PE, isolé du 0 V.

## La TBTS n'est jamais reliée au PE

- **Aucune liaison galvanique entre le 0 V des cartes et la terre.** Les écrans de câbles vont au PE, mais jamais au 0 V.
  - Relier le 0 V à la terre fait passer l'installation en TBTP, contraire à la NF C 15-100 §414.
  - Un BA qui dessert des salles de bains (SC941C) relève de la §701, qui n'admet que la TBTS dans les volumes 1 et 2 (à confirmer avec l'électricien selon l'implantation).
- Les mesures d'équipotentialité relient **un 0 V à un autre 0 V**, jamais au PE.
- **Pas de PE dans le coffret domotique** (classe II), même à côté d'un renfort 0 V : un intervenant finira par les relier.
- **Repérage** : manchons « 0 V TBTS – NE PAS RELIER À LA TERRE » aux deux extrémités. Jamais de vert-jaune ni de bleu clair. Une tresse 0 V doit être gainée, sinon elle ressemble à un conducteur de terre.
- **Pièges qui créent une liaison 0 V–PE de fait :**
  - un éclateur à gaz entre le 0 V et la terre, qui passe en court-circuit en fin de vie ;
  - un parafoudre de données à éclateur vers le PE ;
  - un parafoudre RJ45 relié au PE ;
  - un câble Ethernet blindé dont l'écran est relié au PE, avec un condensateur de blindage percé côté carte.
- **Ethernet du BP.** Le Bob Smith et le blindage RJ45 couplent les 8 fils au 0 V du BP par environ 1 nF/2 kV. On isole par une fibre, dont le convertisseur côté BP est alimenté **depuis l'îlot TBTS** (un bloc classe II recouplerait l'îlot au réseau par ses capacités Y), ou par un isolateur de 4 à 6 kV au moins. On ne pose pas de parafoudre relié au PE.

## Isolement 230 V / TBT sur la carte

- Le statut TBTS suppose une isolation renforcée entre le 230 V et la TBT, sur la carte elle-même.
- Le schéma du BP impose 5,5 mm. Sur les BA, J1/J2 sont estimés à 2-3 mm du relais K1. C'est une alerte à vérifier sur les Gerber.
- La rév. E vise 6 à 8 mm avec une fente fraisée (EN 60664-1 et norme produit, à confirmer).
- Après un choc, on procède dans cet ordre :
  1. sans toucher les cartes, 230 V présent : mesure de la tension 0 V–PE en mode basse impédance (LoZ). Si plusieurs dizaines de volts tiennent en LoZ : arrêt, consignation et appel d'un électricien ;
  2. consignation selon la NF C 18-510, installation photovoltaïque comprise ;
  3. essai d'isolement à 500 V continu sur **chaque** carte : plus de 100 MΩ attendu ; de 10 à 100 MΩ, nettoyer, sécher et refaire l'essai ; moins de 10 MΩ interdit la remise en service ;
  4. nouvelle mesure 0 V–PE en LoZ à la remise sous tension.

## Voir aussi

- [[Protection Surtension Bus I2C]]
- [[Incident Foudre Bus I2C 2026 08]]
- [[Rapport Analyse Foudre Bus I2C 2026 08]]
