## Why

La roadmap produit (`prompts/roadmap-product.md`) ne doit pas rester un document chat éphémère. Il faut une **rubrique OpenSpec** dans `essensys-memory` qui :

- impose **Phase 0** (doc centralisée + doc install) avant les changes feature ;
- découpe les futurs devs en **changes petits et autonomes** ;
- maintient `wiki/synthesis/product-roadmap.md` comme vue Now / Next / Later liée aux changes.

Sans ce change cadre, les agents replanifient en greenfield ou dupliquent les OpenSpec existants.

## What Changes

- Page **`wiki/roadmap/product-roadmap-rubric.md`** — ordre des phases, règles, template de découpage.
- **`wiki/synthesis/product-roadmap.md`** — matrice gap + priorités (vivante, mise à jour à chaque revue).
- Lien explicite rubrique ↔ `wiki/roadmap/index.md` (OpenSpec technique) ↔ roadmap produit (priorisation).
- Prompt `prompts/roadmap-product.md` aligné sur ce workflow.

## Capabilities

### New Capabilities

- `product-roadmap-rubric` : structure phases, critères de découpage change, gate Phase 0.
- `product-roadmap-living-doc` : format et fréquence de mise à jour de `product-roadmap.md`.

### Modified Capabilities

- `openspec-roadmap` : section « Roadmap produit » dans l’index.

## Impact

- **essensys-memory** uniquement (wiki + OpenSpec meta).
- **Aucun code applicatif** dans ce change — cadrage et doc.
- Bloque sémantiquement les nouveaux epics feature tant que Phase 0 doc/install n’est pas **completed**.

## Dépendances

- **Prérequis** (Phase 0, changes séparés) :
  - `essensys-centralized-doc-maintenance`
  - `essensys-install-doc-platform`
- Ensuite seulement : changes feature (mTLS, trusted devices, wizard, …) référencés dans `product-roadmap.md`.

## Liens wiki

- [[Roadmap OpenSpec]]
- [[Platform Overview]]
- [[Migration Legacy To Modern]]
