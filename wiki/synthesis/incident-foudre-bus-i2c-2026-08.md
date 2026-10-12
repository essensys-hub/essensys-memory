---
tags: [synthesis, essensys, domotique, firmware, hardware, incident, foudre, i2c, cem, retex]
sources: [incidents/2026-08-foudre-bus-i2c/rapport-analyse.md]
created: 2026-10-11
updated: 2026-10-12
era: legacy
---

# Incident Foudre Bus I2C 2026 08

> Le 9 août 2026, vers 16 h 20 selon l'exploitant, un coup de foudre (impact non localisé, à confirmer par les données de détection de la foudre) est suivi de la perte de la liaison I2C entre le boîtier principal SC944D et les trois boîtiers auxiliaires d'une armoire Essensys. La panne I2C est attribuée à cet événement, mais sa date exacte reste à établir (dernière commande BA réussie). L'analyse révèle des défauts de conception communs à tout le parc. Sa correction est suivie par un ticket et un change OpenSpec.

## Suivi

| Élément | Référence |
|---|---|
| Ticket (Bug) | `essensys-hub/essensys-board-SC944D#1` |
| Change OpenSpec | `essensys-board-SC944D/openspec/changes/i2c-surge-protection-2026-10-007`. D'après sa proposition, il porte trois capacités : `i2c-bus-surge-protection`, `i2c-bus-fault-containment` et `aux-box-interconnect` |
| Retour d'expérience public | Publié le 2026-10-11 dans [[Essensys DOC]] : `retex/foudre-2026/` (synthèse et analyse experte). Procédure de remise en service et protection des installations proposées dans une PR séparée |
| Source | [[Rapport Analyse Foudre Bus I2C 2026 08]] (rapport v2 du 2026-10-11) |
| Concepts | [[Ilots TBTS Et Equipotentialite]] et [[Protection Surtension Bus I2C]] |
| Carte N2 « étoile 0 V » (tâche 4.1) | [[Essensys I2C Etoile 0v]] : dépôt dédié, révision B conçue, essais 4.2 à 4.4 à faire |
| Module ESP32 de la carte N2 | [[N2 Esp32 Spy Alarm 2026 10 008]] : écoute passive du bus, BA muet et ligne collée, +15 V et PTC, journal horodaté des surtensions, alarme intrusion sur batterie ; doc publique `install/module-n2-esp32` |
| Tests de non-régression | `NR-essensys-board-SC944D-1` à `-13`, prévus par le change, sur banc uniquement (voir [[Feature Lifecycle]]) |

## Récit

1. **9 août 2026, vers 16 h 20.**
   - Selon l'exploitant, un coup de foudre survient sur un site équipé d'une armoire Essensys et d'une installation photovoltaïque avec batterie. L'impact n'est pas localisé : les données de détection de la foudre doivent le confirmer.
   - Le disjoncteur de branchement déclenche, et le PV s'arrête au même moment (déclaration de l'exploitant, capture de la supervision de l'onduleur).
   - Le BP ([[Essensys Board Sc944d]]) ne reçoit plus de réponse d'aucun des trois BA ([[Essensys Board Sc940]], [[Essensys Board Sc941c]], [[Essensys Board Sc942c]]). La panne est attribuée à cet événement, mais sa date exacte reste à établir (dernière commande BA réussie).
   - Le BP, lui, vit encore : sa LED de téléinformation est allumée et le lien Ethernet est actif.
2. **Constats autour de l'armoire.**
   - Le parafoudre AC du coffret photovoltaïque a ses deux fenêtres noires.
   - Le parafoudre de type 2 du tableau a un voyant vert.
   - Le dongle de supervision de l'onduleur, câblé sur le même switch réseau que le BP, ne répondait plus lors de la mesure du 2026-10-11. La date à laquelle il a cessé de répondre n'est pas connue.
3. **11 octobre 2026, analyse.**
   - Une première version (v1), faite sans voir l'installation, suppose des boîtiers distants reliés par plusieurs mètres de câble.
   - Les photos du site montrent au contraire **un seul coffret** : quatre cartes empilées, reliées par trois tronçons d'environ 33 cm, et le SC940D en bout de chaîne.
   - Le rapport v2 refait le mécanisme sur cette base, après deux relectures adversariales.
4. **État au 2026-10-11.**
   - Le diagnostic sur site est en cours.
   - Le BA défaillant n'est **pas encore identifié**.
   - Ses résultats seront versés dans de nouvelles sources datées.

## Mécanisme

- Les quatre cartes sont des **îlots TBT flottants**. Le câble de bus est leur seul lien galvanique. Il sert donc de **pont** aux courants d'équilibrage quand un événement extérieur porte les îlots à des potentiels différents. Voir [[Ilots TBTS Et Equipotentialite]].
- Chaque tronçon présente R + (L − M) ≈ 0,09 Ω + 0,09 à 0,16 µH. Les écrêteurs I2C conduisent dès **≈ 20 A** d'équilibrage en onde 8/20, et dès **≈ 11 A** sur un front rapide.
- Il y a deux voies de destruction :
  1. **Les broches I2C.**
     - Les résistances série R1/R2 valent 0 Ω, et la diode interne du PIC conduit avant la TVS : jusqu'à 1 à 2 A dans la broche.
     - Côté BP, U19 (7 V maximum) voit 9 à 10 V.
  2. **Le fil +15 V.**
     - Il charge sans seuil le rail « +12V » du BA quand son 0 V descend sous celui du BP.
     - C2 (16 V) est dépassé dès ΔV ≈ 2 V, et U1 (24 V) vers ΔV ≈ 10 V, soit environ 28 A.
     - Cette voie explique à elle seule un « BA mort non alimenté ».
- **Pourquoi tout le bus se tait.** Le bus est partagé, sans tampon. Il suffit d'une ligne tenue basse ou à mi-niveau, par une TVS en court-circuit, une broche claquée ou un PIC non alimenté, pour faire taire les trois adresses.
- **Pourquoi la panne dure.**
  - Le firmware du BP ([[Client Essensys Legacy]]) ne sait pas récupérer un bus bloqué.
  - Il abandonne les commandes après 21 échecs et les marque comme acquittées.
  - L'index 12 (`comm_faults`, voir [[Table D Echange]]) n'est mis à jour qu'après une commande.

## Ce qui est établi, ce qui reste hypothèse

| Établi (schémas, BOM, code, photos) | Déduit (calcul, à confirmer par mesure) | Hypothèse (non tranchée) |
|---|---|---|
| Un seul coffret (photos) ; chaîne BP → SC942C → SC941C → SC940D, ordre le plus probable (photos) ; tronçons d'environ 33 cm, probablement en AWG26 | Seuils d'équilibrage de 20 A, 11 A et 4 A selon la pente | **Origine de la surtension** : H-PV (foudre côté PV puis Ethernet), H-RÉS (réseau en mode commun), H-TOV (surtension temporaire ou défaut de l'onduleur), H-IND (événements indépendants, qui recule) |
| Cartes sans liaison au PE, câble 4 fils comme seul lien | Mécanisme du +15 V (U1 atteint vers 28 A) | **Identité du BA défaillant** |
| R1/R2 = 0 Ω, TVS SMF5V0A, BA_ALIM sans TVS ni PTC | ΔVg statique de 0,06 à 0,16 V | J3 du BP vide (pas d'IHM ni de capteur extérieur) |
| C2 en 16 V sous 14,3 V, U16 (15 V maximum) sous 15,2 V | Courant de 0,3 à 1,7 A seulement par l'Ethernet avant amorçage | Consommation réelle d'un BA, nombre de fils par contact |
| Pas de récupération de bus, commandes marquées acquittées, pas de watchdog sur le BA | | Architecture du parafoudre AC du coffret PV (sens du noir) |
| Disjoncteur de branchement et PV coupés au même moment (déclaré par l'exploitant, capture de supervision) ; fenêtres noires du parafoudre AC (photos) ; dongle muet le 2026-10-11 (mesure réseau) | | Marge de niveau bas dans le sens BP → BA |

## Décisions

- **Remise en service sûre avant tout.**
  - Consignation, installation PV comprise.
  - Mesure 0 V–PE en mode basse impédance.
  - Essais d'isolement à 500 V continu sur **les trois BA et le BP**, en commençant par le SC941C (salles de bains). En dessous de 10 MΩ, la carte n'est pas remise en service.
- **Ordre du diagnostic.** Sur le BA, l'alimentation (U1, D3, C2, D6, FI1) se teste avant RC6/RC7. Sur le BP, U19 se teste avant D33/D34.
- **Un BA non alimenté ne reste jamais sur le bus.**
- **Après réparation, on renvoie les configurations de tous les BA**, et pas seulement celle du BA réparé.
  - Avant de remplacer un PIC qui répond encore, on lit son EEPROM (bit CPD à vérifier).
  - Après un changement de PIC, les variateurs repartent en mode gradateur par défaut : à corriger pour les charges qu'on ne peut pas graduer.
- **Firmware à flasher.**
  - BP : uniquement l'image de production 099-37, après une sauvegarde BDM. Jamais un nouveau build tant que le pilote I2C n'est pas reconstitué ([[Essensys GCC]]).
  - BA : les `.hex` v1.7 par type de carte.
- **R1/R2 en 47 Ω**, ou 33 Ω si ΔVg dépasse 0,12 V sans étoile ni renfort. Le critère est conservé contre l'avis de l'analyse CEM, car ΔVg n'est pas mesuré.
- **N2 (étoile 0 V doublée) passe avant N1 (renfort 0 V).**
- **Ethernet du BP isolé** par une fibre ou un isolateur. Pas de parafoudre RJ45 relié au PE.
- **Le dongle de supervision de l'onduleur ne revient pas en cuivre** sur le switch : il passe en Wi-Fi s'il est encore vivant.
- **Solutions écartées :**
  - éclateur à gaz entre le 0 V et la terre ;
  - varistance nue ;
  - TCA4307 sur chaque nœud ;
  - TVS 5 V « plus puissantes » ;
  - L3 seule.
- **Coffret unique** : carte d'interconnexion équipotentielle. Le MIB est réservé aux BA déportés.
- **Protocole HTTP legacy IoT inchangé.** L'index 12 garde son codage.
- **Essais sur banc uniquement**, jamais sur une armoire réelle.

## Actions

### Court terme (phases 0 et 1)

| Action | Qui | Priorité |
|---|---|---|
| Sécurité, isolement des 4 cartes, identification du BA défaillant (vidéo des LED ÉTAT, index 12, débranchements) | Mainteneur et électricien | P0 |
| Débrancher l'Ethernet du dongle côté switch. Horodater l'événement. Conserver les pièces et les traces | Exploitant | P0 |
| Remplacer le parafoudre AC du coffret PV, lire le journal de l'onduleur, contrôler l'équipotentialité PV | Installateur PV | En parallèle, non bloquant |
| Réparer le BP (U19, D33/D34, J32/C63 si besoin) et le BA mort. R1/R2 en 47 Ω | Mainteneur | P0/P1 |
| PTC puis TVS sur BA_ALIM. U16 remplacé par un LM317. C2 en 35 V, D6 en 40 V, TVS après R79 sur chaque BA déposé | Mainteneur | P1 |
| N2 (ou N1). Ethernet du BP isolé. Câbles PV à 30-50 cm au moins du coffret | Mainteneur et installateur | P1 |
| Contrôle du parafoudre de tête (manette, alimentation en amont des ID, 50 cm, terre) et remplacement de la cartouche | Électricien | P1 |
| Option renforcée : pull-ups de 2,2 kΩ, 47 Ω et BAT54S | Mainteneur | P2, selon le temps de montée |
| Parafoudre de type 3 au départ des lignes 230 V extérieures | Électricien | P1/P2 |

### Long terme (phases 2 à 4)

- **Firmware BP.**
  - Pilote I2C MQX à attentes bornées : 2 ms par attente, 20 ms par transaction.
  - Récupération de bus par 9 coups d'horloge.
  - File de commandes par BA, resynchronisation, état de santé par BA.
  - Sonde de présence toutes les 30 à 60 s, pour que l'index 12 reflète l'état réel.
- **Firmware BA 1.8.** Chien de garde, gestion des erreurs SSP, NACK quand le tampon est occupé, octet d'état rétrocompatible.
- **Serveur.** Alerte sur un `comm_faults` non vide ([[Essensys Server Backend]]). Le change la renvoie à un ticket séparé.
- **Matériel.**
  - Prototype de la carte d'interconnexion, qualifié sur banc par injection d'un courant d'équilibrage en onde 8/20 et sur un front rapide. Critères :
    - à 100 A en onde 8/20, aucune conduction des écrêteurs I2C et rail « +12V » sous 20 V (tâche 7.17) ;
    - seuils visés d'au moins 150 A en onde 8/20 et 70 A sur un front de 1 Ipk/µs (tâches 4.3 et 6.3) ;
    - à 1 kA en onde 8/20, aucune dégradation permanente (tâche 6.6, fond de panier et cartes rév. E).
  - Révision E du BP et des BA : zonage, 6 à 8 mm entre le 230 V et la TBT, ordre connecteur → TVS → résistance → écrêteur → circuit intégré.
  - MIB pour les BA déportés.
- **Génération 3.** RS-485 isolé, à décider dans un ADR.
- **Documentation.**
  - Retour d'expérience public.
  - Guide d'installation complété.
  - Corrections relevées par l'annexe E du rapport (tâches 8.6 à 8.9 du change) :
    - `archi/hardware-sc944d.md` et `hardware-overview.md` d'[[Essensys DOC]] : liaison BA par J31 ;
    - `archi/hardware-sc94{0d,1c,2c}.md` : entrées TOR sur J3 et bus sur J1/J2, logique en 5 V, L3 non montée, quantités de TVS et de VDR du SC940D ;
    - `docs/i2c.md` d'[[Essensys Board Sc944d]] : bus à 50 kHz, code ACTIONS = 5, adresses 0x11 à 0x13 ;
    - `docs/Architecture_Overview.md` d'[[Essensys Board Sc940]] : le SC943 est un variateur à IGBT, et non un module RF (voir [[Essensys Board Sc843d]]).

## Leçons apprises

### Pour l'association (conception, parc, process)

- **Un bus interne court reste un chemin de foudre.**
  - Entre des îlots flottants, ce qui compte est le courant d'équilibrage et l'impédance 0 V entre les cartes, et non la tension induite sur le câble.
  - 33 cm suffisent quand rien ne limite le courant.
- **Jamais 0 Ω entre un connecteur et un circuit intégré.** Les protections suivent l'ordre connecteur → TVS → résistance → écrêteur → circuit intégré, et une TVS d'alimentation se place derrière une PTC propre au nœud. Voir [[Protection Surtension Bus I2C]].
- **Revoir les marges en régime nominal.** Deux composants (C2 et U16) étaient déjà hors marge avant tout transitoire.
- **Le firmware doit contenir la panne.** Il faut :
  - des attentes bornées ;
  - une récupération de bus ;
  - aucun acquittement fictif ;
  - une resynchronisation ;
  - une télémétrie par BA qui reflète l'état réel ;
  - un chien de garde sur le BA.
- **Voir l'installation avant de conclure.** Le v1, écrit sans photos, s'est trompé de topologie, de bout de chaîne et de priorités. Il faut demander tôt des photos et des relevés.
- **Horodater tout de suite.** Deux mois après l'événement, les historiques courts (48 h) étaient perdus. La chronologie repose désormais sur les journaux longs (contrôleur réseau, messages MQTT retenus, onduleur, compteur communicant, détection de la foudre), encore à relever.
- **Préserver les binaires de production.** L'image 099-37 et les `.hex` v1.7 sont la seule base sûre tant que le pilote I2C du BP n'est pas reconstitué.
- **Corriger la documentation matériel.** Les écarts relevés (connecteur du bus, tension logique, fréquence du bus) ont ralenti l'analyse.
- **Sécuriser les pièces critiques.** Le PIC16F946 est en approvisionnement tendu : le commander chez Microchip en direct et constituer un stock. Les TVS se commandent en SMF5V0A-E3-08 (le suffixe GS08 n'est plus commandable).
- **Le défaut concerne tout le parc,** qui partage la même conception. Les règles d'installation doivent être publiées pour tous.
- **Méthode.** Les relectures croisées adversariales (calculs recoupés par un script, relecture terrain et sécurité) ont corrigé plusieurs erreurs de chiffres et de sécurité du v1.

### Pour les installateurs

- **Coffret domotique : TBTS stricte.**
  - Pas de PE dans le coffret, pas de conducteur vert-jaune.
  - Le 0 V est repéré « 0 V TBTS – NE PAS RELIER À LA TERRE ».
  - Pas d'éclateur ni de parafoudre de données relié au PE sur les cartes.
- **Séparer la TBT et le 230 V.**
  - Jamais dans la même goulotte.
  - Le bus et les nappes passent loin des bornes de phase, ou sous manchon isolant. Les isolants d'un câble cat. 5e ne sont pas prévus pour côtoyer le 230 V.
- **Éloigner le photovoltaïque.** Les câbles DC, batterie, AC et PE de l'onduleur passent à 30-50 cm au moins du coffret domotique, ou dans une goulotte métallique reliée au PE aux deux bouts.
- **Réseau.**
  - Un équipement relié au PE, comme un onduleur, ne se branche jamais en cuivre sur le même switch que le BP : on utilise le Wi-Fi ou la fibre.
  - L'Ethernet du BP est isolé.
- **Parafoudre de tête.**
  - Type 2 au minimum, type 1 s'il y a un paratonnerre.
  - Alimenté en amont des différentiels 30 mA, avec la règle des 50 cm.
  - Une fenêtre verte ne suffit pas : vérifier aussi la manette du déconnecteur.
  - Remplacer la cartouche après un événement.
- **Départs 230 V extérieurs.** Parafoudre de type 3 conforme à la NF EN 61643-11, au départ dans le tableau. Jamais de varistance nue, et rien de tel dans le coffret domotique.
- **BA déporté** (autre coffret, plus de 2-3 m, autre bâtiment) : poser un module d'isolement données et alimentation (MIB).
- **Après un orage.**
  - Consigner tout, y compris le PV et sa sortie de secours.
  - Mesurer la tension 0 V–PE en mode basse impédance.
  - Faire l'essai d'isolement à 500 V sur chaque carte.
  - Ne rien poser dans un coffret ouvert sous tension.
  - Ne pas sonder J31/J1 à pointe nue : le +15 V est voisin de SCL.
- **Relancer les BA sans ouvrir l'armoire.** Couper le secteur du BP pendant 13 s au moins (20 s pour avoir de la marge). Prérequis : batterie présente, cavalier J58 fermé, `Mode_Test` = 0. Effet de bord : les relais monostables retombent.
- **Archiver.** Photos datées, mesures de référence et pièces déposées serviront au prochain événement.

## Voir aussi

- [[Essensys I2c Ba Sniffer 2026 07 038]] : outil d'observation du bus I2C, qui pourrait aider à départager un NACK d'un bus bloqué. C'est une piste, non citée par le rapport. Le module ESP32 de la carte N2 ([[N2 Esp32 Spy Alarm 2026 10 008]]) en fait une surveillance permanente et conserve la preuve horodatée d'une prochaine surtension.
- [[Essensys Board Sc843d]] : modules variateurs SC943. Leurs varistances sont à remplacer sur le BA mort.
- [[Platform Overview]]
