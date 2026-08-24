# OKF Bundle Update Log

## 2026-06-28
* **Process**: Added [Deployment Perimeters](processes/deployment-perimeters.md) — CM5 LAN, hub OVH, armoire seule WAN, sites publics, jumeaux et commandes deploy.
* **Initialization**: Created the ESSENSYS Open Knowledge Format memory bundle with root index, directory indexes, foundational concepts, and OKF v0.1 reference.
## 2026-06-28
* **Update**: Applied `essensys-okf-discovery-2026-06-029`; generated repository, firmware, protocol, roadmap, portal, process and synthesis concepts.
* **Update**: Added ESSENSYS OKF Memory Sync skill/rule process so agents must refresh wiki/OKF when touching essensys-hub repositories.

## 2026-07-20
* **Update**: Applied OpenSpec `essensys-turnstile-registration-2026-07-036` — Turnstile on public registration (portal-backend + support-site SPA + Ansible templates). Secrets/SOPS values and OVH deploy remain operator steps.

## 2026-08-06
* **Protocol**: Added [Bus I2C BP ↔ BA](protocols/i2c-ba-bus.md) — topologie, transaction write+read, CRC-16/MODBUS, codes de trame et limites d'observabilité du bus interne armoire, sourcés du firmware SC944D et SC942C.
* **Proposal**: OpenSpec `essensys-i2c-ba-sniffer-2026-07-038` — sniffer I2C passif exploratoire (nouveau dépôt `essensys-i2c-ba-sniffer`), sans capacité d'émission.

## 2026-08-24
* **Proposal**: OpenSpec `essensys-password-reset-2026-08-039` — réinitialisation de mot de passe portail (jeton opaque à usage unique en base, lien `{{reset_url}}` remplaçant `{{temporary_password}}`, latence uniforme anti-énumération, extraction de `internal/mailtpl` hors du paquet `admin`, action admin tracée). Gap comblé : `internal/identity/routes.go` ne montait aucune route de reset et le modèle d'email `password_reset` (migration 006) n'était jamais envoyé.
