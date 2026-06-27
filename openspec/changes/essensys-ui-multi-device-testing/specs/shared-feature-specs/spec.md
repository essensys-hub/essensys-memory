# shared-feature-specs

Specs Playwright partagées par feature, paramétrées par project, avec Page Objects jumeaux.

## ADDED Requirements

### Requirement: Une spec par feature, multi-projects

Chaque feature UI jumelle MUST avoir une spec unique (ex. `shutters.spec.ts`) exécutée par tous les projects de la matrice, sans duplication par device.

Helpers MUST extraire cible et device depuis `testInfo.project.name`.

#### Scenario: Volets sur cinq devices demo

- **WHEN** `npx playwright test shutters.spec.ts --project=demo-iphone` s'exécute
- **THEN** la même spec que `demo-desktop` est utilisée
- **AND** les assertions UI s'adaptent au viewport mobile (menu drawer vs sidebar)

#### Scenario: Parité server et portail remote

- **WHEN** la spec volets passe sur `remote-desktop` et `local-desktop`
- **THEN** les sélecteurs Page Object sont identiques
- **AND** seule la baseURL / préfixe API diffère

### Requirement: Page Objects communs jumeaux

Le dossier `e2e/pages/` MUST centraliser les Page Objects pour :

`DashboardPage`, `LightingPage`, `HeatingPage`, `ShuttersPage`, `ScenariosPage`, `SecurityPage`, `SprinklerPage`, `WaterHeaterPage`, `NotificationsPage`, `UniFiProtectPage`, `SettingsPage`.

#### Scenario: Navigation dashboard

- **WHEN** un test ouvre la page dashboard via Page Object
- **THEN** les éléments clés (menu, titre, cartes) sont localisables sans sélecteur inline dans la spec
- **AND** le test vérifie l'absence d'erreur console bloquante

### Requirement: Assertions minimales par feature

Pour chaque feature, les specs MUST vérifier au minimum :

1. Chargement sans erreur console bloquante
2. Éléments clés visibles et interactifs dans le viewport device
3. Layout responsive (sidebar desktop ≥1024px ; `BottomTabs` / `MobileDrawer` <1024px)
4. Action dry-run (ex. clic monter volet) → verdict `test_ok`, jamais live

#### Scenario: Volets — bouton visible sur écran domotique

- **WHEN** la spec volets s'exécute sur `demo-ecran-domo`
- **THEN** le bouton principal de contrôle est visible sans scroll horizontal
- **AND** un clic déclenche un inject dry-run validé

#### Scenario: Scénarios — liste visible demo

- **WHEN** la spec scénarios ouvre `/scenarios` en project demo
- **THEN** au moins un slot scénario est visible
- **AND** aucune erreur parse JSON n'apparaît

### Requirement: Couverture support-site back-office

Des specs MUST couvrir le support-site pour : `Login`, `Profile`, `Admin`, `UserManager`, `LinkRequestsPanel`, `Catalog`, `SyncCloud` — avec mock réseau, projects `support-*`.

#### Scenario: Login support mocké

- **WHEN** la spec support login s'exécute sur `support-iphone`
- **THEN** la page Aurora login se charge
- **AND** le formulaire email/mot de passe est utilisable dans le viewport

### Requirement: Features jumelles couvertes

Les specs MUST couvrir l'ensemble des pages jumelles listées dans le prompt source avant clôture Phase 4.

#### Scenario: Matrice features checklist

- **WHEN** la Phase 4 est marquée complète dans tasks.md
- **THEN** chaque page jumelle possède une spec ou est incluse dans une spec groupe documentée
- **AND** `essensys-server-frontend` et `essensys-user-portal-frontend` sont tous deux exercés via projects local/remote
