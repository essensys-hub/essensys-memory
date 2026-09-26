## Why

Le 25/09/2026, le premier redéploiement du backend cloud depuis plusieurs mois a mis la production hors service pendant environ une heure (`mon.essensys.fr` et `www.essensys.fr` : `502` sur toute l'API, protocole IoT legacy compris — un seul binaire). Aucun des trois défauts en cause n'était dans le code déployé. Tous étaient dans le pipeline, dormants, et se sont réveillés ensemble :

1. **`deploy-security-fix.yml` n'invoquait pas le rôle `sops_load`.** Ce playbook « allégé » (backend + SPA, sans certbot) rendait `/opt/essensys/cloud-backend/.env` sans qu'aucun secret SOPS ne soit chargé. Seules les copies en clair de `group_vars/essensys/vault.yml` (gitignoré, jamais chiffré) alimentaient le template. `TURNSTILE_SECRET_KEY`, présent uniquement dans SOPS, est resté vide ; le binaire l'exige en production (`config.Validate()`) et a refusé de démarrer.
2. **`vault.yml` portait un `portal_db_password` périmé.** Le mot de passe avait été tourné dans SOPS le 29/06 (`01685bde`), jamais répercuté dans la copie en clair. Une fois Turnstile contourné, le binaire a échoué sur `pq: password authentication failed`. Vingt et une clés de `vault.yml` doublonnent SOPS de la même façon ; n'importe laquelle peut diverger de la même manière.
3. **Rien dans Ansible ne vérifiait ce que le binaire vérifie.** `sops_required_cloud_keys` n'exige pas la clé Turnstile ; le service a été redémarré, a crash-loopé cinq fois en 47 ms, et le play a continué jusqu'à la tâche suivante comme si de rien n'était. Le premier signal a été un utilisateur qui ne pouvait plus se connecter.

À quoi s'ajoutent deux constats faits en diagnostiquant : `quick-deploy.yml` déploie le rôle `backend` legacy, invalide en mode consolidé depuis juin ; et la CI de `essensys-user-portal-backend` est rouge sur `main` depuis le 20/07 (`go.mod` exige Go 1.25, le workflow installe 1.22), donc personne ne voyait plus rien passer au rouge.

Cette change fait en sorte qu'un déploiement échoue **dans Ansible, avant de toucher le service**, partout où le binaire échouerait au démarrage — et qu'un service qui ne démarre pas fasse échouer le play plutôt que l'utilisateur.

## What Changes

- **`essensys-ansible`** : `sops_load` devient obligatoire dans tout playbook qui rend une configuration de la prod (`deploy-security-fix.yml` — correctif déjà appliqué localement le 25/09, non commité — renommé `deploy-cloud-stack.yml`) ; `quick-deploy.yml` supprimé ; `sops_required_cloud_keys` aligné sur `config.Validate()` du binaire (ajout de `TURNSTILE_SECRET_KEY`) ; nouvelle assertion pré-template dans le rôle `cloud_backend` sur les variables que le binaire exige ; nouveau gate de santé post-redémarrage (`systemctl is-active` + `GET /api/portal/health` avec tentatives) qui échoue le play avec les 30 dernières lignes de journal ; suppression de `group_vars/essensys/vault.yml` après vérification clé par clé que SOPS porte chaque valeur consommée ; `docs/secrets.md` réécrit autour de « SOPS, une seule source ».
- **`essensys-user-portal-backend`** : `.github/workflows/ci.yml` — `go-version: '1.25'`. Une ligne ; sans elle, la CI restera rouge pour toute PR, y compris celles de 041.
- **`essensys-memory`** : la page [[Portal Authentication]] et la mémoire de topologie sont corrigées (fait le 26/09) ; cette change trace le reste.

Aucun changement de code applicatif, aucune migration, aucun endpoint.

## Capabilities

### New Capabilities
- `deploy-secrets-parity`: tout secret que le binaire exige au démarrage est exigé par Ansible avant de rendre la configuration, depuis une source unique (SOPS)
- `deploy-health-gate`: un play de déploiement du backend échoue si le service ne répond pas en bonne santé après redémarrage

## Impact

- **Repos** : `essensys-ansible` (playbooks, rôle `cloud_backend`, rôle `sops_load`, `docs/secrets.md`), `essensys-user-portal-backend` (`.github/workflows/ci.yml` uniquement).
- **Fichiers Ansible** : `deploy-security-fix.yml` → `deploy-cloud-stack.yml`, `quick-deploy.yml` (supprimé), `roles/sops_load/defaults/main.yml`, `roles/cloud_backend/tasks/main.yml`, `roles/cloud_backend/tasks/health_check.yml` (nouveau), `group_vars/essensys/vault.yml` (supprimé, gitignoré — suppression locale sur le poste opérateur), `docs/secrets.md`.
- **Secrets** : aucune rotation. Aucune valeur n'est lue, affichée ni déplacée par cette change : seules des copies en clair redondantes sont supprimées après vérification que la copie chiffrée existe et est non vide.
- **Non impacté** : `essensys-support-site`, le binaire Go, la base de données, le protocole legacy IoT, les rôles gateway/Raspberry.
- **Hors périmètre, à traiter séparément** : les 6 CVE High Trivy sur `golang.org/x/*` et `grpc` (montée de versions de dépendances, avec ses propres tests) ; la fatalité de la tâche « Import machines » qui, en échouant après le redémarrage, empêche le rôle `frontend` de s'exécuter — comportement conservé car un échec de connexion à la base est une vraie erreur qu'il ne faut pas masquer, et le gate de santé (qui s'exécute avant) la rendra désormais explicite.
