---
tags: [concept, protocol, legacy, backend]
sources: [README.md, essensys-server-backend.md]
created: 2026-06-20
updated: 2026-06-20
era: migration
---

# Dual Protocol

Le backend [[Essensys Server Backend]] gère **deux protocoles HTTP incompatibles** simultanément.

## Legacy IoT (clients embarqués)

- Endpoints figés : `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}`
- JSON malformé (clés non quotées) → normalisation
- Header `Content-Type: application/json ;charset=UTF-8` (espace avant `;`)
- Réponse **single-packet TCP**
- Basic Auth, alarmes chiffrées AES

## Web moderne

- REST/JSON standard, JWT/sessions
- `/api/auth/*`, `/api/user/*`, `/api/admin/inject`, `/api/gateway/*`

## Clients

| Protocole | Clients |
|-----------|---------|
| Legacy | [[Client Essensys Legacy]], [[Essensys Board SC944D]] |
| Modern | [[Essensys Server Frontend]], apps mobiles, [[Essensys Homeassitant]] |

**Règle :** toute modification du protocole legacy exige mise à jour du brain + tests de non-régression.
