# essensys-raspberry-gateway

> Passerelle Essensys « CM5 Edition » : conception matérielle de la carte (Raspberry Pi Compute Module 5, stack 3 PCB, rail DIN) **et** déploiement déclaratif NixOS de la pile applicative Essensys sur cette passerelle.

**Catégorie :** Passerelle / Plan de contrôle
**Stack :** KiCad (conception PCB) · NixOS / Nix Flakes (déploiement) · systemd-networkd, dnsmasq, Mosquitto, Redis, Nginx, Traefik · MkDocs Material (documentation)
**Statut :** Actif et structuré. Branche `main` = matériel + doc ; branche `nixos` = flake de déploiement. Backend et Traefik désactivés par défaut sur l'hôte de référence (à activer quand image/ACME prêts). OpenSpec montre plusieurs chantiers en cours (dual-NIC, NixOS, consolidation backend cloud, portail distant).

## Rôle dans l'architecture Essensys

Ce dépôt est le **cœur de la passerelle physique** déployée chez le client. Il couvre deux dimensions complémentaires :

1. **Matériel (HW)** — la carte « Essensys Gateway CM5 », hub domotique industriel bâti autour du Raspberry Pi Compute Module 5, en « sandwich » de 3 PCB 100×100 mm reliés par connecteurs mezzanine :
   - **Top board** : CM5 (quad-core Cortex-A76), ventilateur PWM, entrée 12–24 V DC sur bornier.
   - **Mid board** : slot M.2 M-Key (NVMe PCIe Gen2 x1), sortie HDMI.
   - **Bottom board** : double Gigabit Ethernet (1× natif CM5, 1× via pont USB 3.0 RTL8153), 3× USB 3.0 (hub VL817), pour clés Z-Wave/Zigbee.
   - Monté sur rail DIN dans un boîtier dédié — orientation tableau électrique / GTL.

2. **Déploiement logiciel (NixOS)** — un flake NixOS qui décrit de façon reproductible **toute la pile Essensys tournant sur la passerelle**, avec un profil « dual-NIC gateway » : `eth0` = LAN client (DHCP ou IP statique), `eth1` = **segment « armoire »** (bus isolé vers les cartes domotiques Essensys, IP statique `10.0.1.1/24`, serveur DHCP + DNS local dnsmasq).

C'est donc à la fois le **pont matériel** (deux NIC : LAN ↔ bus armoire) et le **pont logiciel** (backend + MQTT + reverse-proxy) entre les cartes locales et le cloud.

> Note : malgré son nom, le dépôt frère `essensys-gateway` est un stub vide ; c'est bien `essensys-raspberry-gateway` qui porte la passerelle réelle.

## Stack technique & dépendances

- **Conception matérielle** : projets KiCad (`.kicad_pro/_pcb/_sch/_sym`, footprints `.pretty`, modèles 3D STEP/STP), nomenclatures `CM5IOBOM.txt`, datasheets PDF. Dérivé de la carte de référence Raspberry Pi CM5IO (dossiers `RP-007514` / `RP-008099`). Stackup 4 couches à impédance contrôlée, assemblage SMT (VL817, RTL8153).
- **Déploiement** : **Nix Flakes** (`flake.nix`, `flake.lock`) sur `nixpkgs/nixos-24.11`, cible `aarch64-linux` ; sortie `nixosConfigurations.gateway-cm5`.
  - Input externe : `essensys-nginx` (dépôt frère, en `path:../essensys-nginx`, surchargé en CI via `--override-input`).
  - Modules systemd via `systemd-networkd`, `dnsmasq`, `mosquitto`, `redis`, `nginx`, `traefik`, `docker` (backend lancé en OCI host-network par défaut).
- **Documentation** : MkDocs Material (`mkdocs.yml`, `docs/`), publiée sur GitHub Pages (`gh-pages`).
- **Spécifications** : OpenSpec (`openspec/changes/...`) pour piloter les évolutions par « change/spec/tasks ».
- **CI** : GitHub Actions — `mkdocs.yml` (publication doc) et `nixos-flake-check.yml` (`nix flake check`).

## Structure du dépôt

```
essensys-raspberry-gateway/
├── README.md                  # Présentation matérielle CM5 + lien doc
├── flake.nix / flake.lock     # Flake NixOS (config gateway-cm5)
├── mkdocs.yml                 # Site de doc MkDocs Material
├── assets/                    # Rendus 3D (stack CM5, boîtier rail DIN)
├── src/cm5/                   # Conception KiCad de la carte CM5
│   ├── CM5_Stack_Top/         #   board CPU + ventilateur
│   ├── CM5_Stack_Mid/         #   board M.2 NVMe + HDMI
│   ├── CM5_Stack_Bot/         #   board double Eth + hub USB
│   └── RP-007514.../ RP-008099...  # cartes de référence RPi CM5IO
├── nix/
│   ├── hosts/gateway-cm5/     # default.nix (valeurs hôte réel) + hardware.nix
│   └── modules/
│       ├── essensys/          # backend, frontend, nginx, traefik, redis, mosquitto, optional-services
│       ├── gateway/           # dual-nic, dnsmasq-armoire, nvme-layout
│       └── platform/          # cm5-rpi5 (profil matériel)
├── docs/                      # MkDocs : installation, accès, réseau, logs, maintenance, routeurs…
├── openspec/                  # Changes/specs (dual-nic, nixos, cloud consolidation, portail distant…)
├── prompts/                   # Prompts d'assistance (Gateway, NixOS, RemoteUserInterface…)
└── scripts/test-wan-https-ovh.sh
```

## Build / Installation / Déploiement (sur Raspberry, services, scripts)

**Déploiement NixOS (branche `nixos`)** — la passerelle est décrite par `nixosConfigurations.gateway-cm5` :

- `nix flake check` valide l'évaluation (workflow CI `nixos-flake-check.yml`).
- Build/déploiement type : `nixos-rebuild switch --flake .#gateway-cm5` (sur la cible aarch64) ou build d'image puis flash.
- L'hôte de référence (`nix/hosts/gateway-cm5/default.nix`) reflète une passerelle réelle (CM5 relevé à `192.168.0.14`, 2026-05-31) :
  - `services.essensys.enable = true`, `platform.cm5.enable = true` ;
  - `gateway.enable` avec `eth0` LAN (`192.168.0.14`), `eth1` armoire (`10.0.1.1/24`), DHCP armoire `10.0.1.100–200`, hostname `mon.essensys.fr` rabattu sur `eth1` ;
  - `nvme.enable` (partition de données ext4 montée sur `/mnt/nvme`, `required = true` → boot échoue si NVMe absent) ;
  - services activés : `nginx`, `frontend`, `redis`, `mosquitto` ; **désactivés** : `backend` (en attente d'image), `traefik` (en attente ACME/secrets).

**Services & options Nix notables :**

- `services.essensys.dataDir` = `/mnt/nvme/data`, `logDir` = `/mnt/nvme/logs`, user système `essensys` — données mutables sur le NVMe.
- `essensys-backend` (module `backend.nix`) : par défaut **conteneur OCI** `essensyshub/essensys-backend:latest` en `--network host` (`virtualisation.docker.enable`), avec `ExecStartPre` = `docker pull`. Option `package` pour un binaire natif (service `simple`, port 7070). Ouvre le port TCP 7070 au firewall.
- **Réseau dual-NIC** (`dual-nic.nix`) : `systemd-networkd`, matching par **adresse MAC** (`10-essensys-eth0`, `20-essensys-eth1`) ; eth0 routable (DHCP ou statique /24), eth1 « carrier » **sans route par défaut** (segment armoire isolé).
- **dnsmasq armoire** (`dnsmasq-armoire.nix`) : DHCP + DNS **uniquement sur eth1**, `bind-interfaces`, plage `dhcpRange`, réservations statiques par MAC, résolution de `mon.essensys.fr` → `10.0.1.1`, upstream DNS 1.1.1.1/8.8.8.8, ouverture UDP/67.
- **Mosquitto** : broker MQTT en `127.0.0.1:1883`, données sous `${dataDir}/mosquitto`.
- **Documentation** : `pip install mkdocs-material … && mkdocs serve` (http://127.0.0.1:8000), publiée sur `essensys-hub.github.io/essensys-raspberry-gateway`.

## Intégrations (pont entre cartes locales, MQTT, cloud backend)

- **Cartes locales / bus armoire** : `eth1` matérialise le segment domotique isolé. La passerelle y est serveur DHCP + DNS (dnsmasq) et y bind ses services (Nginx/Traefik via `bindStrict`). Les cartes Essensys (clients legacy type BP_MQX_ETH) joignent ainsi le backend via `mon.essensys.fr` résolu localement.
- **MQTT** : broker Mosquitto local (1883, loopback) pour la messagerie interne entre composants.
- **Cloud backend** : intégration via `eth0` (LAN → routeur → Internet). Les change-sets OpenSpec `essensys-cloud-backend-consolidation`, `gateway-exchange-push`, `gateway-rules-unified` et `essensys-remote-user-interface` (`gateway-https-agent`, `cloud-action-queue`) décrivent la synchronisation passerelle ↔ hub cloud (push d'« exchange », file d'actions distantes, agent HTTPS WAN). Le backend tourne en conteneur (parité avec la pile Docker d'`essensys-raspberry-install`).
- **Reverse-proxy** : Nginx (API locales / client legacy) + Traefik (frontend local et WAN HTTPS/ACME) — modules dédiés, à activer selon l'hôte.

## Points d'attention

- **Deux natures dans un même dépôt** : conception matérielle KiCad (`main`) et déploiement NixOS (`nixos`). Bien identifier la branche selon le besoin.
- **Backend & Traefik désactivés** sur l'hôte de référence : le déploiement n'est « complet » qu'après publication de l'image backend et configuration ACME/secrets Traefik.
- **`nvme.required = true`** : la passerelle **ne démarre pas** sans NVMe montable — point critique en maintenance/SAV.
- **Matching réseau par MAC** : `eth0Mac`/`eth1Mac` sont spécifiques à chaque carte ; un remplacement matériel impose de mettre à jour l'hôte Nix.
- **Input flake `essensys-nginx` en `path:../essensys-nginx`** : nécessite le dépôt frère présent localement (ou `--override-input` en CI).
- **Cohabitation avec `essensys-raspberry-install`** : deux voies de déploiement coexistent (NixOS déclaratif ici vs Ansible/Docker dans `raspberry-install`). Clarifier laquelle est la cible de production pour éviter la divergence.
- Nom très proche du dépôt stub `essensys-gateway` (vide) — risque de confusion.
