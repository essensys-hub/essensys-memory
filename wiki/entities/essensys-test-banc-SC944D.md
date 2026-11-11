---
tags: [entity, repo, hardware, test, production, bp, archives]
sources: [analyses/2026-11-banc-test-bp/synthese.md]
created: 2026-11-11
updated: 2026-11-11
era: legacy
repo: essensys-test-banc-SC944D
---

# Essensys Test Banc SC944D

> Archives et documentation du banc de test de production du boîtier principal ([[Essensys Board Sc944d]]) : interface à lit de clous, carte d'interface SI841A, spécification du logiciel de test.

| | |
|---|---|
| **Catégorie** | Matériel – outillage de test de production (archives 2014-2015) |
| **Dépôt** | `essensys-hub/essensys-test-banc-SC944D` (**privé** : plans du fabricant de l'interface mécanique, documents de fabricants, spécification marquée confidentielle) |
| **Statut** | Archivé et documenté le 2026-11-11 ; banc physique retrouvé, non remis sous tension |
| **Ticket** | `essensys-hub/essensys-doc#36` |
| **Documentation publique** | Page « Banc de test du BP » de [[Essensys DOC]] (`debug/banc-de-test-bp`) |

## Rôle

Contrôler une carte BP à la sortie de fabrication : alimentations sous secteur et sous secouru, pilotage et forçage du +15VSP, alimentations d'alarme, bus BA, puis entrées et sorties à la main. Détail : [[Banc Test BP 2026 11]].

## Contenu du dépôt

| Dossier | Contenu |
|---|---|
| `carte-interface-SI841A/` | Schéma PDF (19 folios), Gerber avant routage, dessin de face avant, sérigraphies |
| `points-de-test-SC944/` | Position et nom des 74 points de test |
| `logiciel/` | Spécification du logiciel de test, v0 à v4, et transcription Markdown de la v4 |
| `mecanique-arf-test-6281/` | Dossier d'étude mécanique de l'interface, nomenclature |
| `etude/`, `datasheets/`, `photos/` | Croquis, scans, fiches techniques, photos de 2016 et 2026 |
| `docs/` | Documentation rédigée (8 pages) et table de correspondance ancien nom → nouveau nom |

## À savoir

- La **SI841A** (carte d'interface du banc) n'est pas la SC841A de [[Essensys Board SC841A]].
- Le code du dsPIC33 du banc n'est pas archivé : seule la spécification existe.
- Ne rien copier de ce dépôt vers un dépôt public sans vérifier les droits.

## Source

`raw/analyses/2026-11-banc-test-bp/synthese.md`
