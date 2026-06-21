---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-05-31
updated: 2026-06-22
status: active
host_repo: essensys-raspberry-gateway
---

# Essensys Gateway Nixos

**Host repo:** [[Essensys Raspberry Gateway]]
**Path:** `essensys-raspberry-gateway/openspec/changes/essensys-gateway-nixos`
**Status:** active
**OpenSpec created:** 2026-05-31

## Why

The Essensys gateway CM5 needs a **declarative, reproducible deployment path** alongside the existing Ansible stack. NixOS on a dedicated `nixos` branch offers atomic upgrades, pinned dependencies, and module-based configuration for the full dual-NIC gateway (eth0 user HTTPS, eth1 armoire HTTP/DHCP/DNS) while preserving functional parity with `prompts/Gateway.md` and the Ansible change `essensys-gateway-dual-nic`. CM5 support is feasible via community flakes (not upstream-official), making this …

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 10

## Source files

- `essensys-raspberry-gateway/openspec/changes/essensys-gateway-nixos/proposal.md`
- `essensys-raspberry-gateway/openspec/changes/essensys-gateway-nixos/design.md`
- `essensys-raspberry-gateway/openspec/changes/essensys-gateway-nixos/tasks.md`
