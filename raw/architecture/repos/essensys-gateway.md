# essensys-gateway

> Dépôt « ombrelle » / réservé de la passerelle Essensys, aujourd'hui réduit à un README stub — le contenu réel (matériel CM5 + déploiement) vit dans `essensys-raspberry-gateway`.

**Catégorie :** Passerelle / Plan de contrôle
**Stack :** Aucune (dépôt placeholder — un seul fichier `README.md` contenant le titre)
**Statut :** Stub / vide. Un seul commit (`first commit`), branche `main` uniquement, pas de code ni de scripts.

## Rôle dans l'architecture Essensys

En l'état actuel, `essensys-gateway` est un **dépôt stub** : son `README.md` ne contient que la ligne `# essensys-gateway`, aucun code, aucun script, aucune configuration. Il n'y a ni `nix/`, ni `src/`, ni `docs/`, ni workflow CI.

Le nom suggère qu'il devait porter le « logiciel passerelle » générique d'Essensys (le pont entre les cartes locales et le cloud). Dans les faits, ce rôle a été matérialisé ailleurs :

- le **matériel** de la passerelle (carte CM5, stack 3 PCB, boîtier rail DIN) et son **déploiement NixOS** sont dans `essensys-raspberry-gateway` ;
- le **provisioning / installation applicative** (Ansible + Docker) est dans `essensys-raspberry-install` ;
- l'**orchestration de la flotte de conteneurs** est dans `essensys-control-plane`.

`essensys-gateway` est donc très probablement soit un dépôt **réservé** (nom déposé sur l'organisation `essensys-hub` pour usage futur), soit un ancien emplacement **abandonné au profit de** `essensys-raspberry-gateway`. À considérer comme non actif tant qu'il n'est pas peuplé.

## Stack technique & dépendances

Aucune. Le dépôt ne déclare aucun langage, runtime, gestionnaire de paquets ni dépendance. Pas de `flake.nix`, `go.mod`, `package.json`, `Dockerfile` ni `docker-compose`.

## Structure du dépôt

```
essensys-gateway/
├── README.md   # contient uniquement « # essensys-gateway »
└── .git/
```

## Build / Installation / Déploiement (sur Raspberry, services, scripts)

Rien à construire ni à déployer : aucun artefact, aucun script, aucun service systemd, aucune image Docker. Pour tout ce qui concerne la passerelle réelle, se reporter à :

- `essensys-raspberry-gateway` (matériel CM5 + flake NixOS) ;
- `essensys-raspberry-install` (bootstrap Ansible/Docker sur Raspberry Pi).

## Intégrations (pont entre cartes locales, MQTT, cloud backend)

Aucune intégration implémentée dans ce dépôt. Le pont effectif entre cartes locales (bus armoire), MQTT (Mosquitto) et le backend cloud est réalisé par la combinaison `essensys-raspberry-gateway` + `essensys-raspberry-install` + `essensys-control-plane`.

## Points d'attention

- **Dépôt stub** : ne pas chercher de code ici ; risque de confusion avec `essensys-raspberry-gateway` (nom très proche).
- **Décision à clarifier** : faut-il l'archiver, le supprimer, ou y migrer le « cœur logiciel passerelle » ? En l'état il crée de l'ambiguïté dans l'organisation des dépôts.
- Aucune licence, aucun CI, aucune doc : à ne pas référencer comme source d'installation.
