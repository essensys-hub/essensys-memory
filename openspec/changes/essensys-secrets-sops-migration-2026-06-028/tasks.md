# Tasks — essensys-secrets-sops-migration-2026-06-028

> **Roadmap ID:** 2026-06.028 — **planned** (scaffold juin 2026)  
> **Source prompt:** `prompts/vault.md`  
> **Périmètre MVP:** cloud OVH (`sops-cloud-secrets`) — gateway en phase 2

## 0. Préparation OpenSpec

- [x] 0.1 `openspec validate essensys-secrets-sops-migration-2026-06-028`
- [x] 0.2 Audit secrets existants : grep `vault_`, `portal_`, defaults dangereux dans `essensys-ansible/roles/*/templates/*.j2`
- [x] 0.3 Exporter inventaire Secret × template × runtime (table section 3 de `prompts/vault.md`)

## 1. Bootstrap SOPS + age (essensys-ansible)

- [x] 1.1 Ajouter `community.sops` dans `essensys-ansible/requirements.yml`
- [x] 1.2 Créer `essensys-ansible/.sops.yaml` avec `creation_rules` (cloud + gateway)
- [x] 1.3 Créer `essensys-ansible/secrets/README.md` (procédure sans secrets)
- [x] 1.4 Générer paire age opérateur ; configurer pubkey dans `.sops.yaml` (hors commit clé privée)
- [x] 1.5 Migrer contenu `group_vars/essensys/vault.yml` → `secrets/cloud/essensys.sops.yaml` (plain temporaire shred après chiffrement)

## 2. Rôle Ansible sops_load

- [x] 2.1 Créer `roles/sops_load/tasks/main.yml` — lookup SOPS cloud, `no_log: true`
- [x] 2.2 Mapper facts : `portal_jwt_secret`, `vault_*`, `portal_db_*`, `cloud_frontend_url`
- [x] 2.3 Assertion fail si clé requise absente après load
- [x] 2.4 Créer `roles/sops_load/defaults/main.yml` (chemin fichier SOPS configurable)

## 3. Intégration playbooks cloud (MVP)

- [x] 3.1 Inclure `sops_load` en tête de `support-site.yml`
- [x] 3.2 Inclure `sops_load` dans `setup-newrelic-alerts.yml`
- [x] 3.3 Retirer defaults dangereux de `roles/cloud_backend/templates/cloud-backend.env.j2`
- [x] 3.4 Déployer clé Apple `.p8` depuis SOPS → `/opt/essensys/secrets/apple/` (`0600`) ; MAJ `APPLE_KEY_FILE`
- [x] 3.5 Vérifier build frontend NR (`roles/frontend/tasks/main.yml`) avec vars SOPS

## 4. Gitignore et config opérateur

- [x] 4.1 MAJ `essensys-ansible/.gitignore` : ignorer `*.age-key`, `**/age-keys.txt` ; retirer `vault.yml` post-migration validée
- [x] 4.2 MAJ `config/.env.example` : documenter `SOPS_AGE_KEY_FILE` (remplace / complète `ANSIBLE_VAULT_PASSWORD`)
- [x] 4.3 Script optionnel `scripts/sops-init.sh` (bootstrap age + edit)

## 5. Documentation

- [x] 5.1 Créer `essensys-ansible/docs/secrets.md` (bootstrap, edit, rotation, rollback, CI)
- [x] 5.2 Cross-ref dans `docs/newrelic.md` et `docs/install-gateway.md`
- [x] 5.3 Créer `essensys-memory/wiki/concepts/secrets-management.md` + wikilinks [[Essensys Ansible]]
- [x] 5.4 MAJ entité `wiki/entities/essensys-ansible.md` (point d'attention SOPS)
- [x] 5.5 Append `wiki/log.md` ; `python3 scripts/lint-wiki.py` → 0 erreur
- [x] 5.6 `ESSENSYS_ROOT=... ./scripts/publish-roadmap-public.sh` si promotion queue active

## 6. CI / validation

- [x] 6.1 Job ou script : vérifier fichiers `*.sops.yaml` chiffrés ; grep anti-secret-clair dans diff
- [x] 6.2 `ansible-playbook -i inventory support-site.yml --check --diff` avec clé age (syntax-check OK ; dry-run complet requiert SSH VPS)
- [ ] 6.3 Deploy staging ou prod ; valider JWT, OAuth Google, SMTP, NR APM, PostgreSQL auth
- [x] 6.4 Documenter rollback vers Ansible Vault temporaire

## 7. Phase 2 — gateway (hors MVP, spec sops-gateway-secrets)

- [x] 7.1 Template `host_vars/example/secrets.sops.yaml.example`
- [x] 7.2 Étendre `sops_load` pour host-scoped gateway vars
- [x] 7.3 Intégrer dans `install.gateway.yml` avant `cloud_sync.yml`
- [x] 7.4 Matrice parité Ansible vs sops-nix dans `docs/secrets.md`

## 8. Validation finale

- [x] 8.1 Aucun secret clair dans `git diff` (`password`, `secret`, `NRAL`, `NRAK`)
- [x] 8.2 PR checklist : `[ ] Brain updated (essensys-memory)` + `[ ] Install doc/brain per essensys-install-doc.mdc`

```bash
cd essensys-memory && openspec validate essensys-secrets-sops-migration-2026-06-028
export SOPS_AGE_KEY_FILE=essensys-ansible/.age/keys.txt
cd essensys-ansible && ./scripts/verify-sops.sh
ansible-playbook support-site.yml --syntax-check
```
