---
tags: [synthesis, essensys, installation, gateway, firmware, exploitation]
sources: [analyses/2026-10-cle-acces-distance/analyse.md]
created: 2026-10-13
updated: 2026-10-14
era: legacy
---

# Ajout BP Gateway CM5

> Ajouter ou remplacer un boîtier principal ([[Essensys Board Sc944d]]) sur une gateway CM5. Procédure publiée dans [[Essensys DOC]] : `docs/install/ajout-bp.md` (ticket essensys-hub/essensys-doc#7). Elle remplace la « Procédure de création de compte Essensys v3 », liée au site ASP.NET disparu.

## À retenir

- **Clé d'accès à distance facultative** avec la gateway : voir [[Cle Acces Distance]].
- **Le BP neuf démarre en configuration d'usine.** Restent dans l'ancien BP :
  - les paramètres `RWS` en flash : plannings, scénarios, réveils, temps et modes des variateurs, configuration de l'alarme ;
  - le code alarme et la clé, en EEPROM.

  La synchronisation planifiée `cloudsync` **lit** l'armoire, puis pousse vers le cloud : après le remplacement, elle publie la configuration d'usine.
- **La configuration des BA n'est pas renvoyée** au démarrage. Il faut modifier chaque paramètre puis le rétablir.
- **Contrôles, tous en lecture seule** :
  - voyant CABLE › DHCP › DNS › SERVEUR ;
  - bail dnsmasq sur le segment armoire ;
  - `Status Update` toutes les ~2 s ;
  - index 12 via `/table_ref` (`& 0x1C` doit valoir 0).
- **Acquitté n'est pas exécuté.** Le BP envoie `/api/done` avant l'envoi I2C. Il faut constater l'effet, avec un essai par BA.

## Premier cas (2026-10-13)

Après l'[[Incident Foudre Bus I2C 2026 08]], le BP et le SC940D ont été remplacés.

- Le BP dialogue normalement et les 15 actions de test ont été acquittées.
- Les 15 visaient les BA CHB ([[Essensys Board Sc942c]]) et PDE ([[Essensys Board Sc941c]]), qui sont en défaut (index 12 = 0x18).
- Le symptôme « aucune action exécutée » vient de l'I2C, pas de la clé.

Le 2026-10-13, l'entrée (BA PDV, [[Essensys Board Sc940]] neuf) s'allume, mais les sorties des BA CHB et PDE ne répondent toujours pas (index 12 = 0x18). La saisie d'une clé n'y change rien. L'identité des BA est figée dans leur firmware, sans appairage : voir [[Espion I2C Passif]]. Pour trancher entre un BA absent, une trame rejetée et un bus bloqué, utiliser l'outil [[Essensys I2C BA Sniffer]]. Suivi : essensys-hub/essensys-board-SC944D#2.

Le 2026-10-14, [[Analyse Demarrage BP BA 2026 10]] montre que le code ne connaît ni appairage ni préférence pour les cartes neuves. Le SC940D, en bout de chaîne, prouve que le bus est sain. Restent deux causes possibles, propres aux deux anciens BA : un dégât de la foudre (le plus probable) ou un firmware antérieur à la v1.5. La LED DL1 et la console Espion du BP permettent de trancher.

## Voir aussi

- [[Analyse Cle Acces Distance 2026 10]]
- [[Analyse Demarrage BP BA 2026 10]]
- [[Protection Surtension Bus I2C]]
- [[Essensys Server Backend]]
