# essensys-prometheus

> Depot stub destine a la supervision Prometheus de la stack Essensys ; actuellement vide, le deploiement reel s'appuie sur l'image upstream `prom/prometheus` configuree par Ansible.

**Catégorie :** Infrastructure
**Stack :** Prometheus (prevu) — depot actuellement non implemente
**Statut :** Stub / a completer

## Rôle dans l'architecture Essensys

Ce depot est cense porter la brique de monitoring (Prometheus) de la gateway Essensys : collecte des metriques (scraping) du backend, de Traefik, des node-exporters, etc. En l'etat, **le depot est un stub** : il ne contient qu'un `README.md` d'une seule ligne (`# essensys-prometheus`), sans Dockerfile, sans `prometheus.yml`, sans workflow CI.

Le monitoring est aujourd'hui assure non pas par une image custom issue de ce depot, mais par l'image officielle upstream `prom/prometheus` deployee directement via Ansible (cf. `essensys-ansible/roles/raspberry_prometheus`). Ce depot reste donc un emplacement reserve, en attente d'eventuelle personnalisation.

## Configuration & fichiers clés

- `README.md` — unique fichier, une ligne : `# essensys-prometheus`.
- Aucun `Dockerfile`, `prometheus.yml`, regle d'alerting ni workflow GitHub Actions present.

Pour reference, le deploiement effectif (hors de ce depot, dans `essensys-ansible`) utilise :
- image `prom/prometheus:v3.2.1`, port `9092`, retention `30d`, scrape interval `15s` ;
- config `prometheus.yml` + repertoire `rules/` montes depuis l'hote ;
- stack monitoring associee : Alertmanager (`prom/alertmanager:v0.28.1`, port 9093) et Node Exporter (`prom/node-exporter:v1.9.0`, port 9101).

## Build / Déploiement (Docker, ports exposés)

- **Aucun build propre a ce depot** (pas de Dockerfile ni de CI).
- Le service `essensys-prometheus` de la compose Ansible pointe vers l'image upstream `prom/prometheus`, lancee avec `--config.file`, `--storage.tsdb.path`, `--storage.tsdb.retention.time`, `--web.listen-address=:9092` et `--web.enable-lifecycle`, en `network_mode: host` (`user: 65534:65534`).
- Port effectif : `9092` (defini cote Ansible, pas dans ce depot).

## Intégrations (quels services route/proxy/surveille-t-il)

Cible (selon la config Ansible, a confirmer une fois le depot rempli) :
- **Traefik** — expose deja des metriques Prometheus (cf. `essensys-traefik/traefik.yml`).
- **Node Exporter** — metriques systeme de la gateway.
- **backend Essensys** et autres services instrumentes.
- **Alertmanager** — pour le routage des alertes.

## Points d'attention

- **Statut stub** : tant que ce depot ne contient pas de `Dockerfile`/`prometheus.yml`/CI, il ne produit aucune image. Le monitoring repose entierement sur l'image upstream et la config geree par Ansible.
- Incoherence a clarifier : la compose Ansible parle de l'image `prom/prometheus` alors que ce depot porte le nom `essensys-prometheus` — verifier l'intention (image custom future vs simple placeholder).
- A completer : config de scraping (`prometheus.yml`), regles d'alerting, et workflow de build si une image custom est souhaitee (sur le modele des autres depots infra : `FROM essensyshub/essensys-base`, push `essensyshub/essensys-prometheus`).
