# essensys-base

> Image Docker de base commune (Alpine 3.19) partagée par tous les services Essensys déployés sur Raspberry Pi.

**Catégorie :** Base
**Stack :** Docker / Alpine Linux 3.19 / buildx multi-arch (arm64 + amd64)
**Statut :** Fonctionnel et minimal — image socle opérationnelle, publiée via CI

## Rôle dans l'architecture Essensys

`essensys-base` fournit l'**image Docker de base mutualisée** dont héritent les autres services de la plateforme (Control Plane, Workers, outils de management). L'objectif est de centraliser en un seul endroit :

- la distribution et sa version (Alpine 3.19) ;
- les outils système communs (certificats, clients HTTP, `jq`, `bash`, Docker CLI) ;
- la configuration locale (timezone `Europe/Paris`) ;
- une convention de système de fichiers (répertoire `/data` pré-créé).

Cela garantit la **cohérence** entre tous les services et réduit la duplication de configuration dans chaque Dockerfile applicatif. La cible matérielle est le **Raspberry Pi** (arm64), tout en restant compatible amd64 pour le développement et la CI.

## Stack technique & dépendances

- **Base** : `alpine:3.19`
- **Paquets installés** (`apk add --no-cache`) : `ca-certificates`, `curl`, `wget`, `jq`, `bash`, `docker-cli`, `tzdata`
- **Variable d'environnement** : `TZ=Europe/Paris`
- **Répertoire** : `/data` créé au build
- **Labels OCI** : `image.source` → `https://github.com/essensys-hub/essensys-base`, `image.description`
- **Build multi-arch** : `docker buildx` ciblant `linux/arm64,linux/amd64`

## Structure du dépôt

```
.
├── .github/
│   └── workflows/
│       └── docker-build.yml   # CI : build & push multi-arch sur tag
├── Dockerfile                 # ~15 lignes, Alpine + paquets + TZ + /data
└── README.md                  # Documentation d'usage et de tags
```

## Build / Exécution / Déploiement

**Build local (manuel) :**

```bash
docker buildx build --platform linux/arm64,linux/amd64 \
  -t essensyshub/essensys-base:raspberry.2026.02 --push .
```

**CI/CD (`.github/workflows/docker-build.yml`) :** déclenchée sur push d'un **tag `raspberry.*`** (ou manuellement via `workflow_dispatch`). Le workflow :

1. configure QEMU + Docker Buildx ;
2. se connecte au Docker Hub (utilisateur `nrineau`, secret `DOCKER_LOGIN`) ;
3. build et push multi-arch vers `essensyshub/essensys-base:<tag>` **et** `:latest`, avec cache GitHub Actions (`type=gha`).

**Convention de tags :**
- `raspberry.YYYY.MM` : tag mensuel (ex. `raspberry.2026.02`) ;
- `latest` : dernière version.

## Intégrations

C'est une **brique fondatrice** : les autres dépôts de services Essensys la réutilisent comme image parente. Exemple type (extrait du README), pattern multi-stage où un binaire compilé ailleurs est copié dans l'image de base :

```dockerfile
FROM essensyshub/essensys-base:raspberry.2026.02
COPY --from=builder /app/myservice /usr/local/bin/myservice
ENTRYPOINT ["myservice"]
```

Ainsi, chaque service hérite automatiquement de la timezone, des certificats, de `jq`/`bash` et du Docker CLI sans les redéclarer. Une montée de version d'Alpine ou un ajout d'outil commun se fait une seule fois ici, puis se propage via le bump du tag de base dans les `FROM` des services.

> Note : le namespace Docker Hub a migré de `nrineau/` vers `essensyshub/` (commit `f8442d4`). Le README montre encore un exemple avec l'ancien préfixe `nrineau/` — la CI, elle, pousse bien sous `essensyshub/`.

## Points d'attention

- **Incohérence de namespace** dans la doc : le README utilise `nrineau/essensys-base` dans l'exemple `FROM`/build alors que la CI publie sous `essensyshub/essensys-base`. À harmoniser pour éviter des `FROM` cassés côté services.
- L'authentification Docker Hub mélange un **username `nrineau`** et un secret `DOCKER_LOGIN` : à clarifier (compte personnel vs organisation).
- Image volontairement **minimale** : tout outil supplémentaire requis par plusieurs services doit être ajouté ici, pas dupliqué.
- La présence de `docker-cli` dans une image de service implique des usages de management/orchestration ; à n'utiliser que pour les conteneurs qui en ont réellement besoin (surface d'attaque accrue).
