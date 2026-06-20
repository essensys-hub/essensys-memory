# Plan de Migration Essensys Legacy → Go + React

## Vue d'ensemble

Ce document décrit le plan de migration des projets legacy vers une architecture moderne :
- **Backend** : `essensys-server-backend` (Go)
- **Frontend** : `essensys-server-frontend` (React + TypeScript)

## Projets à migrer

1. **essensys-web-legacy** : Application ASP.NET MVC 4 (.NET Framework 4.0)
   - Backend : SQL Server + NHibernate
   - Frontend : jQuery + Razor Views
   
2. **client-essensys-legacy** : Client embarqué C (MQX RTOS)
   - ✅ Déjà supporté par le backend Go existant

## État actuel

### Backend Go (`essensys-server-backend`)
✅ **Déjà implémenté** :
- Protocole HTTP legacy pour clients embarqués
- Endpoints : `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}`
- Endpoint admin : `/api/admin/inject`
- Gestion des actions en mémoire
- Normalisation JSON malformé
- Authentification Basic Auth pour clients

❌ **À migrer** :
- Gestion des utilisateurs (login, inscription, validation)
- Gestion des machines/clients
- Persistance en base de données (actuellement en mémoire)
- Services métier (Alarme, Chauffage, Arrosage, Cumulus, Volets)
- Chiffrement AES pour alarmes
- Gestion des versions de firmware
- Gestion des sessions utilisateur

### Frontend React (`essensys-server-frontend`)
✅ **Déjà implémenté** :
- Interface de contrôle (éclairage, chauffage, volets, alarme, etc.)
- Communication avec backend via `/api/admin/inject`
- Composants UI pour toutes les fonctionnalités

❌ **À migrer** :
- Pages d'authentification (login, inscription, mot de passe oublié)
- Gestion de compte utilisateur
- Validation de compte
- Gestion des sessions

## Architecture cible

### ⚠️ IMPORTANT : Architecture Dual-Protocol

Le backend doit gérer **deux protocoles distincts** :

1. **Protocole Legacy** (Client IoT embarqué) : **NE JAMAIS MODIFIER**
   - Endpoints : `/api/serverinfos`, `/api/mystatus`, `/api/myactions`, `/api/done/{guid}`
   - JSON malformé (clés non-quotées) → normalisation automatique
   - Headers HTTP spécifiques (`Content-Type: application/json ;charset=UTF-8`)
   - Single-packet TCP requirement
   - **100% de compatibilité à maintenir**

2. **Protocole Moderne** (Frontend React) : Nouveaux endpoints
   - Endpoints : `/api/auth/*`, `/api/user/*`, `/api/machine/*`, etc.
   - JSON standard (RFC 8259)
   - Headers HTTP standards
   - REST API classique

Voir `docs/ARCHITECTURE_DUAL_PROTOCOL.md` pour les détails.

### Backend Go

```
essensys-server-backend/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── api/              ✅ Existe (handlers legacy)
│   │   ├── handlers.go    ✅ Handlers legacy IoT (NE PAS MODIFIER)
│   │   ├── handlers_web.go ❌ À créer (handlers web React)
│   │   └── router.go     ✅ Existe (à étendre avec séparation)
│   ├── auth/             ❌ À créer (sessions, JWT pour web)
│   ├── config/            ✅ Existe
│   ├── core/              ✅ Existe (action_service, status_service)
│   ├── data/              ✅ Existe (memory_store)
│   │   └── database/      ❌ À créer (repositories PostgreSQL)
│   ├── middleware/        ✅ Existe (auth legacy, logging)
│   │   └── web_auth.go    ❌ À créer (auth web avec sessions)
│   ├── models/            ✅ Créé (User, Machine, Action, State)
│   ├── services/          ❌ À créer (UserService, MachineService, etc.)
│   │   ├── alarm.go
│   │   ├── heating.go
│   │   ├── sprinkler.go
│   │   ├── water_heater.go
│   │   └── shutter.go
│   └── crypto/            ❌ À créer (AES encryption pour alarmes)
└── pkg/
    └── protocol/           ✅ Existe
```

### Frontend React

```
essensys-server-frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard/     ✅ Existe
│   │   ├── Auth/          ❌ À créer (Login, Register, ForgotPassword)
│   │   └── Account/       ❌ À créer (UpdateAccount, CloseAccount)
│   ├── services/
│   │   ├── legacyApi.ts   ✅ Existe
│   │   ├── authApi.ts     ❌ À créer
│   │   └── userApi.ts     ❌ À créer
│   ├── context/
│   │   ├── DashboardContext.tsx  ✅ Existe
│   │   └── AuthContext.tsx        ❌ À créer
│   └── App.tsx            ✅ Existe (à étendre)
```

## Plan de migration détaillé

### Phase 1 : Base de données et modèles (Priorité : Haute)

#### 1.1 Analyse du schéma legacy
- [ ] Analyser les entités NHibernate (EsUser, EsMachine, EsAction, EsState, etc.)
- [ ] Documenter les relations entre entités
- [ ] Identifier les index et contraintes

#### 1.2 Création du schéma PostgreSQL
- [ ] Créer les tables :
  - `users` (id, mail, password_hash, nom, prenom, question, reponse_hash, machine_id, etc.)
  - `machines` (id, no_serie, version, pkey, hashed_pkey, autorise_alarme, etc.)
  - `actions` (id, machine_id, type, guid, created_at, acknowledged_at, etc.)
  - `action_indices` (action_id, index_key, value)
  - `states` (id, machine_id, last_call, created_at)
  - `state_indices` (state_id, index_key, value, updated_at)
  - `versions` (id, version_number, filename, size, descriptif)
  - `version_machines` (id, machine_id, version_id, is_ok, step, date_action)
  - `cle_machines` (id, cle, machine_id)
  - `phones` (id, user_id, numero)
  - `sms_sends` (id, phone_id, message, sent_at)

#### 1.3 Migration des données
- [ ] Créer un script de migration SQL Server → PostgreSQL
- [ ] Tester la migration sur un environnement de test
- [ ] Valider l'intégrité des données

### Phase 2 : Couche de persistance Go (Priorité : Haute)

#### 2.1 Modèles Go
- [ ] Créer `internal/models/user.go`
- [ ] Créer `internal/models/machine.go`
- [ ] Créer `internal/models/action.go`
- [ ] Créer `internal/models/state.go`
- [ ] Créer `internal/models/version.go`

#### 2.2 Repositories
- [ ] Créer `internal/data/database/user_repository.go`
- [ ] Créer `internal/data/database/machine_repository.go`
- [ ] Créer `internal/data/database/action_repository.go`
- [ ] Créer `internal/data/database/state_repository.go`
- [ ] Créer `internal/data/database/version_repository.go`

#### 2.3 Interface Store
- [ ] Étendre `internal/data/store.go` pour supporter la base de données
- [ ] Implémenter `database_store.go` qui remplace `memory_store.go`
- [ ] Maintenir la compatibilité avec le code existant

### Phase 3 : Authentification et utilisateurs (Priorité : Haute)

#### 3.1 Authentification
- [ ] Créer `internal/auth/session.go` (gestion des sessions)
- [ ] Créer `internal/auth/jwt.go` (tokens JWT optionnels)
- [ ] Créer `internal/auth/password.go` (hash SHA1 comme legacy)
- [ ] Créer middleware d'authentification web (sessions)

#### 3.2 Services utilisateurs
- [ ] Créer `internal/services/user_service.go` :
  - `Login(email, password)`
  - `Register(user)`
  - `ValidateAccount(guid, email)`
  - `ForgotPassword(email)`
  - `UpdateUser(user)`
  - `CloseAccount(user)`
  - `TestQuestion(user, response)`

#### 3.3 Endpoints API utilisateurs
- [ ] `POST /api/auth/login`
- [ ] `POST /api/auth/logout`
- [ ] `POST /api/auth/register`
- [ ] `GET /api/auth/validate?guid=...&email=...`
- [ ] `POST /api/auth/forgot-password`
- [ ] `GET /api/user/me`
- [ ] `PUT /api/user/me`
- [ ] `POST /api/user/close-account`
- [ ] `POST /api/user/test-question`

### Phase 4 : Services métier (Priorité : Moyenne)

#### 4.1 Chiffrement AES
- [ ] Créer `internal/crypto/aes.go` :
  - Implémenter le chiffrement comme dans `AlarmeService.cs`
  - Utiliser AES-256-CBC
  - Format de sortie : `"byte1;byte2;byte3;..."`

#### 4.2 Services fonctionnels
- [ ] Créer `internal/services/alarm_service.go` :
  - `RegisterAction(user, machine, activate, response)`
  - Chiffrement AES de la commande alarme
  
- [ ] Créer `internal/services/heating_service.go` :
  - `RegisterAction(machine, value, zone)` (zj, zn, sdb1, sdb2)
  
- [ ] Créer `internal/services/sprinkler_service.go` :
  - `RegisterAction(machine, value)`
  
- [ ] Créer `internal/services/water_heater_service.go` :
  - `RegisterAction(machine, value)`
  
- [ ] Créer `internal/services/shutter_service.go` :
  - `RegisterAction(machine, shutters)` (liste d'indices/valeurs)
  - `RegisterActionAll(machine)`
  
- [ ] Créer `internal/services/store_service.go` :
  - `RegisterAction(machine)`

#### 4.3 Endpoints API actions
- [ ] `POST /api/actions/do` (remplace `HomeController.DoActions`)
  - Accepte les mêmes paramètres que l'endpoint legacy
  - Appelle les services appropriés

### Phase 5 : Gestion des machines et états (Priorité : Moyenne)

#### 5.1 Services machines
- [ ] Créer `internal/services/machine_service.go` :
  - `GetMachineByUser(user)`
  - `GetMachineByNoSerie(noSerie)`
  - `UpdateMachineVersion(machine, version)`
  - `GetLastCall(machine)`
  - `HasRefreshed(machine, lastCall)`
  - `AllActionsOK(machine)`
  - `LastSynchro(machine, lastCall)`

#### 5.2 Endpoints API machines
- [ ] `GET /api/machine/status`
- [ ] `GET /api/machine/wait-box`
- [ ] `POST /api/machine/purge-actions`
- [ ] `GET /api/machine/wait-actions`

### Phase 6 : Gestion des versions (Priorité : Basse)

#### 6.1 Services versions
- [ ] Créer `internal/services/version_service.go` :
  - `GetServerVersion()`
  - `GetVersionForMachine(machine)`
  - `StartVersionDownload(machine, version)`
  - `GetVersionStep(machine, version)`
  - `HasVersionFinished(machine, version)`

#### 6.2 Endpoints API versions
- [ ] `GET /api/version/server`
- [ ] `POST /api/version/init`
- [ ] `GET /api/version/wait`
- [ ] `GET /api/version/content/{step}`

### Phase 7 : Frontend React (Priorité : Haute)

#### 7.1 Authentification
- [ ] Créer `src/components/Auth/Login.tsx`
- [ ] Créer `src/components/Auth/Register.tsx`
- [ ] Créer `src/components/Auth/ForgotPassword.tsx`
- [ ] Créer `src/components/Auth/ValidateAccount.tsx`
- [ ] Créer `src/context/AuthContext.tsx`
- [ ] Créer `src/services/authApi.ts`

#### 7.2 Gestion de compte
- [ ] Créer `src/components/Account/UpdateAccount.tsx`
- [ ] Créer `src/components/Account/CloseAccount.tsx`
- [ ] Créer `src/services/userApi.ts`

#### 7.3 Routing
- [ ] Configurer React Router
- [ ] Routes protégées (nécessitent authentification)
- [ ] Redirection après login

#### 7.4 Intégration avec backend
- [ ] Mettre à jour `src/services/legacyApi.ts` pour utiliser les nouveaux endpoints
- [ ] Gérer les sessions (cookies ou tokens)
- [ ] Gérer les erreurs d'authentification

### Phase 8 : Tests et validation (Priorité : Haute)

#### 8.1 Tests backend
- [ ] Tests unitaires pour tous les services
- [ ] Tests d'intégration pour les endpoints API
- [ ] Tests de migration de données

#### 8.2 Tests frontend
- [ ] Tests des composants React
- [ ] Tests d'intégration des flux utilisateur
- [ ] Tests E2E (optionnel)

#### 8.3 Validation
- [ ] Comparer les fonctionnalités legacy vs nouvelle implémentation
- [ ] Tester avec des clients embarqués réels
- [ ] Valider la migration des données

## Mapping des fonctionnalités

### Contrôleurs ASP.NET → Endpoints Go

#### ⚠️ Endpoints Legacy IoT (NE PAS MODIFIER)

| Contrôleur Legacy | Endpoint Go | Protocole | Statut |
|-------------------|-------------|-----------|--------|
| `ServerInfosController` | `GET /api/serverinfos` | Legacy IoT | ✅ Existe |
| `MyStatusController` | `POST /api/mystatus` | Legacy IoT | ✅ Existe |
| `MyActionsController` | `GET /api/myactions` | Legacy IoT | ✅ Existe |
| `DoneController` | `POST /api/done/{guid}` | Legacy IoT | ✅ Existe |

**Ces endpoints sont pour le client IoT embarqué et ne doivent JAMAIS être modifiés.**

#### Nouveaux Endpoints Web (Frontend React)

| Contrôleur Legacy | Endpoint Go | Protocole | Statut |
|-------------------|-------------|-----------|--------|
| `HomeController.DoActions` | `POST /api/actions/do` | Moderne Web | ❌ À créer |
| `HomeController.WaitBox` | `GET /api/machine/wait-box` | Moderne Web | ❌ À créer |
| `HomeController.WaitActions` | `GET /api/machine/wait-actions` | Moderne Web | ❌ À créer |
| `HomeController.PurgeAllActions` | `POST /api/machine/purge-actions` | Moderne Web | ❌ À créer |
| `AccountController.Login` | `POST /api/auth/login` | Moderne Web | ❌ À créer |
| `AccountController.Register` | `POST /api/auth/register` | Moderne Web | ❌ À créer |
| `AccountController.UpdateMyInfos` | `PUT /api/user/me` | Moderne Web | ❌ À créer |
| `AccountController.TestResponse` | `POST /api/user/test-question` | Moderne Web | ❌ À créer |

### Services C# → Services Go

| Service Legacy | Service Go | Statut |
|----------------|------------|--------|
| `AlarmeService` | `internal/services/alarm_service.go` | ❌ À créer |
| `ChauffageService` | `internal/services/heating_service.go` | ❌ À créer |
| `ArrosageService` | `internal/services/sprinkler_service.go` | ❌ À créer |
| `CumulusService` | `internal/services/water_heater_service.go` | ❌ À créer |
| `VoletService` | `internal/services/shutter_service.go` | ❌ À créer |
| `StoreService` | `internal/services/store_service.go` | ❌ À créer |
| `UserService` | `internal/services/user_service.go` | ❌ À créer |
| `StateService` | `internal/services/state_service.go` | ❌ À créer |
| `ActionService` | `internal/core/action_service.go` | ✅ Existe (à étendre) |

## Technologies et dépendances

### Backend Go
- **Base de données** : PostgreSQL (driver : `github.com/lib/pq` ou `gorm.io/gorm`)
- **ORM/Migrations** : GORM ou sqlx + migrate
- **Sessions** : `github.com/gorilla/sessions`
- **JWT** (optionnel) : `github.com/golang-jwt/jwt/v5`
- **Crypto** : `crypto/aes`, `crypto/cipher` (standard library)

### Frontend React
- **Routing** : `react-router-dom`
- **State Management** : Context API (déjà utilisé)
- **HTTP Client** : `fetch` (standard) ou `axios`
- **Form Validation** : `react-hook-form` (recommandé)

## Ordre de priorité recommandé

1. **Phase 1** : Base de données (bloque tout)
2. **Phase 2** : Couche de persistance (bloque Phase 3)
3. **Phase 3** : Authentification (bloque Phase 7)
4. **Phase 7** : Frontend Auth (peut être fait en parallèle avec Phase 4)
5. **Phase 4** : Services métier
6. **Phase 5** : Gestion machines
7. **Phase 6** : Gestion versions (peut être fait en dernier)
8. **Phase 8** : Tests (tout au long du projet)

## Notes importantes

### ⚠️ CRITIQUE : Protocole Legacy IoT

Le client embarqué `client-essensys-legacy` est un **très vieux client IoT** qui :
- ❌ Ne respecte **PAS** les standards HTTP/REST
- ❌ Envoie du **JSON malformé** (clés non-quotées)
- ❌ Nécessite des **headers HTTP spécifiques** (espace avant `;charset`)
- ❌ Requiert des **réponses en un seul paquet TCP**
- ✅ Utilise Go car Node.js est **impossible** avec ce niveau de client

**RÈGLE ABSOLUE** : Les endpoints legacy **NE DOIVENT JAMAIS ÊTRE MODIFIÉS** :
- `/api/serverinfos` (GET)
- `/api/mystatus` (POST)
- `/api/myactions` (GET)
- `/api/done/{guid}` (POST)

**Séparation des protocoles** :
- **Legacy IoT** : Endpoints existants (non modifiables)
- **Moderne Web** : Nouveaux endpoints séparés (`/api/auth/*`, `/api/user/*`, etc.)

Voir `docs/ARCHITECTURE_DUAL_PROTOCOL.md` pour les détails complets.

### Sécurité
- Les mots de passe sont hashés en SHA1 (comme legacy) pour la migration
- Considérer une migration vers bcrypt/argon2 après migration complète
- Les sessions doivent être sécurisées (HttpOnly, Secure, SameSite)

### Performance
- Le backend actuel utilise un store en mémoire (très rapide)
- La migration vers PostgreSQL nécessitera des optimisations (index, connexions pool)
- Considérer un cache Redis pour les données fréquemment accédées

## Ressources

- Documentation legacy : `essensys-web-legacy/docs/`
- Documentation client : `client-essensys-legacy/docs/`
- Backend Go existant : `essensys-server-backend/`
- Frontend React existant : `essensys-server-frontend/`

