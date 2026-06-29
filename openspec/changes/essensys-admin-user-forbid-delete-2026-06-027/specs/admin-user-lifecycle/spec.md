# admin-user-lifecycle

Modération des comptes utilisateurs depuis l'admin `mon.essensys.fr` : interdiction (soft-ban), réautorisation, suppression ; enforcement à la connexion et sur les JWT actifs.

## ADDED Requirements

### Requirement: Soft-ban utilisateur avec conservation email

Le système MUST conserver l'enregistrement utilisateur (email, métadonnées, audit) lors d'une interdiction et MUST enregistrer `forbidden_at` à l'horodatage courant.

#### Scenario: Admin interdit un utilisateur

- **WHEN** un `admin_global` authentifié envoie `POST /api/admin/users/{id}/forbid`
- **AND** la cible n'est pas déjà interdite
- **THEN** la réponse est `200` ou `204`
- **AND** `forbidden_at` est non null en base
- **AND** l'email de l'utilisateur reste inchangé
- **AND** un événement audit `FORBID_USER` est enregistré

#### Scenario: Admin local interdit un user de sa machine

- **WHEN** un `admin_local` envoie `POST /api/admin/users/{id}/forbid`
- **AND** la cible appartient à la même `linked_machine_id`
- **AND** la cible a le rôle `user` ou `guest_local`
- **THEN** l'interdiction réussit

#### Scenario: Admin local ne peut pas interdire un admin

- **WHEN** un `admin_local` tente d'interdire un utilisateur avec rôle `admin_global`, `admin_local` ou `support`
- **THEN** la réponse est `403 Forbidden`

### Requirement: Réautorisation d'un utilisateur interdit

Le système MUST permettre de lever une interdiction via `POST /api/admin/users/{id}/unforbid`, en remettant `forbidden_at` à NULL.

#### Scenario: Admin réautorise un utilisateur

- **WHEN** un admin autorisé envoie `POST /api/admin/users/{id}/unforbid` sur un compte interdit
- **THEN** `forbidden_at` devient NULL
- **AND** l'utilisateur peut se reconnecter normalement

### Requirement: Suppression admin d'un utilisateur

Le système MUST exposer `DELETE /api/admin/users/{id}` pour supprimer définitivement un compte (distinct de `DELETE /api/profile`).

#### Scenario: Admin global supprime un utilisateur

- **WHEN** un `admin_global` envoie `DELETE /api/admin/users/{id}`
- **AND** la cible n'est pas le dernier `admin_global` du système
- **THEN** la réponse est `204 No Content`
- **AND** l'enregistrement utilisateur n'existe plus en base
- **AND** un événement audit `DELETE_USER` est enregistré

#### Scenario: Interdiction suppression du dernier admin global

- **WHEN** un admin tente de supprimer le seul compte `admin_global` restant
- **THEN** la réponse est `409 Conflict` ou `403 Forbidden`

#### Scenario: Admin ne peut pas se supprimer via admin delete

- **WHEN** un admin tente `DELETE /api/admin/users/{id}` où `id` est son propre compte
- **THEN** la réponse est `403 Forbidden`
- **AND** l'auto-suppression reste disponible uniquement via `DELETE /api/profile`

### Requirement: Redirection page construction pour compte interdit

Un utilisateur dont `forbidden_at` est défini MUST NOT accéder au portail ni recevoir de JWT valide. À la tentative de connexion, le client MUST être redirigé vers `/maintenance/` (page « Site En Construction »).

#### Scenario: Login email refusé avec redirect

- **WHEN** un utilisateur interdit soumet des identifiants valides sur `POST /api/auth/login`
- **THEN** la réponse est `403 Forbidden`
- **AND** le corps JSON contient `error: "account_forbidden"` et `redirect: "/maintenance/"`
- **AND** aucun token JWT n'est émis

#### Scenario: Frontend redirige vers maintenance

- **WHEN** le frontend reçoit `account_forbidden` au login
- **THEN** il effectue `window.location.href = "/maintenance/"`
- **AND** aucun token n'est stocké dans localStorage/sessionStorage

#### Scenario: OAuth refusé pour compte interdit

- **WHEN** un utilisateur interdit complète OAuth Google ou Apple
- **THEN** le backend ne délivre pas de JWT
- **AND** le navigateur est redirigé vers `/maintenance/`

### Requirement: Invalidation JWT pour comptes interdits ou supprimés

Les middlewares protégeant les routes authentifiées MUST revalider l'utilisateur en base après validation du JWT.

#### Scenario: JWT émis avant interdiction rejeté

- **WHEN** un utilisateur possède un JWT valide non expiré
- **AND** un admin interdit ce compte ensuite
- **AND** l'utilisateur appelle une route protégée (ex. `GET /api/profile`)
- **THEN** la réponse est `403 Forbidden` avec `error: "account_forbidden"`
- **AND** l'accès est refusé malgré la signature JWT valide

#### Scenario: JWT après suppression utilisateur

- **WHEN** un utilisateur supprimé présente un JWT encore valide
- **THEN** toute route protégée répond `401 Unauthorized` ou `403 Forbidden`

### Requirement: UI admin actions Interdire et Supprimer

La page **Gestion des Utilisateurs** MUST afficher des actions de modération dans la colonne Actions, avec confirmation utilisateur.

#### Scenario: Boutons visibles pour admin global

- **WHEN** un `admin_global` consulte la liste utilisateurs
- **THEN** chaque ligne affiche **Interdire** (ou **Réautoriser** si interdit) et **Supprimer**
- **AND** les comptes interdits affichent un badge « Interdit »

#### Scenario: Confirmation avant suppression

- **WHEN** l'admin clique **Supprimer**
- **THEN** une boîte de dialogue demande confirmation (email affiché)
- **AND** l'API n'est appelée qu'après validation

#### Scenario: Scope admin local

- **WHEN** un `admin_local` consulte la liste
- **THEN** les actions Interdire/Supprimer ne sont proposées que pour les utilisateurs de son armoire (`linked_machine_id`)
- **AND** pas pour les rôles privilégiés
