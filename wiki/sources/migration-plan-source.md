---
tags: [source, migration, plan]
sources: [MIGRATION_PLAN.md]
created: 2026-06-20
updated: 2026-06-20
---

# Migration Plan Source

**Source:** `raw/plans/MIGRATION_PLAN.md`  
**Date ingested:** 2026-06-20  
**Type:** plan de migration

## Summary

Plan de migration [[Essensys Web Legacy]] + [[Client Essensys Legacy]] vers [[Essensys Server Backend]] (Go) et [[Essensys Server Frontend]] (React).

## Key Claims

- Protocole legacy IoT **déjà supporté** par le backend Go ✅
- Reste à migrer : users, machines, persistance PostgreSQL, services métier, AES alarmes, auth frontend
- Architecture dual-protocol : legacy endpoints sacrés, nouveaux `/api/auth/*`, `/api/user/*`
- Frontend : UI domotique ✅, pages auth/account ❌

## Synthèse wiki

Voir [[Migration Legacy To Modern]] pour la vue consolidée à jour.
