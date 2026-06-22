# Tasks — essensys-lan-mcu-panels-2026-06.025

> **Roadmap ID:** 2026-06.025 — **planned** (scaffold juin 2026)

## Phase 0 — Spec

- [x] 0.1 Proposal + design + spec
- [ ] 0.2 Valider dependance 013 completed
- [ ] 0.3 `openspec validate essensys-lan-mcu-panels-2026-06.025`

## Phase 1 — Backend LAN

- [ ] 1.1 Modèle `McuPanel` + mapping bouton → scénario / action chauffage
- [ ] 1.2 API enrollment (extension trusted devices 013)
- [ ] 1.3 `POST` press bouton → launch scénario ou write heating
- [ ] 1.4 Middleware **LAN-only** (RFC1918 / interface bind)
- [ ] 1.5 Tests table-driven + simulation press

## Phase 2 — Frontend admin

- [ ] 2.1 Page configuration panneaux MCU
- [ ] 2.2 Wizard ajout device (code / QR)
- [ ] 2.3 Parité jumeau portal **N/A** (LAN only)

## Phase 3 — Firmware

- [ ] 3.1 Sketch ESP32 (PlatformIO) — N boutons, debounce, HTTPS
- [ ] 3.2 Sketch Pico W — même contrat API
- [ ] 3.3 Doc flash + `essensys-install-doc` excerpt

## Phase 4 — Clôture

- [ ] 4.1 Post blog si deploy démo (rule roadmap-site)
- [ ] 4.2 `publish-roadmap-public.sh` + wiki/log

## Verification

```bash
cd essensys-memory && openspec validate essensys-lan-mcu-panels-2026-06.025
# Depuis LAN uniquement :
curl -k https://mon.essensys.local/api/mcu/panels
```
