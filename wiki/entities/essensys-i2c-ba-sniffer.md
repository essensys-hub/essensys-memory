---
tags: [entity, repo, outil, debug, i2c, sigrok, python, kicad, fritzing]
sources: [analyses/2026-10-cle-acces-distance/analyse.md]
created: 2026-10-13
updated: 2026-10-13
era: modern
repo: essensys-i2c-ba-sniffer
---

# Essensys I2C BA Sniffer

> Dépôt public `essensys-hub/essensys-i2c-ba-sniffer` : espion **strictement passif** du bus I2C BP ↔ BA. Il repose sur un analyseur logique USB (`fx2lafw`), `sigrok-cli` et un décodeur Python du protocole Essensys. La sonde à trois fils est documentée en KiCad et Fritzing. Voir [[Espion I2C Passif]].

## Rôle

L'outil dit **où** se perd une commande que le BP a acquittée auprès de la gateway :
- BA absent (NACK d'adresse) ;
- trame rejetée (écho CRC `00 00`) ;
- ligne SDA ou SCL bloquée ;
- abandon du maître après répétitions ;
- aucune trame émise.

Il rapproche aussi les journaux du backend CM5 (`Sending Actions` / `Action acknowledged`) des trames observées sur le bus.

## Structure

| Dossier | Contenu |
|---|---|
| `decoder/essensys_i2c_sniffer/` | Paquet Python ≥ 3.11 sans dépendance. CLI `essensys-i2c-sniff` (live, replay, annotations, correlate) |
| `captures/corpus/` | 10 scénarios synthétiques annotés par le décodeur I2C de sigrok (oracle), avec leur sortie NDJSON attendue |
| `tests/` | 76 tests, dont `NR-i2c-ba-sniffer-1` à `-6` |
| `hardware/kicad/` | Schéma généré de la sonde (ERC 0, KiCad 10) et ses exports |
| `hardware/fritzing/` | Câblage généré BA → sonde → FX2 → Raspberry Pi, vue platine exportée |
| `openspec/changes/i2c-ba-sniffer-2026-10-009/` | Change OpenSpec : 6 capacités, 8 groupes de tâches |

## Points d'attention

- **Un seul flux brut**, partagé entre le décodeur I2C de sigrok et la détection des lignes bloquées. Le rejeu est identique au direct (fusion par numéro d'échantillon).
- Le décodeur `timing` de sigrok a été écarté : il ne donne pas le niveau de la ligne.
- **CI** : pytest avec sigrok sur Ubuntu, contrôle d'anonymisation, ERC KiCad dans `kicad/kicad:10.0`. L'image 9.0 n'ouvre pas un schéma dont les symboles viennent de la bibliothèque KiCad 10.
- **Fritzing** : le générateur lit la position des connecteurs dans les SVG des pièces (90 px par pouce). Les pièces génériques créées à la volée sont copiées dans `hardware/fritzing/partfactory/`. Fritzing affiche le texte des notes en HTML, donc pas de `<->` dedans.

## Suivi

- Feature `i2c-ba-sniffer-2026-10-009`, ticket essensys-hub/essensys-feature-lifecycle#29, sous-issues essensys-i2c-ba-sniffer#1 à #6, essensys-doc#9, essensys-memory#16.
- Doc publique : `docs/debug/espion-i2c.md` dans [[Essensys DOC]] (www.essensys.fr/docs/debug/).
- Phase 2 (capture autonome sur Raspberry Pi Pico) : [[Essensys I2c Ba Sniffer 2026 07 038]]. Version permanente : module ESP32 de [[Essensys I2C Etoile 0v]].
