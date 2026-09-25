## Context

Voir `proposal.md` — Why pour la motivation et le point sensible vis-à-vis de la migration 013.

État actuel des briques concernées :

- `internal/middleware/user_status.go` expose `enforceActiveUser(w, users, email)`, traversé par `UserJWTWithStore`, `AdminJWTWithStore` et `AdminAuthWithStore`. Il recharge l'utilisateur depuis la base à chaque requête authentifiée et y applique déjà `domain.IsUserForbidden`. C'est le seul point de passage commun à `identity`, `portal` et `admin`.
- `internal/middleware/jwt.go` produit un JWT à quatre claims (`sub`, `role`, `exp`, `iss`), valable 24 h, sans état côté serveur.
- `internal/admin/password_reset.go` fixe la forme d'une action administrateur d'assistance : `requireAdminGlobal`, `404` compte inconnu, `409 account_forbidden`, envoi de courriel dont l'échec ne fait pas échouer l'action.
- `internal/data/password_reset_store.go` expose `InvalidateForUser(userID)`, déjà utilisé à l'émission d'un nouveau jeton.
- `internal/data/user_store.go` expose `UpdatePasswordHash(userID, hash)`, ajouté par la change 039 précisément pour ne toucher que l'empreinte.
- `internal/pwreset/token.go` porte `MinPasswordLength = 8`, plancher commun à l'inscription et à la réinitialisation.
- `internal/domain/auth.go` fournit `WriteAccountForbidden(w)`, patron d'une réponse d'erreur d'authentification structurée (`error` + `redirect`).
- `site/src/pages/UserManager.jsx` fait 1127 lignes et porte déjà deux modales (édition de liaisons, renvoi de courriel) sur le patron `const [xUser, setXUser] = useState(null)`.

Contraintes structurantes :

- `www.essensys.fr` sert le SPA de `essensys-support-site` et proxifie `/api/` vers `essensys-user-portal-backend` (`cloud_backend_consolidated: true`). La change porte donc sur deux dépôts dont un seul expose l'interface.
- Le protocole legacy IoT est hors périmètre : `middleware.BasicAuth` authentifie des machines contre la table `machines`, sans jamais lire `users.password_hash`.
- Le SMTP de production n'est pas garanti actif : l'émission doit rester correcte et utile quand l'envoi est indisponible.
- Les pages d'authentification n'existent que dans `essensys-support-site` ; la règle de synchronisation des jumeaux UI ne s'applique pas.

## Goals / Non-Goals

**Goals:**

- Une voie de déblocage qui ne dépend pas de la boîte mail de l'utilisateur.
- Un mot de passe temporaire dont la fenêtre d'exposition est bornée dans le temps et dans les usages.
- Un verrou **serveur**, non contournable en appelant l'API directement.
- Une traçabilité qui ne fait jamais figurer le mot de passe en clair.
- Une conception qui répond explicitement aux objections consignées dans la migration 013, plutôt que de les ignorer.

**Non-Goals:**

- Changer le parcours de création de compte par l'administrateur.
- Remplacer la réinitialisation par lien : elle reste la voie nominale quand l'utilisateur reçoit ses courriels.
- Historique des mots de passe, expiration périodique, politique de robustesse au-delà des 8 caractères existants.
- Révocation des JWT émis : hors sujet ici, le verrou étant évalué en base à chaque requête.
- Authentification à deux facteurs.

## Decisions

### D1 — Trois colonnes sur `users` plutôt qu'une table dédiée

```sql
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS password_change_required_at TIMESTAMPTZ NULL,
  ADD COLUMN IF NOT EXISTS temp_password_expires_at    TIMESTAMPTZ NULL,
  ADD COLUMN IF NOT EXISTS temp_password_issued_by     INT NULL REFERENCES users(id) ON DELETE SET NULL;
```

Rationale : contrairement aux jetons de réinitialisation, dont plusieurs peuvent coexister et dont l'historique sert au diagnostic, il existe au plus **un** mot de passe temporaire actif par compte à un instant donné — c'est le mot de passe lui-même, déjà stocké dans `password_hash`. Une table séparée n'aurait qu'une ligne utile par utilisateur et obligerait à une jointure sur le chemin chaud qu'est `enforceActiveUser`.

`temp_password_issued_by` en `ON DELETE SET NULL` : la suppression d'un compte administrateur ne doit pas supprimer en cascade les comptes qu'il a dépannés.

Corollaire assumé : `password_hash` est écrasé, l'ancien mot de passe est irrécupérable. C'est déjà le cas après une réinitialisation ; l'interface doit le dire à l'administrateur avant qu'il confirme.

Conformément à la convention du dépôt (`forbidden_at`, migration 010), le même `ALTER` est répété dans `UserStore.EnsureTableExists`.

### D2 — Le verrou est un drapeau en base, lu dans `enforceActiveUser`

```go
if domain.PasswordChangeRequired(user) {
    domain.WritePasswordChangeRequired(w)  // 409 {"error":"password_change_required", "redirect":"/change-password"}
    return nil, false
}
```

Rationale : un seul ajout couvre `identity`, `portal` et `admin`, puisque les trois middlewares passent par cette fonction. `enforceActiveUser` recharge déjà l'utilisateur depuis la base, donc le test ne coûte aucune requête supplémentaire. Le voisinage immédiat de `IsUserForbidden` rend la symétrie lisible : deux états de compte, deux refus structurés.

Deux propriétés en découlent :

- poser un mot de passe temporaire **gèle immédiatement les sessions déjà ouvertes**, ce qui est le comportement attendu d'une action de dépannage ;
- le JWT existant **redevient pleinement valide** à la seconde où le drapeau s'efface, donc le changement de mot de passe n'a aucun jeton à réémettre.

Alternative écartée : un claim `pwd_change` dans le JWT. Elle échoue sur le premier point — un jeton émis avant l'émission du mot de passe temporaire ne porte pas le claim et resterait pleinement valide jusqu'à 24 h — et impose de modifier `GenerateJWT` plus trois middlewares au lieu d'une fonction. Le code `409` plutôt que `403` : `403` est déjà celui du compte interdit, et les deux situations appellent des réactions différentes côté client.

### D3 — L'exemption est une fonction nommée, pas un drapeau

`middleware.UserJWTAllowPasswordChange(users)` duplique `UserJWTWithStore` en omettant le seul test D2. Elle ne sert qu'à monter `POST /auth/password/change`.

Rationale : un paramètre booléen traversant `enforceActiveUser` serait plus court mais ferait de la dérogation une option disponible partout, qu'un futur appelant pourrait activer par commodité. Une fonction distincte rend l'exemption visible à la lecture des routes et la cantonne à un point de montage unique.

### D4 — Alphabet sans caractères ambigus, 12 caractères

Nouveau paquet `internal/temppass` : `crypto/rand` sur un alphabet de 57 caractères excluant `O`, `0`, `I`, `l`, `1`, soit environ 70 bits d'entropie sur 12 caractères.

Rationale : ce mot de passe a vocation à être **dicté au téléphone**. Un `0` confondu avec un `O` transforme un dépannage en second appel. La contrainte coûte quelques bits d'entropie sur un secret qui vit 72 h et un seul usage, ce qui est un échange favorable. Paquet séparé plutôt que fonction privée dans `admin`, pour la même raison que `pwreset` : la génération est testable sans HTTP ni base.

Le clair n'est ni persisté, ni journalisé, ni renvoyé ailleurs que dans la réponse à l'émission.

### D5 — L'expiration est vérifiée après la comparaison bcrypt

Dans `identity.Login`, le test `TempPasswordExpired` est placé **après** `bcrypt.CompareHashAndPassword`.

Rationale : placé avant, il distinguerait un compte portant un mot de passe temporaire expiré d'un compte ordinaire pour un attaquant qui ne connaît pas le mot de passe, et renseignerait donc sur l'état d'un compte tiers. Après la comparaison, seul quelqu'un qui détient déjà le secret obtient `temporary_password_expired` ; tous les autres reçoivent `Invalid credentials`.

Aucune restauration de l'ancien mot de passe à l'expiration : il a été écrasé (D1). Passé 72 h, l'administrateur réémet, ou l'utilisateur emprunte la voie de réinitialisation par lien.

### D6 — L'émission invalide les jetons de réinitialisation en cours

`PasswordResetStore.InvalidateForUser(userID)` est appelé dans la transaction d'émission.

Rationale : sans cela, un lien de réinitialisation encore vivant et un mot de passe temporaire constituent deux identifiants concurrents pour le même compte. Le second annule l'intention du premier ; le laisser actif élargit la surface sans bénéfice. La méthode existe déjà et est utilisée dans le même esprit à l'émission d'un nouveau jeton.

### D7 — L'échec d'envoi de courriel ne fait pas échouer l'émission

Réponse `200` avec `email_sent: false` et `reason`, jamais `500`.

Rationale : le mot de passe est déjà posé en base et déjà affiché à l'administrateur, donc l'action a réussi ; seule la livraison optionnelle a échoué. Répondre `500` laisserait l'administrateur croire qu'il doit réessayer, ce qui réécrirait le mot de passe et invaliderait celui qu'il vient de lire. C'est exactement le raisonnement déjà tenu par `SendPasswordReset`.

### D8 — La modale part dans son propre fichier

`site/src/components/TemporaryPasswordModal.jsx` plutôt qu'une troisième modale dans `UserManager.jsx`, déjà à 1127 lignes.

Rationale : correction ciblée sur le code que cette change touche, sans refonte du fichier. La modale a un état propre en deux temps (confirmation, puis affichage unique) et une responsabilité qui se décrit en une phrase, donc elle satisfait le critère d'extraction sans en entraîner d'autres.

### D9 — Le modèle de courriel est créé activé, et son commentaire justifie le revirement

Le modèle `temporary_password` est inséré `enabled = true` par la migration 014, avec un commentaire SQL qui renvoie explicitement à 013 et énonce les quatre conditions du `proposal.md`.

Rationale : le modèle n'est envoyé que sur demande explicite de l'administrateur, donc l'activer ne provoque aucun envoi par lui-même. Sans le commentaire, la prochaine personne qui lira 013 puis 014 conclura à un oubli ou à une régression, et pourrait retirer la variable de bonne foi.

## Risks / Trade-offs

- **Le mot de passe transite par la voix.** Un interlocuteur mal identifié au téléphone obtient un accès. Atténuations : durée de vie 72 h, effacement au premier usage, entrée d'audit nominative désignant l'administrateur émetteur. L'authentification de l'appelant reste une procédure humaine, hors du périmètre logiciel ; elle doit figurer dans le guide support.
- **Le courriel optionnel rouvre la fenêtre que 013 avait fermée.** Assumé, borné par le caractère opt-in et par les 72 h. À réévaluer si l'usage montre que la case est cochée par défaut dans les faits.
- **Un compte peut rester gelé.** Si l'utilisateur ne se connecte jamais, le drapeau demeure et toutes ses sessions restent bloquées. Le badge dans la liste des utilisateurs rend l'état visible ; aucune purge automatique n'est prévue, la levée devant rester un geste explicite.
- **`enforceActiveUser` devient un point de défaillance plus large.** Une erreur y bloque tout le trafic authentifié. Atténuation : le test est une comparaison de pointeur nul sur une structure déjà chargée, et les tests couvrent les trois familles de routes.

## Migration Plan

1. Appliquer `014_temporary_password.sql`. Les trois colonnes sont `NULL` partout, donc le verrou D2 est inerte sur l'existant et aucun compte n'est affecté par le déploiement.
2. Déployer le backend. Le nouvel endpoint est monté mais n'a pas encore d'appelant.
3. Déployer le frontend. L'action apparaît dans l'administration et la route `/change-password` devient atteignable.

L'ordre importe : un frontend déployé avant le backend afficherait une action répondant `404`. Le retour arrière consiste à redéployer la version précédente des deux ; les colonnes peuvent rester en place, inertes. Un compte laissé avec le drapeau posé pendant un retour arrière resterait bloqué — la levée manuelle est un `UPDATE users SET password_change_required_at = NULL`, à consigner dans le runbook.

## Open Questions

Aucune. Les arbitrages de transmission, de verrouillage, de durée de vie et de périmètre ont été tranchés avant rédaction.
