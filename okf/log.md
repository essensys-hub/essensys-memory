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
* **Deploy**: `essensys-password-reset-2026-08-039` tranche `admin-password-reset-assist` déployée sur OVH (`--tags cloud_backend`, commit `36ef04a`). Migration 013 appliquée : table `password_reset_tokens` créée, modèle `password_reset` réécrit autour de `{{reset_url}}` et activé. Routes `GET /api/auth/password/reset/validate` et `POST /api/auth/password/reset` vérifiées en production (400 `invalid_token` sur jeton bidon) ; `POST /api/admin/users/{id}/password-reset` monté et gardé (401 sans JWT admin). **Non fait** : SPA support-site (page `/reset-password`) toujours pas déployée, donc le lien émis n'a pas encore de page ; test d'envoi SMTP réel non exécuté faute de JWT admin.
* **Constat**: `www.essensys.fr` sert le build `essensys-support-site` et `mon.essensys.fr` le build `essensys-user-portal-frontend` — même VPS `37.59.106.164`, vhosts distincts. `FRONTEND_URL=https://www.essensys.fr/` est donc correct pour `/reset-password` ; le repli de `pwreset.PortalBaseURL()` visait à tort le portail et a été corrigé.
* **Proposal**: OpenSpec `essensys-password-reset-2026-08-039` — réinitialisation de mot de passe portail (jeton opaque à usage unique en base, lien `{{reset_url}}` remplaçant `{{temporary_password}}`, latence uniforme anti-énumération, extraction de `internal/mailtpl` hors du paquet `admin`, action admin tracée). Gap comblé : `internal/identity/routes.go` ne montait aucune route de reset et le modèle d'email `password_reset` (migration 006) n'était jamais envoyé.
