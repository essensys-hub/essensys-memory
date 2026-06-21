## Context

`essensys-brain.mdc` couvre le « quand mettre à jour le brain » mais pas **quelle doc dépôt** ni **quelle page wiki** pour chaque type de changement.

## Décisions

1. **Canon** : code + README dépôt = source opérationnelle ; **brain** = synthèse traçable (`wiki/entities`, `wiki/concepts`, `raw/` sync).
2. **Règle Cursor** `essensys-centralized-doc.mdc` : `alwaysApply: false`, globs par type de dépôt.
3. **Checklist PR** étendue dans `AGENTS.md`.

## Cartographie (extrait — compléter dans tasks)

| Type de changement | Dépôt(s) | Mettre à jour |
|--------------------|----------|---------------|
| API domotique | server-backend + portal-backend | concept Gateway Exchange, jumeaux sync, brain si indices k/v |
| UI domotique | server-frontend + portal-frontend | parité jumeaux, pas de page wiki sauf nouveau concept |
| Protocole legacy | server-backend | `raw/protocol/`, [[Dual Protocol]], [[Table D Echange]] |
| OpenSpec nouveau | hôte + memory | `update-roadmap.sh`, page change, log |
| Architecture dépôt | docs/architecture | sync-sources + entité wiki |

## Non-goals

- Remplacer la doc inline des README par le wiki.
- Générer doc from code (phase ultérieure).
