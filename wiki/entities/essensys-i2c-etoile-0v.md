---
tags: [entity, repo, hardware, kicad, firmware, esp32, foudre, i2c, tbts, alarme, mqtt]
sources: [incidents/2026-08-foudre-bus-i2c/rapport-analyse.md, manifest.json]
created: 2026-10-12
updated: 2026-10-12
era: modern
repo: essensys-i2c-etoile-0v
---

# Essensys I2C Etoile 0v

> Carte N2 « étoile 0 V » sur rail DIN : relie le BP aux trois BA en étoile autour d'un plan 0 V, à la place du chaînage d'origine, pour relever le seuil du courant d'équilibrage qui a détruit le bus I2C lors de la foudre d'août 2026. Depuis la révision B, elle porte aussi un module ESP32 qui écoute le bus sans pouvoir y émettre, surveille sa santé et le +15 V, horodate les surtensions et gère une alarme intrusion sur batterie.

| | |
|---|---|
| **Catégorie** | Matériel – carte annexe (KiCad 9) et firmware ESP-IDF |
| **Dépôt** | `essensys-hub/essensys-i2c-etoile-0v` (public) |
| **Statut** | Révision B conçue (schéma, PCB routé, BOM, Gerber, ERC/DRC 0 erreur), non fabriquée ; firmware construit et testé sur PC ; essais de banc à faire |
| **Changes** | Partie bus : `i2c-surge-protection-2026-10-007`, tâche 4.1, ticket `essensys-hub/essensys-board-SC944D#1`. Module : [[N2 Esp32 Spy Alarm 2026 10 008]], ticket `essensys-hub/essensys-feature-lifecycle#28` |
| **Documentation publique** | Page « Module N2 ESP32 » de [[Essensys DOC]] (`install/module-n2-esp32`), en ligne depuis le 2026-10-12 |

## Rôle

Mesure de court terme décrite dans [[Ilots TBTS Et Equipotentialite]] (variante N2) à la suite de l'[[Incident Foudre Bus I2C 2026 08]]. Le bus du BP ([[Essensys Board Sc944d]], connecteur J31) arrive sur la carte et repart vers chaque BA ([[Essensys Board Sc940]], [[Essensys Board Sc941c]], [[Essensys Board Sc942c]]) par deux faisceaux AWG20 de 15 cm au plus (J1 et J2 du BA). Le 0 V du BP est doublé par une queue de cochon soudée sur la broche traversante J31-3.

## Contenu

- Révision A : 110 × 68 mm ; révision B : 235 × 68 mm (zone bus à gauche, inchangée ; zone module à droite). 2 couches, cuivre 2 oz, plan 0 V double face ; trous de fixation non reliés, support DIN isolant.
- Par port BA : cavalier 2×3 qui coupe SDA, SCL et +15 V (jamais le 0 V), PTC 1812 ≥ 30 V puis TVS SMAJ16A sur le +15 V.
- Connecteurs WR-MPC3 2×2 (1 SDA, 2 SCL, 3 0 V, 4 +15 V) ; empreinte et PTC à confirmer avant fabrication.
- Le 0 V TBTS n'est jamais relié au PE ; repérage « 0 V TBTS – NE PAS RELIER À LA TERRE ».

## Module ESP32 (révision B)

Change [[N2 Esp32 Spy Alarm 2026 10 008]], hébergé dans ce dépôt (5 capacités, 28 tâches, sous-issues `#1` à `#9`). PR de conception et de firmware fusionnée le 2026-10-12 ; avancement 9/28, le reste demande le banc.

| Fonction | Choix |
|---|---|
| Écoute du bus | Isolateur ISO7720, deux canaux **bus → module** : côté bus il n'y a que des entrées, aucun logiciel ne peut tirer SDA/SCL. Cavalier JP4 pour couper l'écoute |
| Microcontrôleur | ESP32-C3-MINI-1, Wi-Fi, firmware ESP-IDF v5.3.2 (profils dev et release : Secure Boot V2, flash chiffrée) |
| Séparation | Plan 0 V (bus) et plan GND (module) séparés par un sillon, reliés en un seul point ; aucune liaison au PE |
| Alimentation | +15 V du bus par une PTC propre de 0,2 A, anti-retour, TVS ; abaisseur 15 → 5 V puis LDO 3,3 V. Un défaut du module ouvre sa PTC sans couper les BA |
| Secours | LiFePO4 18650 1,5 Ah, chargeur CN3058E (200 mA, 3,6 V), basculement sans coupure ; autonomie de conception ≈ 25 h avec le Wi-Fi en économie |
| Mesures | 4 × MCP3428 : +15 V en amont et en aval de chaque PTC, VBAT, écart de 0 V par port, boucles d'alarme, sortie sirène |
| Surtensions | Latch matériel (LM339 + 74HC74) : écart de 0 V au-delà de ±1 V ou +15 V au-delà de 20 V, même pour quelques µs ; horodatage par RTC RV-3028 secourue, NTP quand le réseau est là |
| Alarme | 4 boucles équilibrées (repos, détection, court-circuit, coupure), zones instantanées, temporisées (30 s) ou 24 h, clé d'armement, sirène 12 V sur batterie (3 min max). Pas certifiée EN 50131 |
| Réseau | MQTT sur TLS uniquement, topics `essensys/n2/<id>/…` ; une seule souscription, `cmd`, pour des commandes signées HMAC-SHA256 avec anti-rejeu ; aucune commande n'agit sur le bus |

Événements journalisés (mémoire non volatile, 256 entrées, effaçables seulement en local) : BA muet (10 s), ligne SDA/SCL collée (> 100 ms), +15 V bas (< 13 V), PTC déclenchée, cavalier ouvert, passage sur batterie, batterie faible, surtension, écart de 0 V, événements d'alarme et de sécurité.

**Points à relire avant fabrication** : routage automatique (boucles de commutation, pistes sous le porte-pile, lignes de mesure), empreintes ESP32-C3 et supercondensateur, brochage du CN3058E, tenue du BTS4140N, adresses des MCP3428, rétro-alimentation possible de l'ISO7720 hors tension (parade : 10 kΩ au lieu de 1 kΩ, ou JP4 retiré), console USB sans authentification.

**Lien avec [[Essensys I2c Ba Sniffer 2026 07 038]]** : ce change antérieur prévoit un sniffer passif sur Raspberry Pi Pico, outil de diagnostic posé ponctuellement. Le module N2 en reprend le principe (aucune émission, décodage des trames et du CRC) mais reste installé en permanence et ajoute la surveillance, la preuve des surtensions et l'alarme.

## Code pointers

- `scripts/n2_module.py` : composants et nets du module (source unique du schéma et du PCB)
- `firmware/components/n2_core/` : logique pure testée sur PC (décodeur, santé du bus, alarme, surtensions, commandes)
- `firmware/main/` : application ESP-IDF (HAL, écoute, réseau, OTA, console)
- `firmware/test/check_no_bus_write.sh` : garde « aucune écriture sur le bus »

## Vérifications restantes

Partie bus : tâches 4.2 (faisceaux < 60 mΩ), 4.3 (seuil d'équilibrage ≥ 4 fois la référence, ΔVg ≤ 0,05 V) et 4.4 (sélectivité des PTC) du change parent. Module : alimentation et batterie, santé du bus, alarme, surtensions, MQTT, OTA et tests `NR-i2c-etoile-0v-*`. Tout sur banc uniquement, jamais sur une armoire en service. Le modèle corrigé du change donne ≈ 80 à 120 A en 8/20 et ≈ 50 à 65 A en front rapide.

## Voir aussi

- [[N2 Esp32 Spy Alarm 2026 10 008]]
- [[Essensys I2c Ba Sniffer 2026 07 038]]
- [[Incident Foudre Bus I2C 2026 08]]
- [[Ilots TBTS Et Equipotentialite]]
- [[Protection Surtension Bus I2C]]
