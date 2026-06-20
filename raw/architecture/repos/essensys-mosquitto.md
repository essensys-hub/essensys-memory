# essensys-mosquitto

> Broker MQTT (Eclipse Mosquitto) de la gateway Essensys, point d'echange temps reel entre les objets domotiques IoT et le backend.

**Catégorie :** Infrastructure
**Stack :** Eclipse Mosquitto (Alpine `apk`), Docker (multi-arch arm64/amd64), image de base `essensyshub/essensys-base`
**Statut :** Actif

## Rôle dans l'architecture Essensys

Mosquitto est le bus de messages MQTT de la gateway. C'est le canal temps reel par lequel les equipements IoT/domotiques (cartes/boards Essensys, capteurs, actionneurs) publient leurs etats et recoivent leurs commandes, en interaction avec le backend Essensys. Il tourne dans la stack Docker de la gateway en `network_mode: host`.

## Configuration & fichiers clés

- `mosquitto.conf` :
  - `listener 1883` — listener MQTT standard ;
  - `allow_anonymous false` + `password_file /mosquitto/config/passwd` — authentification obligatoire par identifiant/mot de passe ;
  - `persistence true` / `persistence_location /mosquitto/data/` — persistance disque ;
  - `log_dest file /mosquitto/log/mosquitto.log` — journalisation fichier.
- `Dockerfile` — installe Mosquitto via `apk`, cree `/mosquitto/{config,data,log}`, copie la config.
- `.dockerignore` — exclut `.git`, `.github`, `README.md`.
- `.github/workflows/docker-build.yml` — CI de build/push.

## Build / Déploiement (Docker, ports exposés)

- Image : `essensyshub/essensys-mosquitto`, taguee par version Essensys + `latest`.
- Build CI multi-arch (`linux/arm64`, `linux/amd64`) sur tags `V.*` ou manuel, push Docker Hub.
- `EXPOSE 1883` ; volumes `/mosquitto/data` et `/mosquitto/log`.
- CMD `mosquitto -c /mosquitto/config/mosquitto.conf`.
- En production (template Ansible) : `network_mode: host`, `user: "0:0"`, `restart: unless-stopped`. Le fichier `passwd` et la config sont montes en lecture seule, les volumes data/log montes depuis l'hote. Le mot de passe de l'utilisateur `essensys` est genere par Ansible (role `raspberry_mosquitto`).

## Intégrations (quels services route/proxy/surveille-t-il)

- **Boards / objets IoT Essensys** — publient/souscrivent les topics MQTT (etats, telemetrie, commandes).
- **backend Essensys** — consomme et emet sur le broker pour piloter les equipements.
- N'est pas expose au WAN : usage interne a la gateway (LAN / boucle locale).

## Points d'attention

- `chmod -R 777 /mosquitto` dans le Dockerfile : permissions tres larges (simplifie le montage de volumes mais a surveiller cote securite).
- Listener `1883` en clair (pas de TLS) : acceptable car broker interne, mais ne doit pas etre expose hors du LAN.
- L'authentification depend du fichier `passwd` : il doit etre provisionne (via Ansible) sinon aucun client ne peut se connecter (`allow_anonymous false`).
- Port 1883 standard non chiffre ; pas de listener `8883` (MQTT/TLS) configure.
