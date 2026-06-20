# essensys-utils

> Boîte à outils de scripts de maintenance pour Essensys ; à ce jour, contient principalement un script Go de bruteforce du code de configuration à 4 chiffres du panneau SC944D via la queue Redis.

**Catégorie :** Outillage
**Stack :** Go (Golang) + Redis (`redis-cli`)
**Statut :** Partiellement implémenté — un seul outil réel committé, README annonce un dépôt « divers scripts »

## Rôle dans l'architecture Essensys

Le dépôt est présenté comme une collection de **scripts et outils utilitaires de maintenance** du système domotique Essensys. Dans les faits, le seul outil versionné est `bruteforce_code.go`, un script offensif/diagnostic qui **énumère les 10 000 combinaisons (`0000`→`9999`)** du code de configuration à 4 chiffres du panneau **SC944D**.

Mécanisme :

- chaque tentative est injectée comme action JSON dans la **queue Redis `essensys:global:actions`**, ensuite dépilée et interprétée par le panneau (via le Control Plane / Worker) ;
- le code à 4 chiffres est encodé en deux octets (paramètres `k:410` = LSB, `k:411` = MSB), chaque chiffre logé sur 4 bits ;
- un `GUID` unique (`bruteforce-%04d`) est associé à chaque tentative et journalisé dans `bruteforce_uids.csv` (mapping *Code,GUID*) ;
- le retour du bon code se fait par corrélation : retrouver le `GUID` de la transaction acquittée/réussie dans le CSV.

**Régulation de débit** : le script lit en continu `LLEN essensys:global:actions` et temporise tant que la file dépasse un seuil (≥ 3). C'est un garde-fou critique : au-delà (~> 5/12 éléments), le firmware du SC944D ne lit que **1500 octets max** (buffer Ethernet) et le **parsing JSON tronqué fait crasher / « brick » la connexion** du panneau.

## Stack technique & dépendances

- **Langage** : Go (`package main`, std lib uniquement : `os`, `os/exec`, `strconv`, `strings`, `time`, `fmt`).
- **Dépendance externe** : binaire `redis-cli` invoqué via `exec.Command` (le script ne parle pas Redis nativement, il *shelle* `redis-cli`).
- **Environnement d'exécution attendu** : directement sur le **Raspberry Pi du Control Plane** (Redis accessible localement, Worker actif pour dépiler la queue).
- Pas de `go.mod` versionné (build via `go run` / `go build` simple).

## Structure du dépôt

```
.
├── README.md            # mode d'emploi détaillé du bruteforce
├── bruteforce_code.go   # source du script (seul code versionné)
└── bruteforce_code      # binaire Go compilé (~2,7 Mo, committé)
```

Fichiers Git versionnés : `README.md` et `bruteforce_code.go` (le binaire est présent sur disque/committé selon le listing).

> Présence sur disque de fichiers **cachés non versionnés** (`.Alarme.c`, `.Json.c`, `.TableEchange.h`, `.TableEchangeAcces.c`, `.www.c`) — sources C du firmware/panneau apparemment utilisées comme matériel de reverse-engineering pour comprendre l'encodage des codes. Ils ne sont **pas suivis par Git** (`git ls-files` ne renvoie que README et le `.go`).

## Build / Exécution / Déploiement

```bash
# Exécution directe
go run bruteforce_code.go

# ou binaire autonome (recommandé pour tourner en arrière-plan)
go build -o bruteforce_code bruteforce_code.go
./bruteforce_code
```

Aucune CI (`.github/` absent), aucun packaging de déploiement. Outil lancé manuellement sur la machine cible.

## Intégrations

- **Redis** (`essensys:global:actions`) : canal d'injection des actions, partagé avec le reste de la plateforme (Control Plane, Workers). C'est l'unique point d'intégration.
- **Firmware SC944D / BP** : le format d'action JSON (`params` avec `k:410`/`k:411`) doit correspondre exactement à ce qu'attend le firmware ColdFire (cf. `essensys-gcc`, board BP/SC944D).

## Points d'attention

- **Outil offensif / à fort risque** : c'est un bruteforce de code de sécurité. À cadrer juridiquement et éthiquement (usage légitime de récupération sur son propre matériel vs détournement). À ne pas exposer publiquement sans avertissement.
- **Risque de « brick »** : un mauvais réglage du seuil de file ou un Worker absent peut saturer le buffer Ethernet 1500 o du panneau et corrompre sa connexion. La régulation `LLEN` est indispensable.
- **Couplage fort à `redis-cli`** : suppose Redis local et le binaire CLI présent ; pas de configuration d'hôte/port paramétrable dans le code.
- **README sur-promet** : annonce « divers scripts » alors qu'un seul outil existe — le dépôt est en réalité mono-outil pour l'instant.
- **Remote différent du reste** : `git@github.com:rhinosys/essensys-utils.git` (org `rhinosys`), là où les autres dépôts sont sous `essensys-hub`. Incohérence d'organisation à noter.
