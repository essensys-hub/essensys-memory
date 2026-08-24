---
tags: [roadmap, openspec]
sources: [manifest.json]
created: 2026-08-06
updated: 2026-08-24
status: active
host_repo: essensys-memory
---

# Essensys I2c Ba Sniffer 2026 07 038

**Host repo:** [[ESSENSYS Memory]]
**Path:** `essensys-memory/openspec/changes/essensys-i2c-ba-sniffer-2026-07-038`
**Status:** active
**OpenSpec created:** 2026-08-06

## Why

Le bus I2C interne de l'armoire ESSENSYS est aujourd'hui une **boîte noire d'exploitation**. Le SC944D
(BP, maître) pilote les boîtiers auxiliaires SC940 / SC942C / SC941C (BA, esclaves) par un protocole
propriétaire, mais aucun outil ne permet de **voir ce qui circule réellement sur le bus** :

- quand un scénario ou une commande portail n'aboutit pas à un relais qui claque, on ne sait pas
  distinguer « la trame I2C n'a jamais été émise » de « la trame a été émise mais rejetée CRC » ou
  « la …

## Artifacts

- Proposal: ✓
- Design: ✓
- Tasks: ✓
- Specs: 4

## Source files

- `essensys-memory/openspec/changes/essensys-i2c-ba-sniffer-2026-07-038/proposal.md`
- `essensys-memory/openspec/changes/essensys-i2c-ba-sniffer-2026-07-038/design.md`
- `essensys-memory/openspec/changes/essensys-i2c-ba-sniffer-2026-07-038/tasks.md`
