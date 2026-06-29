---
tags: [concept, responsive, ux, navigation, hamburger, support-site, lifecycle, playwright]
sources: [essensys-support-nav-responsive-2026-06-032]
created: 2026-06-28
updated: 2026-06-28
era: modern
---

# Support Site Responsive Nav

Correction de la navigation et de la page Support du site `mon.essensys.fr` pour une adaptation correcte sur iPhone, iPad, et ordinateur.

## Problème résolu

La navigation principale et la page `/support` ne s'adaptaient pas aux écrans mobiles et tablettes :
- Sur iPhone : le menu de navigation débordait ou s'empilait sans toggle
- Sur iPad : aucun breakpoint intermédiaire défini
- La page Support : une seule règle `max-width: 600px` sans tap targets adaptés

## Solution implémentée

### Breakpoints CSS

| Format | Breakpoint | Comportement |
|---|---|---|
| Desktop | > 1024px | Nav horizontale, hamburger masqué |
| iPad | 768–1024px | Nav compacte, card support pleine largeur |
| iPhone | ≤ 768px | Menu hamburger ☰, nav en drawer vertical |
| iPhone petit | ≤ 480px | Padding minimal, font-size réduit |

### Bouton hamburger (Layout.jsx)

- `useState menuOpen` dans Layout.jsx
- `aria-expanded` pour l'accessibilité
- Fermeture automatique au clic sur un lien (`closeMenu`)
- CSS : `max-height: 0` → `max-height: 400px` avec transition 0.3s

## Fichiers modifiés

| Fichier | Modification |
|---|---|
| `site/src/components/Layout.jsx` | Ajout hamburger + state menuOpen |
| `site/src/components/Layout.css` | Breakpoints iPad + mobile + hamburger |
| `site/src/pages/Support.css` | Breakpoints iPad + iPhone, tap targets 44px |

## Tests Playwright

- `site/e2e/support-responsive.spec.js` — tests desktop + iphone + ipad
- Playwright config : projects `desktop` (1280×800), `iphone` (iPhone 14), `ipad` (iPad Pro)
- Manifest : `ux_matrix.required: true`, devices `[desktop, iphone, ipad]`

## Feature lifecycle

- OpenSpec : `essensys-support-nav-responsive-2026-06-032`
- Manifest : `features/essensys-support-nav-responsive-2026-06-032.json`
- Gate : `check_feature_gate.py --strict` → OK
- Build : `npm run build` → ✅

## Liens

- [[ESSENSYS UX Matrix Gate]] — règle qui impose cette matrice pour toute feature UI
- [[Kitchen Shutter Test Console]] — autre feature ayant utilisé la même gate
