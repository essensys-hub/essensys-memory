---
title: "Rapport d'analyse : foudre sur la liaison I2C BP ↔ BA (SC944D, SC940D, SC941C, SC942C)"
type: rapport-incident
date_analyse: 2026-10-11
date_evenement: 2026-08-09
heure_evenement: "vers 16 h 20 (fenêtre déduite : 16 h 15 à 16 h 25)"
ticket: essensys-hub/essensys-board-SC944D#1
openspec_change: i2c-surge-protection-2026-10-007
depot_openspec: essensys-hub/essensys-board-SC944D
statut: "analyse ; diagnostic sur site en cours"
methode: "relectures croisées adversariales"
version_source: "rapport v2 du 2026-10-11, qui intègre et corrige le v1 du même jour"
cartes: [SC944D, SC940D, SC941C, SC942C]
anonymise: true
created: 2026-10-11
tags: [essensys, firmware, incident, foudre, cem, i2c, sc944d, sc940d, sc941c, sc942c]
---

# Rapport d'analyse : foudre sur la liaison I2C BP ↔ BA (SC944D / SC940D / SC941C / SC942C)

## Note d'archivage

- **Nature du document.** Enregistrement technique complet de l'analyse menée le 2026-10-11 après le coup de foudre du 9 août 2026. C'est une **source immuable** de la base de connaissance : on ne la corrige pas, on la complète par une nouvelle source datée (résultats du diagnostic sur site, mesures, réparation).
- **Version.** Le texte reprend le rapport v2 (référence), qui intègre les photos du site, les précisions de l'exploitant, un relevé réseau et deux relectures croisées. Le v1, écrit le même jour sans connaître l'installation, est conservé là où il apporte encore quelque chose (mention « (v2) » sur les passages corrigés, annexe G pour ce que le v1 affirmait et qui a été remplacé).
- **Numérotation.** Les sections §0 à §6 et les annexes A à F gardent la numérotation du rapport d'origine, pour que les renvois internes (« §3.5 n° 14 », « §4.1 bis »…) restent valables. Les ajouts d'archivage sont : la fiche de synthèse ci-dessous, l'annexe G, le tableau « Points d'ancrage dans le code » du §5.10, deux précisions au §0.3.3 (recul de H-IND) et au §4.3 (« v2 : 40 V retenu »), et les annexes B et F adaptées à l'anonymisation.
- **Méthode : relectures croisées adversariales.**
  - v1 : cinq analyses spécialisées menées en parallèle (BP SC944D, trois BA, firmware de la liaison I2C, installation électrique et foudre selon NF C 15-100, IEC 62305 et IEC 61643, composants avec recherche de fiches techniques), puis deux volets rédigés (court terme, long terme), chacun soumis à **deux vérificateurs adversariaux** (l'un sur les calculs et affirmations techniques, l'autre sur la pratique terrain et la sécurité), puis une synthèse corrigée. Les corrections et les arbitrages contre un vérificateur sont tracés en annexe D.
  - v2 : audit des 8 photos du site, réévaluation du mécanisme par une analyse CEM, analyse de l'installation photovoltaïque, puis deux relectures adversariales (calculs recoupés par un script indépendant ; relecture électricien et sécurité).
  - Les analyses ont été faites **en lecture seule** : aucun fichier des dépôts n'a été modifié. Toute retouche de carte, de BOM, de firmware ou de documentation passe par un ticket du Project #6 (`/ticket`, puis `/ticket-to-spec`). Les essais décrits sont des **mesures manuelles** ; aucun test automatisé ne doit piloter l'armoire réelle.
- **Anonymisation.** Les marques, modèles et numéros de série des équipements du site (réseau domestique, onduleur, batterie, dongle de supervision, appareillages du tableau et du coffret photovoltaïque, coffret domotique), les adresses réseau, le lieu, les personnes, l'installateur, les démarches administratives personnelles, les journaux d'outils et les chemins locaux sont remplacés par une désignation fonctionnelle. Les caractéristiques techniques utiles (Uc, Up, In, Imax, tensions, courants, calibres, distances) sont conservées. Les références des cartes Essensys, leurs composants et les chemins du code des dépôts du projet sont cités tels quels.

**Conventions de marquage**

| Marque | Sens |
|---|---|
| **[VU]** | Lu sur un schéma, une BOM ou dans le code, source citée. Les points clés ont été relus pour ce rapport. |
| **[DS]** | Lu dans un extrait de fiche technique, constitué pendant l'analyse (liens en annexe B). |
| **[DS?]** | Valeur de fiche citée de mémoire, à vérifier. |
| **[DÉDUIT]** | Calcul ou raisonnement d'ingénieur, à confirmer par une mesure. |
| **[HYP]** | Hypothèse sur l'installation, à confirmer sur place. |
| **[EST]** | Prix estimé, hors taxes, petites quantités. |
| **[VU ph. n]** | (v2) Constaté sur la photo n du site. Photos 1 à 5 : coffret domotique et tableau électrique (ph. 1 : gros plan du côté gauche du coffret domotique, BA du haut et du milieu ; ph. 2 : un câble de bus posé sur l'établi ; ph. 3 : coffret domotique complet ; ph. 4 : parafoudre de tête dans le tableau ; ph. 5 : tableau électrique et coffret domotique). Photos 6 à 8 : coffret photovoltaïque. Les photos et leurs recadrages ne sont pas publiés. |

---

## Fiche de synthèse (ajout d'archivage)

| Rubrique | Contenu |
|---|---|
| Système | Armoire Essensys : BP **SC944D** (MCF52259, Ethernet, maître I2C) et trois BA : **SC940D** pièces de vie (0x11, PDV), **SC941C** pièces d'eau (0x13, PDE), **SC942C** chambres (0x12, CHB). Bus I2C à 50 kHz, câble 4 fils : SDA, SCL, GND, +15 V (BA_ALIM) |
| Implantation | **Un seul coffret domotique** (IP40), cartes empilées : SC940D en haut, SC941C, SC942C, BP SC944D en bas. Le coffret est accolé au tableau électrique (à gauche, parafoudre de type 2 en tête) et au coffret photovoltaïque (à droite, à quelques centimètres). L'onduleur hybride et des câbles DC sont au-dessus du coffret PV |
| Chaîne du bus | Ordre le plus probable : **BP-J31 → SC942C → SC941C → SC940D** (J1 du SC940D libre ; continuité derrière les goulottes [DÉDUIT]). Trois tronçons d'environ **33 cm** de câble cat. 5e souple, probablement **AWG26**, fiches 2×2 Würth |
| Réseau | Le BP est relié en Ethernet à un switch réseau, sur lequel est aussi câblé le **dongle de supervision de l'onduleur** ; ce dongle ne répondait plus lors de la mesure du 2026-10-11, et la date à laquelle il a cessé de répondre n'est pas connue (§0.5 n° 2) |
| Événement | **9 août 2026, vers 16 h 20.** Le disjoncteur de branchement a déclenché, l'installation photovoltaïque s'est arrêtée en même temps |
| Symptôme | Le BP n'a plus d'information d'aucun des trois BA. Un BA est présumé mort ; **il n'est pas encore identifié** |
| Constats annexes | Parafoudre AC du coffret PV : deux fenêtres **noires**. Parafoudres DC : aucun rouge. Parafoudre de type 2 du tableau : voyant vert |
| Mécanisme retenu [DÉDUIT] | Courant d'équilibrage entre îlots TBT flottants à travers le câble de bus (modèle R + (L − M)), écrêteurs I2C conducteurs dès ≈ 20 A (8/20) ; destruction possible par les broches I2C et par le fil +15 V qui surcharge le rail « +12V » du BA |
| Origine | Non établie : quatre hypothèses concurrentes (H-PV, H-RÉS, H-TOV, H-IND), §0.3.3 |
| Suite | Diagnostic sur site (§3), protections court terme (§4), carte d'interconnexion équipotentielle à long terme (§5.1 bis), suivies dans le ticket essensys-hub/essensys-board-SC944D#1 et le change OpenSpec i2c-surge-protection-2026-10-007 |

---

## 0. Mise à jour après les photos du site (2026-10-11)

### 0.1 En bref

1. **La topologie supposée par le v1 est fausse.**
   - Les quatre cartes sont dans **un seul coffret**, empilées, reliées par trois câbles d'environ 33 cm [VU ph. 1-3].
   - Le « ≈ 1 kV sur 10 m » du v1 ne s'applique pas. Le câble de bus n'est pas une antenne : c'est un **pont** entre quatre îlots TBT, qui ont chacun leur propre câblage vers la maison.
2. **Le bout de chaîne est le SC940D** (pièces de vie, 0x11), et non le SC941C [VU ph. 1, 3]. Sa position abaisse son seuil d'environ 3 fois par rapport au SC942C. Elle **ne prouve pas** qu'il est la carte défaillante, qui reste **à identifier**.
3. **Un parafoudre de tête de type 2 est déjà posé**, voyant vert : parafoudre bipolaire auto-protégé (déconnecteur intégré) avec cartouche enfichable [VU ph. 4]. La recommandation P1 du v1 (« en installer un ») devient un **contrôle** par l'électricien.
4. **Fait nouveau, côté photovoltaïque.**
   - Le parafoudre AC du coffret PV a ses deux fenêtres **noires** [VU ph. 6-8, confirmé par l'exploitant].
   - Les parafoudres DC du coffret PV ne montrent aucun rouge [VU ph. 6-8].
   - Le dongle de supervision de l'onduleur, branché sur le **même switch** que le BP, ne répond plus [VU, mesure réseau].
   - Ces faits rendent **plausible** une entrée par l'Ethernet du BP, mais **ne l'établissent pas**. Aucune chronologie ne relie encore le voyant noir, le dongle muet et la panne I2C. Quatre hypothèses restent concurrentes (§0.3.3).
5. **Nouveau mécanisme de destruction**, absent du v1 : le fil +15 V du bus charge le rail « +12V » du BA de bout de chaîne. U1 atteint ses 24 V dès un écart de masse d'environ 10 V (§0.3.2). Il explique directement un « BA mort non alimenté ».
6. **Les priorités changent** (§0.4) :
   - essais d'isolement sur **les trois BA et le BP** ;
   - débrancher l'Ethernet du dongle de supervision de l'onduleur ;
   - **isoler l'Ethernet du BP**, et ne pas y poser de parafoudre relié au PE ;
   - étoile 0 V doublée (N2), plus efficace que le simple renfort 0 V (N1) ;
   - éloigner les câbles PV du coffret domotique ;
   - le module d'isolement par BA (MIB) est réservé aux BA déportés.

### 0.1 bis Chronologie (précision de l'exploitant, ajoutée après la relecture)

- **Date du coup de foudre : 9 août 2026**, selon l'exploitant. Le disjoncteur de branchement (AGCP) a déclenché, ce qui a arrêté en même temps l'installation photovoltaïque.
- **Heure.** Sur la vue « Jour » du 09/08/2026 du portail de supervision de l'onduleur, la production monte normalement en début d'après-midi. À **16 h 25**, toutes les puissances sont à 0 W (solaire, maison, batterie, réseau), avec un état de charge de la batterie de 91 % [VU, capture fournie par l'exploitant]. Le coup de foudre se situe donc vers **16 h 15–16 h 25** [DÉDUIT].
- **Conséquences sur les hypothèses du §0.3.3.**
  - H-IND (événements indépendants) recule : la coupure du branchement et l'arrêt du PV sont simultanés.
  - Un déclenchement du disjoncteur de branchement est compatible avec un écoulement vers le PE à travers les parafoudres : le courant résiduel fait réagir son différentiel [HYP].
  - Les hypothèses H-PV et H-RÉS restent à départager.
- **Deux mois se sont écoulés** entre l'événement et l'analyse, ce qui change l'urgence :
  - le côté AC du PV n'a plus de parafoudre local depuis le 9 août (parafoudre AC au noir), en saison orageuse ;
  - l'onduleur ne produit peut-être plus depuis le 9 août : le dongle est muet, la supervision aussi ;
  - les historiques courts sont perdus (historique court de la passerelle Essensys, 48 h ; probablement une partie des événements du contrôleur réseau). Restent :
    - la date de dernière présence du dongle dans le contrôleur réseau ;
    - le `ts` des derniers messages MQTT retenus de la supervision de l'onduleur ;
    - le journal de l'onduleur ;
    - le portail de supervision de l'onduleur ;
    - l'historique du compteur communicant (gestionnaire du réseau de distribution) ;
  - les données d'un réseau de détection de la foudre (attestation de foudroiement) pour le 09/08/2026 entre 16 h et 16 h 30 permettraient de confirmer un impact proche et son heure.

### 0.2 Constats des photos

| Élément | Constat | Statut |
|---|---|---|
| Implantation | Tableau électrique (deux coffrets) à gauche, coffret domotique Essensys (IP40) au milieu, coffret photovoltaïque (côté AC et DC) à **droite**, à quelques centimètres. L'onduleur et des câbles DC à connecteurs MC4 sont au-dessus du coffret PV | [VU ph. 7] |
| Identité des BA | Haut : « Entrée / Salon / Salle à Manger / Bureau / Dressing » = **SC940D**. Milieu : « Cuisine / Salle de Bain 1… » = **SC941C**. Dessous : « Escalier / Grande Chambre / Petite Chambre 1-3 » = **SC942C**. En bas : **BP SC944D** | [VU ph. 3 + pages Borniers des schémas] |
| Chaînage | SC940D : J1 (connecteur du haut) **libre**, J2 câblé vers le bas. SC941C et SC942C : J1 et J2 câblés. BP : J31 câblé, à gauche du RJ45. Ordre le plus probable : **BP-J31 → SC942C → SC941C → SC940D** | [VU ph. 1, 3]. Continuité derrière les goulottes : [DÉDUIT] |
| Câbles de bus | Câble LAN rond blanc marqué « …5E 100 ohms – 26/07 » (cat. 5e, probablement AWG26 à 7 brins, 0,14 mm²), ≈ 30-35 cm. Fiches noires 2×2 Würth (contacts de 20 mΩ, isolement 1500 V [VU BOM]). Les câbles en place ont une gaine thermo **noire**, celui posé sur l'établi une gaine **bleue** : c'est un autre câble | [VU ph. 1-3]. Nombre de fils par contact (4 sur 8 ?) : inconnu |
| Distance au 230 V | Les câbles de bus descendent à **1 à 5 cm** des bornes « Ph » des premiers borniers, puis passent au bout des goulottes 230 V, sans goulotte séparée. Le 230 V interne est en H07V-U 1,5 mm² (simple isolation) | [VU ph. 1, 3] |
| Nappes J3 (entrées TOR) | Nappes grises visibles sur SC940D et SC941C, sortie par le haut du coffret. Sur le SC942C, une fiche est présente mais la nappe est masquée : **non concluant** (une nappe branchée est le plus probable, car les chambres ont des boutons) | [VU ph. 3] ; [HYP] pour le SC942C |
| BP | RJ45 « Box Internet » avec cordon **orange**, LED de lien verte. LED « TÉLÉINFO » jaune allumée, donc le MCF tourne. Le cordon orange semble remonter dans le coffret et passer **sur la nappe du SC940D**. La fenêtre J3 du BP (capteurs, IHM) **semble vide** | [VU ph. 3, 5]. Trajet du cordon et J3 vide : [HYP] |
| LED « ÉTAT » des BA | Éteintes sur la photo. Non concluant : DL1 ne fait qu'un bref éclair par seconde | [VU ph. 3] |
| Parafoudre de tête | Parafoudre bipolaire de **type 2** à déconnecteur intégré, avec cartouche enfichable (**Uc 275 V, In 5 kA, Imax 15 kA, Up ≤ 1 kV en L-N**). Fenêtre **verte**. Montage 1+1 : seule la varistance L-N a un voyant, l'éclateur N-PE n'en a pas. Position : coffret de droite du tableau, rangée 4, juste à côté du coffret domotique. Alimentation (depuis l'AGCP ou par le peigne derrière l'ID 30 mA type AC) : non visible | [VU ph. 4, 5] |
| Coffret PV, côté DC | 2 disjoncteurs DC bipolaires C16 (« Ue 500 V⎓ », Uimp 4 kV) et 4 parafoudres DC de **type 2** (Ucpv 750 V entre + et − / 600 V vers PE, In 20 kA, Imax 40 kA, Up 2,8 kV). Fenêtres vertes sur les modules lisibles, reflets sur les autres, **aucun rouge** | [VU ph. 6-8] |
| Coffret PV, côté AC | Parafoudre AC de **type 2** (Uc 320 V, Up ≤ 1,5 kV, Imax 15 kA) avec ses **deux fenêtres noires**. Disjoncteur de déconnexion AC bipolaire C32 (voyants rouges, donc fermé). Interrupteur différentiel 40 A 300 mA, en position « I ON » ; son type (AC ou A) n'est pas lisible | [VU ph. 6-8] |
| Réseau (mesure du 2026-10-11) | Routeur et passerelle Essensys joignables. Dongle de supervision de l'onduleur (dans un sous-réseau distinct de celui du routeur et de la passerelle) : ping KO, entrée ARP « incomplete » | [VU, mesure faite pendant l'analyse] |
| Autres anomalies | Aucune trace de brûlure visible sur les faces avant (cartes capotées : non concluant). Un microrupteur de porte (J53 du BP) pend hors du coffret, sans rôle crédible dans la foudre. Un **mètre pliant** est posé à travers les cartes, coffret ouvert et sous tension (ph. 3) | [VU ph. 3] |

### 0.3 Mécanisme révisé

#### 0.3.1 Le câble de bus est un pont, pas une antenne [DÉDUIT, calcul CEM recoupé par un script indépendant du relecteur adversarial]

Par tronçon de 33 cm d'AWG26 :

| Grandeur | Valeur |
|---|---|
| Inductance propre | 0,46 µH |
| Inductance mutuelle avec un conducteur voisin du même câble | 0,30 à 0,37 µH |
| **L − M**, ce que voit l'I2C entre une ligne et son 0 V | **0,09 à 0,16 µH** |
| R (fil 0,046 Ω + 2 contacts de 20 mΩ + cuivre) | ≈ 0,09 Ω : les contacts pèsent autant que le fil |

Un courant de mode commun induit presque la même tension sur SDA, SCL et GND. Seuls R et (L − M) apparaissent entre une ligne et le 0 V. Le bon modèle est donc **R + (L − M)** par tronçon, et non L·di/dt avec l'inductance propre.

**Seuil d'injection.** Les écrêteurs I2C conduisent aux deux bouts quand l'écart entre le 0 V du SC940D et celui du BP dépasse **6,3 à 7,8 V** selon la polarité (diode du PIC ou TVS en direct d'un côté, TVS en avalanche ou U19 de l'autre). Au-delà, SDA et SCL deviennent des chemins parallèles au fil GND. Le courant d'équilibrage nécessaire dépend de la pente de l'onde :

| Configuration entre SC940D et BP | Onde 8/20 (0,2 Ipk/µs) | Front rapide (1 Ipk/µs) | Front très rapide (4 Ipk/µs) |
|---|---|---|---|
| **Actuelle** (3 tronçons AWG26) | **≈ 20 A** | **≈ 11 A** | ≈ 4 A |
| N1 : 0 V de 4 mm² plaqué, soudé sur chaque carte | ≈ 97 A | ≈ 25 A | ≈ 7 A |
| N1 sans retouche (J1 libre du SC940D vers le moins de la batterie du BP) | ≈ 73 A | ≈ 22 A | ≈ 6 A |
| **N2 : étoile, chaque BA par J1 et J2** (AWG20, ≤ 15 cm) | ≈ 173 A | **≈ 79 A** | ≈ 26 A |
| Fond de panier avec plot 0 V soudé (BA rév. E) | ≈ 875 A | ≈ 292 A | ≈ 83 A |

Le gain de N1 tombe de ×5 à moins de ×2 quand le front raidit, celui de N2 reste de ×6 à ×9. **La position compte** : le SC940D, à trois tronçons du BP (z ≈ 0,35 Ω en 8/20), a un seuil environ 3 fois plus bas que le SC942C, à un seul tronçon (≈ 0,12 Ω). Elle ne désigne pas pour autant, à elle seule, la carte défaillante.

#### 0.3.2 Ce que subissent les cartes au-delà du seuil [DÉDUIT]

- **Broches I2C.** Avec R1/R2 = 0 Ω, la diode de protection du PIC est en parallèle avec D1/D2 : 1 à 2 A dans la broche, soit 50 à 100 fois son maximum de 20 mA, dès environ 30 A d'équilibrage en 8/20. Côté BP, la ligne monte à 9-10 V, alors que le maximum de U19 est 7 V.
- **Rail d'alimentation du BA (mécanisme ajouté en v2).**
  - Quand le 0 V du BA descend sous celui du BP, le fil +15 V, qui ne porte pas le courant d'équilibrage, arrive au BA à 15 V + ΔV. D3 est déjà passante : le courant charge **C2 (10 µF / 16 V)** sans aucun seuil (τ ≈ 0,3 Ω × 10 µF ≈ 3 µs).
  - Le rail « +12V » (14,3 V au repos) monte alors d'environ ΔV : C2 dépasse ses 16 V dès ΔV ≈ 2 V, et **U1 (LMR12010, 24 V max) est atteint vers ΔV ≈ 10 V, soit environ 28 A** en 8/20 au SC940D.
  - C'est le même ordre de grandeur que le seuil I2C. Ce mécanisme explique un « BA mort non alimenté » (U1, C2, D6, FI1) **sans** passer par RC6/RC7. N1 et N2 le réduisent aussi, puisqu'ils réduisent ΔV.
- **Avec R1/R2 = 47 Ω (P1).** Le PIC reçoit déjà 19 à 34 mA au seuil de la TVS, environ 140 mA à VC ≈ 12 V et environ 40 mA en polarité négative. **47 Ω transforme une destruction quasi certaine en survie probable, sans respecter le maximum absolu.** Seule l'option BAT54S (§4.4) ramène le PIC près de ses limites. La limite des TVS elles-mêmes est d'environ 240 A en 8/20.

#### 0.3.3 D'où vient le courant d'équilibrage : hypothèses concurrentes, non classées avant les preuves

Le parafoudre de tête limite L-PE et N-PE à ses bornes (environ 1,5 kV) et L-N à 1 kV au plus. Il ne fait rien pour la TBT flottante, pour le côté charge d'un contact de relais ouvert, pour la tension induite le long des circuits intérieurs, ni pour l'Ethernet.

| # | Hypothèse | Pour | Contre ou condition | Test qui départage |
|---|---|---|---|---|
| H-PV | **Foudre côté PV** (induction sur les chaînes ou montée du PE de l'onduleur), puis **Ethernet** : dongle de supervision de l'onduleur → switch réseau → J32 du BP → 0 V du BP → bus → BA | Parafoudre AC du coffret PV au noir, dongle muet, même switch. Le réseau Bob Smith de J32 relie les 8 fils du câble au 0 V du BP par ≈ 1 nF / 2 kV [VU SC944D p. 6] | Avant amorçage, il y a au moins trois capacités de 1 nF en série (dongle, deux ports du switch, J32) : **0,3 à 1,7 A**, trop peu pour faire conduire les écrêteurs du bus (≈ 11 à 20 A). Le régime de 10 à 50 A exige l'amorçage de deux ou trois barrières, qui en garderaient la trace. Un switch relié au PE **détourne** le courant au lieu de l'envoyer au BP | Journal des ports du switch (dongle, BP) ; switch flottant ou relié au PE ; résistance entre les broches 1 et 3 de J32 ; essai à 500 V de J32 et C63 (§3.4) ; journal de l'onduleur (alarme SPD, isolement) |
| H-RÉS | **Foudre côté réseau, en mode commun** (régime TT) | En 1+1, le parafoudre de tête passe par l'éclateur N-PE, sans voyant : son vert ne prouve pas qu'il n'a rien vu. Le parafoudre AC du coffret PV écrête au même niveau (≈ 1,5 kV) | Le chemin vers l'îlot passe alors par le côté 230 V des BA (J1/J2 à 2-3 mm de K1, v1 A6) ou par les nappes J3 qui longent le 230 V | Traces d'amorçage dans la zone J1/J2–K1 ; isolement 230 V / TBT < 10 MΩ ; TVS d'entrée de J3 claquées ; données de détection de la foudre |
| H-TOV | **Surtension temporaire** d'origine HTA en L/N-PE (U0 + 1200 V pendant ≤ 0,2 s), ou **défaut de l'onduleur** | Si le parafoudre AC du coffret PV a deux varistances vers le PE (architecture CT1, ce que suggèrent ses deux fenêtres), il meurt alors qu'un 1+1 à éclateur résiste. L'argument « Uc 320 V > 275 V » n'exclut qu'une surtension L-N | Ne produit pas forcément d'impulsion sur l'îlot Essensys | Notice du parafoudre AC du coffret PV (architecture, sens des fenêtres, sens du noir) ; historique du compteur communicant ; journal de l'onduleur |
| H-IND | **Événements indépendants** | Le parafoudre AC a pu noircir bien avant la panne. Un onduleur à l'arrêt (le dongle est alimenté par lui) suffit à expliquer l'ARP « incomplete » | — | Date à laquelle le parafoudre AC a été vu vert pour la dernière fois ; état de l'onduleur ; dernière donnée du portail de supervision ; `ts` MQTT de la supervision de l'onduleur ; dernière commande BA réussie |

Depuis la précision de chronologie (§0.1 bis), H-IND recule : la coupure du branchement et l'arrêt du PV sont simultanés.

**Chemins secondaires, à garder en vue** [HYP] :
- **Nappes J3 des BA.** Le 0 V de chaque BA s'étend à tous ses boutons. Une tension de mode commun le long d'une nappe ne fait circuler un courant que si la boucle se ferme à l'autre bout (amorçage dans une boîte, plaque reliée au PE, autre réseau). Pour un câble TBT à 1 cm d'un câble 230 V qui écoule un choc, la mutuelle vaut de l'ordre de 0,5 à 1 µH/m : environ 0,5 à 1 kV sur 10 m à 100 A/µs **si la boucle est fermée**. C'est le seul usage légitime de l'ordre de grandeur « ≈ 1 kV sur 10 m ».
- **230 V commuté vers l'extérieur** (électrovanne, Terrasse et Annexes du SC941C, Entrée et Annexe sur EDP4) : contact de relais ouvert, la surtension arrive sur la piste, à 2-3 mm de J1/J2.
- **Boucle écran IHM / boutons de l'entrée** (H1 de la première analyse) : **conditionnelle**. Elle suppose une IHM câblée sur le J3 du BP, qui semble vide [VU ph. 5, à confirmer].
- **Induction directe par les câbles PV** qui passent dans l'angle haut droit du coffret domotique [VU ph. 7]. Elle peut atteindre le côté 230 V droit du SC940D et sa nappe J3 (2 à 18 V pour 0,5 à 2 kA/µs). Elle **ne désigne pas** son port I2C : J1/J2 sont au bord gauche, à 50-60 cm, et la boucle SDA/GND du câble fait environ 1 mm (M ≈ 0,1 nH).

**Le BA défaillant n'est pas identifié.** Les photos ne permettent pas de conclure (LED ÉTAT éteintes sur la photo, cartes capotées). Il faut d'abord la vidéo E0, l'index 12 après une commande vers chaque BA, puis E1/E2 (§3.1, §3.2).

**Ordre des suspects révisé** (remplace celui du v1 §1) :
1. Sur le BA en défaut, et d'abord le SC940D s'il est le défaillant : alimentation **U1, D3, C2, D6, FI1** (§3.5 n° 7 à 11), puis RC6/RC7 du PIC et D1/D2.
2. Sur le BP : U19, puis D33/D34. Le MCF tourne (LED de téléinfo), mais ses broches 28/29 restent à contrôler (§3.4). J32 et C63 si H-PV se confirme.
3. Les autres BA, dans l'ordre SC941C puis SC942C.
4. Effondrement du +15VSP.

La panne « BA mort qui tient le bus » (v1 §1) reste en tête si DL1 est éteinte sur une seule carte.

### 0.4 Ce qui change dans les priorités

| Prio | Mesure | Avant (v1) | Maintenant (v2) |
|---|---|---|---|
| **P0** | Essais d'isolement à 500 V continu, 230 V contre TBT | Sur le BA mort | **Sur les trois BA et le BP**, en commençant par le SC941C (salles de bains). < 10 MΩ : pas de remise en service (§3.0, §3.5 n° 14) |
| **P0** | Ethernet du dongle de supervision de l'onduleur | — | **Débrancher côté switch**, ne pas le rebrancher en cuivre. Passer le dongle en Wi-Fi s'il est vivant (§3.0, n° 8) |
| **P0** | Horodatage | — | Contrôleur du réseau, passerelle Essensys, portail de supervision de l'onduleur, serveur Essensys, historique du compteur communicant, données de détection de la foudre, avant expiration des historiques (§3.1) |
| P0 | Diagnostic et réparation | BA mort supposé en bout de chaîne | BA défaillant à identifier ; tester l'alimentation du BA avant RC6/RC7 (§0.3.2) |
| **P0** (urgence relevée : 2 mois sans protection) | Coffret PV | — | **Installateur PV** : remplacer le parafoudre AC, lire le journal de l'onduleur, vérifier que l'onduleur produit, contrôler le côté DC et l'équipotentialité, vérifier le type de l'interrupteur différentiel 300 mA. Non bloquant pour la remise en service d'Essensys. Le côté AC du PV n'a plus de parafoudre local **depuis le 9 août** |
| **P0** | Conservation des preuves | — | Conserver le parafoudre AC déposé, la cartouche du parafoudre de tête si elle est remplacée, le dongle, les cartes et pièces déposées, les photos horodatées, les journaux et la capture de la courbe de production du 09/08 (§0.1 bis) |
| P1 | R1/R2 en 47 Ω | « 33 Ω si ΔVg > 0,1 V » | **Maintenu, critère conditionnel conservé** jusqu'à la mesure : ΔVg attendu de 0,06 à 0,16 V sans renfort (§2.3, §4.2) |
| **P1** | Isolement de l'Ethernet du BP | P2 « parafoudre RJ45 relié au PE » | **Fibre** (convertisseur côté BP alimenté depuis l'îlot TBTS) ou **isolateur Ethernet ≥ 4-6 kV**. **Pas de parafoudre RJ45 relié au PE au BP** |
| P1 | Impédance entre cartes | « Câble de bus court, ≥ 10 cm du 230 V » | **N2 (étoile doublée) en premier** ; N1 (renfort 0 V) en complément ou à défaut (§4.1 bis, §5.1 bis) |
| P1 | Alimentation des BA | C2 35 V, D6 30-40 V sur le BA réparé | **Remontée** à cause du mécanisme +15 V : C2 35 V, D6 40 V, TVS après R79 sur chaque BA déposé |
| P1 | Séparation physique | — | Câbles PV (DC, batterie, AC, PE) à ≥ 30-50 cm du coffret domotique, ou en goulotte métallique reliée au PE aux deux bouts. Cordon Ethernet du BP sorti directement du coffret. Bus et nappes éloignés des bornes Ph |
| P1 | Parafoudre de tête | À installer | **Présent**. Contrôle par l'électricien : manette du parafoudre, alimentation en amont des ID, liaisons ≤ 50 cm, PE, terre ; cartouche à remplacer par précaution |
| P1/P2 | Départs 230 V extérieurs | « Parafoudre de type 3 ou varistance 275 V » | Parafoudre modulaire de type 3 conforme NF EN 61643-11, **au départ dans le tableau électrique**, jamais dans le coffret domotique ; **jamais de varistance nue** |
| Long terme | Architecture | MIB par BA | **Carte d'interconnexion équipotentielle** (fond de panier) pour un coffret unique + isolement des ports qui en sortent. MIB réservé aux BA déportés (§5.1 bis) |

### 0.5 Ce qui reste à vérifier

1. **Quel BA est défaillant** : vidéo de 10 s des trois fenêtres ÉTAT et de la LED de téléinfo (fixe ou clignotante), index 12 après une commande vers chaque BA, puis E1/E2.
2. **Chronologie** (date connue : 09/08/2026 vers 16 h 20, §0.1 bis) : date à laquelle le parafoudre AC du coffret PV a été vu vert pour la dernière fois ; données du portail de supervision de l'onduleur après le 09/08 ; `ts` des derniers messages MQTT retenus de la supervision de l'onduleur et historique court de la passerelle Essensys (48 h) ; journal du contrôleur réseau (dernier « seen » du dongle, « port down », erreurs) ; dernière commande BA réussie ; historique du compteur communicant ; données de détection de la foudre.
3. **Onduleur et dongle** : afficheur, production, journal (alarmes SPD, isolement, défaut de terre), LED du dongle. Parafoudres internes de l'onduleur [DS?]. Câblage de la sortie de secours (EPS).
4. **Notice du parafoudre AC du coffret PV** (à demander à l'installateur) : architecture CT1 ou 1+1, sens des deux fenêtres et du noir (drapeau, voyant, module mal enfiché).
5. **Switch réseau** : modèle, alimentation (bloc 2 broches ou relié au PE), emplacement, longueur et trajet des câbles du dongle et du BP, compteurs d'erreurs des deux ports, présence du routeur et de la passerelle Essensys sur ce même switch.
6. **Coffret domotique** : nappe J3 du SC942C ; contenu de J3 du BP (IHM, capteurs extérieurs) ; nature des conducteurs rouges et marron qui entrent en haut à droite ; trajet du cordon orange ; parcours dans les goulottes (TBT et 230 V dans un même conduit ?).
7. **Câble de bus** : origine du câble posé sur l'établi (gaines bleues) ; nombre de fils par contact.
8. **Parafoudre de tête** : manette du déconnecteur, mode d'alimentation, identité de l'appareil de tête (AGCP de type S ?), résistance de terre, paratonnerre ou ligne aérienne.
9. **Prise de terre unique** : le PE du coffret PV, l'équipotentialité des cadres et les parafoudres AC et DC du coffret PV rejoignent-ils la même borne principale de terre que le parafoudre de tête ?
10. **Courant de chaque BA**, relais collés : il fixe le ΔVg statique.
11. **Distances 230 V / TBT** sur les Gerber (J1/J2 ↔ K1, VR1) : le schéma du BP impose lui-même 5,5 mm.
12. **Microrupteur de porte** (J53) qui pend hors du coffret : à refixer.

---

## 1. Ce qui s'est très probablement passé

- **L'origine de la surtension** (corrigé en v2).
  - Le BP et les trois BA sont chacun un îlot TBT flottant, sans aucune liaison au PE [VU, sur les quatre schémas]. Le seul lien galvanique entre eux est le câble 4 fils (SDA, SCL, GND, +15 V) [VU].
  - Les quatre cartes sont dans le même coffret, reliées par trois tronçons d'environ 33 cm [VU ph. 1-3]. Le câble de bus n'est donc pas l'antenne : il est le **pont** entre quatre îlots qui ont chacun leur câblage de terrain (nappes J3 vers les boutons, sorties 230 V, et côté BP : Ethernet, téléinfo, électrovanne, fils pilotes).
  - Un événement extérieur a porté ces îlots à des potentiels différents. Entre une ligne et le 0 V, chaque tronçon présente R + (L − M) ≈ 0,09 Ω + 0,09 à 0,16 µH. Les écrêteurs I2C conduisent dès **≈ 20 A** de courant d'équilibrage en onde 8/20, ≈ 11 A sur un front rapide (§0.3.1) [DÉDUIT]. Le « ≈ 1 kV sur 10 m » du v1 ne s'applique pas ici.
  - La porte d'entrée de ce courant n'est pas établie. Quatre hypothèses restent concurrentes, dont une entrée par l'Ethernet depuis l'installation photovoltaïque (§0.3.3).
- **Le chemin dans les cartes.** Les diodes TVS SMF5V0A, câblées de chaque ligne vers la masse locale (D33/D34 au BP, D1/D2 sur chaque BA), ont renvoyé ce courant dans SDA et SCL, donc :
  - dans U19 (PCA9306), limité à 7 V ;
  - dans RC6/RC7 des PIC, reliées au connecteur par des résistances de **0 Ω** [VU].
  - (v2) **Et par le fil +15 V**, qui charge sans seuil le rail « +12V » du BA quand son 0 V descend sous celui du BP : U1 atteint ses 24 V vers 28 A d'équilibrage (§0.3.2) [DÉDUIT].
- **Le BA de bout de chaîne** (corrigé en v2) est le **SC940D** (pièces de vie, 0x11), et non le SC941C [VU ph. 1, 3]. Son seuil est environ 3 fois plus bas que celui du SC942C. Cela ne suffit pas à le désigner comme la carte qui a le plus souffert : il faut l'identifier (§3.1, §3.2).
- **Pourquoi plus aucun BA ne répond.** Le bus est partagé, sans tampon [VU]. Il suffit d'**une seule** ligne tenue basse ou à mi-niveau pour faire taire les trois adresses en même temps [DÉDUIT]. Trois causes possibles :
  - une TVS en court-circuit ;
  - une broche de PIC claquée ;
  - le BA mort, qui n'est plus alimenté et dont le PIC tire SDA et SCL vers le bas par ses diodes internes.
- **Ordre des suspects** (révisé en v2, détail au §0.3.3) : d'abord le BA mort, en testant son alimentation (U1, D3, C2, D6, FI1) avant RC6/RC7 ; ensuite U19 puis D33/D34 sur le BP ; puis une TVS ou une broche sur un autre BA ; enfin un effondrement du +15VSP.

---

## 2. Ce que montrent les schémas

### 2.1 Interface I2C du BP (SC944D, page 7 du PDF) [VU, crops relus]

```
MCF52259 (3,3 V) br.28 SCL / br.29 SDA (I2C0, 50 kHz, ba_i2c.c:106)
   │ ≈55 mm de piste, AUCUNE protection (ni R série ni écrêtage)
   ├─ R157 (SCL) / R158 (SDA) 4,7 kΩ → +3V3S
U19 PCA9306DCUT : VREF1 = +3V3S (C86) ; VREF2 = EN, tirés par R154 200 kΩ → +5VS, C87 100 nF
   ├─ R156 (SCL2) / R155 (SDA2) 1 kΩ → +5VS     ← entre U19 et les perles
   ├─ C80 (SCL) / C79 (SDA) 18 pF NON MONTÉS     ← côté U19
L30 (SCL) / L32 (SDA) Würth 742792643 : 0603, 400 mA, 0,35 Ω, 700 Ω à 250 MHz
D33 (SCL) / D34 (SDA) SMF5V0A → GND, à 6 et 8 mm de J31
J31 Würth 66200421122 : 1 = BA_SDA, 2 = BA_SCL, 3 = GND, 4 = BA_ALIM
BA_ALIM = +15VSP (T32 NTD2955G, « 2 A », commandé par TE2 via T33, cavalier J58) → L31 100 Ω/8 A → J31-4
          ni TVS, ni fusible, ni PTC.  U16 LD1117 (+12VSP) est alimenté directement par +15VSP.
```

**Faiblesses chiffrées du BP**

| # | Constat | Chiffres | Conséquence |
|---|---|---|---|
| B1 | La TVS SMF5V0A écrête trop haut pour U19 | VBR de 6,4 à 7,1 V. VC = 9,2 V à 21,7 A en onde 10/1000 [DS]. Vers 12 à 14 V à 50–70 A en onde 8/20 [DÉDUIT, extrapolation à environ 0,1 Ω dynamique]. Max absolu de U19 : 7 V [DS] | U19 partage le courant avec la TVS : la perle (0,35 Ω, 400 mA) ne le limite pas à l'échelle de la µs |
| B2 | Polarité négative | La TVS conduit en direct, jusqu'à −2,5 V à 50 A [DS]. Limites : U19 −0,5 V et −50 mA ; MCF −0,3 V [DS] | L'impulsion négative traverse le FET passant de U19 jusqu'au MCF |
| B3 | Côté µC | MCF : VIN max 4,0 V (non tolérant 5 V), 25 mA par broche, VIL 1,155 V [DS]. Piste de 55 mm sans aucune protection [VU P&P] | Interface la moins protégée de la carte. À titre de comparaison, les entrées pluie et vent ont une perle, 4,7 kΩ, un condensateur et une BAT54S |
| B4 | BA_ALIM non protégé | Une surtension positive remonte par la diode interne de T32 vers +15VS (environ 66 µF de céramique), puis atteint U2 (LMR12010, 24 V max) et **U16 (LD1117, entrée 15 V max [BOM]) alors que +15VSP vaut 15,17 V en nominal** | U16 est déjà hors spécification en régime normal |
| B5 | Couplages de masse | Le 0 V du BP est relié au blindage RJ45 par C63 (1 nF/2 kV) et à la terminaison Bob Smith par la capacité interne du module (broche 8 à GND, ≈ 1 nF/2 kV [DS?]). Les huit fils du câble Ethernet sont donc couplés en mode commun au 0 V du BP. Le RJ45 J32 n'est isolé qu'à 1,5 kV et se trouve à 18 mm de J31. Le domaine du fil pilote est au potentiel de la phase (+12VISOFP relié à PH_FP) [VU p. 6] | Pendant un transitoire, le 0 V du BP suit les câbles : Ethernet, J3 (capteurs extérieurs) et câble des BA. (v2) Le switch du BP porte aussi le dongle de supervision de l'onduleur [VU, précision de l'exploitant] : c'est le seul port de l'îlot avec une liaison métallique directe vers des équipements potentiellement reliés au PE (§0.3.3, H-PV) |
| B6 | Comportement de U19 | EN = VREF2 ≈ VREF1 + 0,6 V ≈ 3,9 V en fonctionnement normal [DS]. Les grilles des transistors de passage sont reliées à EN | Voir le diagnostic au §3.4. Une valeur EN ≈ 5 V ne signifie **pas** « interrupteur ouvert » |

### 2.2 Interface I2C des BA (page 2 « Cœur », topologie identique sur les trois cartes) [VU, crop SC940D relu]

```
J1 ∥ J2 (Micro-MaTe-N-Lok, câblés en parallèle) : 1 SDA, 2 SCL, 3 GNDBUS, 4 +VBUS
  SDA/SCL : D1 (SDA) / D2 (SCL) SMF5V0A → GND local, côté connecteur
          → R1 / R2 = 0 Ω (SC941C : R1/R3), 0805
          → nœud côté PIC : R40 / R41 10 kΩ → +5 V et C23 / C25 22 pF NON MONTÉS
          → PIC16F946 RC7 = SDA (broche 62), RC6 = SCL (broche 61), module SSP esclave
  +VBUS → R79 0 Ω « Monté » (L3 744272102, 2 × 1 mH, barrée) → +Vin
        (empreinte C40 220 pF NON MONTÉE entre +Vin et GND)
        → FI1 NFE31PT221D1E9L (25 V) → D3 GF1B → « +12V » ≈ 14,3 V (C2 10 µF/16 V)
        → U1 LMR12010YMK (VIN 24 V abs, BOOST 30 V abs) → L1/L2 → +5 V = 4,93 V
  GNDBUS → R80 0 Ω « Monté » → GND
```

**Désignateurs par carte**

| Fonction | SC940D | SC941C | SC942C |
|---|---|---|---|
| PIC / NCP803 | U4 / U3 | U4 / U3 | U5 / U4 |
| Série SDA / SCL (0 Ω) | R1 / R2 | R1 / **R3** | R1 / R2 |
| Pull-ups 10 kΩ SDA / SCL | R40 / R41 | R43 / R44 | R51 / R52 |
| 22 pF non montés SDA / SCL | C23 / C25 | C24 / C26 | C27 / C29 |
| 0 Ω VBUS / GNDBUS | R79 / R80 | R93 / R94 | R84 / R85 |
| Empreinte C 220 pF (+Vin–GND) | C40 | C40 | C42 |
| Connecteur ICSP | J83 | J97 | J92 |
| Adresse (fichier .hex v1.7) | 0x11 | 0x13 | 0x12 |

**Faiblesses chiffrées des BA**

| # | Constat | Chiffres | Conséquence |
|---|---|---|---|
| A1 | Le PIC conduit **avant** la TVS, sans limitation de courant | La diode interne du PIC conduit vers 5,5 V, alors que la TVS ne claque qu'à partir de 6,4 V. Limites du PIC : broches de −0,3 V à VDD + 0,3 V, IIK ±20 mA, 25 mA par broche [DS] | Le PIC sert d'écrêteur principal. Les entrées TOR de la même carte ont, elles, 22 kΩ en série |
| A2 | Seuils I2C du PIC | VIL ≤ 0,3·VDD = 1,48 V ; VIH ≥ 0,7·VDD = 3,45 V ; VOL ≤ 0,6 V à 8,5 mA [DS] | Le niveau haut exige au moins 3,45 V : la fuite d'une TVS se voit vite |
| A3 | Alimentation d'entrée sans TVS | Le rail « +12V » est à 14,3 V. Tenues : C2 16 V, D6 20 V, LMR12010 24 V (abs) et 20 V en fonctionnement, FI1 25 V | La carte a été conçue pour 12 V et tourne sous 15 V : moins de 2 V de marge sur C2 |
| A4 | Masse du bus reliée en direct au 0 V local | Depuis la modification DM de janvier 2017, R79/R80 (0 Ω) sont montées et L3/C40 retirées [VU, BOM DM et BOM d'archive] | Le fil GND du câble est le chemin principal des courants d'équilibrage |
| A5 | Le 0 V du BA s'étend dans tout le bâtiment | 20 à 22 entrées TOR à contact sec vers le 0 V, sans optocoupleur, par la nappe J3 [VU] | Grande antenne de captation. Chaque TVS d'entrée renvoie son courant dans le 0 V, qui est aussi la référence I2C |
| A6 | Isolement 230 V / TBT | J1/J2 estimés à **2–3 mm** du relais K1 (230 V), mesure prise sur les contours du plan d'assemblage [estimation]. (v2) Sur le SC940D, K1 est le relais « Entrée » et la varistance VR1 du variateur du salon est voisine de J2 [VU plan d'assemblage]. D1/D2 sont à environ 28-48 mm de J1/J2 [VU plan, relecture] | Risque d'amorçage 230 V vers TBT. À contrôler par un essai d'isolement **sur chaque BA** (§3) et sur les Gerber. Le schéma du BP impose lui-même 5,5 mm pour le 230 V [VU SC944D p. 2] : en dessous, l'îlot n'est pas TBTS par construction |
| A7 | Un BA non alimenté charge le bus | Le PIC est réalimenté par ses diodes de clamp. SDA et SCL se retrouvent entre 0,6 et ≈ 3 V [DÉDUIT] | Un BA mort qui reste branché suffit à bloquer les trois |
| A8 | Pas de watchdog sur le BA | `__CONFIG(HS & WDTDIS)` (`main.c:17`) ; branche `else;` sans traitement d'erreur SSP (`slavenode.c:361`) [VU] | Un PIC bloqué avec CKP = 0 tient SCL bas jusqu'à une coupure d'alimentation |

### 2.3 Le bus dans son ensemble [DÉDUIT à partir des valeurs VUES]

- **Pull-ups.** 1 kΩ ∥ 3 × 10 kΩ = **769 Ω**. Le courant à l'état bas vaut environ **6,5 mA** (5,9 mA côté 5 V plus 0,6 mA par R157/R158). La norme I2C en mode standard prévoit 3 mA.
- **Capacité.** Quatre SMF5V0A par ligne, à 1120 pF chacune sous 0 V [DS], soit environ **2 à 3 nF** en moyenne sur la plage 0–5 V. C'est la TVS, et non le câble, qui fixe le temps de montée : de 1,4 à 3,2 µs entre 0 et 3,45 V. (v2) Le câble réel (≈ 1 m de cat. 5e) n'ajoute qu'environ 50 pF [DÉDUIT].
- **Marge de niveau bas dans le sens BA → BP** (le MCF lit, seuil de 1,155 V) : **0,70 V** si ΔVg = 0. ΔVg est l'écart de masse statique entre le BP et un BA, causé par le courant de BA_ALIM qui revient par le fil GND.
- **ΔVg attendu sur ce site** (v2) [DÉDUIT]. Le tronçon BP → SC942C porte le retour des trois BA, le suivant celui de deux, le dernier celui du SC940D seul. Au SC940D : ΔVg = 6 × R_tronçon × I_BA.
  - Avec R_tronçon ≈ 0,09 Ω (fil AWG26 de 33 cm + deux contacts de 20 mΩ) et I_BA = 0,15 à 0,3 A [HYP, non mesuré] : **0,08 à 0,16 V**.
  - Avec deux fils par contact (câble 8 fils sur 4 contacts, à vérifier) : 0,06 à 0,12 V.
  - Les contacts pèsent autant que le fil. Avec un renfort 0 V (N1) ou une étoile (N2) : < 0,02 V.
  - La mesure du §3.7 reste nécessaire : elle conditionne le choix entre 47 et 33 Ω (§4.2).
- **Marge dans le sens BP → BA** (le PIC lit, seuil de 1,48 V) : elle **n'est pas déterminée**.
  - Les sorties du MCF sont par défaut en sortance faible (2 mA) [DS]. Aucune écriture de PDSR n'a été trouvée dans le code. Le BSP de production est absent.
  - En sortance faible, la marge peut tomber à environ 0,15 V [DÉDUIT].
  - Le système fonctionne depuis environ neuf ans, ce qui plaide pour une marge réelle suffisante. Il faut la **mesurer** (§3.7).
- **Firmware** [VU] :
  - pas de récupération de bus (9 coups d'horloge) ;
  - la reprise se limite à `fclose`/`fopen`, jusqu'à 50 fois ;
  - au-delà de 21 échecs, la commande est **abandonnée et marquée acquittée** ;
  - les trames de configuration perdues ne sont jamais renvoyées ;
  - l'index 12 (`comm_faults` côté serveur) n'est mis à jour qu'**après une commande** envoyée au BA concerné.

---

## 3. Diagnostic et réparation immédiate

### 3.0 Sécurité, avant de toucher quoi que ce soit (étape E-1)

Après un coup de foudre, la barrière entre TBTS et 230 V peut être rompue. Tout le réseau TBT (câble de bus, nappes J3 vers les boutons muraux, capteurs extérieurs) peut alors se trouver au potentiel du secteur.

0. (v2) **Ne rien introduire dans le coffret ouvert tant qu'il n'est pas consigné**, ni outil ni mètre : un mètre pliant posé à travers les cartes sous tension apparaît sur la photo 3. Pour les photos, porte ouverte, ne rien toucher.
1. **Sans toucher les cartes, 230 V présent.** Mesurer la tension alternative entre un 0 V TBT accessible (moins de la batterie du BP, ou une borne GND) et le PE. Utiliser un VAT ou un multimètre en mode basse impédance (LoZ).
   - Quelques volts qui s'effondrent en LoZ : c'est normal (couplage capacitif).
   - Plusieurs dizaines à 230 V qui tiennent en LoZ : **arrêt**, consigner l'ensemble et appeler un électricien.
2. **Consigner** selon la NF C 18-510 :
   - le disjoncteur du BP **et tous les départs** commandés par les BA (il peut y en avoir plusieurs par BA) ;
   - la batterie du BP (J56-4) ;
   - (v2) **l'installation photovoltaïque** : l'onduleur hybride a une batterie et peut avoir une **sortie de secours (EPS)** qui maintient des circuits sous tension AGCP ouvert. Vérifier que le départ qui alimente le tableau domotique et les départs commandés par les BA n'y sont pas raccordés. La personne habilitée (BR/BC) qui consigne ouvre aussi le disjoncteur de déconnexion AC C32 et l'interrupteur différentiel du coffret PV, par simple manœuvre des manettes en face avant ;
   - puis vérifier l'absence de tension (VAT conforme NF EN 61243-3) sur chaque bornier de BA, ainsi qu'entre J1/J2 et le PE.
   - Si vous n'êtes pas habilité, faites intervenir un électricien.
   - (v2) **Personne d'autre que l'installateur PV ne touche** aux parafoudres AC et DC du coffret PV, aux disjoncteurs DC ni aux connecteurs MC4. Les chaînes sont sous tension dès qu'il fait jour, **plusieurs centaines de volts continus** : tension mortelle. Ouvrir les disjoncteurs DC ne met pas les chaînes hors tension, un arc en courant continu ne s'éteint pas seul, et un MC4 ne se débranche jamais en charge. La batterie de l'onduleur (plus de 100 V continus [DS?]) est au-delà de la TBT, avec un très fort courant de court-circuit : réservée à l'installateur.
3. **Charges figées.** Les relais bistables du BA mort sont restés dans leur dernier état. Couper au disjoncteur toute charge restée sous tension (chauffage, pompe).
4. **Essais d'isolement à 500 V continu, avant toute remise sous tension :**
   - transformateur externe, primaire ↔ secondaire ;
   - BP : toutes les bornes 230 V reliées ensemble (PH_FP comprise) contre toutes les bornes TBT reliées ensemble (J3, J31, J56-3, blindage RJ45) ;
   - (v2) **les trois BA, et non le seul BA mort** : voir §3.5, test n° 14. Le courant d'équilibrage a traversé tout le bus, et les BA d'apparence saine ont subi la même contrainte. **Commencer par le SC941C**, qui dessert les salles de bains. Une valeur inférieure à 10 MΩ interdit la remise en service de la carte ;
   - circuits extérieurs (terrasse, annexes, arrosage, sirène) : au moins 0,5 MΩ, mesure faite par l'électricien au tableau ;
   - (v2) à la remise sous tension, l'électricien refait la mesure 0 V–PE en LoZ du point 1.
5. **Mode de travail recommandé pour les étapes E0 à E2 :**
   - tout le 230 V consigné, transformateur débranché ;
   - BP alimenté par une **alimentation de laboratoire flottante** de 22 à 24 V continu, limitée à 1,5–2 A, sur J56-1/J56-2 (entrée du pont, la polarité est indifférente). Autre point d'injection possible : +24 V (C13+) et J56-3.
   - En dessous d'environ 20 V, le BP pourrait se croire sur batterie et couper +15VSP au bout de 12 s [HYP, seuil non vérifié].
   - La logique des BA n'a besoin que du +15VSP. Les commandes de test font coller les relais à vide, et l'index 12 se met quand même à jour.
6. **Oscilloscope.** S'il est relié à la terre, sa pince de masse va **uniquement** sur GND (J31-3 ou J1-3), jamais sur GNDISOFP ni GNDISOTI. Tant que l'isolement n'est pas vérifié, utiliser un oscilloscope sur batterie ou une sonde différentielle.
7. **Ne pas sonder les broches de J31/J1 avec des pointes nues.** La broche 4 (+15 V, sans fusible) est voisine de la broche 2 (SCL) [VU, symbole 2×2 : 1-3 / 2-4]. Un glissement de pointe met 15 V sur SCL et recrée la panne. Mesurer plutôt :
   - avec un connecteur femelle 3 mm aux fils sertis et repérés ;
   - ou sur les points de test : JT10/JT11, pastilles de R155/R156, cathodes de D33/D34 au BP ; cathodes de D1/D2 et pastilles de R1/R2 sur un BA.
8. (v2) **Couper le cuivre entre l'installation PV et le réseau local**, sans attendre le diagnostic :
   - avant, vérifier sur l'afficheur de l'onduleur ou dans son portail de supervision qu'il n'y a aucune alarme d'isolement ou de défaut de terre. Si le port de communication a été endommagé, l'isolement de cet onduleur sans transformateur n'est plus garanti (risque faible, mais pas nul) ;
   - débrancher le câble Ethernet du dongle de supervision de l'onduleur **côté switch**, en tenant la fiche par son corps, sans toucher en même temps une masse métallique. L'étiqueter et ne pas le rebrancher en cuivre ;
   - si le dongle est vivant, le passer en **Wi-Fi** (application du fabricant de l'onduleur) avec une réservation DHCP. Son adresse changera : mettre à jour la configuration de la supervision de l'onduleur (via un ticket) ;
   - l'absence du point d'accès Wi-Fi du dongle ne prouve rien : il peut avoir été désactivé après la mise en service.

### 3.1 E0 : observation, porte du tableau ouverte, sans rien toucher

| Indice | Lecture | Interprétation |
|---|---|---|
| LED DL1 de chaque BA | Bref éclair environ toutes les secondes quand le PIC tourne [VU `gestionsorties.c:15-30`, appel actif ligne 224] | **Toutes éteintes** : +15VSP perdu (T32, L31, J58, ou court-circuit sur un BA). **Seule celle du BA mort éteinte** : ce BA n'est pas alimenté ou son PIC est arrêté. C'est le cas le plus probable |
| Index 12 (`system.comm_faults`) | Bits 0x04 = PDV (0x11, SC940D), 0x08 = CHB (0x12, SC942C), 0x10 = PDE (0x13, SC941C). La valeur 28 signifie que les trois sont en défaut [VU] | Ne se met à jour qu'**après une commande** vers le BA concerné. Utiliser des éclairages, pas les volets |
| Composants visibles | TVS fendues ou noircies, L31, broches de J31/J1/J2, VDR des variateurs, relais | Indique la porte d'entrée de la surtension |
| (v2) Fenêtres « ÉTAT » des 3 BA et LED « TÉLÉINFO » du BP | Visibles capot fermé [VU ph. 3]. **Filmer 10 s** : une photo ne saisit pas l'éclair bref de DL1 | Identifie le BA défaillant sans ouvrir. Téléinfo fixe : MCF vivant et TIC bonne ; clignotante : défaut TIC [VU `client-essensys-legacy/docs/embedded-client/architecture.md:193`]. LED verte du RJ45 : PHY vivant |
| (v2) Voyants du coffret PV et du tableau | Parafoudre AC et parafoudres DC du coffret PV, cartouche et manette du parafoudre de tête, afficheur et LED de l'onduleur, LED du dongle, LED des ports du switch | Photographier de face, avec et sans flash, avant toute intervention |
| (v2) Horodatages, avant expiration des historiques | Contrôleur du réseau (dernier « seen » du dongle, « port down », compteurs d'erreurs des ports du dongle et du BP) ; passerelle Essensys : journal du service de supervision de l'onduleur, `ts` des derniers messages MQTT retenus de la supervision de l'onduleur, historique court (48 h) ; portail de supervision de l'onduleur (dernière donnée, journal des défauts) ; serveur Essensys (dernière commande BA réussie) ; historique du compteur communicant | Établit si le parafoudre AC, le dongle et la panne I2C datent du même événement. À croiser avec les données de détection de la foudre |

### 3.2 E1 et E2 : isoler la carte fautive par débranchement (tout consigné à chaque manipulation)

(v2) **Ordre du chaînage sur ce site** [VU ph. 1, 3] : BP-J31 → SC942C (J2, puis J1) → SC941C (J2, puis J1) → SC940D (J2 ; J1 libre). Le connecteur du bas d'un BA (J2) reçoit le câble qui vient du dessous ; le connecteur du haut (J1) part vers le BA du dessus. Si le SC940D est le BA mort, retirer le câble entre le J1 du SC941C et le J2 du SC940D ; ensuite SC941C ↔ SC942C, puis SC942C ↔ BP.

1. **Retirer entièrement** le câble qui va au BA mort, des deux côtés (côté BA précédent, c'est son J1 sur ce site). Ne laisser aucun bout de câble branché d'un seul côté. **Règle générale : un BA non alimenté ne doit jamais rester sur le bus.**
2. Remettre sous tension : de préférence selon le §3.0.5, sinon après avoir refermé le tableau. Envoyer une commande à chacun des deux BA restants, puis relire l'index 12.
   - **S'ils répondent**, le BA mort tenait le bus. Le service est en partie rétabli, et la suite peut se faire à l'établi.
3. Sinon, retirer le BA suivant, et ainsi de suite jusqu'à avoir le BP seul (§3.4).
4. Rebrancher depuis le BP **un BA à la fois**, en mesurant SDA/SCL au repos par rapport au rail +5 V local (critère du §3.7). Le BA qui fait chuter le niveau ou bloque les échanges est la carte fautive.

**Critère de repos, en relatif.** Le +5 V réel varie de 4,83 à 5,03 V selon la tolérance du LMR12010 [DS]. On mesure donc l'écart ΔV = V(+5 V local) − V(ligne) :

| ΔV au repos | Interprétation [DÉDUIT] |
|---|---|
| ≤ 40 mV | Lignes libres. Si les BA ne répondent toujours pas, c'est un NACK : U19 bloqué, PIC hors service. Passer à l'oscilloscope |
| 40 mV à 0,5 V | Fuite d'environ ΔV / 769 Ω, de 50 µA à 0,6 mA : TVS fatiguée |
| Ligne entre 0,6 et ≈ 3 V | BA non alimenté qui réalimente son PIC par ses diodes, ou forte fuite |
| Ligne ≈ 0 V | Court-circuit franc : TVS, U19 côté 2 ou RC6/RC7 d'un PIC |

### 3.3 Console « Espion » du BP (optionnelle, mais très utile pour départager NACK et bus bloqué)

- **Elle est compilée dans le firmware de production.** Le `.xMAP` de 099-37 (configuration `Int_Flash_Debug`) contient les symboles `vd_EspionRS_*` [VU].
- **Matériel :** sortie sur l'UART2, broches 101/102. **Il faut souder R109/R110 (68 Ω) et J102**, qui ne sont pas montés [VU p.5].
  - Niveaux : TTL 3,3 V.
  - Débit : 9600 8N1 d'après le BSP essensys-gcc [VU `m52259evb.h:363`]. Le BSP de production n'est pas disponible pour confirmer.
  - Adaptateur USB-série : de préférence isolé.
- **Activation :** taper le mot de passe d'activation défini dans le source (constante `uc_ESPION_MOT_PASSE_ACTIVATION`, `EspionRS.c`).
- **Navigation :** `m`, puis `2`, puis :
  - `0` : statistiques MQX (`Tx naks`, `Tx lost arb`) ;
  - `3` : masques `ErreursDialogueBA` ;
  - `5` : compteurs `NbBlocageI2C` et `While_x TimeOut`.
- **Remise à zéro :** menu `3`.

| Constat | Interprétation |
|---|---|
| `CHK 0x0002` sur les trois BA, `Tx naks` qui monte, aucun blocage | Lignes hautes mais personne n'acquitte : U19 bloqué, liaison coupée, PIC hors service |
| `NbBlocageI2C` et `TimeOut` qui montent | Une ligne est tenue basse |
| Erreurs sur un seul BA | Le bus est sain, le défaut est local à ce BA |
| Erreurs de CRC ou de code (0x0080 / 0x0100 / 0x0400) | Signal dégradé, pas de court-circuit franc |

### 3.4 BP déposé à l'établi

**Hors tension, batterie débranchée**

| Mesure | Valeur saine | Défaut et suite |
|---|---|---|
| Cathode de D34 (BA_SDA) ↔ pastille +5VS de R155 | ≈ 1,0 kΩ | Ouvert : L32 fondue ou R155 |
| Cathode de D33 (BA_SCL) ↔ pastille +5VS de R156 | ≈ 1,0 kΩ | Ouvert : L30 ou R156 |
| Continuité de L30, L32, L31 | < 1 Ω (L31 < 0,1 Ω) | — |
| Mode diode, + sur GND, − sur la cathode de D34 puis de D33 | 0,55 à 0,70 V | ≈ 0 : TVS, ou U19 broches 5/6. **Lever une patte de la TVS** pour départager |
| JT11 / JT10 ↔ +3V3S | ≈ 4,7 kΩ (R158 / R157) | — |
| JT10/JT11 → GND en mode diode | Comparaison avec JT12–JT15 | Peu concluant tant que U19 et R157/R158 sont en place : n'en tirer une conclusion qu'avec U19 dessoudé, sinon se fier à l'oscilloscope |
| +15VS, +5VS, +3V3S, BA_ALIM ↔ GND | Pas de court-circuit | — |
| Entrées extérieures : SMAJ16A D59–D62, BAT54S des entrées pluie et vent | Pas de court-circuit | Un court-circuit ici désigne la porte d'entrée de l'énergie |
| (v2) J32 : résistance entre les broches 1 et 3 (deux paires différentes), à l'ohmmètre | ≈ 150 Ω (deux résistances Bob Smith de 75 Ω en série par la prise médiane) [DÉDUIT, 75 Ω DS?] | Circuit ouvert : résistances Bob Smith fondues, donc un courant de 10 A ou plus est passé par l'Ethernet (H-PV confirmée). Comparer avec un autre RJ45 du même modèle si possible |
| (v2) J32 : isolement à 500 V continu, les huit contacts reliés ensemble contre GND, puis le blindage contre GND (C63) | > 100 MΩ | Valeur basse : condensateur Bob Smith interne ou C63 percé, le câble se retrouve en liaison galvanique sur le 0 V : remplacer J32 (Würth 74990101210) ou C63. Ne pas dépasser 500 V. Inspecter à la loupe J32, C63 et la piste de la broche 8 |

**Sous tension** : alimentation flottante de 22 à 24 V, rien de branché sur J31.

| Point | Valeur attendue | Défaut et suite |
|---|---|---|
| +15VS / +5VS / +3V3S | ≈ 15,2 V / 4,83–5,03 V / 3,3–3,4 V | — |
| BA_ALIM (pastille J31 de L31) | ≈ 15 V | 0 V : T32/T33, cavalier J58, L31, ou BP qui se croit sur batterie (§3.0) |
| +12VSP | ≈ 12,1 V | Hors service : U16, exposé par conception (B4) |
| Cathodes de D34 et D33 | ΔV ≤ 40 mV par rapport à +5VS | Fuite de ΔV / 1 kΩ ; ≈ 0 V : court-circuit |
| U19 broche 2 (VREF1) | 3,3 V | — |
| **U19 broches 7/8 (EN = VREF2)** | **3,6 à 4,4 V** | **≈ +5VS** : transistor de référence ouvert. L'interrupteur reste **passant mais sans limitation de niveau** : le côté µC peut monter vers 4,3 V, au-delà des 4,0 V max du MCF. Mesurer alors JT10/JT11 au repos : au-dessus de 3,5 V, remplacer U19 tout de suite et contrôler les broches 28/29. **< 1 V (≤ 3,3 V)** : interrupteur bloqué, NACK sur tous les BA (U19 ou C87 en court-circuit) |
| U19 broches 3/4 puis 5/6 | 3,3 V puis +5VS | — |

**Test fonctionnel de U19.** Passer par le connecteur d'interface, avec BA_ALIM non raccordé.
1. Relier SDA du connecteur à GND : R155 limite le courant à 5 mA. JT11 doit descendre sous 0,1 V, puis remonter à 3,3 V quand on relâche.
2. Même chose avec SCL : c'est JT10 qui doit descendre.
3. Sens inverse : JT11 à GND, la cathode de D34 doit descendre sous 0,1 V.
4. Un sens qui ne passe pas indique un canal ouvert.

**Oscilloscope, BA débranchés, à l'envoi d'une commande :** on doit voir START, 0x22, NACK, STOP à 50 kHz, avec un niveau bas inférieur à 0,6 V. Si JT10/JT11 restent muets, le problème vient du MCF (broches 28/29) ou du BSP.

**Avant toute retouche lourde du BP :**
- sauvegarder la flash par BDM ;
- l'image de production existe : `essensys-board-SC944D/SC944D/Prog/099-37/BP_MQX_ETH 20170116 save 099-37.elf_BOOT_CRC.S19` [VU] ;
- en cas de remplacement du MCF, flasher ce `.S19` et **jamais un nouveau build**. Le BSP I2C modifié (avec timeouts) est perdu, et un rebuild réintroduit 5 boucles d'attente infinies [VU rapport FW].

### 3.5 BA mort déposé à l'établi

Tout est débranché, y compris J3 et les borniers. Désignateurs donnés pour le SC940D (voir le tableau du §2.2 pour les autres). **Toujours comparer à un BA sain, dans la même polarité.**

| # | Mesure | Valeur saine | Défaut et suite |
|---|---|---|---|
| 1 | J1-1 (SDA) ↔ +5 V, **pointe + sur +5 V** | ≈ 10 kΩ (R40) | Ouvert : R1 fondue ou piste coupée. Nettement plus bas qu'un BA sain : fuite du PIC |
| 2 | J1-2 (SCL) ↔ +5 V, même polarité | ≈ 10 kΩ (R41) | Idem avec R2 (R3 sur SC941C) |
| 3 | J1-1 ↔ J1-2 | **≈ 20 kΩ** (R40 + R41 par le rail +5 V) | < 15 kΩ : carbonisation ou PIC |
| 4 | Mode diode, + sur J1-3, − sur J1-1 puis J1-2 | 0,55 à 0,70 V | < 0,1 V : court-circuit |
| 5 | Mode diode, + sur J1-1/J1-2, − sur J1-3 | OL, ou 1 à 1,6 V | < 0,3 V : court-circuit |
| 6 | Localiser un court-circuit : dessouder R1 (SDA) ou R2 (SCL) | — | Côté connecteur : D1/D2. Côté PIC : RC7/RC6 |
| 7 | « +12V » (cathode de D3) ↔ GND | **≈ 0,8 kΩ** (20 à 22 diviseurs TOR de 10 k + 6,8 k : 0,84 / 0,76 / 0,80 kΩ) | < 10 Ω : C2, U1 ou D6 |
| 8 | J1-4 ↔ J1-3 | À comparer à un BA sain. La lecture dépend de la tension d'essai de l'ohmmètre, à cause de D3 en série | < 10 Ω : FI1 ou court-circuit en amont de D3 |
| 9 | +5 V ↔ GND | Comparable à un BA sain | Court-circuit : soulever L2, puis chercher sur le PIC (VDD–VSS), C4, le NCP803 et le côté 5 V des SC943 |
| 10 | D3 en mode diode ; D6 avec + sur GND et − sur SW | D3 : 0,5–0,7 V en direct, OL en inverse. D6 : 0,15–0,30 V en direct, OL en inverse | ≈ 0 : diode en court-circuit |
| 11 | U1 : VIN–GND, SW–GND, BOOST–SW | Pas de court-circuit | U1 ou D6 |
| 12 | FI1 : traversée, puis entrée → GND | < 1 Ω, puis OL | — |
| 13 | Chaque entrée IN de J3 ↔ GND, en mode diode | Pas de court-circuit | TVS d'entrée claquée : l'entrée se comporte comme un bouton appuyé en permanence |
| 14 | **Isolement à 500 V continu**, carte nue : toutes les bornes 230 V reliées ensemble, contre **toutes** les broches TBT reliées ensemble (J1, J2, J3, ICSP). (v2) **Obligatoire sur les trois BA**, le SC941C en premier | > 100 MΩ | 10 à 100 MΩ : nettoyer, sécher, refaire l'essai. < 10 MΩ : **ne pas remettre la carte en service**. Un essai en continu ne révèle pas un amorçage en impulsion : inspecter aussi la zone J1/J2–K1 à la loupe (sur le SC940D : K1 « Entrée » et VR1) |
| 15 | Varistances des SC943 (Würth 820572711, 275 Vac) | — | Elles se dégradent sans trace visible : les **remplacer** sur le BA mort. Sur les autres, comparer leur fuite à celle d'une pièce neuve à 250 V continu, variateur isolé. Ne jamais tester une varistance 275 Vac à 500 V |

**Sous tension à l'établi.** Commencer par **un BA sain** pour obtenir la consommation de référence : aucune valeur fiable n'existe dans le dossier. Alimenter en 15,0 V sur J1-4 (+) et J1-3 (−), limite de courant à 50 mA, puis 150 à 200 mA.

| Point | Valeur attendue |
|---|---|
| Sortie de FI1 / cathode de D3 | 15 V / 14,2 à 14,4 V |
| Nœud SW de U1 | Découpage à environ 3 MHz, en salves à vide |
| +5 V après L2 | 4,83 à 5,03 V |
| MCLR | ≈ 5 V, au moins 140 ms après la mise sous tension |
| Oscillateur Q1 | 20 MHz (sonde ×10) |
| SDA/SCL au repos | ΔV ≤ 40 mV |
| LED DL1 | Un éclair environ toutes les secondes |

**Test de communication autonome.** Brancher un maître I2C 5 V (Arduino Uno ou Nano avec un scanner) sur J1-1/2/3. L'adresse **0x11, 0x13 ou 0x12** doit être acquittée [VU dans les .hex].

**Arbre de diagnostic :**

(v2) Commencer par les mesures n° 7 à 11 (alimentation) avant les n° 1 à 6 (I2C) : le mécanisme du fil +15 V (§0.3.2) détruit U1, C2 ou D6 dès environ 10 V d'écart de masse, sans toucher RC6/RC7.

1. L'alimentation passe en limitation et la tension s'effondre : chercher le point chaud (injection de 1 V sous 1 A, caméra thermique ou alcool) le long de FI1 → D3 → C2 → U1 → L1/D6 → C4/L2.
2. « +12V » présent, +5 V absent : U1, D6, L1, C3/D4.
3. +5 V bas avec un courant élevé : PIC, C4, NCP803, ADuM6201 des SC943.
4. +5 V correct mais LED éteinte : MCLR, Q1, PIC. Lire le PIC au PICkit : un identifiant illisible signifie que le PIC est mort.
5. LED qui clignote, mais aucun acquittement : RC6/RC7 endommagées, changer le PIC.
6. Le BA acquitte seul mais bloque le bus une fois câblé : D1/D2 fuient.

**Programmation du PIC :**
- MPLAB IPE et un PICkit, par le connecteur ICSP (J83 / J97 / J92), selon `essensys-board-SC940/SC940D/Prog/Fiche programmation SC940 v1.docx`.
- Fichiers : `ba v1_7 piece vie.hex`, `piece eau`, `piece chambre`. **Jamais** le build essensys-gcc : ses trois macros `TYPE_*` sont définies ensemble [VU].
- **Avant le remplacement**, si l'ancien PIC répond encore, lire son EEPROM (bit CPD à vérifier). Cela évite de tout reconfigurer à la main.

### 3.6 Pièces de rechange

| Repère | Monté [VU BOM] | À commander | Quand |
|---|---|---|---|
| D33, D34 (BP) ; D1, D2 (BA mort) | Vishay SMF5V0A-GS08 | **SMF5V0A-E3-08**. Le suffixe GS08 n'est plus dans le tableau de commande Vishay [DS] | Systématique sur le BP et sur le BA mort. Sur les deux BA sains : seulement si la fuite dépasse environ 10 µA par ligne (ΔV > 8 mV) ou si un dommage est visible. Déposer une carte saine, c'est environ 20 raccordements 230 V à refaire |
| U19 | PCA9306DCUT | PCA9306DCUR / DCUT (VSSOP-8, pas de 0,5 mm) | Si le test du §3.4 échoue. Fortement conseillé si D33/D34 ont claqué |
| L30, L32 / L31 | Würth 742792643 / 74279226101 | Idem, ou option du §4 | Si coupées |
| U16 (BP) | LD1117 (entrée 15 V max) | **LM317 en SOT-223** (même brochage ADJ/OUT/IN ; R66 = 115 Ω donne 10,9 mA de charge minimale) [DS?, à valider] | Recommandé pendant que le BP est ouvert |
| U4 (SC940D, SC941C) / U5 (SC942C) | PIC16F946-I/PT | Idem. **Approvisionnement tendu** : passer par Microchip en direct et constituer un stock | Si RC6/RC7 ou VDD sont en défaut |
| U1 | LMR12010YMK | LMR12010YMK/NOPB | BA mort |
| D3 / FI1 | GF1B / NFE31PT221D1E9L | Idem | Selon le diagnostic |
| D6 | PMEG2020AEA (20 V) | PMEG3020EJ (30 V) ou PMEG4010CEJ (40 V), en SOD-323F (empreinte à vérifier) | BA mort, puis à chaque dépose |
| C2 | 10 µF / 16 V 0805 | **10 µF / 35 V X5R**, en 0805 si disponible (par exemple Murata GRM21BR6YA106KE43 [DS?]), sinon 1206 | Idem |
| U3 (U4 sur SC942C), Q1, L2 | NCP803SN308T1G, quartz 20 MHz, 74279218 | Idem | Selon le diagnostic |
| Varistances des SC943 | Würth 820572711 | Idem | BA mort, systématique |
| (v2) J32 / C63 (BP) | Würth 74990101210 / 1 nF 2 kV | Idem | Si les tests de J32 du §3.4 échouent |
| (v2) Cartouche du parafoudre de tête | Cartouche enfichable de type 2 (Uc 275 V, In 5 kA, Imax 15 kA) | Même référence que la cartouche en place, environ 30 à 60 € [EST] | Par précaution, **par l'électricien uniquement** : manette du parafoudre sur O avant l'extraction |
| (v2) Parafoudre AC du coffret PV | Parafoudre de type 2 (Uc 320 V, Up ≤ 1,5 kV, Imax 15 kA), intégré à un ensemble de protection AC avec le disjoncteur C32 | Module enfichable ou ensemble complet (≈ 80 à 200 € [EST]), selon la notice | **Par l'installateur PV**. Conserver la pièce déposée |

### 3.7 Remise en service et réception

| Vérification | Critère |
|---|---|
| SDA/SCL au repos, tout branché, mesurés à J31 et au dernier BA | ΔV ≤ 40 mV par rapport au +5 V local |
| ΔVg entre J31-3 et J1-3 du dernier BA (le SC940D), relais monostables collés | (v2) Attendu : 0,06 à 0,16 V sans renfort, < 0,02 V avec N1 ou N2 (§2.3). **≤ 0,1 V : 47 Ω. > 0,12 V : poser N2 ou N1 avant de passer à 47 Ω, sinon 33 Ω.** Entre les deux : 47 Ω, et vérifier le niveau bas au MCF (< 0,85 V) |
| BA_ALIM au dernier BA | ≥ 14 V |
| Niveau bas BA → BP, mesuré au BP | < 0,85 V |
| **Niveau bas BP → BA, mesuré au PIC** | **< 1,2 V, mesure obligatoire**. Elle tranche la question de la sortance du port AS (§2.3) |
| Temps de montée de 0 à 3,45 V, au BA le plus éloigné | < 4 µs. **À noter** : cette valeur conditionne l'option P2 |
| Fonctionnement | Une commande vers chaque BA réussit, l'index 12 revient à 0, aucun blocage pendant 24 h |
| Isolement | Tests du §3.0.4 et §3.5 n° 14 réussis, **sur les trois BA et le BP** (v2) |
| (v2) Ethernet | Câble du dongle de supervision de l'onduleur débranché du switch ; Ethernet du BP isolé (fibre ou isolateur), ou à défaut décision tracée dans le ticket |
| **Configurations** | **Les renvoyer pour tous les BA**, pas seulement pour celui qui a changé de PIC. Le BP a abandonné et marqué acquittées les trames de configuration perdues pendant la panne [VU `ba.c:202-209, 313-316`]. Méthode : modifier chaque paramètre (modes des variateurs, temps d'extinction, temps des volets) puis revenir à sa valeur. Après un changement de PIC, les variateurs repartent en mode gradateur par défaut : à corriger pour les charges qu'on ne peut pas graduer |

Consigner toutes les mesures, elles serviront de référence au prochain événement. Tracer l'intervention dans un ticket Bug.

**Relancer les BA sans ouvrir l'armoire** [VU `Hard.c:879-945`, `global.h:50-51`] : couper le disjoncteur secteur du BP pendant **au moins 13 s** (20 s pour avoir de la marge). Le BP passe sur batterie, coupe +15VSP au bout d'environ 12 s, puis le **rétablit environ 1 s** après le retour du secteur.
- Prérequis : batterie présente, **cavalier J58 fermé** (à vérifier visuellement ; ouvert, +15VSP reste permanent), `Mode_Test` = 0.
- Effet de bord : les relais monostables retombent.

---

## 4. Protection à court terme, sans refaire de circuit imprimé

### 4.1 Tableau des priorités

| Prio | Action | Effet | Coût [EST] | Difficulté |
|---|---|---|---|---|
| P0 | Sécurité et essais d'isolement (§3.0), **sur les trois BA et le BP** (v2), diagnostic, réparation du BP et du BA mort, renvoi des configurations | Remise en service sûre | Pièces 10 à 30 € | Moyenne (VSSOP et TQFP au pas de 0,5 mm) |
| P0 | Remplacer D33/D34 et les D1/D2 du BA mort. Pour les autres BA, seulement si la fuite est mesurée | Supprime les courts-circuits et fuites latents | ≈ 2 € | Facile |
| P0 (v2) | **Débrancher l'Ethernet du dongle de supervision de l'onduleur** côté switch, passer le dongle en Wi-Fi (§3.0 n° 8) ; **horodater** l'événement (§3.1) | Coupe le seul lien métallique direct entre la zone PV et l'îlot du BP ; permet d'attribuer ou non une cause commune | 0 € | Facile |
| Parallèle (v2) | **Installateur PV** : remplacer le parafoudre AC du coffret PV, lire le journal de l'onduleur, contrôler le côté DC et l'équipotentialité (§4.6) | Rend au côté AC du PV son parafoudre local. **Non bloquant** pour la remise en service d'Essensys | Selon devis | Installateur PV |
| P1 | **R1/R2 du BA réparé : 0 Ω → 47 Ω anti-impulsion**. (v2) Critère conservé jusqu'à la mesure du §3.7 : 33 Ω, ou N2/N1 d'abord, si ΔVg > 0,12 V | Le courant n'est plus illimité : environ 20 à 140 mA selon l'écrêtage (§4.2). Survie probable du PIC, sans respecter son maximum absolu | 0,5 € | Facile |
| P1 | **BA_ALIM : PTC en amont, puis TVS** (§4.3) | Écrête les surtensions du +15 V ; une TVS morte n'arrête plus le BP | 3 à 8 € | Facile à moyenne |
| P1 | **U16 → LM317** (BP) ; **C2 en 35 V, D6 en 40 V, TVS après R79** (§4.3) sur **chaque BA déposé** (v2 : priorité relevée à cause du mécanisme +15 V, §0.3.2) | Supprime les composants hors marge en régime nominal ; relève la tenue du rail « +12V » | 2 à 3 € par carte | Facile |
| P1 (v2) | **Isolement de l'Ethernet du BP** : paire de convertisseurs fibre, celui du BP alimenté **depuis l'îlot TBTS** (12-24 V du BP ou alimentation TBTS flottante dédiée), ou isolateur Ethernet ≥ 4-6 kV. **Pas de parafoudre RJ45 relié au PE au BP** (§4.5) | Coupe le couplage par le Bob Smith de J32 | 60 à 200 € | Facile à moyenne |
| P1 (v2) | **N2 : étoile 0 V doublée** (§4.1 bis). À défaut ou en complément, **N1 : renfort 0 V** soudé au SC940D et au BP pendant leur dépose | Seuil d'équilibrage : 20 → 173 A en 8/20, 11 → 79 A en front rapide (N2) ; 20 → 97 A et 11 → 25 A (N1) | 30 à 60 € (N2), 10 à 30 € (N1) | Moyenne |
| P1 (v2) | **Contrôle du parafoudre de tête existant** (parafoudre de type 2 du tableau, voyant vert) par l'électricien : manette, alimentation en amont des ID, liaisons ≤ 50 cm, PE, terre ; cartouche remplacée par précaution ; essai des différentiels | Le parafoudre est présent : le v1 le croyait absent | 30 à 60 € + électricien | Électricien |
| P1 (v2) | **Cheminement** : bus et nappes éloignés des bornes Ph, avec manchon isolant là où ils les longent ; cordon Ethernet du BP sorti directement du coffret ; câbles PV (DC, batterie, AC, PE) à ≥ 30-50 cm du coffret domotique, ou en goulotte métallique reliée au PE aux deux bouts ; croisements à 90° | Réduit le couplage avec le 230 V et avec les courants de décharge du PV | 10 à 30 € + installateur | Facile à électricien |
| P2 | R1/R2 en 47 Ω sur les deux BA sains, **à leur prochaine dépose** | Même effet que ci-dessus | 1 € | Facile, mais dépose de la carte |
| P2 | **Option renforcée** (§4.4) : R155/R156 en 2,2 kΩ, L30/L32 remplacées par 47 Ω, BAT54S sur C79/C80 au BP ; 100 Ω et BAT54S sur C23/C25 (C24/C26, C27/C29) aux BA | U19 limité vers 5,8 V au lieu de 9 à 14 V ; courant dans le PIC nettement réduit ; meilleure marge BP → BA | 3 € | Moyenne (SOT-23 monté « en l'air ») |
| P2 | PTC propre à chaque BA + TVS sur +Vin (§4.3) | Une TVS de BA en court-circuit ne coupe que son BA | 2 € par BA | Moyenne |
| P1/P2 (v2) | Lignes qui sortent du bâtiment (§4.6) : départs 230 V extérieurs commutés (électrovanne, Terrasse et Annexes, Entrée/Annexe sur EDP4 si extérieurs, PAC) ; lignes TBT extérieures du J3 du BP **si elles existent** | Ferme les portes d'entrée. Parafoudres de type 3 conformes, **au départ dans le tableau électrique**, jamais dans le coffret domotique | 40 à 80 € par départ | Électricien |
| P2 | Alerte serveur sur `comm_faults` non vide | Détection rapide d'une panne | Développement, ticket | — |
| P3 | Ferrite à clipser autour **des 4 fils ensemble** | Fronts rapides seulement, presque rien en foudre | 2 à 5 € | Facile |

**Abandonné (voir §4.5 et l'annexe D) :** l'éclateur à gaz entre le 0 V et la terre ; (v2) le parafoudre RJ45 relié au PE au BP ; la varistance nue sur les départs extérieurs.

### 4.1 bis Abaisser l'impédance entre les cartes d'un même coffret (v2)

Ces deux mesures relient un 0 V à un autre 0 V, jamais au PE : elles sont **compatibles avec la TBTS**. Toute pose se fait sous consignation complète (§3.0), batterie du BP et installation PV comprises.

**N2 (recommandée). Étoile 0 V doublée, sans retouche de carte.**
- Petite carte passive de distribution sur rail DIN, au bord gauche du coffret, là où sont tous les J1/J2 [VU ph. 3]. Elle porte un plan 0 V.
- Chaque BA y est relié par **J1 et J2** : deux faisceaux AWG20 de 15 cm au plus, ce qui double les quatre conducteurs. Le BP y est relié par J31.
- Seuil d'équilibrage [DÉDUIT, §0.3.1] : environ 173 A en 8/20 et **79 A en front rapide**, contre 20 et 11 A aujourd'hui. C'est la seule mesure de court terme qui garde son efficacité quand le front raidit.
- On y loge aussi, par port, la PTC et la TVS du +15 V (règle du §4.3) et un cavalier pour retirer un BA mort du bus (règle du §3.2).
- Coût : 30 à 60 € [EST], plus un essai de banc. Elle ne demande ni firmware ni retouche des BA.

**N1 (complément ou solution d'attente). Renfort 0 V d'accompagnement.**
- Conducteur souple de 2,5 à 4 mm², isolé 450/750 V (H07V-K), **plaqué contre chaque tronçon du bus sur toute sa longueur** (collier tous les 5 cm). Le cheminement fait la moitié du gain : un renfort qui suit un autre chemin crée une boucle dont toute l'inductance apparaît entre le 0 V et SDA/SCL.
- **Point de raccordement sur une carte déposée** : une queue de cochon AWG20 soudée sur la **broche traversante J1-3 ou J2-3** (nœud GNDBUS), avec arrêt de traction, puis une jonction hors de la carte. Ne jamais souder un conducteur de forte section sur une pastille CMS : il l'arrache. Sur le SC940D, D1/D2 sont à 28-48 mm de J1/J2 : relier aussi leurs anodes au même point par un fil fin, sinon ces 30 à 50 nH de piste s'ajoutent. Au BP : anodes de D33/D34 et broche J31-3.
- **Variante sans retouche, dite dégradée** : J1 libre du SC940D (contact serti AWG20) vers la borne moins de la batterie du BP (J56-3 est bien le GND [VU SC944D p. 2]). Le courant entre alors par la batterie et traverse le plan de masse logique du BP jusqu'à J31, ce que le §5.7 interdit pour une carte neuve. Raccordement batterie déconnectée, avec des outils isolés (languettes Faston).
- Gain : facteur 2 à 5 selon la pente du front (§0.3.1). Coût : 10 à 30 € [EST].
- **Repérage** : dans ce coffret, le violet, l'orange, le marron, le gris, le rouge et le blanc servent déjà au 230 V [VU ph. 3]. La couleur ne suffit pas : manchons aux deux extrémités « 0 V TBTS – NE PAS RELIER À LA TERRE », jamais vert-jaune ni bleu clair, mention au dossier de l'installation.

### 4.2 R1/R2 : 47 Ω à la place des 0 Ω (P1)

**Pourquoi.** Aujourd'hui le PIC écrête seul et sans limite. Avec une résistance, la TVS prend l'essentiel du courant au-delà de son seuil, et le courant injecté dans le PIC est enfin borné.

**Courant injecté dans le PIC** [DÉDUIT]. La diode interne du PIC conduit toujours la première, vers 5,5 V :

| R série | TVS au seuil (6,4–7,1 V) | VC ≈ 12 V (onde 8/20, ≈ 50 A) | Polarité négative (TVS en direct, ≈ −2,5 V) |
|---|---|---|---|
| 0 Ω (actuel) | Non limité | Non limité | Non limité |
| 47 Ω | 19 à 34 mA | ≈ 140 mA | ≈ 40 mA, risque de latch-up |
| 100 Ω | 9 à 16 mA | ≈ 65 mA | ≈ 19 mA |

La limite absolue du PIC est de ±20 mA : **47 Ω seul ne suffit pas à la respecter**. Seul l'écrêteur secondaire de l'option P2 (BAT54S sur C23/C25) peut s'en approcher à court terme. (v2) Autrement dit, 47 Ω transforme une destruction quasi certaine en survie probable. Le seuil d'équilibrage du système reste fixé par les écrêteurs (≈ 20 A en 8/20 sur ce site), et non par la résistance ; seules l'étoile N2 ou le renfort N1 (§4.1 bis) le relèvent.

**Budget de niveau, sens BA → BP** (le MCF lit, seuil de 1,155 V, marge visée ≥ 0,3 V). Modèle au pire : PIC 70 Ω, U19 6 Ω.

| Configuration | ΔVg = 0 | ΔVg = 0,1 V | ΔVg = 0,25 V | Verdict |
|---|---|---|---|---|
| Actuelle | 0,46 V (marge 0,70) | 0,55 (0,61) | 0,69 (0,47) | Référence |
| **BA 47 Ω, pull-ups 1 kΩ** | 0,70 (0,46) | 0,78 (0,37) | 0,92 (0,24) | **P1 si ΔVg ≤ 0,1 V** |
| BA 33 Ω, pull-ups 1 kΩ | 0,63 (0,53) | 0,72 (0,44) | 0,85 (0,31) | P1 si ΔVg > 0,1 V |
| BA 100 Ω, pull-ups 1 kΩ | 0,94 (0,22) | 1,02 (0,13) | 1,15 (0,01) | **Refusé** |
| BA 47 Ω + BP 47 Ω, pull-ups 1 kΩ | 0,88 (0,27) | 0,97 (0,19) | 1,09 (0,06) | **Refusé** |

(v2) **Lecture sur ce site.** ΔVg attendu au SC940D : 0,06 à 0,16 V sans renfort, < 0,02 V avec N1 ou N2 (§2.3). Avec 47 Ω, la marge vaut 0,37 V à 0,1 V et environ 0,32 V à 0,16 V (interpolation), juste au-dessus de la cible de 0,30 V. Cet écart de 0,02 V repose sur un modèle au pire et un ΔVg non mesuré : **le critère est conservé**. ΔVg ≤ 0,1 V : 47 Ω. ΔVg > 0,12 V : poser N2 ou N1 d'abord (ΔVg < 0,02 V, marge 0,45 V), sinon 33 Ω. Entre les deux : 47 Ω avec vérification du niveau bas au MCF (§3.7).

**Sens BP → BA.** La résistance du BA ne porte alors que le courant de son propre 10 kΩ, soit 0,45 mA : P1 ne dégrade pas ce sens de façon notable. En revanche, cette marge n'est pas connue (§2.3), d'où la mesure obligatoire avant et après.

**Composant :** 0805 anti-impulsion, Panasonic ERJ-P06J470V ou Vishay CRCW080547R0FKEAHP (33 Ω : ERJ-P06J330V). L'énergie par impulsion vaut quelques dizaines de µJ, ce qui ne pose aucun problème.

**Méthode :** une carte à la fois, avec un test du bus après chacune.

### 4.3 Alimentation BA_ALIM / +VBUS (P1 et P2)

**Règle de topologie.** Une TVS d'alimentation finit en court-circuit. Elle doit donc toujours se trouver **en aval** d'un élément qui l'isole quand elle claque, et cet élément doit être **propre au nœud** qu'elle protège.

- **Côté BP (P1).** Deux solutions au choix :
  - (a) remplacer **L31** (empreinte 1812) par une **PTC CMS ≥ 30 V**, par exemple Littelfuse 1812L110/33 [DS?, à sélectionner], et souder une **SMAJ16A** (déjà dans la BOM du BP) entre J31-4 (cathode) et J31-3, côté soudure. La PTC se trouve ainsi en amont de la TVS.
  - (b) installer un petit module sur rail DIN entre J31 et les BA : fil +15 V → PTC Bourns MF-R1xx → TVS (SMAJ16A, ou P6KE18A axiale) vers le fil 0 V → départ vers les BA.
  - **Dimensionnement de la PTC :** courant de maintien à la **température du tableau** ≥ 1,5 × le courant de BA_ALIM **mesuré** avec les relais monostables collés. Le MF-R110 tient 1,10 A à 23 °C, environ 0,91 A à 40 °C et 0,85 A à 50 °C [DS] : prendre un MF-R135 ou MF-R160 si nécessaire.
  - Pendant le déclenchement, il faut s'attendre à un redémarrage du BP.
  - Ne pas enfermer une PTC sous gaine thermorétractable au contact d'autres conducteurs : elle chauffe à plus de 100 °C quand elle déclenche.
- **U16 → LM317** : la SMAJ16A écrête entre 19 et 26 V, au-delà des 15 V tolérés par le LD1117.
- **Côté BA (P2 ; v2 : P1 sur chaque BA déposé, à cause du mécanisme du fil +15 V, §0.3.2) :**
  - TVS **après R79**, sur les pastilles de **C40** (220 pF non monté, entre +Vin et GND [VU]). Une SMF16A (VC 26 V à 7,7 A [DS]) en boîtier DO-219AB peut y tenir, boîtier de C40 à vérifier ; sinon une SMAJ16A avec des fils courts.
  - **R79 (0 Ω) remplacée par une PTC CMS ≥ 30 V** propre au BA, référence à choisir.
  - **Ne jamais poser la TVS sur +VBUS, en amont de R79.** C'est le nœud de chaînage partagé (J1 ∥ J2) : une TVS morte y couperait les trois BA.
- **Limite assumée [DÉDUIT].** Au courant crête, la tension monte jusqu'à environ 26 V, soit environ 25 V après D3. Cela dépasse la tenue du LMR12010 (VIN 24 V abs, **BOOST 30 V abs**, alors qu'on atteint SW + 5 V ≈ 30 V) et frôle FI1 (25 V). D'où :
  - **C2 en 35 V et D6 en 30–40 V** (v2 : 40 V retenu) ;
  - une protection qui reste partielle.
  - Option pour le BA réparé, **à valider au banc** : LMR16006 (4–60 V), même ordre de broches en SOT-23-6 [VU, rapport composants]. Points à revoir :
    - VFB ≈ 0,765 V [DS?] : R4 ≈ 8,66 kΩ pour retrouver 4,93 V ;
    - fréquence : 0,7 MHz en version X, 2,1 MHz en version Y ;
    - courant max de 0,6 A au lieu de 1 A ;
    - circuit de bootstrap.

### 4.4 Option renforcée P2, après relevé à l'oscilloscope

1. **BP :** R155/R156 de 1 kΩ passent à **2,2 kΩ** (CRCW06032K20FKEA).
   - Courant à l'état bas : 6,4 mA → 3,9 mA.
   - Temps de montée multiplié par 1,72.
2. **BP :** L30/L32 sont remplacées par des **47 Ω** 0603 anti-impulsion (ERJ-P03J470V).
3. **BP :** une **BAT54S montée « en l'air »** sur chacune des empreintes C79 (SDA) et C80 (SCL), qui sont côté U19 [VU] :
   - anode basse sur la pastille GND ;
   - point commun sur la pastille de la ligne ;
   - cathode haute reliée à +5VS par un fil court, sur la pastille haute de R155/R156.
4. **BA :** même montage sur **C23/C25** (C24/C26 sur SC941C, C27/C29 sur SC942C), côté PIC après R1/R2 [VU]. Cathode reliée au +5 V, sur la pastille haute de R40/R41. R1/R2 passent à **100 Ω** si ΔVg ≤ 0,1 V, sinon restent à 47 Ω.

**Calcul, avec VC = 12 V** (valeur réaliste en onde 8/20, et non 9,2 V) [DÉDUIT] :
- **Positif :** (12 − 5,7) / 47 ≈ 135 mA dans la Schottky. U19 reste vers **5,8 V**, sous ses 7 V. La BAT54 tient environ 600 mA en surcharge brève [DS?].
- **Négatif :** (2,5 − 0,6) / 47 ≈ 40 mA. U19 se retrouve vers −0,6 V (−0,5 V toléré si le courant reste ≤ 50 mA). **Une injection négative résiduelle d'environ −0,5 V subsiste sur les broches 28/29 du MCF**, dont la limite est −0,3 V : c'est faible, mais à connaître.
- **Rail d'alimentation.** Un régulateur (LMR12010, LD1117) n'absorbe pas de courant entrant. Le courant injecté est absorbé par la consommation du rail et par C4 : une impulsion de 0,15 A pendant 20 µs dans 10 µF fait monter le rail d'environ 0,3 V. Acceptable pour une impulsion brève.
- **Effet de bord sur les BA :** un BA non alimenté tirera le bus un peu plus fort (Schottky). Raison de plus pour ne jamais le laisser branché.

**Budget avec 2,2 kΩ** (BA 100 Ω + BP 47 Ω) : le MCF lit 0,72 / 0,81 / 0,94 V pour ΔVg = 0 / 0,1 / 0,25 V. Le sens BP → BA s'améliore aussi, car le courant baisse.

**Condition d'application, d'après le temps de montée mesuré aujourd'hui (pull-ups 1 kΩ, de 0 à 3,45 V) :**

| Temps mesuré | Action |
|---|---|
| ≤ 2,3 µs | 2,2 kΩ |
| 2,3 à **2,97 µs** | 1,5 kΩ, avec 47 Ω côté BA et côté BP |
| Au-delà | Rester en P1 |

Après la modification, refaire tous les relevés du §3.7.

### 4.5 À ne pas faire

- **Monter L3 seule ou retirer R79/R80.** Le retour de SDA/SCL passe par GNDBUS. L3 y ajouterait environ 314 Ω à 50 kHz, ferait rebondir la masse et pousserait le mode commun dans D1/D2. C'est sans doute la raison de la modification DM de 2017.
- **Mettre 100 Ω côté BA avec les pull-ups de 1 kΩ**, ou ajouter une résistance côté BP sans changer les pull-ups (§4.2).
- **Monter des TVS 5 V « plus puissantes »** (SMBJ5.0A, SMF4L5.0A) : leur fuite peut atteindre 800 µA, soit environ 2,5 V perdus sur le niveau haut [DS].
- **Monter C23/C25 en condensateurs.** Avec 47 à 100 Ω, la constante de temps n'est que de 1 à 2 ns, sans effet contre la foudre. Ces empreintes servent mieux à la BAT54S.
- **Éclateur à gaz (GDT) entre le 0 V et la terre.** Abandonné :
  - en fin de vie, il se met en court-circuit et relie le 0 V à la terre, ce qui fait passer de fait en TBTP, contraire à la NF C 15-100 §414 ;
  - le SC941C dessert des salles de bains, et la §701 n'y admet que la TBTS en volumes 1 et 2 [à confirmer avec l'électricien] ;
  - il ne protège pas les ports I2C (amorçage à plusieurs centaines de volts) ;
  - il crée une boucle masse du bus / barrette de terre.
- **Reflasher le BP avec un nouveau build**, ou **flasher un BA avec le build essensys-gcc**.
- (v2) **Poser un parafoudre RJ45 relié au PE au BP**, ou au PE du coffret PV voisin. Lors d'une montée du PE de la zone PV, il porterait les paires Ethernet au potentiel de ce PE et injecterait directement, par J32 (1,5 kV) et le Bob Smith, dans le 0 V de l'îlot : un nouveau chemin, ouvert pendant l'événement même qu'on redoute. Si le switch doit être protégé, poser le parafoudre **à l'extrémité du dongle de supervision de l'onduleur**, relié au PE de l'onduleur, ou mieux, supprimer le cuivre (Wi-Fi, fibre).
- (v2) **Amener un conducteur PE dans le coffret domotique** (classe II, TBTS), à côté d'un renfort 0 V ou d'une tresse : un intervenant finira par les relier, et l'on passe en TBTP de fait (§414, §701). Si un câble Ethernet blindé arrive au BP avec un écran relié au PE, un C63 percé suffit à créer la même liaison : câble non blindé, ou écran non raccordé côté BP.
- (v2) **Poser une varistance nue** sur une sortie 230 V. Ce n'est pas un parafoudre au sens de la NF EN 61643-11 : ni déconnecteur thermique ni protection de secours ; en fin de vie, elle passe en court-circuit avec emballement thermique (risque d'incendie dans un coffret plastique). Posée aux borniers d'un BA, elle ferait de plus entrer le courant de choc dans le coffret, à quelques centimètres de la TBT.
- (v2) **Faire passer un renfort 0 V par un autre chemin que le câble de bus** (§4.1 bis), ou le relier au PE.

### 4.6 Installation (électricien)

| Mesure | Détail |
|---|---|
| Parafoudre de tête | (v2) **Présent** : parafoudre de type 2 du tableau, bipolaire, déconnecteur intégré, cartouche Uc 275 V, In 5 kA, Imax 15 kA, Up ≤ 1 kV en L-N, voyant vert [VU ph. 4]. À **contrôler** : manette du déconnecteur sur « I » (une fenêtre verte ne suffit pas si le déconnecteur a ouvert) ; l'éclateur N-PE n'a pas de voyant ; alimentation **en amont de tous les ID 30 mA** (par câble depuis l'AGCP, et non par le peigne de l'ID type AC de la rangée 4) ; **règle des 50 cm** ; section du PE (valeur selon l'édition de la norme appliquée [DS?]) ; terre (régime TT) et liaisons équipotentielles ; identité de l'appareil de tête (AGCP de type S ?). Remplacer la cartouche par précaution : une varistance vieillit sans faire basculer son voyant [DS?]. Type exigé : **type 1 si paratonnerre** ; parafoudre obligatoire, de type 2 au minimum, si alimentation aérienne en zone AQ2 (NF C 15-100, édition à préciser : 2002 + A5 ou 2024) |
| Second parafoudre (type 3) | (v2) **Sans objet** pour l'équipement Essensys : le coffret domotique est accolé au tableau, à moins de 2 m du parafoudre de tête [VU ph. 5, 7] |
| Câble de bus | (v2) Les tronçons font déjà environ 33 cm [VU]. Sur cette longueur, les contacts (2 × 20 mΩ) pèsent autant que le fil : l'AWG20 n'apporte qu'un facteur 1,4. Le levier est l'impédance entre cartes (N2, N1, §4.1 bis). Garder un câble souple serti à l'outil ; vérifier le nombre de fils par contact ; les isolants d'un câble cat. 5e **ne sont pas prévus pour côtoyer le 230 V** (NF C 15-100 §528) : manchon isolant ou éloignement des bornes Ph |
| Ethernet | (v2) **Isolement**, pas parafoudre : dongle de supervision de l'onduleur en Wi-Fi ; Ethernet du BP en fibre (convertisseur côté BP alimenté depuis l'îlot TBTS, sinon un bloc classe II recouple le BP au réseau par ses capacités Y) ou par un isolateur ≥ 4-6 kV. **Pas de parafoudre RJ45 relié au PE au BP** (§4.5). Box en cuivre : protéger l'arrivée télécom à l'entrée du bâtiment. Faire sortir le cordon du BP directement du coffret, loin des nappes |
| Switch réseau | (v2) Relever le modèle, l'alimentation (bloc 2 broches ou relié au PE), les compteurs d'erreurs de tous les ports ; remplacer le switch si des ports sont dégradés ; vérifier les équipements PoE extérieurs (caméras, points d'accès), autre porte d'entrée possible |
| Lignes TBT extérieures (pluie, vent, sirène, sur J3 du BP) | (v2) **Probablement sans objet** : la fenêtre J3 du BP semble vide [VU ph. 5, à confirmer]. Si elles existent : préférer un isolement de ces lignes (interface à relais ou optocoupleur ≥ 4 kV), ou des parafoudres à défaillance « ouverte », car un parafoudre à éclateur vers le PE en court-circuit en fin de vie fait passer l'îlot en TBTP (même raison que le §4.5). À valider avec l'électricien |
| Départs 230 V extérieurs | (v2) Lignes identifiées [VU ph. 5] : électrovanne (sortie du BP, disjoncteur de l'électrovanne d'arrosage), Terrasse et Annexes (SC941C), Entrée et Annexe sur EDP4 (le luminaire « Entrée » de K1 du SC940D est-il extérieur ?), PAC extérieures 1 à 3. Parafoudre modulaire de **type 3** conforme NF EN 61643-11 (voyant, déconnecteur thermique), coordonné avec le parafoudre de tête selon le fabricant, **au départ dans le tableau électrique** ou côté charge extérieure, **jamais dans le coffret domotique**. Il couvre le cas du relais ouvert. Interconnecter les terres si une annexe a la sienne |
| (v2) Installation photovoltaïque (installateur, habilitation selon NF C 18-510) | Informer l'installateur PV, au titre de la garantie. Remplacer le parafoudre AC du coffret PV (le côté AC du PV n'a plus de parafoudre local d'ici là) et faire justifier son calibre (Imax 15 kA, contre 40 kA côté DC). Lire le **journal de l'onduleur** : heure, alarmes SPD, résistance d'isolement, défaut de terre ; état des parafoudres internes de l'onduleur [DS?]. Contrôler ou remplacer préventivement les parafoudres DC et mesurer l'isolement des chaînes. Vérifier le **type de l'interrupteur différentiel** 300 mA (symbole illisible ; un onduleur sans transformateur demande en général un type A, voire B [DS?]) et le Ue des disjoncteurs DC (« 500 V⎓ » [VU ph. 8]) face au Voc maximal des chaînes par temps froid. **Équipotentialité** : conducteur des cadres ≥ 6 mm² Cu (16 mm² avec paratonnerre [DS?]), même borne principale de terre que le parafoudre de tête, connexions des parafoudres ≤ 50 cm, + et − de chaque chaîne côte à côte avec le conducteur d'équipotentialité. Faire justifier l'absence d'un parafoudre DC côté modules selon la longueur critique (guide UTE C 15-712-1, Lcrit = 115/Ng, soit ≈ 40 à 75 m pour Ng de 1,5 à 3 [DS?]). Câbles PV à ≥ 30-50 cm du coffret domotique. Contrôle visuel ou thermographique du parafoudre AC : en cas d'odeur ou de décoloration, ouverture du disjoncteur C32 par une personne habilitée |
| Inventaire | Bouton test de chaque différentiel 30 mA, voyants des parafoudres (tableau, AC et DC du coffret PV), autres appareils touchés (box, ports du switch du BP et du dongle, compteur d'énergie associé à l'onduleur et liaison BMS de la batterie s'ils existent) |
| (v2) Conservation des pièces et des traces | Conserver le parafoudre AC déposé, le dongle, les cartes et pièces déposées, les photos horodatées, les journaux. Les données d'un réseau de détection de la foudre sur la fenêtre horaire tirée des journaux (attestation de foudroiement, ≈ 30 à 100 € [EST]) recoupent l'heure de l'événement. Informer l'installateur PV |

---

## 5. Solution long terme

### 5.1 Principe

**Écrêter plus fort ne supprime pas le chemin.** Il faut **couper la boucle galvanique entre les îlots, en isolant les données ET l'alimentation ensemble**, et rendre l'installation équipotentielle.
- Isoler l'I2C sans isoler l'alimentation ne sert à rien : le courant continue de passer par GND et +15 V.
- **On garde la TBTS**, à cause des salles de bains desservies par le SC941C. Aucune liaison galvanique entre le 0 V des cartes et la terre. Les écrans de câbles vont au PE, mais jamais au 0 V.

(v2) **Ce que change le coffret unique.** Le principe se décline selon la géométrie :
- **à l'intérieur d'un coffret** : rendre les 0 V **équipotentiels à basse impédance** (ΔV entre cartes négligeable devant les seuils I2C) ;
- **à sa frontière** : **isoler ou protéger chaque port qui en sort**. Sur ce site, la première boucle à couper est **Ethernet ↔ îlot TBTS du BP** (seul port avec une liaison métallique directe vers des équipements potentiellement reliés au PE), avant la liaison BA ↔ BA ;
- **pour un BA déporté** (autre coffret, plus de 2-3 m, autre bâtiment) : l'isolement par BA du §5.2 reste la bonne réponse.

### 5.1 bis Coffret unique : carte d'interconnexion équipotentielle (recommandée sur ce site, v2)

| Critère | A. MIB par BA (§5.2) | B. Protection des ports à la frontière | C. **Carte d'interconnexion** (fond de panier) |
|---|---|---|---|
| Principe | Couper le chemin galvanique entre îlots | Réduire le courant capté à la source | Rendre la ΔV entre cartes négligeable devant les seuils I2C et d'alimentation |
| Effet chiffré [DÉDUIT] | Courant résiduel ≈ C·dV/dt : 200 pF à 1 kV/µs donnent 0,2 A. La barrière doit tenir la force électromotrice de la boucle | Courant d'équilibrage réduit, ΔV entre cartes inchangée | Seuil ≈ 173 A (8/20) et ≈ 79 A (front rapide) sans retouche des BA ; ≈ 875 A et ≈ 292 A avec un plot 0 V sur des BA rév. E |
| Effets de bord | La tension non court-circuitée se reporte sur la barrière la plus faible, J1/J2 à 2-3 mm de K1. Convertisseur, superviseur et firmware : trois points de défaillance de plus | Référence PE des parafoudres à arbitrer (TBTS). Ne traite pas les nappes intérieures | Ne coupe rien : au-delà, les TVS conduisent encore. Le 47 Ω et les BAT54S (§4.4) protègent alors les circuits intégrés |
| Matériel [EST] | 150 à 250 € (3 MIB) | Ethernet 60 à 200 € ; type 3 sur départs extérieurs 40 à 80 € par départ | **60 à 100 €** (PCB 2 couches 2 oz, embases bus et IDC, protections par port, support DIN, faisceaux) |
| **Coffret unique** | Surdimensionné | Nécessaire pour les ports qui sortent | **Recommandé** |
| **BA déporté** | **Recommandé** | Nécessaire | Insuffisant |

**Contenu de C :**
- plan 0 V complet, éventuellement renforcé par une tresse **gainée et étiquetée « 0 V TBTS – ne pas relier au PE »** (une tresse nue dans un coffret ressemble à un conducteur de terre) ;
- bus en étoile, chaque BA par J1 et J2 ;
- par port : SDA et SCL avec 47 Ω et une TVS ≤ 50 pF côté port ; +15 V avec PTC ≥ 30 V et SMCJ16A ; un cavalier de déconnexion ;
- traversées IDC 26 points pour les nappes J3 (3 BA et BP), dont les GND sont liés au plan. Seuls 4 à 6 fils sur 26 sont ainsi déviés : les 20 à 22 entrées portent encore leur part du mode commun jusqu'au BA. Prévoir une TVS par entrée vers le plan sur la carte, ou ne pas compter sur cet effet.

**Recommandation.** C + B ciblé (Ethernet isolé, départs extérieurs), avec R1/R2 en 47 Ω et l'option BAT54S (§4.4) pour U19 et les PIC. MIB réservé aux BA déportés, ou en option si les essais de banc de C (§5.9) montrent des erreurs sous 8/20 à 1 kA. **BA rév. E** : plot 0 V vissable près de J1/J2 ; J1/J2 éloignés de K1 et VR1 d'au moins 6-8 mm, avec fente (§5.7) ; R1/R2 de 47 à 100 Ω montées.

### 5.2 Architecture recommandée : îlot isolé par BA, I2C conservé (« A2 révisée »)

(v2) **Domaine d'application révisé** : un ou plusieurs BA **déportés** (autre coffret, plus de 2-3 m de câble, autre bâtiment). Pour un coffret unique comme sur ce site, voir le §5.1 bis ; le MIB y reste une option, et un candidat à l'intégration en rév. E, où il coûte moins cher sur carte.

Elle se réalise d'abord sous forme de **module d'isolement par BA (MIB)** en rétrofit, puis s'intègre dans une révision E des BA.

**Ce qu'on garde :** les adresses 0x11 à 0x13, les trames, le CRC, le PIC16F946, le MCF52259 et le protocole avec le serveur.

```
Réseau 230 V ─ AGCP ─[T2 (T1+T2 si paratonnerre), ≤50 cm]─ ID 30 mA ─ départs (+T3 si >30 m)
Prise de terre ═ borne principale ═ LEP ═ barrette PE du tableau ═ écrans, parafoudres de lignes
                                                                     (Ethernet, TBT ext., départs ext.)
┌──────────── ÎLOT BP = ÎLOT BUS (TBTS, flottant) ─────────────┐
│ BP rév. E : MCF ─[≤33 Ω]─ PCA9306 ─ 2,2 kΩ→+5VS              │
│             └─[47 Ω]─BAT54S─[TVS faible C]─ J31 SDA/SCL      │
│ +15VSP ─ T32 ─[eFuse : limitation + démarrage progressif]─[SMCJ16A]─ J31 +15 V
│ U16 → régulateur ≥ 40 V ; ports extérieurs : TVS + découplage, parafoudres DIN
└────────┬─────────────────────────────────────────────────────┘
         │ câble bus ≤ 3 m, même tableau : SDA+0V │ SCL+0V │ +15V+0V (paire alim dédiée)
    ┌────┴─────┐          ┌──────────┐          ┌──────────┐
    │  MIB 1   │──────────│  MIB 2   │──────────│  MIB 3   │  chaînage par les MIB ; J2 des BA neutralisé
    └────╫─────┘          └────╫─────┘          └────╫─────┘
         ║ barrière RENFORCÉE (données + alimentation), ≥ 8 mm
    [îlot BA 1]           [îlot BA 2]           [îlot BA 3]   ← TOR, relais et variateurs 230 V
```

**Nœud MIB, puis BA rév. E**

```
      ÎLOT BUS (0 V = 0 V du BP)            ┊ barrière ┊          ÎLOT BA n
J_IN/J_OUT (connecteur détrompé, autre série que le côté BA)
 +15V ─[PTC ≥30 V]─[SMCJ16A]─[π LC]─ DC/DC isolé 9–36 V → 12 V, 6–10 W, RENFORCÉ ─ +12 V → +VBUS du BA
       └─[LDO 5 V, entrée ≥40 V]─ VCC2 (+ zener ou TVS 5,6–6 V sur VCC2)
 SDA ─[TVS ≤50 pF]─[47 Ω]─┬─[22 Ω]─ SDA2 ┤ ISO1640DW ├ SDA1 ─(≤30 cm)─ J1 du BA → R1 47 Ω → RC7
                     BAT54S→VCC2/GND2     │ (SOIC-16W)│ VCC1 ← +5 V du BA (VDD de l'ICSP en rétrofit),
 SCL ─ idem ──────────────── SCL2 ┤            ├ SCL1     via interrupteur + décharge ≤1 kΩ
 0 V bus = GND2                           │            │ GND1 = 0 V du BA ; D1/D2 du BA DÉPOSÉES
 Superviseur de nœud (côté 1) : SDA1 ou SCL1 bas > 100 ms → coupe VCC1 → ISO1640 en Z des deux côtés
```

**Choix structurants et leurs raisons :**

1. **Pas de TCA4307 par nœud.**
   - TI déconseille explicitement plusieurs tampons sur un nœud commun (« avoid common node architectures ») : l'étirement d'horloge par une cible y produit de faux fronts [DS, fiche TCA4307 l.662-697].
   - Il exige aussi des tirages côté OUT, absents du schéma initial [DS l.135-137].
   - Il est remplacé par les deux points suivants.
2. **VCC1 prélevé sur le +5 V du BA.** Un BA mort (VCC1 < 2,3 V) met l'ISO1640 en haute impédance des deux côtés et **libère le bus** [DS, tableau de fonctions : « VCC1 < 2.3 V or VCC2 < 1.7 V → Z »].
   - Un VCC1 fourni par le module laisserait le côté 1 tiré bas par le PIC non alimenté, donc un bus bloqué.
   - En rétrofit, on prend VDD/VSS sur le connecteur ICSP du BA.
3. **Superviseur de nœud.** Il couvre le cas d'un PIC bloqué alors que son +5 V est présent (aucun watchdog sur le BA).
   - Coupure de VCC1 avec une résistance de décharge, pour que la réalimentation par les diodes internes reste sous le seuil UVLO (note 2 du tableau TI).
   - **À concevoir et valider au banc.**
4. **Barrière renforcée** (ISO1640**DW**, convertisseur 4–5 kVAC, tension de service ≥ 250 Vac, ≥ 8 mm sur le circuit du module). L'isolement 230 V / TBT du BA lui-même n'est pas démontré (J1/J2 à 2–3 mm de K1, estimation).
5. **Sortie du convertisseur à 12 V.**
   - Le rail « +12V » revient vers 11,1 V, sa tension de conception.
   - Les entrées TOR au repos passent sous les 5 V de tension de veille des TVS d'entrée.
   - Le LMR12010 n'est plus exposé.
   - À vérifier : tension d'enclenchement des relais Finder 34.51 et 40.61 à 11 V et à chaud [DS?]. Sur batterie, le rail descend déjà vers 9,7 V quand J58 est ouvert, ce qui est rassurant.
6. **Mécanique.**
   - Module en boîtier IP20 sur rail DIN, isolation adaptée au 230 V.
   - Connecteur du côté isolé **d'une autre série**, pour qu'une inversion soit impossible.
   - **J2 neutralisé** sur chaque BA retouché, avec une étiquette « ne pas raccorder sans MIB ». Un chaînage par J2 court-circuiterait la barrière.

### 5.3 Budgets [DÉDUIT, à valider au banc avec le câble réel et la charge maximale]

**Côté bus (îlot BP)**
- **Pull-ups :** seuls R155/R156 restent sur le bus, à **2,2 kΩ**. Les 10 kΩ des BA sont désormais derrière les isolateurs. Courant à l'état bas : environ 2,6 mA.
- **Niveau bas vu par le MCF** quand un nœud acquitte :
  - VOL2 de l'isolateur ≤ 0,4 V [DS] ;
  - + 69 Ω × 2,6 mA = 0,18 V ;
  - + BP 47 Ω × 2,6 mA = 0,12 V ;
  - + RON de U19 ≈ 0,04 V ;
  - + ΔVg dû au courant d'alimentation dans le 0 V : environ 0,07 V pour 3 m en AWG20 sous 1 A réparti. (v2) Sur ce site (≈ 1 m, trois tronçons de 33 cm) : 0,06 à 0,16 V en AWG26 avec les contacts actuels, négligeable avec N1/N2 ou un fond de panier (§2.3) ;
  - total ≈ **0,8 V**, contre un seuil de 1,155 V : **marge d'environ 0,35 V**. Elle disparaît au-delà d'environ 6 m en AWG24, d'où la limite de longueur et la section minimale.
- **Capacité :** C2 ≤ 400 pF est une condition recommandée par TI [DS].
  - Bilan : câble (50 à 150 pF/m ; un câble blindé est en haut de la fourchette) + 3 nœuds (≈ 30 pF chacun) + BP (TVS faible capacité).
  - Cela suffit pour **3 m environ**. Les SMF5V0A actuelles (1120 pF) sont incompatibles.
  - (v2) Sur ce site : ≈ 70 pF de câble + 3 × 30 pF + TVS du BP ≤ 50 pF ≈ **210 pF**, largement sous 400 pF.
  - Au-delà, à 50 kHz, le montage fonctionne probablement, mais hors garantie : essai de banc obligatoire, sinon tampon ou génération 3.
- **Temps de montée :** 0,85 × 2,2 kΩ × 400 pF ≈ 0,75 µs.

**Côté BA (côté 1 de l'isolateur)**
- Tirages : R40/R41 (10 kΩ) ∥ 4,7 kΩ vers VCC1, soit 3,2 kΩ et ≈ 1,6 mA, dans la plage IOL1 de 0,5 à 3,5 mA [DS].
- Niveau bas imposé par le PIC : ≈ 0,1–0,2 V + 47 Ω × 1,6 mA ≈ **0,3 V**, sous VILT1 (480 mV min [DS]). **Ne pas dépasser 100 Ω en série côté PIC.**
- Niveau bas imposé par l'isolateur : VOL1 de 0,57 à 0,71 V [DS], sous le VIL I2C du PIC (1,48 V).
- Capacité : **C1 ≤ 80 pF**, ce qui impose de déposer D1/D2 (ou de les remplacer par une protection ESD de 10 pF ou moins), une queue de cochon ≤ 30 cm et de laisser C23/C25 non montés.

**Alimentation**
- La consommation réelle d'un BA est **inconnue** : 2 à 5 W [HYP]. Pour trois BA, cela donne de 0,5 à 1,1 A sous 15 V, à comparer aux repères « 1A current » de BA_ALIM et « 2 A » de T32 [VU].
- **Mesurer avant de choisir le convertisseur.**
- Démarrage simultané des trois convertisseurs à l'activation de TE2 : eFuse avec démarrage progressif au BP, et étude de la sélectivité entre les PTC des modules et la protection du BP.

**Variante d'alimentation locale (valable, à retenir si la consommation ou la longueur pose problème)**
- Une alimentation 230 V → 15 V **classe II** sur rail DIN par BA (par exemple de la gamme Mean Well HDR, isolation 4 kVAC [DS?]). Elle se raccorde au neutre du tableau, pas aux borniers du BA.
- Le câble ne transporte plus qu'un +15VSP de **commande** (quelques mA, vers l'entrée marche/arrêt du convertisseur par optocoupleur). Le BP garde ainsi la relance par TE2.
- Gains : ΔVg nul, plus de problème de sélectivité des PTC.
- Coût : un départ 230 V et un module de plus par BA.

### 5.4 Alternatives écartées

| Option | Raison du rejet |
|---|---|
| TVS plus grosses, seules | Fuite des TVS 5 V puissantes ; et surtout, le chemin de courant n'est pas coupé |
| Isolement au BP seulement (a1), ou ISO1640 à la place du PCA9306 | Les BA restent reliés entre eux, et un BA mort bloque toujours le bus. C2 ≤ 400 pF est incompatible avec les quatre TVS d'environ 1 nF du bus actuel |
| TCA4307 sur chaque nœud | Architecture à nœud commun déconseillée par TI ; tirages côté OUT oubliés ; faux fronts avec l'étirement d'horloge du PIC |
| NXP PCA9615 (I2C différentiel) | Non isolé, broches de −0,5 à +6 V, décalage de masse ≤ 2,5 V, 3 m : aucune tenue à la foudre |
| ADI LTC4331 | Point à point, non isolé |
| GDT 0 V–terre (90 V ou 350 V ‖ condensateur Y ‖ 1 MΩ) | La résistance de 1 MΩ est une liaison galvanique (on passe en TBTP). Amorçage de 297 à 403 V, contre 325 à 358 V crête pour un défaut 230 V : il ne garantit **pas** le déclenchement du différentiel. Fin de vie en court-circuit. §701 pour les salles de bains |
| Self de mode commun L3 sans isolement | Pousse le mode commun dans SDA/SCL |
| CAN isolé (ISO1042) | Le PIC16F946 n'a pas de contrôleur CAN. Un MCP2515 en SPI entre en conflit sur RC4 (SDO). À réserver à un nouveau MCU |
| Étoile avec un multiplexeur TCA9548A au BP | Recâblage et firmware ; à réserver à la génération 3. (v2) Une étoile **passive** (N2, §4.1 bis) suffit dans un coffret unique : des piquages de 15 cm à 50 kHz ne posent aucun problème de ligne, sans multiplexeur ni firmware |

### 5.5 Génération 3 : RS-485 isolé

C'est la bonne couche physique quand le PIC16F946 (en approvisionnement tendu) devra être remplacé.

```
BP : UART2 sur les broches 28/29 (UTXD2/URXD2) [DS] ─ ISO1410 / ADM2587E / MAX14943 ─┐ 120 Ω, polarisation de repos
BA : AUSART RC6/RC7 + détection d'adresse 9 bits (ADDEN) [DS] ─ transceiver isolé ────┤ paire torsadée blindée
     + alimentation isolée par nœud ; SM712 côté ligne ; 120 Ω au dernier nœud ───────┘ multipoint
```

**Avantages :**
- différentiel, adapté aux câbles longs ;
- transceivers en haute impédance quand ils ne sont pas alimentés ;
- **remplace le BSP I2C perdu par le pilote série MQX standard** ;
- les trames et le CRC-16 restent identiques, avec l'adresse portée par le 9ᵉ bit ;
- débit de 19 200 bit/s (+0,16 %) ou 38 400 bit/s (−1,36 %) avec le quartz de 20 MHz [DS].

**Coûts :**
- firmware à réécrire des deux côtés, et tous les BA à reflasher ;
- signal DE : disponible sur SC940D (RB1) et SC942C (RA1 ou RE2), **absent sur SC941C**, qui demande un montage à direction automatique [VU] ;
- la console Espion (UART2) doit être déplacée sur telnet.

### 5.6 Composants

| Fonction | Référence | Statut [DS] | Prix [EST] |
|---|---|---|---|
| Isolateur I2C | **TI ISO1640DW** (SOIC-16W, 5 kVrms, qualification renforcée) | Actif | 4 à 6 € |
| Convertisseur isolé par BA | Module certifié EN 62368-1, entrée 9–36 V, sortie 12 V, 6–10 W, **isolation renforcée 4–5 kVAC**, tension de service ≥ 250 Vac, **tenue en onde de choc spécifiée**, Ciso ≤ 100–200 pF. Écarter les modules à 1,5–1,6 kVDC | Référence à sélectionner | 20 à 40 € |
| TVS de ligne du bus | 5–6 V, ≤ 50 pF, Ipp(8/20) ≥ 5–10 A, boîtier SOD-323 ou SOD-123 (soudable à la main) | À sélectionner. TPD1E10B06 écarté : 6 A seulement et boîtier X1SON/SOD-523 | 0,3 € |
| Écrêteur secondaire | BAT54S (SOT-23), plus zener ou TVS 5,6–6 V sur VCC2 | Actif | 0,1 € |
| Résistances série | Vishay CRCW-HP, Panasonic ERJ-P06 / ERJ-P03 (anti-impulsion) | Actif | 0,1 € |
| Alimentation d'entrée du module | PTC ≥ 30 V (courant de maintien selon mesure à 50 °C), **SMCJ16A** (et non SMBJ, pour tenir 0,5 kV / 2 Ω), LDO 5 V à entrée ≥ 40 V (un 78L05 limité à 30 V ne convient pas) | Actif | 1 à 2 € |
| Protection +15 V au BP | eFuse avec limitation et démarrage progressif (familles TI TPS259x [DS?]) + SMCJ16A ; U16 remplacé par un régulateur ≥ 40 V | À sélectionner | 2 à 4 € |
| BA rév. E | LMR16006 (4–60 V, même brochage) ; C2 en 50 V ; D6 en 40 V | Actif | 2 € |
| Liaison RS-485 isolée (génération 3) | TI ISO1410, ADI ADM2587E, ADI MAX14943 | Actif / production | 5 à 12 € |
| Tampon pour câble long (option) | TI/NXP P82B96, NXP PCA9600 | Actif | 2 € |

**Coût indicatif par installation [EST] :**
- 3 MIB : 150 à 250 €, boîtiers compris ;
- surcoût du BP rév. E : 10 à 20 € ;
- installation électrique (T2, Ethernet, lignes TBT extérieures) : 150 à 600 € plus la main-d'œuvre. (v2) Sur ce site, le T2 est déjà posé : cartouche de rechange, isolement Ethernet et type 3 sur les départs extérieurs, soit 150 à 500 € ;
- (v2) carte d'interconnexion pour coffret unique (§5.1 bis) : 60 à 100 €, à la place des 3 MIB.

### 5.7 Règles de placement et de routage (rév. E du BA, du BP et du MIB)

- **Zonage :**
  - Z1 « bus » : connecteurs, TVS, résistances, entrée du convertisseur ;
  - Z2 « TBTS locale » : PIC, J3 ;
  - Z3 « 230 V ».
  - Entre Z1 et Z2 : **≥ 8 mm sans cuivre sur toutes les couches**, rien sous l'isolateur ni sous le convertisseur.
  - Entre Z2 et Z3 : **≥ 6 à 8 mm avec une fente fraisée** (selon EN 60664-1 et la norme produit, à confirmer). Aujourd'hui, J1/J2 sont à environ 2–3 mm de K1.
- **Ordre fixe sur chaque ligne :** connecteur → TVS (≤ 10 mm de la broche) → résistance série → écrêteur → circuit intégré.
  - Le retour de la TVS va par une piste ≤ 5 mm, ou des vias, vers un petit plan GND_BUS sous Z1 relié à la broche 0 V du connecteur.
  - **Le courant de surtension ne doit jamais traverser le plan logique.**
- **Masse :** un plan par îlot, sans recouvrement entre îlots. Condensateur Y de barrière ≤ 1 nF seulement si les émissions l'exigent (le courant de mode commun à travers lui vaut environ 2 A pour 1 nF à 2 kV/µs).
- **Signaux :** SDA/SCL côté bus ≤ 20 mm ; côté PIC en couche interne, avec garde de masse ; jamais parallèles aux commandes de relais.
- **BP :**
  - J31 et le RJ45 sur des bords opposés (aujourd'hui à 18 mm l'un de l'autre) ;
  - protection du MCU **au pied du MCU** (la piste fait aujourd'hui 55 mm sans rien) ;
  - borne commune pour le blindage RJ45 et les parafoudres, reliée au PE de façon capacitive seulement (statut TBTS à valider) ;
  - (v2) Ethernet : le Bob Smith est déjà relié au 0 V par une capacité (≈ 1 nF / 2 kV), et non directement [VU p. 6]. Demander des magnétiques de 2,25 à 4 kV et une capacité Bob Smith ≥ 3 kV, ou mieux un Ethernet isolé ou en fibre ;
  - (v2) J32 éloigné de J31 et du fil du contact de porte (J53), qui partent aujourd'hui ensemble du coin bas-gauche [VU P&P].
- **Faisceau :**
  - une paire +15 V / 0 V dédiée ;
  - SDA et SCL chacune torsadée avec un 0 V de signal ;
  - **jamais SCL torsadée avec le +15 V** (couplage de l'ondulation, et 15 V sur SCL en cas d'écrasement) ;
  - (v2) **dans un coffret unique** : ≤ 0,5 m par liaison, 0 V renforcé (étoile ou fond de panier), pas d'écran ni de PE dans le coffret ;
  - **pour un BA déporté** : écran repris à 360° sur la barrette PE, isolé du 0 V ; ≤ 3 m en AWG20 (au-delà, refaire le budget) ; le long du PE, en goulotte séparée du 230 V.

### 5.8 Protection de l'installation

Elle reprend le §4.6, plus les points suivants :

- **une seule terre** : si une annexe a sa propre prise de terre, interconnecter les terres ou protéger les lignes aux deux extrémités ;
- **LEP** vérifiée ;
- **résistance de terre** mesurée et notée ;
- si un paratonnerre est présent, parafoudres de **courant de foudre** (catégorie D1, 10/350) sur les lignes qui entrent dans le bâtiment.

À ajouter au guide d'installation (dans `essensys-doc`, avec un ticket) :
- parafoudre de tête et règle des 50 cm ;
- valeur de terre ;
- type, longueur et section du câble de bus ;
- parafoudres de lignes ;
- photos archivées avec l'issue ;
- (v2) aucun câble PV, onduleur ou batterie le long du coffret domotique (≥ 30-50 cm) ;
- (v2) liaisons réseau des onduleurs et autres équipements reliés au PE en Wi-Fi ou en fibre, jamais en cuivre sur le même switch que le BP ;
- (v2) équipotentialité PV vérifiée, même borne principale de terre ;
- (v2) TBT et 230 V jamais dans une même goulotte du coffret domotique.

### 5.9 Plan de test

Tous les essais se font sur un **banc** (BP + 3 BA + câble représentatif, charges factices, sans 230 V sur les sorties), jamais sur l'armoire réelle.

**Critère B redéfini :**
- la communication peut s'interrompre ;
- reprise automatique en moins de 10 s, **avec resynchronisation** ;
- aucune sortie ne change d'état sans commande, **sauf** lors d'un cycle de BA_ALIM par TE2, classé en critère C ;
- aucune dégradation permanente.

| Essai | Niveau ou objectif | Surveillance |
|---|---|---|
| IEC 61000-4-2 (ESD) | ±8 kV contact, ±15 kV air | Compteurs Espion, état des sorties |
| IEC 61000-4-4 (EFT) | ±1 kV par pince capacitive sur le bus, ±2 kV sur l'alimentation et le secteur. Le chemin haute fréquence formé par les condensateurs Y et la Ciso des convertisseurs referme une boucle : l'essai doit le couvrir | Idem |
| IEC 61000-4-5, mode commun **entre îlots** | 2 kV ; 4 kV en essai de type seulement si la tenue en onde de choc du convertisseur le permet | Analyseur logique **à sondes isolées** |
| IEC 61000-4-5, bus et alimentation 15 V | Ligne-ligne 0,5 kV, comme essai de marge (un port de moins de 30 m en est normalement dispensé, à vérifier dans EN 61000-6-1) | — |
| Barrière | 1,5 kVAC pendant 60 s entre îlots, dans la limite de la tenue des modules | — |
| Marge de destruction | 2 ou 3 échantillons poussés jusqu'à défaillance : le premier élément à lâcher doit être une TVS, **et cela ne doit pas bloquer le bus** (vérifier le comportement du superviseur) | — |
| (v2) Courant d'équilibrage entre îlots | Onde 8/20 de 100 A puis 1 kA, et un front rapide (≈ 1 Ipk/µs), injectés entre le GND J3 d'un BA en bout de chaîne et le GND J3 (ou le RJ45) du BP, sur la configuration actuelle puis avec N2 / la carte d'interconnexion. Critère : aucune conduction des écrêteurs I2C sous le seuil visé, rail « +12V » des BA < 20 V, aucune dégradation | Rail « +12V », SDA/SCL, analyseur à sondes isolées |
| (v2) Couplage Ethernet | Onde de mode commun sur le câble Ethernet du BP (8 fils ensemble contre le 0 V), avec et sans isolateur ou fibre | Courant dans le fil GND du bus |

**Non-régression fonctionnelle (tests `NR-*` liés aux Bugs) :**

| Test | Attendu |
|---|---|
| Niveaux et temps de montée à 50 kHz, avec 1 et 3 m de câble, charge maximale | VOL ≤ 0,85 V au MCF ; côté 1 < 0,48 V ; montée ≤ 1 µs |
| Un BA hors tension | Les deux autres fonctionnent, le bus reste libre |
| SDA ou SCL forcée basse côté 1 d'un BA (mire à MOSFET) | Le superviseur libère le bus en ≤ 150 ms ; les autres BA continuent |
| Branchement à chaud d'un nœud | Aucune erreur de CRC sur les autres |
| Cycle de TE2 | Reprise complète et resynchronisation de la configuration |
| Compatibilité croisée | BP actuel avec MIB ; BA 1.7 / 1.8. **BA retouché sans module : interdit** |
| Endurance 72 h | 0 NACK, 0 erreur de CRC, tas du BP stable |

Moyens envisageables : location d'un générateur ESD/EFT/onde de choc pour la pré-qualification, puis un laboratoire COFRAC pour les essais finaux (environ 1 000 à 1 800 € par jour [EST]).

### 5.10 Évolutions du firmware (toutes avec ticket ; protocole serveur inchangé)

**BP**
1. **Préalable :** réécrire et publier dans `essensys-gcc` le pilote I2C MQX avec des timeouts **en temps** (environ 2 ms par attente, 20 ms par transaction). Sans cela, aucun rebuild du BP n'est sûr.
2. **Récupération du bus :** PAS0/PAS1 en GPIO, lecture des niveaux, jusqu'à 9 coups d'horloge en drain ouvert émulé, STOP, puis `I2CR=0` et `IEN`.
3. **Corrections :** pointeur de fichier périmé après réinitialisation (`ba_i2c.c:86/98/180…`) et fuite mémoire quand `fclose` échoue.
4. **Obligatoire dès la phase de rétrofit, pour tenir le critère B :**
   - commandes conservées au lieu d'être abandonnées ;
   - **resynchronisation** de la configuration au démarrage du BP et au retour d'un BA ;
   - état de santé par BA (OK → SUSPECT → ABSENT) ;
   - sonde de présence périodique toutes les 30 à 60 s, pour que l'index 12 reflète l'état réel ;
   - une file par BA.
5. **Dernier recours :** cycle de TE2, limité en nombre et tracé (critère C). Compteur « événement de surtension ».

**BA 1.8** (reflash par ICSP)
- watchdog activé ;
- état d'erreur du SSP (SSPEN à 0 puis 1, CKP à 1, purge de SSPOV et WCOL) ;
- NACK quand `CmdBuf` est occupé ;
- LED d'état ;
- `comm_stat` dans un 6ᵉ octet de lecture (rétrocompatible) ;
- correction de `essensys-gcc/ba/source/hard.h`.

**Serveur :** alerte quand `system.comm_faults` n'est pas vide (`essensys-server-backend/internal/armoire/decode.go`).

**Points d'ancrage dans le code (relevés pendant l'analyse) [VU] :**

| Fichier : ligne | Objet |
|---|---|
| `client-essensys-legacy/C/ba_i2c.c:106` | Initialisation I2C0 à 50 kHz |
| `client-essensys-legacy/C/ba_i2c.c:86`, `:98`, `:180…` | Pointeur de fichier périmé après réinitialisation |
| `client-essensys-legacy/C/ba.c:202-209`, `:313-316` | Trames de configuration perdues pendant la panne abandonnées et marquées acquittées, jamais renvoyées (d'où le renvoi des configurations de tous les BA, §3.7) |
| `client-essensys-legacy/C/Hard.c:879-945`, `H/global.h:50-51` | Coupure de +15VSP sur batterie (≈ 12 s) et rétablissement ≈ 1 s après le retour secteur |
| `client-essensys-legacy/C/EspionRS.c` | Console Espion (menus, constante d'activation) |
| `client-essensys-legacy/docs/embedded-client/architecture.md:193` | Comportement de la LED de téléinfo |
| `essensys-gcc/bp/bsp/m52259evb/m52259evb.h:363` | Débit UART de la console (9600 8N1, BSP de référence) |
| `essensys-board-SC940/SC940D/Prog/code_ba (fichiers sources 1.7)/source/main.c:17` | `__CONFIG(HS & WDTDIS)` : watchdog désactivé |
| `…/source/slavenode.c:361` | Branche `else;` sans traitement d'erreur SSP |
| `…/source/gestionsorties.c:15-30`, appel ligne 224 | Clignotement de DL1 |
| `essensys-gcc/ba/source/hard.h` | À corriger (BA 1.8) ; build essensys-gcc du BA à ne pas flasher (trois macros `TYPE_*` définies ensemble) |
| `essensys-server-backend/internal/armoire/decode.go` | Décodage de `system.comm_faults` (index 12) |

### 5.11 Phasage

| Phase | Contenu |
|---|---|
| 0 | Installation (§4.6, §5.8), (v2) coupure du cuivre PV ↔ LAN, intervention de l'installateur PV |
| 1 | Réparation et retouches court terme (§3, §4), (v2) isolement de l'Ethernet du BP, N2 |
| 2 | (v2) Prototype de la carte d'interconnexion (§5.1 bis) et banc ; pilote I2C du BP reconstitué, resynchronisation. MIB en option, pour les BA déportés |
| 3 | BP rév. E et BA rév. E (isolation intégrée, zonage) |
| 4 | Génération 3 en RS-485 isolé, décision à formaliser dans un ADR |

---

## 6. Annexes

### A. Calculs

- **Pull-ups :**
  - 1 kΩ ∥ 3 × 10 kΩ = 769 Ω. À VOL = 0,4 V : (4,93 − 0,4) / 769 = 5,9 mA, plus 0,62 mA par R157/R158, soit ≈ 6,5 mA. Norme : ≤ 3 mA, donc Rp ≥ 1,53 kΩ.
  - Avec 2,2 kΩ au BP : 1,325 kΩ, soit 3,4 mA, plus 0,6 mA.
- **Temps de montée :**
  - de 0 à 3,45 V : t = R·C·ln(1/(1 − 3,45/4,93)) = 1,2 × R × C. Avec 769 Ω et 1,5 à 3,5 nF : 1,4 à 3,2 µs.
  - Critère : < 4 µs, car à 50 kHz la demi-période dure 10 µs et le MCF se synchronise sur son seuil de 2,31 V.
  - Facteurs : × 1,345 pour 1,5 kΩ, × 1,72 pour 2,2 kΩ.
- **Capacité du bus :** C ≈ t(10 → 90 %) / (2,2 × 769 Ω).
- **TVS SMF5V0A :**
  - VRWM 5 V, IR ≤ 5 µA (à 25 °C, la fuite croît avec la température), VBR 6,4 à 7,1 V, VC 9,2 V à 21,7 A en 10/1000, 1000 W en 8/20, CD 1120 pF à 0 V [DS].
  - Résistance dynamique ≈ (9,2 − 7,1) / 21,7 ≈ 0,1 Ω, d'où environ 70 A et VC ≈ 14 V à 1000 W en 8/20, et VC ≈ 11,8 V à 48 A [DÉDUIT].
  - IEC 61000-4-5 avec une source de 42 Ω : 1 kV donne 24 A, 2 kV donnent 48 A.
- **Courant injecté dans le PIC :** (V_TVS − 5,5) / R en positif ; (2,5 − 0,6) / R en négatif (tableau du §4.2).
- **Différence de potentiel entre masses** (remplacé en v2) : entre une ligne et son 0 V dans un même câble, seul compte R + (L − M). Tronçon de 33 cm d'AWG26 (r ≈ 0,24 mm) : L propre 0,46 µH ; M 0,30 à 0,37 µH (conducteur voisin à 2,5 ou 0,9 mm) ; L − M 0,09 à 0,16 µH ; R ≈ 0,09 Ω (fil 0,046 Ω + 2 × 20 mΩ de contacts + PCB). Seuil d'équilibrage = 6,3 à 7,8 V / z, avec z = R + (L − M)·(dI/dt)/I selon la pente (tableau du §0.3.1). Calcul fait par l'analyse CEM et recoupé par un script indépendant du relecteur adversarial. L'ancienne formule « V = L·di/dt, ≈ 1 µH/m, 1 kV sur 10 m » ne vaut que pour un câble long dont la boucle est fermée (§0.3.3, nappes J3).
- **Couplage capacitif par l'Ethernet** (v2) : capacités de 1 nF en série (dongle de supervision de l'onduleur, deux ports du switch, J32) : 0,33 nF, soit 0,3 à 1,7 A pour 1 à 5 kV/µs avant amorçage.
- **Mutuelle conducteur rectiligne / boucle** (v2) : M = (µ0·h / 2π)·ln((d + w)/d). Pour h = 0,3 m : 3,9 nH (d = 15 cm, w = 1 cm) ; 9,2 nH (d = 15 cm, w = 2,5 cm) ; 1,5 nH (d = 40 cm, w = 1 cm) ; ≈ 0,1 nH pour la boucle SDA/GND d'un câble (w ≈ 1 mm, d ≈ 50-60 cm).
- **Rail « +12V » du BA** (v2) : V_rail ≈ 14,3 V + ΔV quand le 0 V du BA descend sous celui du BP (D3 passante, C2 = 10 µF, τ ≈ 3 µs). C2 (16 V) dépassé dès ΔV ≈ 2 V ; U1 (24 V) vers ΔV ≈ 10 V, soit ≈ 28 A en 8/20 au SC940D.
- **ΔVg statique :** I × R_fil. Fil de 0,22 mm² ≈ 0,08 Ω/m ; AWG20 ≈ 0,033 Ω/m. Exemple : 5 m en 0,22 mm² sous 0,4 A donnent 0,16 V. (v2) Sur ce site : 6 × R_tronçon × I_BA, avec R_tronçon ≈ 0,09 Ω contacts compris, soit 0,08 à 0,16 V pour 0,15 à 0,3 A par BA.
- **TVS d'alimentation SMAJ16A :** VRWM 16 V, VBR 17,8 à 19,7 V, VC 26 V à 15,4 A en 10/1000. Après D3, on atteint environ 25 V, au-delà de VIN 24 V et BOOST 30 V du LMR12010, et à la limite de FI1 (25 V).
- **PTC MF-R110 :** courant de maintien 1,10 / 0,91 / 0,85 A à 23 / 40 / 50 °C [DS].
- **Coordination GDT → TVS :** R ≥ (amorçage dynamique du GDT − VC de la TVS) / Ipp(8/20) de la TVS, avec l'Ipp en 8/20 lu sur la courbe Ppk(tp) de la TVS retenue. Sur une ligne qui porte de la puissance, découpler par une inductance ou une PTC, ou utiliser un parafoudre DIN coordonné, jamais par une résistance.

### B. Références (liens relevés lors de l'analyse composants)

- **Composants en place :**
  - [Vishay SMF5V0A, fiche 85881](https://www.vishay.com/docs/85881/smf5v0atosmf58a.pdf)
  - [TI PCA9306](https://www.ti.com/lit/ds/symlink/pca9306.pdf)
  - [NXP MCF52259](https://www.nxp.com/docs/en/data-sheet/MCF52259.pdf)
  - [Microchip PIC16F946 DS41265](https://ww1.microchip.com/downloads/en/DeviceDoc/41265A.pdf)
  - [TI LMR12010](https://www.ti.com/lit/ds/symlink/lmr12010.pdf)
  - [Würth 742792643](https://www.we-online.com/components/products/datasheet/742792643.pdf), [Würth 744272102](https://www.we-online.com/components/products/datasheet/744272102.pdf)
- **Long terme :**
  - [TI ISO1640](https://www.ti.com/lit/ds/symlink/iso1640.pdf)
  - [TI TCA4307](https://www.ti.com/lit/ds/symlink/tca4307.pdf)
  - [NXP PCA9615](https://www.nxp.com/docs/en/data-sheet/PCA9615.pdf)
  - [TI P82B96](https://ti.com/document-viewer/P82B96/datasheet)
  - [TI LMR16006](https://www.ti.com/product/LMR16006)
  - [ADI ADM2587E](https://www.analog.com/ADM2587E)
  - [TI ISO1410](https://ti.com/lit/gpn/ISO1410)
  - [MAX14943](https://www.mouser.vn/ds/2/256/MAX14943-779857.pdf)
- **Protection :**
  - [Vishay CRCW-HP](https://www.mouser.lt/pdfDocs/crcwhp.pdf)
  - [Bourns MF-R110](https://octopart.com/part/bourns/MF-R110)
  - [Littelfuse SMBJ5.0A (fuite)](https://datasheet.lcsc.com/lcsc/1809042032_Littelfuse-SMBJ5-0A_C83333.pdf)
- **Installation :**
  - [DEHN DPA M CAT6](https://www.dehn-international.com/store/p/en-DE/F32581/dehnpatch-arrester-for-data-networks-and-ethernet-applications) et [Phoenix DT-LAN-CAT.6+](https://www.phoenixcontact.com/us/products/2881007) : parafoudres RJ45 cités par le v1 ; (v2) **à ne pas poser au BP** reliés au PE (§4.5), éventuellement à l'extrémité d'un équipement relié au PE
  - [Legrand, obligation NF C 15-100](https://www.legrand.fr/questions-frequentes/le-parafoudre-est-il-obligatoire)
  - [Legrand, parafoudres PV](https://assets.legrand.com/pim/NP-FT-GT/F01271FR-02.pdf)
  - Le v1 citait aussi deux références du marché de parafoudres modulaires de type 2 (bipolaires, Up ≤ 1,5 kV, avec report à distance) comme exemples pour un parafoudre de tête ; (v2) sans objet sur ce site, où un parafoudre de type 2 est déjà posé.
- **Équipements du site (v2) :** les fiches du parafoudre de tête, de sa cartouche, de l'ensemble de protection AC et des parafoudres DC du coffret PV, et de l'onduleur ont été consultées pendant l'analyse. Elles ne sont pas citées ici (anonymisation) ; les caractéristiques utiles sont reprises dans le texte. Point à retenir : pour le parafoudre AC du coffret PV, seule la fiche d'un **produit voisin de la même gamme** a été trouvée, **pas sa notice** (architecture, sens des fenêtres et du noir non confirmés, §0.5 n° 4).

### C. Points restant à vérifier sur place ou avant de figer la conception

1. ~~Quel BA est en bout de chaîne. Les BA sont-ils dans le même tableau que le BP ? Longueur, section et type du câble.~~ **Résolu en grande partie (v2)** : même coffret ; bout de chaîne = SC940D ; trois tronçons d'environ 33 cm de câble cat. 5e AWG26 souple [VU ph. 1-3]. Reste : nombre de fils par contact, origine du câble à gaines bleues posé sur l'établi.
2. État des LED DL1 (vidéo de 10 s par les fenêtres ÉTAT). Valeur de l'index 12 après une commande à chaque BA. (v2) **C'est ce point qui identifie le BA défaillant**, encore inconnu.
3. ΔVg mesuré (attendu 0,06 à 0,16 V), et courant de BA_ALIM avec les relais collés, à la température du tableau.
4. Niveau bas BP → BA mesuré au PIC : il tranche la question de la sortance du port AS.
5. Temps de montée actuel de 0 à 3,45 V : il décide de l'option P2.
6. Cavalier J58, présence de la batterie, `Mode_Test`.
7. ~~Parafoudre présent et son état~~ **Résolu en partie (v2)** : parafoudre de type 2 du tableau présent, voyant L-N vert [VU ph. 4] ; reste la manette, l'éclateur N-PE, l'alimentation en amont des ID, le PE et la terre. Toujours ouverts : déclenchements des différentiels, autres appareils touchés, box en cuivre ou en fibre.
8. Contenu des départs Terrasse et Annexes : luminaires de classe I, bâtiment séparé, autre prise de terre. Résistance de terre, LEP, paratonnerre, ligne aérienne.
9. Emplacement des boutons-poussoirs dans les salles de bains (volumes 1 et 2) : la TBTS est-elle imposée ?
10. Distances 230 V / TBT réelles sur les Gerber (J1/J2 ↔ K1, VR1, U2).
11. Boîtier de C40 sur les BA (pour la TVS de +Vin) ; plage AWG des contacts WR-MPC3 ; disponibilité d'une PTC 1812 ≥ 30 V.
12. Tension d'enclenchement des relais Finder à 11 V et à chaud. Comportement de l'ISO1640 avec un côté non alimenté et réalimentation par les broches, à vérifier au banc.
13. Disponibilité d'un oscilloscope.
14. (v2) **Chronologie croisée** : date à laquelle le parafoudre AC du coffret PV a été vu vert pour la dernière fois, journaux du contrôleur réseau, passerelle Essensys (MQTT, historique court), portail de supervision de l'onduleur, serveur Essensys, historique du compteur communicant, données de détection de la foudre. Sans elle, aucune cause commune ne peut être attribuée.
15. (v2) **Onduleur et dongle de supervision** : en marche ou à l'arrêt, journal (SPD, isolement, défaut de terre), LED du dongle, parafoudres internes, sortie de secours câblée ou non.
16. (v2) **Notice du parafoudre AC du coffret PV** (à demander à l'installateur PV) : architecture CT1 ou 1+1, sens des deux fenêtres et du noir.
17. (v2) **Switch réseau** : modèle, alimentation (avec ou sans terre), emplacement et trajet des câbles du dongle et du BP, compteurs d'erreurs des ports, autres équipements raccordés (routeur, passerelle Essensys, PoE extérieur).
18. (v2) **Coffret domotique** : nappe J3 du SC942C, contenu de J3 du BP (IHM, capteurs extérieurs), destination et longueur des nappes J3, conducteurs rouges et marron en haut à droite, trajet du cordon orange, TBT et 230 V dans une même goulotte.
19. (v2) **Installation PV** : type de l'interrupteur différentiel 300 mA, Ue des disjoncteurs DC face au Voc froid, équipotentialité et prise de terre unique, trajet des câbles AC et PE du PV, compteur d'énergie de l'onduleur en RS-485, valeur locale de Ng.
20. (v2) Microrupteur de porte (J53 du BP) qui pend hors du coffret : à refixer.

### D. Corrections appliquées et arbitrages

**Corrections retenues** (vérificateurs, appliquées au texte) :
- U19 avec EN ≈ 5 V : interrupteur passant sans limitation de niveau, d'où un risque de surtension sur le MCF, et non un NACK. EN bas : interrupteur bloqué.
- +VBUS ↔ GND sain ≠ « > 100 kΩ » : environ 0,8 kΩ sur « +12V », à cause des diviseurs TOR.
- Critères de repos relatifs (ΔV ≤ 40 mV) au lieu d'un seuil absolu de 4,9 V.
- PTC en amont de la TVS. TVS de BA après R79, avec un élément de protection propre à chaque BA.
- U16 hors marge ; C2 en 35 V ; limite BOOST de 30 V.
- GDT 0 V–terre retiré du court terme comme du long terme (TBTS, §414, §701, pas de déclenchement garanti du différentiel).
- Étape E-1 de sécurité et essais d'isolement avant toute manipulation ; pas de sondage direct de J31.
- 47 Ω ne ramène pas l'injection sous 20 mA ; cas négatif ajouté ; BAT54S proposée aussi côté BA.
- VC recalculé à 12–14 V en onde 8/20.
- Borne de l'option 1,5 kΩ fixée à 2,97 µs.
- +15VSP rétabli environ 1 s après le retour du secteur ; prérequis J58, batterie et `Mode_Test`.
- Marge BP → BA non démontrée (sortance du port AS).
- TCA4307 par nœud abandonné ; budget long terme refait (ΔVg, résistances série, 2,2 kΩ) ; barrière renforcée ; IP20 et détrompage ; J2 neutralisé.
- SMCJ au lieu de SMBJ ; LDO ≥ 40 V ; critère tSTUCK ≤ 70 ms si un TCA4307 est utilisé.
- Paire d'alimentation dédiée dans le câble.
- Second parafoudre au-delà de 30 m (et non 10 m).
- Configurations à renvoyer pour **tous** les BA.
- Varistances remplacées sur le BA mort.
- Sauvegarde de la flash du BP par BDM.
- Remplacement des TVS sur les BA sains seulement si leur fuite est mesurée.

**Arbitrages contre un vérificateur ou un rapport :**
- **PTC ou fusible en série avec la TVS de bus de chaque nœud** (vérificateur pratique, long terme) : non retenu. Le courant des pull-ups (2 à 6 mA) ne peut jamais le faire déclencher, donc une TVS en court-circuit bloquerait toujours le bus. Le confinement d'un défaut passe par l'isolement, VCC1 prélevé sur le BA et le superviseur de nœud.
- **R ≥ 37 Ω** (vérificateur calculs, long terme) : il a utilisé l'Ipp en 10/1000 de la SMAJ16A (15,4 A), ce qui donne un majorant. L'Ipp en 8/20 est plusieurs fois plus élevé. La conclusion reste juste : pas de résistance série sur une ligne d'alimentation, découpler par inductance ou PTC, ou utiliser un parafoudre DIN.
- **« J1-4 ↔ GND ≈ 1–2 kΩ avec D3 passante »** (vérificateur calculs, court terme) : la tension d'essai d'un ohmmètre ne rend pas D3 passante de façon fiable. On mesure sur le nœud « +12V » (≈ 0,8 kΩ) et on compare J1-4 à un BA sain.
- **Seuil secteur d'environ 19–20 V sur alimentation continue** (vérificateur pratique, court terme) : non vérifié sur le schéma. Il est gardé comme précaution, d'où l'exigence de 22 V ou plus.
- **Seuils du PIC à 0,2 / 0,8·VDD** (rapport BA) : ce sont les valeurs hors mode I2C. En mode I2C, ce sont 0,3 / 0,7·VDD (DS41265, D034/D044).
- **« MSSP »** (relevés préliminaires) : le PIC16F946 n'a qu'un module **SSP**, esclave I2C seulement.
- **Menu et débit de la console** (rapport système, « menu 3, 9600 ») : la navigation retenue est celle du rapport FW (`m` → `2` → `0/3/5`). Le débit de 9600 bit/s est confirmé par le BSP essensys-gcc ; le BSP de production est absent. La console est bien compilée dans le firmware 099-37 [VU, `.xMAP`].
- **ISO1640 à la place du PCA9306, « côté 2 sur le bus à 1 kΩ »** (rapport composants) : incompatible avec C2 ≤ 400 pF tant que les quatre TVS d'environ 1 nF restent sur le bus.

**Version 2 (2026-10-11) : corrections retenues** (audit des photos, analyse CEM, analyse PV, deux relectures) :
- Topologie : coffret unique, trois tronçons de 33 cm, bout de chaîne au SC940D ; « 1 kV sur 10 m » retiré du mécanisme du bus et gardé seulement pour un câble long à boucle fermée.
- Modèle unique R + (L − M) pour l'I2C ; mutuelle M sur des boucles définies pour l'induction. Les chiffres en inductance propre (« 0,3 µH, 30 V à 100 A/µs ») de l'analyse PV sont remplacés.
- Seuils donnés pour deux pentes ; N2 placée devant N1, dont le gain tombe de ×5 à moins de ×2 sur un front raide (N2 : ×6 à ×9).
- 47 Ω : survie probable du PIC, sans respect du maximum absolu ; 240 A est la limite des TVS, pas du PIC.
- Mécanisme du fil +15 V (charge de C2 et du rail « +12V », U1 à 24 V vers 28 A) ajouté ; tests d'alimentation avant RC6/RC7 ; C2 35 V, D6 40 V, TVS après R79 remontés en P1.
- Origine de la surtension : quatre hypothèses concurrentes (PV, réseau en mode commun, surtension temporaire ou défaut d'onduleur, événements indépendants), non classées avant la chronologie, la notice du parafoudre AC du coffret PV et l'état de l'onduleur. L'argument « Uc 320 V exclut une surtension temporaire » est retiré : il ne vaut que pour L-N.
- BA défaillant « non identifié » : la ligne « SC940D totalement mort » de l'analyse PV est retirée.
- L'induction par les câbles PV ne désigne pas le port I2C du SC940D ; borne haute ramenée à environ 18 V.
- Chemin Ethernet rechiffré avec les capacités en série (0,3 à 1,7 A avant amorçage) ; un switch relié au PE détourne le courant ; tests de J32 (résistance broches 1-3, isolement 500 V) ajoutés.
- Bob Smith de J32 relié au 0 V **par une capacité**, et non directement ; demande rév. E corrigée.
- Ethernet du BP : isolement (fibre alimentée depuis l'îlot TBTS, ou isolateur ≥ 4-6 kV) ; aucun parafoudre RJ45 relié au PE au BP ni au PE du PV ; aucun PE dans le coffret domotique ; renfort et tresse étiquetés « 0 V TBTS – NE PAS RELIER À LA TERRE ».
- Essais d'isolement obligatoires sur les trois BA et le BP, SC941C en premier ; nouvelle mesure LoZ à la remise sous tension.
- Varistance nue supprimée ; type 3 conforme, au départ dans le tableau électrique.
- Point de soudure du renfort sur la broche traversante J1/J2-3, anodes de D1/D2 reliées ; variante par la batterie classée « dégradée ».
- Fond de panier : les GND de nappe ne dévient que 4 à 6 fils sur 26 ; TVS par entrée ou phrase nuancée.
- Remplacement du parafoudre AC du coffret PV sorti du P0 Essensys : action PV parallèle, non bloquante.
- Sécurité PV : chaînes à plusieurs centaines de volts continus, bornées par la conception de l'onduleur (les 720-750 V sont les Ucpv des parafoudres DC, pas la tension des chaînes) ; batterie de l'onduleur en BT (plus de 100 V continus) et non « haute tension » ; ouverture du disjoncteur de déconnexion AC C32 intégrée à la consignation par la personne habilitée ; sortie de secours de l'onduleur dans E-1 ; précautions avant de débrancher le dongle de supervision ; objets dans le coffret sous tension proscrits.
- Type de parafoudre selon la norme : type 1 si paratonnerre ; parafoudre obligatoire, type 2 au minimum, si ligne aérienne en AQ2.
- Audit des photos : la position « bout de chaîne » compte (facteur jusqu'à 3) ; nappe J3 du SC942C « non concluant » et non « vide » ; ΔVg de l'audit (0,05-0,1 V) sous-estimé car il omet les contacts.
- Ajouts des relectures : type de l'interrupteur différentiel du coffret PV, parafoudres internes de l'onduleur, prise de terre unique, risque thermique du parafoudre AC du coffret PV, manipulation de la cartouche du parafoudre de tête, historique du compteur communicant, inventaire du switch, conservation des pièces et des traces.

**Version 2 : arbitrages**
- **Critère 33 / 47 Ω** : l'analyse CEM proposait de supprimer l'option 33 Ω ; le critère est conservé, car la marge gagnée (0,02 V) repose sur un ΔVg non mesuré et un modèle au pire.
- **« Le parafoudre AC du coffret PV était en place et fonctionnel au moment de l'événement »** (relecture pratique) : prémisse non retenue, car la date du passage au noir est inconnue ; la conclusion (remplacement non bloquant pour Essensys) est retenue.
- **« Un interrupteur différentiel de type AC ne convient pas à un onduleur sans transformateur »** (relecture pratique) : gardé comme point à vérifier par l'installateur [DS?], et non comme non-conformité, faute d'avoir lu l'exigence du fabricant et le type réel de l'appareil.
- **« Moins de 5,5 mm entre J1/J2 et K1 : îlot non TBTS par construction »** (relecture pratique) : retenu comme alerte, en précisant que 5,5 mm est la consigne de conception du BP ; la valeur exigible pour une isolation renforcée relève de l'EN 60664-1 et de la norme produit.
- **Statut des MIB** (analyse CEM : rétrogradés ; analyse PV : à garder pour la rév. E) : fusionnés, le MIB est la solution des BA déportés et un candidat à l'intégration en rév. E, pas la solution de ce coffret.
- **Remplacement du parafoudre AC du coffret PV par un type 2 de In ≥ 10-20 kA** (analyse PV) : laissé à l'appréciation de l'installateur, qui doit justifier le calibre, car la coordination avec le parafoudre de tête et la notice du fabricant n'ont pas été vues.

### E. Écarts de documentation à corriger (avec ticket)

- `essensys-doc/archi/hardware-sc944d.md` et `hardware-overview.md` : la liaison BA passe par J31, et non par J3 ou la « feuille 17 ».
- `hardware-sc94{0d,1c,2c}.md` :
  - J3 porte les entrées TOR, et le bus passe par J1/J2 ;
  - la logique est en 5 V, et non en 3,3 V ;
  - L3 n'est pas montée ;
  - les quantités de TVS et de VDR du SC940D sont fausses.
- `essensys-board-SC944D/docs/i2c.md` :
  - le bus tourne à 50 kHz, et non 100 kHz ;
  - le code ACTIONS vaut 5 ;
  - les adresses vont de 0x11 à 0x13.
- `essensys-board-SC940/docs/Architecture_Overview.md` : le SC943 est un variateur à IGBT, et non un module RF.

### F. Fichiers sources principaux

Chemins relatifs à la racine des dépôts du projet Essensys.

- `essensys-board-SC944D/SC944D/Assembly/SC944D_Schematic.pdf` (p. 3, 5, 7 ; p. 2 et 6 citées pour le 5,5 mm, J56-3 et l'Ethernet)
- `essensys-board-SC940/SC940D/Assembly/SC940D_Schematic (DM).pdf`
- `essensys-board-SC941C/SC941C/Assembly/SC941C_Schematic (DM).pdf`
- `essensys-board-SC942C/SC942C/Assembly/SC942C_Schematic (DM).pdf`
- BOM des quatre cartes (BOM DM et BOM d'archive des BA, pour la modification DM de janvier 2017) et plans d'assemblage (P&P)
- `essensys-board-SC944D/SC944D/Prog/099-37/BP_MQX_ETH 20170116 save 099-37.elf_BOOT_CRC.S19` (image de production du BP) et le `.xMAP` de 099-37 (symboles `vd_EspionRS_*`)
- `client-essensys-legacy/C/ba_i2c.c`, `C/ba.c`, `C/Hard.c`, `C/EspionRS.c`, `H/global.h`
- `client-essensys-legacy/docs/embedded-client/architecture.md`
- `essensys-board-SC940/SC940D/Prog/code_ba (fichiers sources 1.7)/source/` (`slavenode.c`, `main.c`, `gestionsorties.c`)
- `essensys-board-SC940/SC940D/Prog/Fiche programmation SC940 v1.docx` ; fichiers `ba v1_7 piece vie.hex`, `piece eau`, `piece chambre`
- `essensys-gcc/bp/bsp/m52259evb/m52259evb.h`, `essensys-gcc/ba/source/hard.h`
- `essensys-server-backend/internal/armoire/decode.go`
- Non publiés (conservés hors dépôt) : rapports v1 et v2 d'origine, photos du site et recadrages, extraits de fiches techniques, scripts de calcul CEM et de recoupement, relevés des relectures

### G. Historique : ce que le v1 affirmait et qui a été remplacé (ajout d'archivage)

Le v1 a été écrit sans connaître l'installation : il supposait des boîtiers distants, reliés par un câble de plusieurs mètres. Ses affirmations remplacées sont gardées ici pour mémoire, avec leur sort en v2.

| Sujet | v1 | Sort en v2 |
|---|---|---|
| Mécanisme | « Le coup de foudre indirect a porté ces îlots à des potentiels différents. Le fil GND crée environ 1 kV sur 10 m pour 100 A/µs (V = L·di/dt). » Annexe A : ≈ 1 µH/m ; pour 10 m, 1 kV à 100 A/µs, 10 kV à 1 kA/µs | Remplacé par R + (L − M) par tronçon de 33 cm (§0.3.1). L'ordre de grandeur ne vaut que pour un câble long à boucle fermée (nappes J3) |
| Bout de chaîne | « S'il s'agit du SC941C, il pilote aussi la terrasse et les annexes [HYP sur sa position]. C'est lui qui a le plus souffert. » | Bout de chaîne = SC940D [VU ph. 1, 3] ; la position abaisse le seuil, mais ne désigne pas la carte défaillante |
| Ordre des suspects | BA mort, puis D33/D34 ou U19, puis TVS ou broche d'un autre BA, puis +15VSP | Alimentation du BA (U1, D3, C2, D6, FI1) avant RC6/RC7 ; U19 avant D33/D34 ; J32/C63 si H-PV |
| B5 (couplages de masse) | 0 V relié au blindage RJ45 (1 nF/2 kV) et à la terminaison Bob Smith | Précisé : Bob Smith relié au 0 V par une capacité (≈ 1 nF/2 kV), les 8 fils Ethernet couplés en mode commun ; switch partagé avec le dongle de supervision de l'onduleur |
| A6 (isolement) | J1/J2 à 2-3 mm de K1, essai d'isolement « (§3) » | Essai sur chaque BA ; sur le SC940D, K1 « Entrée » et VR1 voisins de J2 ; D1/D2 à 28-48 mm de J1/J2 ; 5,5 mm imposés par le schéma du BP |
| ΔVg | « Écart de masse statique entre les deux boîtiers » ; critère de réception « < 0,1 V » | ΔVg attendu 0,06 à 0,16 V sur ce site (contacts compris), < 0,02 V avec N1/N2 ; critère 47 / 33 Ω conditionnel (§3.7) |
| Essais d'isolement | « Chaque BA touché » ; BA mort | Les trois BA et le BP, SC941C en premier ; nouvelle mesure LoZ à la remise sous tension |
| Retrait du BA mort | Câble retiré « côté J2 du BA précédent » | Câble retiré des deux côtés ; sur ce site, c'est le J1 du BA précédent |
| R1/R2 47 Ω | « 33 Ω si ΔVg > 0,1 V » ; courant « reste au-dessus de 20 mA » | Critère conservé ; 47 Ω = survie probable du PIC sans respect du maximum absolu ; seul N1/N2 relève le seuil d'équilibrage |
| Alimentation des BA | P1 : C2 35 V, D6 30-40 V sur le BA réparé ; TVS de +Vin en P2 | P1 sur chaque BA déposé : C2 35 V, D6 40 V, TVS après R79 (mécanisme du fil +15 V) |
| Parafoudre de tête | P1 : installer un type 2 (1+2 si paratonnerre ou ligne aérienne en AQ2), Up ≤ 1,5 kV, déconnecteur, règle des 50 cm, contrôle de la terre (TT) et des liaisons équipotentielles, essai des différentiels ; 60 à 150 € + électricien | Présent ; devient un contrôle (§4.6) |
| Second parafoudre (type 3) | Seulement si l'équipement est à plus d'environ 30 m du parafoudre de tête ; alors au moins 10 m de câble entre les deux, ou produits coordonnés du même fabricant | Sans objet sur ce site (coffret accolé au tableau) ; règle toujours valable pour un autre site |
| Câble de bus | P1 : 4 fils torsadés ensemble, court, plaqué contre la plaque de fond, ≥ 10 cm du 230 V ou en goulotte séparée, croisements à 90°, pas de boucle. §4.6 : souple, serti à l'outil ou faisceaux pré-sertis ; **pas de Cat6 rigide** ; pas deux fils dans un même contact ; section la plus forte acceptée par les contacts WR-MPC3, au moins 0,34 mm² pour GND et +15 V ; isolation 300/500 V ou goulotte séparée (NF C 15-100 §528) | Les tronçons font déjà ≈ 33 cm ; les contacts pèsent autant que le fil (l'AWG20 n'apporte que ×1,4) ; le levier est l'impédance entre cartes (N2, N1). La règle d'isolation (§528) reste : manchon ou éloignement des bornes Ph |
| Ethernet | P2 : parafoudre RJ45 Cat6 près du BP, **relié au PE** ; protéger la ligne télécom si elle est en cuivre ; autre option : paire de convertisseurs fibre | **Abandonné au BP** (§4.5) : isolement par fibre (convertisseur alimenté depuis l'îlot TBTS) ou isolateur ≥ 4-6 kV, passé en P1 |
| Lignes TBT extérieures | Parafoudre de données sur rail DIN (GDT + TVS), dimensionné pour 12 à 24 V, à l'entrée du bâtiment, sur la même terre | Probablement sans objet (J3 du BP semble vide) ; sinon isolement (relais, optocoupleur ≥ 4 kV) ou parafoudre à défaillance « ouverte », pour ne pas passer l'îlot en TBTP |
| Départs 230 V extérieurs | Parafoudre au départ, et à l'arrivée si l'annexe a sa propre terre ou si le câble est long ; interconnecter les terres ; type 3 ou varistance 275 V (formule résumée au §0.4 du v2) | Type 3 conforme NF EN 61643-11, au départ dans le tableau, jamais dans le coffret domotique ; **jamais de varistance nue** |
| Inventaire | Bouton test des différentiels, voyant du parafoudre, autres appareils touchés (box, port du switch en face du BP) | Étendu aux parafoudres AC et DC du coffret PV, au port du dongle, au compteur de l'onduleur et à la liaison BMS |
| Architecture long terme | MIB par BA ; phasage : phase 2 « prototype du MIB, banc, pilote I2C du BP reconstitué, resynchronisation » | Carte d'interconnexion équipotentielle pour un coffret unique ; MIB réservé aux BA déportés |
| Multiplexeur TCA9548A | Étoile active à réserver à la génération 3 | Inchangé, mais une étoile **passive** (N2) suffit dans un coffret unique |
| Installation (coût) | T2, Ethernet, lignes TBT extérieures : 150 à 600 € plus la main-d'œuvre | Sur ce site : 150 à 500 € (cartouche, isolement Ethernet, type 3 sur les départs extérieurs) |
| Points à vérifier | Bout de chaîne, même tableau ou non, longueur/section/type du câble ; parafoudre présent et son état | Résolus en grande partie par les photos (annexe C n° 1 et 7) |
