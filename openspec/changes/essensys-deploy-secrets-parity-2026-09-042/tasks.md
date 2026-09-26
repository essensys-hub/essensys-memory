## 1. Sauvegarder le correctif de l'incident — essensys-ansible

- [ ] 1.1 Committer `deploy-security-fix.yml` avec l'ajout de `sops_load` exactement tel qu'appliqué le 25/09 (commit isolé, message renvoyant à cette change) ; vérifier `git show --stat HEAD` : un seul fichier, quatre lignes

## 2. Parité déclarée et vérifiée — essensys-ansible

- [ ] 2.1 Ajouter `TURNSTILE_SECRET_KEY` à `sops_required_cloud_keys` dans `roles/sops_load/defaults/main.yml`, avec un commentaire renvoyant à `essensys-user-portal-backend/internal/config/config.go` (D2) ; vérifier en retirant temporairement la clé du coffre déchiffré en mémoire (`-e TURNSTILE_SECRET_KEY=""`) que le play échoue à l'assertion `sops_load` avant toute tâche sur l'hôte
- [ ] 2.2 Ajouter la tâche d'assertion pré-template dans `roles/cloud_backend/tasks/main.yml` (rendu en mémoire, `JWT_SECRET`/`ADMIN_TOKEN`/`TURNSTILE_SECRET_KEY`/`DB_PASSWORD` ≥ 16 caractères, `no_log: true`) juste avant « Deploy cloud backend environment » (D3) ; vérifier par le même test négatif que l'échec se produit avant l'écriture du fichier
- [ ] 2.3 Supprimer `quick-deploy.yml` (D1) ; vérifier `grep -rn quick-deploy` dans le dépôt, la doc et `essensys-memory` : aucune référence restante

## 3. Gate de santé — essensys-ansible

- [ ] 3.1 Créer `roles/cloud_backend/tasks/health_check.yml` (`systemctl is-active` puis `uri` sur `/api/portal/health`, 10 tentatives × 3 s, `journalctl -n 30` dans le message de `fail`) et l'importer après « Enable and start cloud backend » précédé d'un `meta: flush_handlers` (D4) ; vérifier sur une base saine que le play passe sans tentative supplémentaire
- [ ] 3.2 Test négatif du gate : sur le VPS, poser temporairement `ENV=production` avec un `.env` dont `TURNSTILE_SECRET_KEY=` est vide (copie du fichier, restauration immédiate après), relancer le play, vérifier qu'il échoue au gate et que la ligne `config: TURNSTILE_SECRET_KEY is required` apparaît dans la sortie Ansible ; restaurer et vérifier `is-active`

## 4. Renommage et documentation — essensys-ansible

- [ ] 4.1 Renommer `deploy-security-fix.yml` en `deploy-cloud-stack.yml` avec un en-tête à jour (D1) ; laisser un `deploy-security-fix.yml` d'une tâche `fail` indiquant le nouveau nom ; vérifier `ansible-playbook --syntax-check` sur les deux
- [ ] 4.2 Réécrire `docs/secrets.md` (D7) : source unique, règle `sops_load` en premier, parité avec `config.Validate()`, vérification sans affichage, topologie `www`/`mon`/`:8080` avec racines Nginx ; vérifier que chaque commande citée s'exécute
- [ ] 4.3 Mettre à jour le README et la mémoire `prod-deploy-topology` pour le nouveau nom de playbook ; vérifier `grep -rn deploy-security-fix` : seul le fichier de redirection reste

## 5. Suppression des copies en clair — essensys-ansible (poste opérateur)

- [ ] 5.1 Pour chacune des 21 clés doublonnées, vérifier que SOPS porte la clé avec une valeur non vide (`sops -d … | awk` sur la longueur, jamais la valeur), et vérifier par `grep -rn` qu'aucun consommateur ne la lit ailleurs que via Ansible (D5) ; consigner la liste vérifiée dans le message de commit de 5.3
- [ ] 5.2 Rendu à blanc avant retrait : `ansible-playbook -i inventory deploy-cloud-stack.yml --check --diff --tags cloud_backend`, noter le diff du template (attendu vide)
- [ ] 5.3 Retirer les 21 lignes doublonnées et les 3 orphelines de `group_vars/essensys/vault.yml`, supprimer le fichier vide, conserver la règle `.gitignore` ; relancer le rendu à blanc et vérifier que le diff du template est toujours vide
- [ ] 5.4 Vérification en conditions réelles : déployer avec `deploy-cloud-stack.yml`, vérifier le passage de D3 et D4 sans bruit, `journalctl` : `Connected to PostgreSQL`, `Applied N migration(s)`, `listening on :8080`

## 6. CI — essensys-user-portal-backend

- [ ] 6.1 Passer `go-version: '1.22'` à `'1.25'` dans `.github/workflows/ci.yml` (D6), PR isolée ; vérifier que le job `test` passe au vert sur la PR (le job Security Gate restera rouge sur les CVE Trivy, hors périmètre — le noter dans la PR)

## 7. Mémoire — essensys-memory

- [ ] 7.1 Mettre à jour [[Portal Authentication]] (section Implémentation) avec la topologie réelle et le nom du playbook ; ajouter au wiki une page de concept [[Deploy Secrets Parity]] (source unique, parité, gate de santé, l'incident du 25/09 comme source) et l'indexer ; `openspec validate essensys-deploy-secrets-parity-2026-09-042 --strict`
