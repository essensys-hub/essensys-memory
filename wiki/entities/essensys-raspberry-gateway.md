---
tags: [entity, repo, modern]
sources: [essensys-raspberry-gateway.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-raspberry-gateway
---

# Essensys Raspberry Gateway

> Passerelle Essensys « CM5 Edition » : conception matérielle de la carte (Raspberry Pi Compute Module 5, stack 3 PCB, rail DIN) **et** déploiement déclaratif NixOS de la pile applicative Essensys sur cette passerelle.

| | |
|---|---|
| **Catégorie** | Passerelle / Plan de contrôle |
| **Stack** | KiCad (conception PCB) · NixOS / Nix Flakes (déploiement) · systemd-networkd, dnsmasq, Mosquitto, Redis, Nginx, Traefik · MkDocs Material (documentation) |
| **Statut** | Actif et structuré. Branche `main` = matériel + doc ; branche `nixos` = flake de déploiement. Backend et Traefik désactivés par défaut sur l'hôte de référence (à activer quand image/ACME prêts). OpenSpec montre plusieurs chantiers en cours (dual-NIC, NixOS, consolidation backend cloud, portail distant). |
| **Era** | modern |

## Rôle

Ce dépôt est le **cœur de la passerelle physique** déployée chez le client. Il couvre deux dimensions complémentaires :

1. **Matériel (HW)** — la carte « Essensys Gateway CM5 », hub domotique industriel bâti autour du Raspberry Pi Compute Module 5, en « sandwich » de 3 PCB 100×100 mm reliés par connecteurs mezzanine :
   - **Top board** : CM5 (quad-core Cortex-A76), ventilateur PWM, entrée 12–24 V DC sur bornier.
   - **Mid board** : slot M.2 M-Key (NVMe PCIe Gen2 x1), sortie HDMI.
   - **Bottom board** : double Gigabit Ethernet (1× natif CM5, 1× via pont USB 3.0 RTL8153), 3× USB 3.0 (hub VL817), pour clés Z-Wave/Zigbee.
   - Monté sur rail DIN dans un boîtier dédié — orientation tableau électrique / GTL.

2. **Déploiement logiciel (NixOS)** — un flake NixOS qui décrit de façon reproductible **toute la pile Essensys tournant sur la passerelle**, avec un profil « dual-NIC gateway » : `eth0` = LAN client (DHCP ou IP statique), `eth1` = **segment « armoire »** (bus isolé vers les cartes domotiques Essensys, IP statique `10.0.1.1/24`, serveur DHCP + DNS local dnsmasq).

C'est donc à la fois le **pont matériel** (deux NIC : LAN ↔ bus armoire) et le **pont logiciel** (backend + MQTT + reverse-proxy) entre les cartes locales et le cloud.

> Note : malgré son nom, le dépôt frère `essensys-gateway` est un stub vide ; c'est bien `essensys-raspberry-gateway` qui porte la passerelle réelle.

## Intégrations

_Non documenté._

## Structure

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
│       ├── essensys/          # backend, frontend, nginx, traefik, redis, mos

_… voir source complète dans raw/_

## Points d'attention

- **Deux natures dans un même dépôt** : conception matérielle KiCad (`main`) et déploiement NixOS (`nixos`). Bien identifier la branche selon le besoin.
- **Backend & Traefik désactivés** sur l'hôte de référence : le déploiement n'est « complet » qu'après publication de l'image backend et configuration ACME/secrets Traefik.
- **`nvme.required = true`** : la passerelle **ne démarre pas** sans NVMe montable — point critique en maintenance/SAV.
- **Matching réseau par MAC** : `eth0Mac`/`eth1Mac` sont spécifiques à chaque carte ; un remplacement matériel impose de mettre à jour l'hôte Nix.
- **Input flake `essensys-nginx` en `path:../essensys-nginx`** : nécessite le dépôt frère présent localement (ou `--override-input` en CI).
- **Cohabitation avec `essensys-raspberry-install`** : deux voies de déploiement coexistent (NixOS déclaratif ici vs Ansible/Docker dans `raspberry-install`). Clarifier laquelle est la cible de production pour éviter la divergence.
- Nom très proche du dépôt stub `essensys-gateway` (vide) — risque de confusion.

## Liens

- [[Essensys Raspberry Install]]
- [[Essensys Gateway Dual Nic]]
- [[Client Essensys Legacy]]

## Source

`raw/architecture/repos/essensys-raspberry-gateway.md`
