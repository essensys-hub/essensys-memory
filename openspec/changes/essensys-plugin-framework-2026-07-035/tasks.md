## 1. Dépôt hôte et contrat manifest

- [x] 1.1 Créer le dépôt `essensys-plugin-framework` (structure `/go`, `/ts`, `/schema`, `/examples`) et l'inventorier
- [x] 1.2 Définir `plugin.manifest.json` comme extension de `features/schema/feature.schema.json` (`id`, `manifest_version`, `framework_version`, `capabilities`, `perimeters`, `surfaces`, `visibility`, `secrets`, `metrics`)
- [x] 1.3 Écrire le validateur de manifest + test CI (accepte valide, rejette champ manquant)
- [ ] 1.4 Adapter `check_feature_gate.py` pour reconnaître un plugin

## 2. SDK Go (registre compilé)

- [x] 2.1 Définir l'interface `PluginAdapter` (routes, souscription MQTT, exposition Prometheus, health)
- [x] 2.2 Implémenter le registre compilé (activation/désactivation par manifest, refus `plugin.Open`)
- [x] 2.3 Montage des routes `/api/plugins/<id>/*` derrière les middlewares d'auth existants
- [x] 2.4 Abonnement MQTT → écriture Redis (last-value + flag `stale`) et Prometheus (série `(plugin_id, machine_id, metric)`)
- [x] 2.5 Gestion du heartbeat collecteur et du marquage `stale`
- [x] 2.6 Diff-guard CI : interdire toute référence legacy depuis le package `plugins`
- [x] 2.7 Tests unitaires : RBAC déclaratif (403 hors visibilité), idempotence série, résilience bus

## 3. Package TS partagé (server-driven UI)

- [x] 3.1 Définir le format du descripteur UI serveur (tuile, page détail, panneau réglages)
- [x] 3.2 Implémenter le renderer générique + client `/api/plugins/*`
- [x] 3.3 Bloquer/mocker par défaut les mutations armoire (no-armoire)
- [x] 3.4 Harnais UX Matrix (Playwright desktop + iPhone + iPad, screenshots, visual regression) sur le renderer
- [x] 3.5 Tests : rendu identique, état `stale` affiché, message d'indisponibilité par périmètre

## 4. Intégration aux 4 apps (changes-satellites)

- [x] 4.1 `essensys-server-backend` : câbler le registre + routes plugins (LAN `:7070`)
- [ ] 4.2 `essensys-user-portal-backend` : câbler le registre + relais cloudsync (cloud `:8080`, pas d'accès device direct)
- [x] 4.3 `essensys-server-frontend` : intégrer le renderer partagé (LAN)
- [ ] 4.4 `essensys-user-portal-frontend` : intégrer le même renderer (cloud)
- [ ] 4.5 Vérifier la synchro jumeaux (backend et UI) — aucun composant plugin spécifique à un frontend

## 5. Plugin de référence `sungrow-solar`

- [x] 5.1 Transformer `sungrow_winet_collector.py` en collecteur MQTT conforme (topics + heartbeat), identifiants via SOPS
- [x] 5.2 Adaptateur Go `sungrow-solar` (souscription bus, `/api/plugins/sungrow-solar/current` + historique)
- [x] 5.3 Descripteur UI : tuile « Solaire » (flux instantané) + page détail (historique Prometheus), lecture seule
- [x] 5.4 Manifest `sungrow-solar` : `perimeters` = LAN/gateway, indisponible en « armoire seule WAN »
- [ ] 5.5 Déploiement Ansible du collecteur sur CM5 ; ACL Mosquitto par plugin
- [x] 5.6 Tests end-to-end : ingestion, `stale` sur collecteur down, zéro mutation armoire, masquage armoire seule WAN

## 6. Gates, sécurité et CI

- [x] 6.1 Lint CI bloquant : aucun secret en clair dans un manifest
- [x] 6.2 Security-gate : no-armoire + diff-guard legacy verts
- [ ] 6.3 UX Matrix Gate verte pour l'UI Sungrow (snapshot par plugin)
- [ ] 6.4 Feature-gate verte (plugin reconnu, manifest valide)

## 7. Documentation et mémoire (essensys-memory)

- [ ] 7.1 `essensys-doc` : guide « écrire un plugin » (contrat, périmètres, gates)
- [ ] 7.2 Ingest `wiki/concepts/plugin-framework.md` + fiche `okf/systems/essensys-plugin-framework.md`
- [ ] 7.3 Mettre à jour `okf/log.md` et la page roadmap OpenSpec
- [ ] 7.4 Exécuter `./scripts/refresh-all.sh` puis `./scripts/publish-roadmap-public.sh`
- [ ] 7.5 Cocher la checklist PR (tests, jumeaux, brain, tasks OpenSpec)
