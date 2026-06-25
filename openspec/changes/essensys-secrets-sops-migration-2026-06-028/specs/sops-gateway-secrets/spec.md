# sops-gateway-secrets

Convention SOPS + age pour les secrets par passerelle CM5 (tokens cloudsync, identité gateway) — **phase 2**, alignée avec sops-nix.

## ADDED Requirements

### Requirement: Secrets gateway par hôte en SOPS

Chaque passerelle CM5 MUST pouvoir stocker ses secrets dans `host_vars/<hostname>/secrets.sops.yaml` chiffré avec age. Le fichier MUST contenir au minimum : `cloud_gateway_id`, `cloud_gateway_token`, `cloud_gateway_machine_id`, et les identifiants MAC si non dérivés de l'inventaire.

#### Scenario: Fichier SOPS gateway par hostname

- **WHEN** une gateway `cm5-client-dupont` est ajoutée à l'inventaire `inventory.gateway`
- **THEN** `host_vars/cm5-client-dupont/secrets.sops.yaml` peut être créé et chiffré
- **AND** les secrets ne sont pas mélangés avec le fichier cloud `secrets/cloud/essensys.sops.yaml`

#### Scenario: Token gateway distinct par site

- **WHEN** deux gateways distinctes sont déployées
- **THEN** chaque `secrets.sops.yaml` host-scoped contient un `cloud_gateway_token` différent
- **AND** la révocation d'un token n'expose pas l'autre gateway

### Requirement: Chargement gateway dans install.gateway.yml

Le playbook `install.gateway.yml` (phase 2) MUST charger les secrets host-scoped via extension du rôle `sops_load` ou rôle dédié, avant `raspberry_backend/tasks/cloud_sync.yml`. Les variables MUST alimenter `config.yaml` cloudsync sans fichier vault local gitignored.

#### Scenario: cloudsync config depuis SOPS gateway

- **WHEN** `install.gateway.yml` s'exécute sur un hôte avec `host_vars/<hostname>/secrets.sops.yaml`
- **THEN** `gateway_token` est écrit dans `config.yaml` du backend Go
- **AND** l'agent cloudsync peut authentifier sur `/api/gateway/*` du hub

### Requirement: Alignement format SOPS avec sops-nix

Les chemins et le format de chiffrement age MUST être compatibles avec la convention documentée dans `essensys-raspberry-gateway/openspec/changes/essensys-gateway-nixos/` (sops-nix ou agenix utilisant les mêmes fichiers SOPS source). La doc `essensys-ansible/docs/secrets.md` MUST inclure une matrice de parité Ansible vs NixOS.

#### Scenario: Même secret source Ansible et NixOS

- **WHEN** une gateway est migrée de Ansible vers NixOS
- **THEN** le fichier SOPS gateway peut être réutilisé sans re-chiffrement format incompatible
- **AND** la doc secrets décrit les deux voies de déploiement

### Requirement: Phase 2 explicitement hors MVP cloud

L'implémentation gateway MUST NOT bloquer la livraison MVP cloud (`sops-cloud-secrets`). Les playbooks gateway MAY continuer à utiliser `host_vars` plain ou vault local jusqu'à activation phase 2.

#### Scenario: MVP cloud sans gateway SOPS

- **WHEN** seule la phase MVP cloud est déployée
- **THEN** `install.gateway.yml` fonctionne comme avant (vars inventaire / vault local)
- **AND** aucune régression cloudsync n'est introduite par l'absence de SOPS gateway
