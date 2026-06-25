# sops-cloud-secrets

Gestion des secrets cloud OVH (hub `mon.essensys.fr`) via fichiers SOPS chiffrés avec age, chargés par Ansible au déploiement.

## ADDED Requirements

### Requirement: Secrets cloud chiffrés versionnés dans Git

Le dépôt `essensys-ansible` MUST contenir un fichier `secrets/cloud/essensys.sops.yaml` chiffré avec **age**, versionné dans Git. Le fichier MUST inclure au minimum les clés équivalentes à l'actuel `group_vars/essensys/vault.yml` : `portal_db_password`, `portal_jwt_secret`, `vault_admin_token`, `vault_smtp_*`, `vault_google_*`, `vault_apple_*`, `vault_newrelic_*`, `cloud_frontend_url`.

Aucune clé **age privée** ni contenu déchiffré MUST NOT être commité.

#### Scenario: Fichier SOPS présent et chiffré

- **WHEN** un développeur clone `essensys-ansible` sans clé age
- **THEN** `secrets/cloud/essensys.sops.yaml` est lisible mais non déchiffrable sans `SOPS_AGE_KEY_FILE`
- **AND** le contenu dans Git ne contient pas de mots de passe en clair

#### Scenario: Édition opérateur

- **WHEN** l'opérateur exporte `SOPS_AGE_KEY_FILE` et exécute `sops secrets/cloud/essensys.sops.yaml`
- **THEN** l'éditeur ouvre le YAML déchiffré
- **AND** à la sauvegarde le fichier reste chiffré avec les recipients age configurés dans `.sops.yaml`

### Requirement: Chargement Ansible via rôle sops_load

Les playbooks cloud (`support-site.yml`, `setup-newrelic-alerts.yml`) MUST inclure le rôle `sops_load` avant tout rôle consommant des variables `vault_*` ou `portal_*`. Le rôle MUST déchiffrer `secrets/cloud/essensys.sops.yaml` et exposer les clés comme facts Ansible portant les **mêmes noms** que l'ancien `vault.yml`. Toutes les tâches manipulant le contenu déchiffré MUST utiliser `no_log: true`.

#### Scenario: Déploiement support-site avec SOPS

- **WHEN** `ansible-playbook -i inventory support-site.yml` est exécuté avec clé age valide
- **THEN** le rôle `sops_load` charge les secrets cloud
- **AND** `cloud-backend.env.j2` reçoit `portal_jwt_secret` et `vault_smtp_pass` sans fichier `vault.yml` local

#### Scenario: Échec sans clé age

- **WHEN** le playbook cloud s'exécute sans `SOPS_AGE_KEY_FILE` ni clé age locale
- **THEN** le rôle `sops_load` échoue avec un message explicite
- **AND** aucun `.env` partiel n'est déployé sur le VPS

### Requirement: Runtime cloud inchangé en MVP

Le déploiement MVP MUST continuer à générer `/opt/essensys/cloud-backend/.env` (et `.env` legacy portal si applicable) via templates Jinja2 existants, consommés par systemd `EnvironmentFile`. Les permissions des fichiers `.env` on-host MUST être restrictives (`0600`, owner service).

#### Scenario: Service cloud-backend démarre après migration

- **WHEN** le playbook cloud se termine avec succès post-migration SOPS
- **THEN** `essensys-cloud-backend` systemd unit charge `EnvironmentFile=/opt/essensys/cloud-backend/.env`
- **AND** l'API répond sur le port configuré avec auth JWT fonctionnelle

### Requirement: Absence de defaults dangereux

Les templates cloud (`cloud-backend.env.j2`, tâches NR) MUST NOT utiliser de valeurs par défaut faibles pour les secrets (`changeme_random_secret`, `essensys_secure_password`, `essensys-admin-secret`). Si une clé requise est absente après `sops_load`, le playbook MUST fail.

#### Scenario: Secret manquant bloque le deploy

- **WHEN** `portal_jwt_secret` est absent du fichier SOPS
- **THEN** le template ou une assertion Ansible échoue avant écriture du `.env` sur le VPS
- **AND** le service cloud-backend n'est pas redémarré avec un secret par défaut

### Requirement: Documentation opérateur et brain

Le dépôt MUST contenir `essensys-ansible/docs/secrets.md` décrivant bootstrap age, édition SOPS, migration depuis Ansible Vault, rotation et rollback. Le brain MUST contenir `essensys-memory/wiki/concepts/secrets-management.md` avec wikilinks vers [[Essensys Ansible]] et cross-ref install-doc.

#### Scenario: Onboarding nouvel opérateur

- **WHEN** un opérateur suit `docs/secrets.md`
- **THEN** il peut générer ou recevoir une clé age, éditer un secret cloud et lancer un déploiement dry-run
- **AND** la page wiki brain indexe la procédure sans copier de secrets

### Requirement: Clé Apple OAuth déployée de façon reproductible

La clé privée Apple Sign-In MUST être stockée dans SOPS et déployée par Ansible vers un chemin fixe sous `/opt/essensys/secrets/apple/` avec permissions `0600`. Le `.env` généré MUST référencer ce chemin dans `APPLE_KEY_FILE`.

#### Scenario: OAuth Apple après migration SOPS

- **WHEN** le cloud-backend démarre avec secrets SOPS incluant la clé Apple
- **THEN** le fichier `.p8` existe on-host au chemin documenté
- **AND** `APPLE_KEY_FILE` dans `.env` pointe vers ce fichier
