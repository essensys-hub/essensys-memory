## Context

Essensys déploie le hub cloud sur un **VPS OVH** (`mon.essensys.fr`) via `essensys-ansible/support-site.yml` et les passerelles **CM5** via `install.gateway.yml`. Les secrets cloud sont centralisés dans `group_vars/essensys/vault.yml` (Ansible Vault, gitignored). Ansible génère des fichiers `.env` consommés par systemd (`cloud-backend.env.j2`, `portal-backend.env.j2`). Les gateways utilisent `host_vars` pour `cloud_gateway_token` et identité MAC.

Contraintes projet : pas de Kubernetes, pas de SaaS secrets manager, open source, alignement future **sops-nix** ([[Essensys Gateway Nixos]]). Le protocole domotique legacy et la table d'échange ne sont pas concernés.

Référence détaillée : `prompts/vault.md`, entité [[Essensys Ansible]], [[Gateway PKI]] (tokens gateway).

## Goals / Non-Goals

**Goals:**

- Secrets cloud **chiffrés et versionnés dans Git** (review PR via diff SOPS).
- **Migration** depuis Ansible Vault sans renommer les variables Ansible (`vault_*`, `portal_*`).
- Rôle **`sops_load`** réutilisable en tête des playbooks cloud.
- Doc opérateur complète (création, édition, rotation clés age, CI).
- Page brain `secrets-management.md` indexant la procédure.
- Préparer la **phase 2 gateway** avec la même convention SOPS + age.

**Non-Goals:**

- HashiCorp Vault server, AWS Secrets Manager, Doppler.
- Montages Docker `/run/secrets/` et refacto Go lecture fichier (phase 3).
- mTLS gateway / certificats client PKI ([[Gateway PKI]] — change séparé).
- Chiffrement applicatif in-transit au-delà de HTTPS/TLS existant.
- Remplacement Prometheus edge.

## Decisions

### 1. SOPS + age (vs garder Ansible Vault seul)

**Choix :** migrer le cloud vers SOPS + age, conserver les noms de variables Ansible.

**Alternatives :**

| Option | Rejet / Retenu |
|--------|----------------|
| Ansible Vault seul | Retenu temporairement en rollback ; pas de secrets in Git |
| SOPS + age | **Retenu** — PR review, multi-clés, compat sops-nix |
| agenix seul | Réservé NixOS ; pas adapté VPS Ubuntu + Ansible pur |

### 2. Runtime MVP : conserver `.env` + systemd

**Choix :** ne pas changer la consommation runtime cloud en MVP — Ansible continue à templater `/opt/essensys/cloud-backend/.env`.

**Alternatives :** `/run/secrets/` Docker — reporté phase 3 (refacto Go + compose).

### 3. Arborescence `essensys-ansible/secrets/`

```text
essensys-ansible/
├── .sops.yaml
├── secrets/
│   ├── README.md
│   ├── cloud/essensys.sops.yaml      # MVP
│   └── gateway/example.sops.yaml.example
├── roles/sops_load/
└── docs/secrets.md
```

**Choix :** séparer `secrets/cloud/` et `host_vars/<host>/secrets.sops.yaml` (phase 2) avec `creation_rules` distinctes dans `.sops.yaml`.

### 4. Chargement Ansible : `community.sops` lookup

**Choix :** collection `community.sops`, lookup `community.sops.sops`, tâches avec `no_log: true`.

**Prérequis opérateur :** binaires `sops` et `age` sur la machine de déploiement ; `SOPS_AGE_KEY_FILE` ou clé dans `~/.config/sops/age/keys.txt`.

### 5. Fail hard sur secrets manquants

**Choix :** retirer les defaults dangereux (`changeme_random_secret`, `essensys_secure_password`) des templates `.j2` cloud — le playbook MUST échouer si une clé SOPS requise est absente.

### 6. Clé Apple OAuth `.p8`

**Choix :** stocker le contenu du fichier `.p8` dans SOPS (clé `vault_apple_key_content` ou équivalent) ; Ansible déploie vers `/opt/essensys/secrets/apple/AuthKey.p8` avec mode `0600` ; mettre à jour `APPLE_KEY_FILE` dans le `.env` généré.

**Alternative rejetée :** chemin manuel sur hôte (`/home/ubuntu/AuthKey_*.p8`) — non reproductible, hors Git.

### 7. CI validation

**Choix :** job CI (GitHub Actions ou script local) qui vérifie :
- les fichiers `*.sops.yaml` sont bien chiffrés (`sops -d` avec clé factice ou validation structure) ;
- aucune clé age privée ni secret clair dans le diff.

## Risks / Trade-offs

| Risque | Mitigation |
|--------|------------|
| Perte clé age → secrets illisibles | Backup clés age hors repo ; doc rotation ; ≥2 recipients age sur prod |
| Secret clair commité par erreur | pre-commit hook + grep CI + review |
| Régression déploiement cloud | dry-run `ansible-playbook --check` ; rollback documenté vers vault.yml |
| Divergence Ansible vs NixOS | même format SOPS ; matrice parité dans `docs/secrets.md` |
| Exposition logs Ansible | `no_log: true` sur toutes tâches SOPS |
| **BREAKING** pour opérateurs habitués à `ansible-vault` | guide migration + période transition documentée |

## Migration Plan

### Phase MVP (cloud OVH)

1. Générer paire age ; configurer `.sops.yaml` avec pubkey cloud.
2. Exporter contenu actuel : `ansible-vault view group_vars/essensys/vault.yml` → restructurer YAML plat.
3. Créer `secrets/cloud/essensys.sops.yaml` chiffré ; **ne pas** committer le fichier plain.
4. Implémenter rôle `sops_load` ; inclure en tête de `support-site.yml` et `setup-newrelic-alerts.yml`.
5. Déployer staging ou dry-run prod ; valider OAuth, SMTP, NR, PostgreSQL.
6. Retirer `group_vars/essensys/vault.yml` du workflow opérateur ; MAJ `.gitignore` et doc.
7. Mettre à jour brain + `publish-roadmap-public.sh` si promotion queue.

### Rollback

- Conserver une copie chiffrée Ansible Vault hors repo jusqu'à validation prod.
- Réintroduire `vault.yml` local + retirer rôle `sops_load` des playbooks si échec critique.

### Phase 2 (gateway)

- Template `host_vars/<hostname>/secrets.sops.yaml` pour `cloud_gateway_token`, MAC, machine_id.
- Intégrer `sops_load` dans `install.gateway.yml` (vars host-scoped).

## Open Questions

- [ ] Nombre de recipients age prod (Nicolas seul vs backup secondaire) — décision opérateur avant premier commit SOPS.
- [ ] CI GitHub Actions dans `essensys-ansible` ou script local seulement — à trancher en implémentation.
- [ ] Chiffrement clé Apple `.p8` en base64 dans SOPS vs fichier binaire SOPS — préférer YAML string base64 pour simplicité Ansible.
