## Why

L’authentification gateway cloud repose sur un **secret partagé** (`gateway_token`) et des **MAC Ethernet** en headers — suffisant pour le NAT traversal initial, insuffisant pour une identité matérielle forte et une révocation fine. Voir [[Gateway PKI]].

## What Changes

- **Phase 1** : enrollment CSR → certificat client + fingerprint en `gateway_sessions`.
- **Phase 2** : mTLS optionnel sur `/api/gateway/*` (nginx OVH + `tls.Config` cloudsync).
- **Phase 3** : clé TPM 2.0 CM5, mTLS obligatoire, dépréciation token seul.

## Impact

| Composant | Impact |
|-----------|--------|
| [[Essensys Server Backend]] | `internal/cloudsync/` — transport TLS client |
| [[Essensys User Portal Backend]] | Middleware cert + migration PG |
| [[Essensys Ansible]] | nginx `ssl_verify_client`, CA, vault |
| [[Essensys Raspberry Gateway]] / [[Essensys Gateway Nixos]] | TPM SPI, enrollment first-boot |
| Protocole legacy firmware | **Aucun** |

## Liens wiki

- [[Gateway PKI]]
- [[Gateway Exchange]]
- [[Cloud Relay]]
