# essensys-android-phone-apps

> Application Android native (Kotlin / Jetpack Compose) « Mon Essensys » permettant de piloter une installation domotique Essensys (éclairage, volets, scénarios) en local Wi-Fi ou à distance.

**Catégorie :** Application mobile
**Stack :** Kotlin, Jetpack Compose (Material 3), OkHttp / Retrofit, Gradle (KTS), Android SDK 26-34
**Statut :** Active (v1.0.0, APK distribué dans le dépôt) — fonctionnelle mais légère et partiellement « boucle ouverte » (Alarme en cours de dev).

## Rôle dans l'architecture Essensys
Client mobile grand public destiné à l'utilisateur final pour contrôler son installation domotique Essensys depuis un smartphone Android. C'est une télécommande légère qui s'appuie entièrement sur le backend Essensys (serveur tournant typiquement sur un Raspberry Pi). L'app n'embarque aucune logique métier domotique : elle envoie des commandes d'« injection » (paires clé/valeur) dans la table d'échange Essensys et n'a quasiment pas de retour d'état (commandes en boucle ouverte, l'état affiché est l'état supposé après action). Elle est le pendant Android de l'app iOS (`essensys-ios-phone-apps`), avec le même contrat backend.

## Stack technique & dépendances
- **Langage :** Kotlin 2.0.0, JVM target 1.8.
- **UI :** Jetpack Compose avec Compose BOM 2023.08.00, Material 3, `material-icons-extended`, `activity-compose` 1.8.2, Navigation Compose 2.7.6.
- **Réseau :** OkHttp 4.12.0 (client réellement utilisé via `okhttp3.Request`/`Callback`), Retrofit 2.9.0 + converter-scalars (déclarés mais l'implémentation réelle passe par OkHttp brut et `org.json.JSONObject`).
- **Build :** Android Gradle Plugin 8.2.2, Gradle Kotlin DSL, module unique `:app`. `namespace`/`applicationId` = `com.essensys.android`, `compileSdk` 34, `minSdk` 26, `targetSdk` 34, `versionCode` 1 / `versionName` "1.0".
- **Prérequis dev :** Android Studio Ladybug+, JDK 17.
- **Permissions Android :** `INTERNET`, `ACCESS_NETWORK_STATE`. `usesCleartextTraffic="true"` activé (nécessaire pour l'accès HTTP local non chiffré vers `http://mon.essensys.fr`).

## Structure du dépôt
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
            ├── MainActivity.kt        # Point d'entrée, charge la config depuis SharedPreferences
            ├── data/EssensysAPI.kt    # Couche réseau (object singleton, OkHttp)
            └── ui/
                ├── MainScreen.kt      # Navigation Compose (NavHost) entre les écrans
                ├── HomeView.kt / HomeComponents.kt  # Accueil, scénarios, résumé config
                ├── LightingView.kt    # Éclairage par pièce (data lightingData)
                ├── ShuttersView.kt    # Volets roulants
                ├── HeatingView.kt     # Chauffage
                ├── WateringView.kt    # Arrosage
                ├── AlarmView.kt       # Alarme (en cours de dev)
                └── SettingsView.kt    # Configuration des URLs local/WAN + auth
```
Routes de navigation déclarées dans `MainScreen.kt` : `home`, `lighting`, `shutters`, `heating`, `alarm`, `watering`, `settings`.

Note : le dépôt contient plusieurs fichiers de débogage volumineux non pertinents qui devraient être ignorés/nettoyés (`java_pid*.hprof` ≈ 750 Mo chacun, dossiers `build/`, `.gradle/`).

## Build / Exécution / Déploiement
- **Compilation debug :** `./gradlew assembleDebug`.
- **Release :** build type `release` configuré, `isMinifyEnabled = false`, ProGuard par défaut référencé mais non actif (pas d'obfuscation/minification). Pas de signature configurée dans le repo.
- **Distribution :** l'APK release (`mon.essensys.v.1.0.0.apk`) est livré directement dans le dépôt et téléchargeable via un lien GitHub raw depuis le README (pas de publication Play Store visible). Installation manuelle via « sources inconnues ».
- **Configuration runtime :** persistée dans les `SharedPreferences` `EssensysPrefs` (`localUrl`, `wanUrl`, `username`, `password`, `isWanMode`), saisie par l'utilisateur dans l'écran Réglages.

## Intégrations (endpoints backend appelés)
L'app dialogue avec le backend Essensys via deux endpoints HTTP, gérés dans `data/EssensysAPI.kt` :
- **`GET {baseUrl}/api/serverinfos`** — vérification légère de la connexion au démarrage (`checkConnection`).
- **`POST {baseUrl}/api/admin/inject`** — envoi des commandes domotiques. Corps JSON `{"k": <indice>, "v": "<valeur>"}` où `k` est l'indice de la table d'échange Essensys et `v` la valeur (ex. `612`/`606` pour allumer/éteindre le salon, indices ~605-622). Toutes les actions UI (lumières, volets, scénarios) passent par `sendInjection(k, v, callback)`.

Sélection de l'URL : `baseUrl` = `localUrl` (mode local, par défaut `http://mon.essensys.fr`, sans auth) ou `wanUrl` (mode WAN distant). En mode WAN, ajout d'un header `Authorization: Basic` (Credentials OkHttp à partir de username/password).

## Points d'attention
- **Mode démo / fallback silencieux :** si `checkConnection` échoue (réseau indisponible ou HTTP non-2xx), l'app bascule automatiquement et silencieusement en `isDemoMode` (commandes simulées comme réussies). Pratique pour démo/validation mais masque les vrais échecs de connexion à l'utilisateur.
- **Boucle ouverte :** pas de remontée d'état des équipements — l'UI affiche l'état présumé après envoi, pas l'état réel.
- **Sécurité :** `usesCleartextTraffic` activé (HTTP local en clair) ; identifiants WAN stockés en clair dans les SharedPreferences ; auth limitée au Basic Auth.
- **Retrofit déclaré mais inutilisé :** les dépendances Retrofit sont présentes mais le code réel utilise OkHttp brut + `org.json` — dette/dépendance superflue.
- **Indices codés en dur :** les indices k/v (table d'échange) sont des exemples figés dans le code et doivent correspondre à la configuration réelle de l'installation cible ; aucune découverte dynamique des équipements.
- **Fonctionnalité Alarme incomplète** (annoncée « en cours de développement » dans le README).
- **Propreté du dépôt :** présence de dumps heap `.hprof` (~3 Go cumulés) et d'artefacts de build à exclure du versionnement.
