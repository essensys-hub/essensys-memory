## 1. Documentation

- [x] 1.1 Wiki [[Gateway PKI]] (`wiki/concepts/gateway-pki.md`)
- [x] 1.2 Backlinks Platform Overview / Gateway Exchange / Index

## 2. Phase 1 — Enrollment

- [ ] 2.1 Migration PG `client_cert_fingerprint` (ou table dédiée)
- [ ] 2.2 API admin enroll CSR → cert signé
- [ ] 2.3 Ansible : génération CSR / déploiement cert gateway

## 3. Phase 2 — mTLS optionnel

- [ ] 3.1 `cloudsync` : `tls.Config` + cert client
- [ ] 3.2 nginx OVH : `ssl_verify_client optional` sur `/api/gateway/`
- [ ] 3.3 Tests : gateway avec cert seul, token seul, les deux

## 4. Phase 3 — TPM + strict

- [ ] 4.1 Intégration TPM CM5 (NixOS puis Ansible)
- [ ] 4.2 nginx `ssl_verify_client on` ; retrait token obligatoire
- [ ] 4.3 Procédure révocation / rotation cert
