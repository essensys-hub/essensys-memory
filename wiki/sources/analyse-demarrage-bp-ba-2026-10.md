---
tags: [source, essensys, firmware, i2c, diagnostic, sc944d, sc940d, sc941c, sc942c]
sources: [analyses/2026-10-demarrage-bp-ba/analyse.md]
created: 2026-10-14
updated: 2026-10-14
era: legacy
---

# Analyse Demarrage BP BA 2026 10

**Source :** `raw/analyses/2026-10-demarrage-bp-ba/analyse.md`
**Type :** analyse de code anonymisée (firmware BP 099-37, firmware BA v1.7, 22 fichiers `.hex` des BA)

## Métadonnées

| Champ | Valeur |
|---|---|
| Date | 2026-10-14 |
| Déclencheur | Après l'[[Incident Foudre Bus I2C 2026 08]], seuls le BP neuf et le SC940D neuf dialoguent ; index 12 = 0x18 (CHB 0x12 et PDE 0x13 en défaut) |
| Périmètre | [[Essensys Board Sc944d]], [[Essensys Board Sc940]], [[Essensys Board Sc941c]], [[Essensys Board Sc942c]] |
| Méthode | Lecture du code BP et BA, comparaison des archives BP 095 à 099, décodage des `.hex` (polynôme CRC `0xA001`, valeur de `SSPADD`) |
| Suivi | essensys-hub/essensys-board-SC944D#2 |

## Affirmations clés

- **Ni appairage, ni présentation, ni négociation de version.** Le BP appelle chaque BA à une adresse fixe (`0x11 + n`, I2C à 50 kHz). Le BA répond dès que son PIC tourne. Rien ne permet à des boîtiers neufs de se « reconnaître ».
- **Le bus est sain.** Le SC940D est en bout de chaîne (BP → SC942C → SC941C → SC940D). Il reçoit SDA, SCL et +15 V à travers les connecteurs des deux anciens BA.
- **Démarrage du BP** : les BA sont alimentés par le BP (`+15VSP`), environ 1,6 s après son démarrage. Ce +15 V est coupé en mode secouru. **Aucune configuration n'est poussée au démarrage** : le bus reste silencieux jusqu'au premier ordre, et un BA en panne n'apparaît en défaut qu'après un ordre qui le vise.
- **Démarrage d'un BA** (PIC16F946) : aucune attente du BP, configuration relue en EEPROM, I2C entièrement en interruption, pas de watchdog, pas de mode de repli. La LED DL1 clignote une fois par seconde quel que soit l'état de l'I2C.
- **Historique du protocole** :
  - BA 1.30 à 1.4 : somme de contrôle 8 bits, trames 10/10/18/10/3, incompatibles avec le BP 099-37 ;
  - **BA 1.5 et suivantes : CRC16**, compatibles ;
  - BA 1.10 : pas d'I2C du tout.

  Tous les BP archivés (095-34 à 099-37) sont en CRC16. Les adresses sont les mêmes dans toutes les versions.
- **Causes probables, dans l'ordre** :
  1. dégât de la foudre sur les anciens BA : broches RC6/RC7 du PIC, alimentation (U1, D3, C2, D6, FI1), quartz ;
  2. firmware antérieur à 1.5, peu probable si le BP d'avant la foudre était en version 095 ou plus récente.
- **Signatures pour trancher** :
  - console Espion du BP : `ErreursDialogueBA` = 0x0002 (NACK, matériel) ou 0x0100 (ancien firmware) ;
  - LED DL1 : éteinte (alimentation), figée (quartz ou plantage) ;
  - espion I2C : NACK, ou réponse terminée par `55 55`.
- **Piège** : les `.hex` de `essensys_ba.X/dist/` répondent tous en 0x12. Ne reflasher que `Prog/ba v1_7 <type>.hex`.

## Pages liées

- [[Espion I2C Passif]], [[Essensys I2C BA Sniffer]] : la capture qui tranchera sur le bus
- [[Ajout BP Gateway CM5]] : le premier cas, où les actions sont acquittées mais non exécutées
- [[Analyse Cle Acces Distance 2026 10]] : la clé d'accès à distance est hors de cause
