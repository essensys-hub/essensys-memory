## Context

Document de référence : `wiki/concepts/gateway-pki.md`. État actuel vérifié dans `internal/cloudsync/sync.go` et `GatewayAuth`.

## Décisions

1. **Périmètre mTLS** : uniquement `/api/gateway/*` — pas `/api/portal/*` ni legacy IoT WAN.
2. **Terminaison** : nginx OVH en priorité (`ssl_verify_client`) ; validation Go en fallback optionnel.
3. **Bascule** : 3 phases (token → token+cert → cert seul).
4. **CA** : CA interne Essensys pour gateways ; LE reste pour SAN public `mon.essensys.fr`.

## Risques

- Gateways déjà en prod sans TPM : phase 1 soft-key acceptable, migration par re-register.
- Mode nginx consolidé vs dual : deux snippets à maintenir jusqu’à un seul vhost.

## Open questions

- Hardware TPM sur carrier CM5 Essensys (schéma PCB).
- Fichier nginx principal OVH mode consolidé pour `/api/gateway/`.
