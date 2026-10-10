## 1. Socle backend : modèle, filtre et API — essensys-user-portal-backend (essensys-user-portal-backend#27)

- [x] 1.1 Aligner `features/schema/feature.schema.json` sur la référence `essensys-feature-lifecycle` (bloc `github`, `tests.junit`) et créer `features/support-reports-2026-10-004.json` ; vérifier avec `validate_feature_manifests.py` et `check_feature_gate.py --strict`
- [x] 1.2 Créer `migrations/015_support_reports.sql` (table et index de D2, idempotente) ; vérifier en rejouant deux fois la migration sur un Postgres local, sans erreur, puis `\d support_reports`
- [x] 1.3 `internal/data/support_report_store.go` : `Create`, `ListByUser`, `CountSince`, `OldestSince`, `MarkSent` (pose repo, numéro, url, statut `open`, vide `payload`), `MarkFailed`, `ListPending`, `ListOpenToSync`, `UpdateStatus` ; vérifier par tests `sqlmock`
- [x] 1.4 `internal/support/sensitive.go` (D4) : catégories `password`, `secret`, `postal_address`, `email` ; vérifier par tests table-driven, dont `Test_NR_backend_1_password_is_rejected`, `Test_NR_backend_2_postal_address_is_rejected` et un jeu de textes techniques légitimes acceptés (« 25 s », « v2.0.0 », « k=612 v=128 »)
- [x] 1.5 `internal/support/pseudonym.go` (D5) et rendu Markdown de l'issue (D6 : neutralisation des `@`, échappement HTML, troncature) ; vérifier par tests : référence stable pour un même id, différente pour deux ids, corps sans email, sans nom ni identifiant d'armoire, mention `@x` neutralisée
- [x] 1.6 Handlers `POST` et `GET /api/support/reports` derrière `UserJWTWithStore` ; validation des champs (400), contenu sensible (422 sans écho), limite 5/24 h (429 + `retry_after`), réponse 201 `{ref, status}` ; `GET` sans `issue_url` pour un incident ; vérifier par tests httptest, dont `Test_NR_backend_3_sixth_report_in_24h_is_429`, `Test_NR_backend_4_no_session_is_401` et `Test_NR_backend_5_user_only_sees_own_reports`
- [x] 1.7 Configuration (D9) : nouvelles variables dans `internal/config`, `SUPPORT_PSEUDONYM_KEY` passée par `checkSecret` en production consolidée, App absente = avertissement au démarrage ; vérifier avec `config_test.go` (clé manquante en prod refusée, App absente acceptée)
- [x] 1.8 Montage `support.Mount` dans le bloc `ConsolidatedMode` du routeur ; vérifier par un test de routage et `go build ./... && go vet ./... && go test ./...`

## 2. Envoi GitHub et resynchronisation — essensys-user-portal-backend (essensys-user-portal-backend#28)

- [x] 2.1 `internal/support/github.go` (D7) : JWT d'App RS256, jeton d'installation mis en cache, `CreateIssue` (labels, type), `AddToProject` (GraphQL), `GetIssue` ; base URL surchargeable ; vérifier contre un faux serveur `httptest` (en-têtes, corps, cache du jeton, erreurs 401/403/5xx)
- [x] 2.2 Routage public/privé dans le handler de création : tentative immédiate, échec = `pending` et réponse 201 ; vérifier par tests `Test_NR_backend_6_incident_goes_to_private_repo` et `Test_NR_backend_7_github_down_keeps_pending`
- [x] 2.3 Worker `support.Syncer` (D8) : `pg_try_advisory_lock`, envoi des `pending` avec recul, relecture des `open` (> 10 min), mapping `completed`→`resolved`, autre raison → `closed` ; démarrage dans `cmd/server/main.go` ; vérifier par tests avec horloge injectable et faux GitHub
- [x] 2.4 CI : sortie JUnit de `go test` (`go-junit-report`) publiée en artefact, puis `nonreg_report.py --sources .` ; vérifier que le rapport liste `NR-backend-1` à `NR-backend-7` avec la référence `essensys-hub/essensys-feature-lifecycle#15`

## 3. Formulaire et suivi — essensys-support-site (essensys-support-site#8)

- [x] 3.1 Aligner `features/schema/feature.schema.json` sur la référence et créer `features/support-reports-2026-10-004.json` ; vérifier avec `validate_feature_manifests.py`
- [x] 3.2 Page `/signaler?type=bug|incident` (D10) : invitation à se connecter sans jeton ; formulaire avec bandeau d'avertissement au-dessus du premier champ libre, compteurs de caractères, erreurs 400/422/429 sous le champ sans perte de saisie, écran de confirmation avec la référence ; vérifier `npm run lint` et `npm run build`
- [x] 3.3 Accueil : pour un utilisateur connecté, les cartes Bug et Incident ouvrent `/signaler?type=…` ; vérifier dans le navigateur (connecté et déconnecté)
- [x] 3.4 « Mes signalements » dans `Profile.jsx` (D11) : liste, pastille d'état, lien GitHub pour les bugs seulement, état vide avec bouton « Signaler un problème » ; vérifier dans le navigateur avec une API simulée
- [x] 3.5 Playwright `e2e/support-reports.spec.js`, projets desktop, iPhone et iPad, API simulée par `page.route` (mode no-armoire) : `NR-site-1` avertissement visible sans défilement horizontal, `NR-site-2` refus 422 affiché sous le champ avec saisie conservée, `NR-site-3` visiteur invité à se connecter, `NR-site-4` incident sans lien GitHub dans Mes signalements ; vérifier `npx playwright test e2e/support-reports.spec.js` vert sur les 3 projets

## 4. Secrets et déploiement — essensys-ansible (essensys-ansible#4)

- [x] 4.1 Ajouter les variables de D9 à `roles/cloud_backend/templates/cloud-backend.env.j2` et la tâche d'écriture de la clé `github-app.pem` (0700/0600, `no_log`, conditionnelle), sur le modèle de `apple_oauth_key.yml` ; vérifier par `ansible-playbook --syntax-check` et un rendu `--check --diff` qui n'affiche aucun secret
- [x] 4.2 Ajouter `vault_support_pseudonym_key` (généré, 64 caractères hexadécimaux) au fichier SOPS cloud et à `sops_required_cloud_keys` ; documenter les clés GitHub App dans `docs/secrets.md` ; vérifier par `sops -d --extract` (présence seulement, sans afficher la valeur)

## 5. Prérequis GitHub, livraison et documentation — essensys-feature-lifecycle (essensys-feature-lifecycle#16)

- [x] 5.1 Action humaine (admin de l'org) : créer le dépôt privé `essensys-support`, les labels `incident` et `via-portal` dans les deux dépôts, la GitHub App « Essensys Support » (Issues lecture/écriture sur les deux dépôts, Projects lecture/écriture sur l'org, sans webhook), l'installer, ranger App ID, Installation ID et clé dans SOPS ; vérifier par `gh api /orgs/essensys-hub/installations` (App listée)
- [x] 5.2 `/checkup support-reports-2026-10-004` vert (build, lint, unitaires, NR, Playwright, feature-gate, security-gate) et rapport posté sur #15
- [ ] 5.3 (partiel, archivé le 2026-10-10 : backend et site déployés et vérifiés, GitHub App testée de bout en bout dans le dépôt privé ; reste le test avec un vrai compte sur le dépôt public) Déployer le backend puis le site (tags `prod-ovh-…`) ; vérifier en production avec un compte de test : un bug arrive anonymisé dans `essensys-support-site`, un incident dans `essensys-support`, les deux dans le Project #6, puis l'état « résolu » apparaît dans Mes signalements moins de 15 minutes après la fermeture
- [x] 5.4 Mettre à jour la politique de confidentialité (`/privacy`) pour mentionner les signalements et la pseudonymisation, et la page support ; vérifier en ligne
- [x] 5.5 Mettre à jour essensys-memory : pages wiki [[Essensys User Portal Backend]] et [[Essensys Support Site]] (nouveau module, table, routes), `wiki/log.md`, scripts `sync-sources.sh` et `update-roadmap.sh` ; vérifier que `wiki/index.md` reste cohérent
