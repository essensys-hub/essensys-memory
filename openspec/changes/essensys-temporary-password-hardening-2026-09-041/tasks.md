## 1. Indicateur persisté et garde structurel — essensys-support-site

- [ ] 1.1 Créer `site/src/lib/authState.js` exposant `isPasswordChangeRequired()`, `markPasswordChangeRequired()`, `clearPasswordChangeRequired()` sur la clé `adminPasswordChangeRequired` dans `localStorage` et `sessionStorage` (D1) ; vérifier par un test unitaire Vitest ou, à défaut d'infrastructure Vitest dans ce dépôt, par un test Playwright qui pose l'indicateur, recharge, et lit le storage
- [ ] 1.2 Dans `Login.jsx`, appeler `markPasswordChangeRequired()` avant `navigate('/change-password?…')` quand la réponse porte `password_change_required: true` ; vérifier par le test e2e existant « connexion avec mot de passe temporaire redirige vers /change-password » étendu d'une assertion sur le storage
- [ ] 1.3 Dans `passwordChangeGuard.js`, sur `409 password_change_required` : appeler `markPasswordChangeRequired()`, puis rediriger vers `/change-password?return=<pathname+search>` construit localement, sans redirection si la page courante est `/change-password` ou `/login` (D3) ; vérifier par le test e2e « un 409 sur une session existante ramène à /change-password » étendu d'une assertion sur le paramètre `return`
- [ ] 1.4 Dans `ChangePassword.jsx`, appeler `clearPasswordChangeRequired()` juste avant `redirectAfterAuth` au succès ; au montage, si l'indicateur est posé, tenter `GET /api/profile` et, sur `200`, effacer l'indicateur et rediriger directement (Risks, indicateur orphelin) ; vérifier par test e2e des deux cas
- [ ] 1.5 Dans `Admin.jsx` (`handleLogout`) et `ChangePassword.jsx` (déconnexion), appeler `clearPasswordChangeRequired()` ; vérifier par test e2e « déconnexion disponible depuis /change-password » étendu d'une assertion sur le storage
- [ ] 1.6 Créer `site/src/components/RequirePasswordChange.jsx` : rend `<Navigate to="/change-password?return=…" replace />` si l'indicateur est posé, sinon ses enfants (D2) ; envelopper `/admin` et `/profile` dans `App.jsx` ; vérifier par le nouveau test e2e « accès direct à une autre page ramène à /change-password » : indicateur posé via `page.evaluate`, `page.goto('/admin')`, assertion sur l'URL finale, et un `page.route('**/api/**')` qui fait échouer le test s'il est atteint

## 2. Manifest et tests — essensys-support-site

- [ ] 2.1 Renommer les projets de `site/playwright.config.js` en `support-desktop`, `support-iphone`, `support-ipad` et adapter les gardes par nom de projet dans `site/e2e/*.spec.js` (`endsWith('-desktop')`) (D8) ; vérifier que chaque entrée de `required_projects` des manifestes 040 et 041 existe désormais dans la configuration, et que `npx playwright test --list` montre les trois nouveaux noms
- [ ] 2.2 Renommer les tests de `site/e2e/temporary-password.spec.js` pour que chaque titre soit exactement une entrée de `coverage_must_test`, et retirer de `coverage_must_test` toute entrée sans test correspondant (D8) ; vérifier que `check_feature_gate.py --strict` n'émet plus aucun avertissement « Coverage requirement not matched »
- [ ] 2.3 Ajouter les scénarios « bascule d'affichage des mots de passe » et « pages publiques non affectées » aux tests e2e (D9) ; exécuter la suite complète sur les trois projets et vérifier 0 échec

- [ ] 2.4 Dans `features/essensys-temporary-password-hardening-2026-09-041.json`, ajouter à `implementation.paths` et `release.paths` les fichiers créés par 1.1, 1.6 et 3.1 (`site/src/lib/authState.js`, `site/src/components/RequirePasswordChange.jsx`, `site/src/hooks/usePasswordConfirmation.js`) — le gate refuse tout chemin inexistant, ils ne peuvent y figurer qu'une fois créés ; passer `status` à `in-progress` ; vérifier `check_feature_gate.py --strict` : 0 erreur, 0 avertissement de couverture

## 3. Déduplication — essensys-support-site

- [ ] 3.1 Créer `site/src/hooks/usePasswordConfirmation.js` retournant `{ tooShort, mismatch, hint }` à partir de `{ password, confirm, minLength }`, `MIN_PASSWORD_LENGTH` déplacé dans le hook (D7) ; l'utiliser dans `ResetPassword.jsx` et `ChangePassword.jsx` en supprimant les dérivations dupliquées ; vérifier que les tests e2e de réinitialisation existants et ceux de 040 passent à l'identique

## 4. Sécurité et déduplication — essensys-user-portal-backend

- [ ] 4.1 Dans `.gitleaks.toml`, supprimer `'''_test\.go$'''` de `paths` et ajouter à `regexes` : `'''^test-secret-key(-[0-9]+)?$'''`, `'''^(secret|test-admin)-token$'''`, `'''^0123456789abcdef$'''`, chacune commentée avec le fichier de test qui porte le littéral (D5) ; vérifier `gitleaks detect --config .gitleaks.toml --no-git` à zéro finding
- [ ] 4.2 Test négatif de couverture : ajouter temporairement une chaîne au format clé AWS (`AKIA` + 16 majuscules/chiffres) dans un `_test.go`, vérifier que gitleaks la détecte, la retirer (D5) ; consigner le résultat dans le message de commit
- [ ] 4.3 Dans `internal/identity/routes.go`, créer `rateLimitMiddleware(rl, auditAction, message)` et réécrire `registerRateLimitMiddleware`, `resetRateLimitMiddleware`, `changePasswordRateLimitMiddleware` comme appels à cette fonction, messages et actions d'audit inchangés (D6) ; vérifier `go test ./internal/identity/...` vert et, par un test, que les trois routes répondent toujours `429` au-delà de leur plafond avec le même message qu'avant

## 5. Spécification 040 et mémoire — essensys-memory

- [ ] 5.1 Amender D6 dans `openspec/changes/essensys-temporary-password-2026-09-040/design.md` avec le texte de D4 de cette change et une ligne « Amendé par essensys-temporary-password-hardening-2026-09-041 » ; vérifier `openspec validate essensys-temporary-password-2026-09-040 --strict`
- [ ] 5.2 Mettre à jour la page [[Portal Authentication]] : verrou structurel + réactif, préservation de `?return=`, et retirer la mention « les modales préexistantes n'ont pas été retouchées » si 3.x les touche (elle ne les touche pas — vérifier et laisser telle quelle)
- [ ] 5.3 Faire passer `check_feature_gate.py --strict` sur les deux manifestes (`essensys-user-portal-backend`, `essensys-support-site`) et vérifier 0 erreur et 0 avertissement de couverture

## 6. Livraison

- [ ] 6.1 Ouvrir une PR par dépôt de code (backend : base `main` ; support-site : base `feat/essensys-support-nav-responsive-2026-06-032`), lancer `/code-review ultra` sur chacune, et vérifier qu'aucun des six points du `proposal.md` n'est de nouveau signalé
- [ ] 6.2 Après merge, poser le tag `V.1.2.0` sur `essensys-support-site` et déployer avec le playbook durci par `essensys-deploy-secrets-parity-2026-09-042` (prérequis : 042 livrée d'abord) ; vérifier en prod, sur un compte de test, le scénario « accès direct par URL » avec l'onglet réseau ouvert
