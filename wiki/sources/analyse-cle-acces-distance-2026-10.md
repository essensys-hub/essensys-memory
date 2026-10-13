---
tags: [source, essensys, firmware, protocole, gateway, authentification, diagnostic]
sources: [analyses/2026-10-cle-acces-distance/analyse.md]
created: 2026-10-13
updated: 2026-10-13
era: legacy
---

# Analyse Cle Acces Distance 2026 10

**Source :** `raw/analyses/2026-10-cle-acces-distance/analyse.md`
**Type :** analyse de code et diagnostic d'exploitation, anonymisés

## Métadonnées

| Champ | Valeur |
|---|---|
| Date | 2026-10-13 |
| Déclencheur | Premier BP neuf posé sur une gateway CM5 après l'[[Incident Foudre Bus I2C 2026 08]] : « la gateway voit le BP mais aucune action n'est exécutée » |
| Périmètre | Firmware 099-37 ([[Client Essensys Legacy]]), écran [[Essensys Board SC945D]], [[Essensys WEB Legacy]] (ASP.NET), [[Essensys Server Backend]] |
| Méthode | 7 lecteurs parallèles, chaque hypothèse vérifiée selon 3 angles, puis diagnostic SSH en lecture seule sur la gateway |
| Suivi | essensys-hub/essensys-doc#7 (procédure), essensys-hub/essensys-board-SC944D#2 (remise en service) |

## Affirmations clés

- La [[Cle Acces Distance]] ne sert qu'à deux choses : l'en-tête `Authorization: Basic` (MD5) et le déchiffrement AES de l'ordre d'alarme distant `_de67f`. Le firmware ne teste jamais sa validité.
- Elle n'a bloqué les actions qu'avec l'ancien serveur ASP.NET, qui répondait 401 à une clé inconnue. Le voyant SERVEUR restait alors rouge.
- Avec la gateway CM5, l'authentification legacy est désactivée et la file d'actions Redis est globale : un BP sans clé fonctionne.
- La clé est dans l'EEPROM du BP et se perd au remplacement. Une clé saisie est prise en compte à chaud, sans redémarrage.
- Le BP acquitte `/api/done` **avant** l'envoi I2C aux BA, donc un acquittement ne prouve pas l'exécution.
- `GET /table_ref` ne vide pas la file (`LRANGE` sans retrait). Cette affirmation, d'abord erronée, a été corrigée pendant l'analyse.

## Diagnostic du 2026-10-13

15 actions de test, toutes acquittées en 1 à 2 s. Toutes visaient les BA CHB et PDE. L'index 12 vaut 0x18 : ces deux BA sont en défaut et le BA PDV répond.

Les actions sont donc perdues sur l'I2C, pas à cause de la clé. Voir [[Ajout BP Gateway CM5]].
