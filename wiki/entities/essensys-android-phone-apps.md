---
tags: [entity, repo, modern]
sources: [essensys-android-phone-apps.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-android-phone-apps
---

# Essensys Android Phone Apps

> Application Android native (Kotlin / Jetpack Compose) « Mon Essensys » permettant de piloter une installation domotique Essensys (éclairage, volets, scénarios) en local Wi-Fi ou à distance.

| | |
|---|---|
| **Catégorie** | Application mobile |
| **Stack** | Kotlin, Jetpack Compose (Material 3), OkHttp / Retrofit, Gradle (KTS), Android SDK 26-34 |
| **Statut** | Active (v1.0.0, APK distribué dans le dépôt) — fonctionnelle mais légère et partiellement « boucle ouverte » (Alarme en cours de dev). |
| **Era** | modern |

## Rôle

Client mobile grand public destiné à l'utilisateur final pour contrôler son installation domotique Essensys depuis un smartphone Android. C'est une télécommande légère qui s'appuie entièrement sur le backend Essensys (serveur tournant typiquement sur un Raspberry Pi). L'app n'embarque aucune logique métier domotique : elle envoie des commandes d'« injection » (paires clé/valeur) dans la table d'échange Essensys et n'a quasiment pas de retour d'état (commandes en boucle ouverte, l'état affiché est l'état supposé après action). Elle est le pendant Android de l'app iOS (`essensys-ios-phone-apps`), avec le même contrat backend.

## Intégrations

_Non documenté._

## Structure

```
essensys-android-phone-apps/
├── README.md                 # Présentation, fonctionnalités, captures, lien APK
├── build.gradle.kts          # Build top-level (plugins AGP/Kotlin/Compose)
├── settings.gradle.kts       # rootProject "EssensysAndroid", include :app
├── gradle.properties / gradlew / gradlew.bat
├── mon.essensys.v.1.0.0.apk  # APK pré-compilé distribué (≈15 Mo)
├── img/                       # Captures d'écran (app_android_00x.png)
└── app/
    ├── build.gradle.kts       # Config du module app + dépendances
    └── src/main/
        ├── AndroidManifest.xml
        ├── res/               # icônes, styles, strings (app_name = "Mon Essensys")
        └── java/com/essensys/android/
            ├── MainActivity.kt        # Point d'entrée, charge la config depuis SharedPreferenc

_… voir source complète dans raw/_

## Points d'attention

- **Mode démo / fallback silencieux :** si `checkConnection` échoue (réseau indisponible ou HTTP non-2xx), l'app bascule automatiquement et silencieusement en `isDemoMode` (commandes simulées comme réussies). Pratique pour démo/validation mais masque les vrais échecs de connexion à l'utilisateur.
- **Boucle ouverte :** pas de remontée d'état des équipements — l'UI affiche l'état présumé après envoi, pas l'état réel.
- **Sécurité :** `usesCleartextTraffic` activé (HTTP local en clair) ; identifiants WAN stockés en clair dans les SharedPreferences ; auth limitée au Basic Auth.
- **Retrofit déclaré mais inutilisé :** les dépendances Retrofit sont présentes mais le code réel utilise OkHttp brut + `org.json` — dette/dépendance superflue.
- **Indices codés en dur :** les indices k/v (table d'échange) sont des exemples figés dans le code et doivent correspondre à la configuration réelle de l'installation cible ; aucune découverte dynamique des équipements.
- **Fonctionnalité Alarme incomplète** (annoncée « en cours de développement » dans le README).
- **Propreté du dépôt :** présence de dumps heap `.hprof` (~3 Go cumulés) et d'artefacts de build à exclure du versionnement.

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-android-phone-apps.md`
