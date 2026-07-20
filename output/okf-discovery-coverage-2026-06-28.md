# OKF Discovery Coverage Report

Date: 2026-06-28
Change: `essensys-okf-discovery-2026-06-029`

## Summary

- Repositories discovered: 39
- Repositories covered by OKF: 39
- OKF concept documents: 104
- Missing repository coverage: 0

## Repository coverage

- covered: `client-essensys-legacy` — layer `firmware`, era `legacy`
- covered: `essensys-android-phone-apps` — layer `tooling`, era `modern`
- covered: `essensys-ansible` — layer `infra`, era `modern`
- covered: `essensys-api-doc` — layer `documentation`, era `modern`
- covered: `essensys-base` — layer `infra`, era `modern`
- covered: `essensys-board-SC840B` — layer `firmware`, era `legacy`
- covered: `essensys-board-SC841A` — layer `firmware`, era `legacy`
- covered: `essensys-board-SC843D` — layer `firmware`, era `legacy`
- covered: `essensys-board-SC940` — layer `firmware`, era `legacy`
- covered: `essensys-board-SC941C` — layer `firmware`, era `legacy`
- covered: `essensys-board-SC942C` — layer `firmware`, era `legacy`
- covered: `essensys-board-SC944D` — layer `firmware`, era `legacy`
- covered: `essensys-board-SC945D` — layer `firmware`, era `legacy`
- covered: `essensys-board-SC946D` — layer `firmware`, era `legacy`
- covered: `essensys-board-SC947-xB` — layer `firmware`, era `legacy`
- covered: `essensys-control-plane` — layer `gateway-lan`, era `modern`
- covered: `essensys-doc` — layer `documentation`, era `modern`
- covered: `essensys-feature-lifecycle` — layer `documentation`, era `modern`
- covered: `essensys-gateway` — layer `gateway-lan`, era `modern`
- covered: `essensys-gcc` — layer `tooling`, era `modern`
- covered: `essensys-homeassitant` — layer `tooling`, era `modern`
- covered: `essensys-ios-phone-apps` — layer `tooling`, era `modern`
- covered: `essensys-mcp` — layer `tooling`, era `modern`
- covered: `essensys-memory` — layer `documentation`, era `modern`
- covered: `essensys-mosquitto` — layer `infra`, era `modern`
- covered: `essensys-n8n` — layer `tooling`, era `modern`
- covered: `essensys-nginx` — layer `infra`, era `modern`
- covered: `essensys-prometheus` — layer `infra`, era `modern`
- covered: `essensys-raspberry-gateway` — layer `gateway-lan`, era `modern`
- covered: `essensys-raspberry-install` — layer `gateway-lan`, era `modern`
- covered: `essensys-redis` — layer `infra`, era `modern`
- covered: `essensys-server-backend` — layer `gateway-lan`, era `modern`
- covered: `essensys-server-frontend` — layer `gateway-lan`, era `modern`
- covered: `essensys-support-site` — layer `cloud`, era `modern`
- covered: `essensys-traefik` — layer `infra`, era `modern`
- covered: `essensys-user-portal-backend` — layer `cloud`, era `modern`
- covered: `essensys-user-portal-frontend` — layer `cloud`, era `modern`
- covered: `essensys-utils` — layer `tooling`, era `modern`
- covered: `essensys-web-legacy` — layer `legacy`, era `legacy`

## Mandatory legacy / architecture coverage

- covered: Armoire architecture — `okf/synthesis/armoire-architecture.md`
- covered: Table d'échange — `okf/protocols/table-d-echange.md`
- covered: Legacy HTTP — `okf/protocols/legacy-http.md`
- covered: Dual Protocol — `okf/protocols/dual-protocol.md`

## Roadmap and portals

- Roadmap concepts: 37
- Portal concept: `lan-local-portal`
- Portal concept: `cloud-user-portal`
- Portal concept: `support-site`
- Portal concept: `documentation-site`
- Portal concept: `roadmap-site`
- Portal concept: `admin-surfaces`
- Portal concept: `gateway-install-control`

## Gaps and contradictions

- No hard contradictions were automatically detected in this generation pass.
- Any index/protocol contradiction discovered during future manual review must be added to the affected OKF concept and to this report family.
- Items with `TBD` horizon or deployment state require source-backed follow-up rather than inference.

## Validation

Run:

```bash
python3 scripts/okf/validate_okf.py okf
openspec validate essensys-okf-discovery-2026-06-029 --strict
```

## Security notes

- Discovery avoids `.env`, decrypted SOPS material, private keys, tokens and credentials.
- OKF records code pointers and citations, not full source code dumps.
