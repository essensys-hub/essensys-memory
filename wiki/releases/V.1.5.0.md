# Release V.1.5.0 — Baseline pré audit-trail

| Champ | Valeur |
|-------|--------|
| **ID** | V.1.5.0 |
| **Date** | 2026-07-03 |
| **Statut** | Figée — point de départ avant **DEV 1** audit-trail ([[OpenSpec 2026-07-034]]) |
| **Manifeste** | `releases/V.1.5.0-manifest.yaml` |
| **Ansible** | `essensys-ansible/releases/V.1.5.0.yml` |

## Périmètres couverts

| Périmètre | Accès | Stack |
|-----------|-------|-------|
| **Gateway CM5/CM6** | `https://mon.essensys.local` | Docker `V.1.3.0` + backend source git |
| **OVH cloud** | `https://mon.essensys.fr` | `essensys-cloud-backend` consolidé `:8080` |
| **Raspberry classique** | `https://mon.essensys.local` | Docker `V.1.3.0` mono-NIC |

## Tags Git (source)

| Dépôt | Tag | SHA | Branche |
|-------|-----|-----|---------|
| `essensys-server-backend` | `V.1.5.0` | `bb953d0` | `V.1.3.0` |
| `essensys-server-frontend` | `V.1.5.0` | `25e7649` | `V.1.3.0` |
| `essensys-user-portal-backend` | `V.1.5.0` | `9525a01` | `main` |
| `essensys-user-portal-frontend` | `V.1.5.0` | `974298a` | `main` |
| `essensys-ansible` | `V.1.5.0` | *(tag sur commit release)* | `V.1.3.0` |
| `essensys-raspberry-install` | `V.1.5.0` | *(tag sur commit release)* | `V.1.3.0` |
| `essensys-raspberry-gateway` | `V.1.5.0` | `1c6cab3` | `nixos` |
| `essensys-memory` | `V.1.5.0` | *(tag sur commit release)* | `main` |

## Contenu fonctionnel (par rapport à V.1.4.0)

- Héritage **V.1.4.0** scénarios + **V.1.3.1** sync cloud scheduler
- **LAN IAM** preview (comptes locaux, `/login`, `/settings/users`)
- Inventaire OVH : `machines.id` stable, affichage `UNKNOWN-*`, **persistance MAC** (`9525a01`)
- Hub cloud consolidé (`CONSOLIDATED_MODE`)
- Spécification OpenSpec **audit-trail + immudb** — **non déployée**

## Hors scope runtime V.1.5.0

- `essensys-audit-service`, immudb, `armoire_audit_events`
- Toute tâche `DEV 1` / `DEV 2` du change `essensys-armoire-audit-trail-2026-07-034`

## Déploiement figé

```bash
# CM5 gateway
ansible-playbook -i inventory.gateway install.gateway.yml -e @releases/V.1.5.0.yml

# OVH
export SOPS_AGE_KEY_FILE="$PWD/.age/keys.txt"
ansible-playbook -i inventory deploy-portal-stack.yml -e @releases/V.1.5.0.yml

# Raspberry classique
ansible-playbook -i inventory install.raspberrypi.yml -e @releases/V.1.5.0.yml
```

## Vérification rapide

| Cible | Commande attendue |
|-------|-------------------|
| CM5 | `docker ps` → images `essensyshub/*:V.1.3.0` |
| OVH | `systemctl is-active essensys-cloud-backend` → `active` |
| OVH MAC | Admin machines → colonne MAC après poll identity |

## Liens

- [[Deployment Perimeters]]
- Change audit : `openspec/changes/essensys-armoire-audit-trail-2026-07-034/`
- Versions install : `essensys-raspberry-install/docs/versions.md`
