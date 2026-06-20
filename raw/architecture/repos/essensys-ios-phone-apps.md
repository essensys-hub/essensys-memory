# essensys-ios-phone-apps

> Application iOS native (Swift / SwiftUI) « Essensys » permettant de piloter une installation domotique Essensys (éclairage, volets, scénarios, chauffage…) depuis un iPhone, en local Wi-Fi ou à distance via WAN.

**Catégorie :** Application mobile
**Stack :** Swift 5.0, SwiftUI, URLSession, Xcode project, iOS 18.2+ (déclaré ; README mentionne iOS 15+)
**Statut :** Active (CFBundleShortVersionString 1.2) — pendant iOS de l'app Android, même contrat backend. Projet partiellement « boucle ouverte » ; quelques écrans en évolution.

## Rôle dans l'architecture Essensys
Client mobile iOS grand public pour contrôler une installation domotique Essensys depuis un iPhone (et iPad). Comme l'app Android, c'est une télécommande légère sans logique métier embarquée : elle envoie des commandes d'injection (paires clé/valeur) dans la table d'échange Essensys via le backend (serveur Raspberry Pi, cf. `essensys-raspberry-install`). Elle nécessite une installation serveur Essensys fonctionnelle. Le contrat API et le modèle de connexion (local/WAN + mode démo) sont identiques à ceux de `essensys-android-phone-apps`.

## Stack technique & dépendances
- **Langage :** Swift 5.0.
- **UI :** SwiftUI (architecture déclarative, `@main` dans `essensys_iphoneApp.swift`, navigation par `TabView`), `ObservableObject`/Combine pour l'état de connexion.
- **Réseau :** `URLSession` natif + `JSONSerialization`/`Codable` (aucune dépendance tierce, pas de SPM/CocoaPods/Carthage).
- **Projet :** Xcode (`essensys-iphone.xcodeproj`), `IPHONEOS_DEPLOYMENT_TARGET = 18.2`, bundle identifier `essensys.essensys-iphone`, nom affiché « Essensys ». Targets : app `essensys-iphone`, `essensys-iphoneTests` (unit), `essensys-iphoneUITests` (UI).
- **Prérequis dev (README) :** Xcode 14.0+, iOS 15.0+ — à noter l'écart avec le deployment target réel (18.2) configuré dans le projet.
- **Info.plist :** `NSAppTransportSecurity` → `NSAllowsArbitraryLoads = true` (autorise HTTP non chiffré pour l'accès local) ; versions `CFBundleShortVersionString` 1.2 / `CFBundleVersion` 2.

## Structure du dépôt
```
essensys-ios-phone-apps/
├── README.md, SETUP.md, STRUCTURE.md, VERIFICATION.md,
│   TROUBLESHOOTING.md, PRIVACY.md, INDICES.md   # Documentation (FR)
├── LAMPES_LISTE.md                              # Inventaire des lampes / indices
├── img/, screen.png                             # Captures d'écran (App00x.png)
└── EssensysApp/
    ├── Info.plist
    └── essensys-iphone/
        ├── essensys-iphone.xcodeproj/           # Projet Xcode (à ouvrir)
        ├── essensys-iphone/                     # Target principale
        │   ├── essensys_iphoneApp.swift         # Point d'entrée @main
        │   └── ContentView.swift                # TabView racine, switch local/WAN
        ├── Models/
        │   └── ConnectionConfig.swift           # Config connexion (mode/URL/auth)
        ├── Services/
        │   ├── ConnectionManager.swift          # État connexion + auth + mode démo
        │   └── EssensysAPI.swift                # Appels API (inject, serverinfos)
        ├── Views/
        │   ├── HomeView.swift                   # Dashboard, scènes
        │   ├── LightingView.swift               # Éclairage par pièce (drag&drop réordonnable)
        │   ├── ShuttersView.swift               # Volets (Monter/Stop/Descendre)
        │   ├── HeatingView.swift                # Chauffage
        │   ├── WateringView.swift               # Arrosage
        │   ├── AlarmView.swift                  # Alarme
        │   └── ConfigurationView.swift          # Paramètres connexion
        ├── essensys-iphoneTests/                # Tests unitaires
        └── essensys-iphoneUITests/              # Tests UI
```
Écrans branchés dans `ContentView.swift` (TabView) : Home, Lighting, Shutters, Heating, Alarm, Watering, Configuration.

Note de structure : la doc (`STRUCTURE.md`/`SETUP.md`) signale que les fichiers `Models/`, `Services/`, `Views/` doivent être correctement rattachés à la target dans Xcode ; ces fichiers vivent à côté du `.xcodeproj`. Le dépôt est suivi comme un sous-module dans certains contextes (cf. messages de commit « Update EssensysApp submodule »).

## Build / Exécution / Déploiement
- **Ouverture :** `EssensysApp/essensys-iphone/essensys-iphone.xcodeproj`, target `essensys-iphone`.
- **Compilation/exécution :** `Cmd + R` sur simulateur ou appareil. L'app démarre sur l'onglet « Accueil ».
- **Signature/distribution :** ciblage App Store implicite (la logique de fallback mode démo est explicitement commentée comme « requise pour la validation App Store si le backend n'est pas joignable »). Aucune capability spéciale requise (cf. SETUP.md).
- **Configuration runtime :** persistée via `UserDefaults` (clé `essensys_connection_config`, `ConnectionConfig` encodé en JSON). Saisie dans l'écran Configuration (URL locale, URL WAN, utilisateur, mot de passe WAN).

## Intégrations (endpoints backend appelés)
Couche réseau dans `Services/EssensysAPI.swift` (singleton `EssensysAPI.shared`), deux endpoints :
- **`GET {currentURL}/api/serverinfos`** — test de connexion (au démarrage via `ConnectionManager.testConnection()` et `getServerInfos`). Réponse décodée en `ServerInfos { isconnected, infos[], newversion }`.
- **`POST {currentURL}/api/admin/inject`** — envoi des commandes domotiques. En-tête `Content-Type: application/json`, corps `{"k": <indice>, "v": "<valeur>"}` ; succès sur HTTP 200/201. `k` = indice de la table d'échange Essensys (~605-622 pour lumières/volets, cf. `INDICES.md`), `v` = valeur (souvent "4").

Sélection d'URL via `ConnectionConfig.currentURL` : mode `.local` → `localURL` (défaut `http://mon.essensys.fr`, sans auth) ; mode `.wan` → `wanURL` (ou fallback `https://mon.essensys.fr`). En WAN (`needsPassword`), ajout d'un header `Authorization: Basic` (base64 `user:motdepasse`, username « user » par défaut). Bascule local/WAN possible depuis l'en-tête (menu logo) et l'écran d'accueil.

## Points d'attention
- **Mode démo / fallback silencieux :** `ConnectionManager.testConnection()` bascule automatiquement et silencieusement en `isDemoMode` en cas d'erreur réseau ou HTTP non-200 (`enableDemoMode`). En démo, `sendInjection` et `getServerInfos` simulent un succès avec données fictives. Commentaire dans le code : comportement voulu pour passer la revue App Store quand le backend n'est pas joignable (IPv6, etc.) — masque les vrais échecs de connexion.
- **Boucle ouverte :** pas de retour d'état réel des équipements ; l'UI affiche l'état présumé après commande (note explicite dans le README).
- **Sécurité :** `NSAllowsArbitraryLoads` (HTTP en clair autorisé partout) ; mot de passe WAN stocké en clair dans `UserDefaults` ; auth limitée au Basic Auth.
- **Indices codés en dur :** les indices k/v sont des exemples figés (cf. `INDICES.md`, `LAMPES_LISTE.md`) à adapter à l'installation réelle ; pas de découverte dynamique des équipements.
- **Incohérence de cible iOS :** README annonce iOS 15.0+ alors que le projet impose `IPHONEOS_DEPLOYMENT_TARGET = 18.2` ; `UIRequiredDeviceCapabilities` contient encore `armv7` (architecture 32 bits obsolète, incohérent avec iOS 18).
- **Organisation projet fragile :** plusieurs documents (STRUCTURE.md/SETUP.md) traitent de l'ajout manuel des fichiers à la target Xcode, signe d'une intégration de projet pas totalement automatisée ; gestion en sous-module à surveiller.
