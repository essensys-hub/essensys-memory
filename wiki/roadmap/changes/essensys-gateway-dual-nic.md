---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-05-14
updated: 2026-06-28
status: active
host_repo: essensys-raspberry-gateway
---

# Essensys Gateway Dual Nic

**Host repo:** [[Essensys Raspberry Gateway]]
**Path:** `essensys-raspberry-gateway/openspec/changes/essensys-gateway-dual-nic`
**Status:** active
**OpenSpec created:** 2026-05-14

## Why

The Essensys gateway must physically isolate user-facing traffic (LAN/HTTPS on eth0) from equipment bus traffic (armoire/HTTP on eth1) while retaining full backward compatibility with the legacy BP_MQX_ETH firmware client. A Raspberry Pi CM5 is now the target hardware, adding NVMe storage that must absorb write-heavy workloads (logs, TSDB, caches) to prevent premature eMMC wear-out.

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 5

## Source files

- `essensys-raspberry-gateway/openspec/changes/essensys-gateway-dual-nic/proposal.md`
- `essensys-raspberry-gateway/openspec/changes/essensys-gateway-dual-nic/design.md`
- `essensys-raspberry-gateway/openspec/changes/essensys-gateway-dual-nic/tasks.md`
