## Context

Voir `proposal.md`. Faits établis pendant l'incident, tous vérifiés directement sur l'hôte ou dans les dépôts :

- `support-site.yml` invoque `sops_load` (`sops_load_cloud: true`, `tags: [always]`) ; `deploy-security-fix.yml`, `quick-deploy.yml`, `promote-admin.yml`, `cloud-nginx-only.yml`, `deploy-docs-site.yml`, `deploy-roadmap-site.yml`, `enable-https-*.yml` ne l'invoquent pas. Seul `deploy-security-fix.yml` (et `quick-deploy.yml`, via le rôle legacy) rend une configuration qui a besoin de secrets.
- `roles/sops_load/tasks/main.yml` déchiffre sur `localhost` (là où se trouve la clé age, qui ne doit jamais aller sur le VPS) puis fusionne les clés en variables de play. Ce mécanisme fonctionne : dès que le rôle est invoqué, le déploiement du 25/09 à 11:47 a rendu un `.env` correct du premier coup.
- `roles/cloud_backend/templates/cloud-backend.env.j2` accepte déjà deux noms pour Turnstile (`vault_turnstile_secret_key | default(TURNSTILE_SECRET_KEY | default(''))`). SOPS porte `TURNSTILE_SECRET_KEY` (35 caractères, valeur valide). Le `default('')` est la raison pour laquelle l'absence est passée silencieusement.
- `config.Validate()` du binaire exige, en `ENV=production` + `CONSOLIDATED_MODE=true` : `JWT_SECRET`, `ADMIN_TOKEN` (≥ 16 caractères, hors liste de valeurs connues), `TURNSTILE_SECRET_KEY` (non vide). Il exige de fait aussi `DB_PASSWORD` (sinon `sqlx.Connect` échoue). `sops_required_cloud_keys` exige `portal_db_password`, `portal_db_name`, `portal_jwt_secret`, `vault_admin_token`, `vault_newrelic_license_key` — pas Turnstile.
- Vingt et une clés de `group_vars/essensys/vault.yml` existent aussi dans SOPS ; trois n'y existent que sous un autre nom ou pas du tout (`jira_token`, `vault_gitguardian_token`, `vault_turnstile_secret_key`) et n'ont aucun consommateur dans `essensys-ansible`.
- Le rôle `cloud_backend` redémarre le service (`state: restarted`) et enchaîne immédiatement sur `import_machines.yml`. Aucune vérification que le service est vivant.
- `GET /api/portal/health` existe (`internal/portal/routes.go`), sans authentification, et répond `200` dès que le binaire écoute.

## Goals / Non-Goals

**Goals :**
- Une seule source de secrets pour la prod : SOPS. Plus aucune copie en clair susceptible de diverger.
- Symétrie : ce que le binaire refuse au démarrage, Ansible le refuse avant de rendre le fichier.
- Un service qui ne démarre pas = un play qui échoue, avec le diagnostic dans la sortie Ansible.
- Aucun playbook trompeur : ni nom qui ne dit pas ce qu'il fait, ni playbook qui déploie un rôle mort.

**Non-Goals :**
- Rotation de secrets. Aucune valeur ne change.
- Déplacer la clé age sur le VPS ou changer le modèle « déchiffrement sur le poste opérateur » : il est correct.
- Rendre non fatale la tâche `Import machines` — voir `proposal.md`, Hors périmètre.
- Corriger les CVE Trivy.

## Decisions

### D1 — `sops_load` en premier dans tout playbook qui rend une configuration prod

`deploy-security-fix.yml` (déjà corrigé localement) est renommé `deploy-cloud-stack.yml`, avec un en-tête qui dit ce qu'il fait aujourd'hui : « déploie le backend consolidé et la SPA support-site ; ne touche ni certbot ni la base ; les migrations SQL sont appliquées par le binaire au redémarrage ». `quick-deploy.yml` est supprimé.

Rationale : le nom « security-fix » et le commentaire « pour les correctifs HIGH » décrivent une raison d'être de juin, plus son usage réel (c'est devenu *le* playbook de déploiement courant). `quick-deploy.yml` invoque le rôle `backend` — le backend legacy de `essensys-support-site`, arrêté par `cloud_backend` lui-même (« Stop legacy backends before port 8080 cutover ») : l'exécuter remettrait un service mort sur le port 8080. Un playbook qui ne peut que nuire n'a pas à exister.

Alternative écartée : un `pre_tasks` commun via `import_playbook`. Plus indirect pour deux playbooks ; la règle « `sops_load` en premier » tient en une ligne de `docs/secrets.md`.

### D2 — Parité déclarée : `sops_required_cloud_keys` reflète `config.Validate()`

`roles/sops_load/defaults/main.yml` ajoute `TURNSTILE_SECRET_KEY` à `sops_required_cloud_keys`, avec un commentaire qui renvoie explicitement à `internal/config/config.go` du backend et dit : « toute clé ajoutée à `Validate()` doit être ajoutée ici ».

Rationale : l'assertion existante (`vars[item] is defined` et non vide) est exactement le bon garde-fou ; elle avait juste une entrée en moins. C'est la correction la moins invasive et elle se déclenche avant tout contact avec l'hôte.

### D3 — Parité vérifiée : assertion pré-template dans `cloud_backend`

Nouvelle tâche dans `roles/cloud_backend/tasks/main.yml`, juste avant « Deploy cloud backend environment », qui rend le template en mémoire (`template` lookup) et affirme que `JWT_SECRET=`, `ADMIN_TOKEN=`, `TURNSTILE_SECRET_KEY=`, `DB_PASSWORD=` y sont suivis d'une valeur d'au moins 16 caractères, `no_log: true`.

Rationale : D2 vérifie que les variables *existent* ; D3 vérifie que le *fichier rendu* les porte — ce qui couvre aussi une erreur de nom dans le template, cas exact du `default('')` qui a masqué l'absence de Turnstile. Le seuil de 16 reproduit `minSecretLen` du binaire. Les deux vérifications sont redondantes à dessein : elles échouent à deux moments différents avec deux messages différents.

### D4 — Gate de santé post-redémarrage

Nouveau `roles/cloud_backend/tasks/health_check.yml`, importé immédiatement après « Enable and start cloud backend » et avant `import_machines.yml` :

1. `systemctl is-active essensys-cloud-backend` — jusqu'à 10 tentatives, 3 s d'intervalle.
2. `uri: http://127.0.0.1:8080/api/portal/health`, statut 200 attendu — mêmes tentatives.
3. En cas d'échec de l'une ou l'autre : `journalctl -u essensys-cloud-backend -n 30 --no-pager` capturé et affiché dans le message de `fail`, puis `fail`.

Rationale : le 25/09, le service a crash-loopé cinq fois en une seconde et Ansible a enchaîné. Le journal contenait la cause en clair (`config: TURNSTILE_SECRET_KEY is required…`) ; il a fallu une connexion SSH manuelle pour le lire. Trente secondes d'attente maximum est un coût négligeable ; un play qui s'arrête en affichant `config: … is required` en aurait économisé cinquante minutes. Le handler `Restart cloud backend` existant (déclenché par le changement de `.env`) est conservé — le gate s'exécute après l'ensemble des redémarrages du play grâce à un `meta: flush_handlers` placé avant lui.

### D5 — `vault.yml` disparaît, clé par clé, avec preuve

Pour chacune des 21 clés doublonnées : vérifier que SOPS porte la même clé avec une valeur non vide (`sops -d … | awk` sur la *longueur*, jamais la valeur), puis retirer la ligne de `vault.yml`. Pour les trois clés sans consommateur Ansible (`jira_token`, `vault_gitguardian_token`, `vault_turnstile_secret_key`) : retirer. Le fichier vide est supprimé ; `.gitignore` conserve la règle, pour qu'une recréation accidentelle ne soit jamais versionnée.

Rationale : chaque copie en clair est une valeur qui peut diverger de SOPS sans que rien ne l'indique — c'est précisément le mécanisme de la panne. Le fichier est gitignoré, donc local au poste opérateur : le supprimer ne touche aucun dépôt. `AGENTS.md` dit « Aucun secret en clair » ; ce fichier était l'exception qui n'aurait jamais dû exister.

La vérification finale est un rendu à blanc : `ansible-playbook -i inventory deploy-cloud-stack.yml --check --diff --tags cloud_backend` limité à la tâche de template, dont le `--diff` montre les lignes changées **sans les appliquer** ; le diff attendu est vide (mêmes valeurs qu'au dernier déploiement réussi).

### D6 — CI verte : `go-version: '1.25'`

Une ligne dans `essensys-user-portal-backend/.github/workflows/ci.yml`. Pas de manifest de feature : le changement ne touche aucun chemin d'implémentation.

Rationale : une CI rouge depuis deux mois sur `main` a supprimé le signal ; les PR de 041 seraient rouges pour une raison sans rapport avec leur contenu. Les CVE Trivy resteront rouges — c'est un autre chantier, et un rouge qui dit vrai vaut mieux qu'un rouge qui dit n'importe quoi.

### D7 — `docs/secrets.md` : la règle en cinq lignes

Réécriture autour de : SOPS est la seule source ; `sops_load` est le premier rôle de tout playbook qui rend une config prod ; `sops_required_cloud_keys` doit refléter `config.Validate()` ; comment vérifier une valeur sans l'afficher (`awk` sur la longueur, `psql` via stdin) ; et la topologie `www` (support-site) / `mon` (portal-frontend) / `:8080` (backend commun) avec les racines Nginx.

## Risks / Trade-offs

- **Suppression de `vault.yml` sur le poste opérateur** : si une clé y était consommée ailleurs qu'en Ansible (script local, autre outil), elle disparaît. Atténuation : D5 exige un `grep` des consommateurs avant chaque retrait ; les trois clés orphelines identifiées n'en ont aucun dans le dépôt. Le fichier peut être régénéré depuis SOPS en cas d'erreur (`sops -d` vers un fichier local, jamais commité).
- **Le gate de santé ajoute jusqu'à 30 s** à chaque déploiement backend. Accepté.
- **Renommer le playbook casse les habitudes et les notes** : `docs/secrets.md`, le README et la mémoire `prod-deploy-topology` sont mis à jour ; l'ancien nom est conservé un cycle sous forme de fichier d'une ligne qui `fail` avec le nouveau nom.
- **D3 rend le template deux fois** (une en mémoire, une pour de vrai). Négligeable.

## Migration Plan

1. Committer le correctif local de `deploy-security-fix.yml` tel quel (c'est l'état qui a réparé la prod) — premier commit, isolé, pour que l'historique montre le fix avant le durcissement.
2. Livrer D2, D3, D4, D7, le renommage, la suppression de `quick-deploy.yml`.
3. D5 en dernier, clé par clé, avec rendu à blanc avant et après.
4. D6 dans son propre commit sur `essensys-user-portal-backend`.
5. Premier déploiement réel avec le playbook durci : sur une base saine, D3 et D4 doivent passer sans bruit. S'ils échouent, c'est qu'ils ont trouvé quelque chose — ne pas les contourner.

Retour arrière : `git revert` du commit de durcissement ; `vault.yml` régénérable depuis SOPS.

## Open Questions

Aucune.
