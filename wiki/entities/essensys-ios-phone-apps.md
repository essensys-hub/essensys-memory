---
tags: [entity, repo, modern]
sources: [essensys-ios-phone-apps.md]
created: 2026-06-20
updated: 2026-06-20
era: modern
repo: essensys-ios-phone-apps
---

# Essensys IOS Phone Apps

> Application iOS native (Swift / SwiftUI) « Essensys » permettant de piloter une installation domotique Essensys (éclairage, volets, scénarios, chauffage…) depuis un iPhone, en local Wi-Fi ou à distance via WAN.

| | |
|---|---|
| **Catégorie** | Application mobile |
| **Stack** | Swift 5.0, SwiftUI, URLSession, Xcode project, iOS 18.2+ (déclaré ; README mentionne iOS 15+) |
| **Statut** | Active (CFBundleShortVersionString 1.2) — pendant iOS de l'app Android, même contrat backend. Projet partiellement « boucle ouverte » ; quelques écrans en évolution. |
| **Era** | modern |

## Rôle

Client mobile iOS grand public pour contrôler une installation domotique Essensys depuis un iPhone (et iPad). Comme l'app Android, c'est une télécommande légère sans logique métier embarquée : elle envoie des commandes d'injection (paires clé/valeur) dans la table d'échange Essensys via le backend (serveur Raspberry Pi, cf. `essensys-raspberry-install`). Elle nécessite une installation serveur Essensys fonctionnelle. Le contrat API et le modèle de connexion (local/WAN + mode démo) sont identiques à ceux de `essensys-android-phone-apps`.

## Intégrations

_Non documenté._

## Structure

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
        ├── Serv

_… voir source complète dans raw/_

## Points d'attention

- **Mode démo / fallback silencieux :** `ConnectionManager.testConnection()` bascule automatiquement et silencieusement en `isDemoMode` en cas d'erreur réseau ou HTTP non-200 (`enableDemoMode`). En démo, `sendInjection` et `getServerInfos` simulent un succès avec données fictives. Commentaire dans le code : comportement voulu pour passer la revue App Store quand le backend n'est pas joignable (IPv6, etc.) — masque les vrais échecs de connexion.
- **Boucle ouverte :** pas de retour d'état réel des équipements ; l'UI affiche l'état présumé après commande (note explicite dans le README).
- **Sécurité :** `NSAllowsArbitraryLoads` (HTTP en clair autorisé partout) ; mot de passe WAN stocké en clair dans `UserDefaults` ; auth limitée au Basic Auth.
- **Indices codés en dur :** les indices k/v sont des exemples figés (cf. `INDICES.md`, `LAMPES_LISTE.md`) à adapter à l'installation réelle ; pas de découverte dynamique des équipements.
- **Incohérence de cible iOS :** README annonce iOS 15.0+ alors que le projet impose `IPHONEOS_DEPLOYMENT_TARGET = 18.2` ; `UIRequiredDeviceCapabilities` contient encore `armv7` (architecture 32 bits obsolète, incohérent avec iOS 18).
- **Organisation projet f

_… voir source complète dans raw/_

## Liens

- [[Platform Overview]]

## Source

`raw/architecture/repos/essensys-ios-phone-apps.md`
