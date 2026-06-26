# lan-iam

Gestion des comptes et mots de passe sur le réseau local (`mon.essensys.local`). Comptes dans la table **`lan_users`** ; sessions cookie (TTL **7 jours**) ; RBAC LAN. Protocole legacy IoT inchangé.

## ADDED Requirements

### Requirement: Persistance comptes dans `lan_users`

Le système MUST stocker les identités IAM LAN dans une table PostgreSQL dédiée `lan_users`, distincte de la table legacy `users`.

#### Scenario: Login lit uniquement lan_users

- **WHEN** un utilisateur envoie `POST /api/auth/login`
- **THEN** les credentials sont validés contre `lan_users` uniquement
- **AND** aucune lecture de la table legacy `users` n'est effectuée pour l'authentification LAN v1

#### Scenario: Création compte dans lan_users

- **WHEN** un `lan_admin` crée un utilisateur
- **THEN** une ligne est insérée dans `lan_users` avec `role` ∈ {`lan_admin`, `lan_user`, `lan_guest`}

### Requirement: Bootstrap premier administrateur LAN

Le système MUST permettre la création du premier compte `lan_admin` via un mécanisme à usage unique (token fichier ou Ansible), sans inscription publique ouverte.

#### Scenario: Bootstrap réussi avec token valide

- **WHEN** aucun compte `lan_admin` n'existe
- **AND** une requête `POST /api/admin/lan-users/bootstrap` inclut le token one-shot et un email/mot de passe conforme à la politique
- **THEN** le compte `lan_admin` est créé avec `password_algo` moderne (bcrypt ou argon2id)
- **AND** le token bootstrap est invalidé
- **AND** la réponse est `201 Created`

#### Scenario: Bootstrap refusé si admin existe déjà

- **WHEN** au moins un compte `lan_admin` actif existe
- **AND** une requête bootstrap est envoyée
- **THEN** la réponse est `409 Conflict`

### Requirement: Authentification session LAN

Le système MUST authentifier les utilisateurs LAN par email et mot de passe et MUST émettre une session cookie HttpOnly, Secure, SameSite=Lax.

#### Scenario: Login réussi

- **WHEN** un utilisateur actif envoie `POST /api/auth/login` avec email et mot de passe valides
- **THEN** la réponse est `200 OK` avec profil utilisateur (sans hash)
- **AND** un cookie de session est défini

#### Scenario: Login échoué — identifiants invalides

- **WHEN** email ou mot de passe incorrect
- **THEN** la réponse est `401 Unauthorized` sans révéler si l'email existe

#### Scenario: Login échoué — compte désactivé

- **WHEN** l'utilisateur a `disabled_at` renseigné
- **THEN** la réponse est `403 Forbidden` avec code `account_disabled`

#### Scenario: Logout

- **WHEN** un utilisateur authentifié envoie `POST /api/auth/logout`
- **THEN** la session est invalidée et le cookie est effacé

### Requirement: Durée de session sept jours

Le système MUST émettre des sessions valides **7 jours** (168 h) avec prolongation glissante sur activité API authentifiée.

#### Scenario: Session active dans la fenêtre 7 jours

- **WHEN** un utilisateur authentifié appelle une route protégée dans les 7 jours suivant la dernière activité
- **THEN** la session reste valide
- **AND** la date d'expiration glissante est prolongée (max 7 j depuis dernière activité)

#### Scenario: Session expirée après 7 jours d'inactivité

- **WHEN** plus de 7 jours se sont écoulés sans activité authentifiée
- **THEN** la session est rejetée avec `401 Unauthorized`
- **AND** le client MUST rediriger vers `/login`

### Requirement: Droits rôle lan_guest

Le rôle `lan_guest` MUST disposer des **mêmes droits de pilotage domotique LAN** que `lan_user` et MUST NOT accéder aux routes d'administration des comptes.

#### Scenario: Guest injecte une action domotique

- **WHEN** un `lan_guest` authentifié envoie `POST /api/admin/inject`
- **THEN** la requête est acceptée (même comportement que `lan_user`)

#### Scenario: Guest lance un scénario

- **WHEN** un `lan_guest` authentifié appelle une route de lancement scénario UI
- **THEN** la requête est acceptée

#### Scenario: Guest ne gère pas les utilisateurs

- **WHEN** un `lan_guest` tente `GET /api/admin/lan-users`
- **THEN** la réponse est `403 Forbidden`

### Requirement: Protection des routes dashboard

Les routes de pilotage UI MUST exiger une session valide. Les routes legacy IoT MUST rester accessibles sans session cookie.

#### Scenario: Route admin sans session

- **WHEN** une requête `POST /api/admin/inject` est envoyée sans cookie de session
- **THEN** la réponse est `401 Unauthorized`

#### Scenario: Route legacy IoT sans session

- **WHEN** le firmware envoie `POST /api/mystatus` sans cookie de session
- **THEN** la requête est traitée normalement (compatibilité BP_MQX_ETH)

### Requirement: CRUD administrateur utilisateurs LAN

Un `lan_admin` MUST pouvoir créer, lister, désactiver et réinitialiser le mot de passe des comptes LAN.

#### Scenario: Création utilisateur par admin

- **WHEN** un `lan_admin` envoie `POST /api/admin/lan-users` avec email, rôle (`lan_user` ou `lan_guest`) et mot de passe temporaire
- **THEN** le compte est créé avec `password_algo` moderne
- **AND** la réponse est `201 Created`

#### Scenario: Non-admin ne peut pas créer d'utilisateur

- **WHEN** un `lan_user` tente `POST /api/admin/lan-users`
- **THEN** la réponse est `403 Forbidden`

#### Scenario: Réinitialisation mot de passe par admin

- **WHEN** un `lan_admin` envoie `POST /api/admin/lan-users/{id}/reset-password` avec un nouveau mot de passe
- **THEN** le hash est mis à jour avec algorithme moderne
- **AND** les sessions actives de l'utilisateur sont invalidées

#### Scenario: Désactivation compte

- **WHEN** un `lan_admin` envoie `POST /api/admin/lan-users/{id}/disable`
- **THEN** `disabled_at` est renseigné
- **AND** les sessions actives sont invalidées

### Requirement: Changement mot de passe self-service

Un utilisateur authentifié MUST pouvoir changer son propre mot de passe.

#### Scenario: Changement mot de passe réussi

- **WHEN** un utilisateur envoie `PUT /api/user/me/password` avec mot de passe actuel et nouveau mot de passe valide
- **THEN** le hash est mis à jour (algo moderne)
- **AND** la session courante reste valide

#### Scenario: Ancien mot de passe incorrect

- **WHEN** le mot de passe actuel est incorrect
- **THEN** la réponse est `401 Unauthorized`

### Requirement: Inscription publique fermée

Le système MUST refuser l'inscription ouverte sur le LAN en v1.

#### Scenario: Register public refusé

- **WHEN** une requête `POST /api/auth/register` est reçue sans token admin ou bootstrap
- **THEN** la réponse est `403 Forbidden`

### Requirement: Fin de la capture Basic Auth passive

Le système MUST NOT stocker les credentials Basic Auth encodés en Redis lorsque l'IAM LAN est activé.

#### Scenario: IAM LAN activé — pas de capture passive

- **WHEN** `LAN_IAM_ENABLED=true`
- **AND** une requête inclut un header `Authorization: Basic …`
- **THEN** les credentials ne sont pas persistés dans Redis à des fins d'audit passive
- **AND** l'authentification repose sur la session cookie pour les routes protégées

### Requirement: Compatibilité hash legacy (import optionnel)

Si un script de migration importe des comptes depuis la table legacy `users` vers `lan_users`, le système MAY accepter temporairement `password_algo=sha1_legacy`. Tout compte créé nativement dans `lan_users` MUST utiliser bcrypt ou argon2id.

#### Scenario: Login compte importé SHA1

- **WHEN** un compte dans `lan_users` a `password_algo=sha1_legacy` (import migration)
- **AND** le mot de passe correspond au hash SHA1 UTF-16
- **THEN** le login réussit

#### Scenario: Nouveau compte jamais en SHA1

- **WHEN** un compte est créé via bootstrap ou CRUD admin dans `lan_users`
- **THEN** `password_algo` MUST NOT être `sha1_legacy`

#### Scenario: Upgrade hash au changement mot de passe

- **WHEN** un compte change son mot de passe avec succès
- **THEN** `password_algo` passe à l'algorithme moderne configuré
