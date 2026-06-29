## 1. Schéma et modèle

- [x] 1.1 Migration PostgreSQL : `ALTER TABLE users ADD COLUMN forbidden_at TIMESTAMPTZ NULL`
- [x] 1.2 Ajouter `ForbiddenAt *time.Time` au modèle `User` (`essensys-user-portal-backend/internal/domain`, miroir support-site)
- [x] 1.3 Méthodes store : `ForbidUser(id)`, `UnforbidUser(id)`, `CountAdminGlobal()` ; exposer `forbidden_at` dans les requêtes liste

## 2. Backend prod — essensys-user-portal-backend

- [x] 2.1 Helper `authorizeAdminTargetUser(caller, targetID, action)` partagé (role, links, forbid, delete)
- [x] 2.2 `POST /api/admin/users/{id}/forbid` et `POST …/unforbid` dans `internal/admin/handlers.go`
- [x] 2.3 `DELETE /api/admin/users/{id}` avec garde dernier admin_global et anti auto-delete
- [x] 2.4 Audit : `FORBID_USER`, `UNFORBID_USER`, `DELETE_USER`
- [x] 2.5 Login email + OAuth : refus si `forbidden_at` set, JSON `{ error, redirect }`
- [x] 2.6 Middleware JWT : lookup DB post-validation ; refus si interdit/supprimé
- [x] 2.7 Enregistrer routes dans `internal/admin/routes.go`
- [x] 2.8 Tests unitaires handlers (scope global/local, dernier admin, compte interdit)

## 3. Backend miroir — essensys-support-site/backend

- [x] 3.1 Reporter migration, modèle, store, handlers, middleware (parité avec portal-backend)
- [x] 3.2 `go test ./...` clean dans les deux backends

## 4. Frontend — essensys-support-site

- [x] 4.1 `UserManager.jsx` : badge « Interdit », boutons Interdire / Réautoriser / Supprimer + confirmations
- [x] 4.2 Appels API forbid/unforbid/delete avec refresh liste
- [x] 4.3 Scope UI : actions selon `adminRole` (global vs local)
- [x] 4.4 `Login.jsx` : redirect `/maintenance/` si `account_forbidden`
- [x] 4.5 Callback OAuth (Admin.jsx / redirect token) : même redirect si interdit
- [x] 4.6 Vérifier nginx sert `/maintenance/` en prod (doc ou playbook si manquant)

## 5. Sécurité et doc

- [x] 5.1 Corriger IDOR `UpdateUserLinks` via helper autorisation (finding revue #1)
- [x] 5.2 Re-run revue sécurité sur le diff implémenté
- [x] 5.3 Mettre à jour essensys-memory wiki si décision architecture (modération comptes)
- [x] 5.4 PR checklist : `[ ] Brain updated` ou N/A

## 6. Validation

- [ ] 6.1 Test manuel : interdire → login → redirect maintenance ; JWT existant rejeté
- [ ] 6.2 Test manuel : unforbid → login OK ; delete → compte absent
- [ ] 6.3 Test admin_local : forbid user scope OK, forbid admin refusé
