---
tags: [concept, essensys, firmware, protocole, authentification, legacy]
sources: [analyses/2026-10-cle-acces-distance/analyse.md]
created: 2026-10-13
updated: 2026-10-13
era: legacy
---

# Cle Acces Distance

La « clé d'accès à distance » est une clé de 32 chiffres saisie sur l'écran ([[Essensys Board SC945D]]), dans **Réglages → Accès à distance**. Elle donne au BP ([[Essensys Board Sc944d]]) son identité auprès du serveur legacy. Source : [[Analyse Cle Acces Distance 2026 10]].

## Cycle de vie

1. **Génération** : par l'ancien site [[Essensys WEB Legacy]], à la création du compte. C'était une clé aléatoire ; le site en stockait le MD5 (`HashedPkey`).
2. **Saisie** : 16 octets aux index 922 à 937 de la [[Table D Echange]], en écriture seule. La page écran ne la réaffiche jamais : ses tirets sont un gabarit fixe.
3. **Persistance** : dans l'EEPROM SPI du BP (0x00 à 0x0F, à côté du code alarme et de la MAC). La clé se perd quand on remplace le BP.
4. **Prise en compte** : à chaud. La boucle principale détecte le changement, écrit l'EEPROM et rappelle `cryptage()`.
5. **Usage** :
   - l'en-tête `Authorization: Basic`, sous la forme base64(« MD5[0:16] : MD5[16:32] ») de la chaîne `'0' + demi-octet` ;
   - le déchiffrement AES de l'ordre d'alarme distant `_de67f`.

## Effet sur les actions

| Serveur | Clé absente ou fausse |
|---|---|
| ASP.NET legacy (disparu) | 401 sur `serverinfos`. Le BP ne demande jamais `myactions`, le voyant SERVEUR est rouge, **aucune action**. |
| Gateway CM5 ([[Essensys Server Backend]]) | Aucun effet. L'authentification est désactivée, la file est globale et `_de67f` vaut toujours `null`. |
| Hub cloud ([[Essensys User Portal Backend]]) | Machine `UNKNOWN-…` inactive, et 403 sur `myactions`. Ce cas ne se présente pas tant que `mon.essensys.fr` est réécrit vers la gateway sur le segment armoire. |

**Règle pratique :** si le voyant SERVEUR est vert, la clé n'est pas en cause.

## Voir aussi

- [[Ajout BP Gateway CM5]]
- [[Dual Protocol]]
- [[LAN IAM]]
