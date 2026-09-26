## Context

Voir `proposal.md`. État des briques touchées :

- `site/src/lib/passwordChangeGuard.js` patche `window.fetch` au démarrage et redirige vers `data.redirect` sur `409 password_change_required`. C'est le seul mécanisme actuel ; il ne connaît pas la page courante.
- `site/src/pages/Login.jsx` persiste `adminToken`/`adminRole` dans `localStorage` **et** `sessionStorage` via `persistAuth`, puis, si `password_change_required`, navigue vers `/change-password?return=<returnTo>`. L'indicateur lui-même n'est persisté nulle part : il ne survit pas à un rechargement.
- `site/src/App.jsx` déclare `/admin` et `/profile` comme routes plates sous `<Layout />`. Aucun garde de route n'existe dans ce SPA ; chaque page fait sa propre vérification de token dans un `useEffect`.
- `site/src/pages/Admin.jsx` traite le `409` en no-op (correctif de 040), et `handleLogout` efface `adminToken`/`adminRole` des deux storages.
- `internal/identity/routes.go` porte trois middlewares de rate-limit structurellement identiques (`registerRateLimitMiddleware`, `resetRateLimitMiddleware`, `changePasswordRateLimitMiddleware`), différant par l'action d'audit et le message.
- `.gitleaks.toml` : toutes les entrées existantes sont des chemins non-exécutables ou des regex de contenu. `_test\.go$` (040) est la seule entrée qui exempte du code compilé.

## Goals / Non-Goals

**Goals :**
- Qu'un compte verrouillé ne puisse atteindre aucune page de l'espace connecté, quel que soit le chemin (URL directe, historique, rechargement), sans dépendre du comportement au montage de chaque page.
- Que le manifest ne contienne aucune affirmation invérifiable.
- Que gitleaks ne perde aucune couverture sur le code compilé.
- Que `design.md` de 040 dise la vérité sur D6.

**Non-Goals :**
- Changer le contrat serveur (endpoints, codes, colonnes).
- Étendre le verrou aux pages publiques (`/`, `/blog`, `/support`) : le spec parle de « l'espace connecté », et un compte verrouillé qui lit le blog n'est pas un problème.
- Rendre l'émission transactionnelle (D6) : décision explicite de corriger le document, pas le code — voir D4.
- Corriger le feature-gate lui-même pour qu'il valide `required_projects` contre `playwright.config.js` : c'est un changement dans `essensys-feature-lifecycle`, à traiter là-bas. Cette change se contente de rendre le manifest vrai.

## Decisions

### D1 — Un indicateur persisté, une seule fonction pour le lire et l'écrire

Nouveau module `site/src/lib/authState.js` exposant `isPasswordChangeRequired()`, `markPasswordChangeRequired()`, `clearPasswordChangeRequired()`, sur la clé `adminPasswordChangeRequired` écrite dans les deux storages, comme `persistAuth` le fait pour le token.

Rationale : trois producteurs (login, garde 409, changement réussi) et deux consommateurs (garde de route, déconnexion) ; sans module partagé, la clé et la convention « les deux storages » se recopieraient cinq fois — la Duplicated Code que la revue a déjà relevée ailleurs. `authRedirect.js` a été extrait pour la même raison en 040 ; même patron.

Alternative écartée : dériver l'état du JWT. Le jeton ne porte pas cette information (D2 de 040 : le verrou est en base, pas dans le jeton), et c'est voulu.

### D2 — Garde de route par enveloppe, sur les routes protégées uniquement

`site/src/components/RequirePasswordChange.jsx` : si `isPasswordChangeRequired()` et que le chemin courant n'est pas `/change-password`, rend `<Navigate to="/change-password?return=<pathname+search>" replace />` ; sinon rend ses enfants. Appliqué dans `App.jsx` à `/admin` et `/profile`.

Rationale : `Navigate` s'exécute au rendu, **avant** tout `useEffect` de la page enveloppée — donc avant tout `fetch`. C'est ce que la tâche 7.5 demandait. Une enveloppe par route plutôt qu'un écouteur global sur `useLocation` : le périmètre (« espace connecté ») reste explicite et lisible dans `App.jsx`, et une future route protégée doit choisir de s'envelopper — un oubli est visible à la relecture, alors qu'un écouteur global avec liste d'exclusions rate silencieusement.

Le garde réactif (`passwordChangeGuard.js`) est **conservé** : c'est lui qui détecte un verrou posé *pendant* une session déjà ouverte, cas que l'indicateur persisté ne peut pas connaître avant le premier `409`. Les deux mécanismes sont complémentaires, pas redondants — le réactif écrit l'indicateur, le structurel l'applique ensuite partout.

### D3 — Le garde 409 construit lui-même la destination

`passwordChangeGuard.js` cesse d'utiliser `data.redirect` et construit `/change-password?return=${encodeURIComponent(location.pathname + location.search)}` — sauf si la page courante est déjà `/change-password` (aucune redirection) ou `/login` (le login gère lui-même son `returnTo`).

Rationale : `data.redirect` est un chemin nu émis par le serveur, qui ne connaît pas la page du client. Le serveur continue de l'envoyer (contrat inchangé) ; le client cesse de le suivre aveuglément.

### D4 — D6 de 040 : corriger le texte, pas le code

`design.md` de 040 est amendé en place : « `InvalidateForUser` est appelé **immédiatement après** `SetTemporaryPassword`, dans le même handler, sans transaction SQL commune. Un échec entre les deux laisse un ancien lien de réinitialisation valide en plus du mot de passe temporaire : les deux mènent au même résultat (un mot de passe choisi par l'utilisateur), ce n'est pas une élévation. Rendre ces deux écritures transactionnelles exigerait des variantes `WithTx` sur deux stores qui n'en ont pas ; le gain ne le justifie pas. » Une ligne « Amendé par 041 » est ajoutée.

Rationale : le document a divergé du code parce que l'implémenteur a tranché mentalement sans reporter. La correction est celle-là — reporter — pas celle de complexifier le code pour rejoindre un mot mal choisi.

### D5 — gitleaks : des regex de contenu, pas un chemin

Remplacement de `'''_test\.go$'''` par trois entrées de `regexes` couvrant les valeurs factices réellement présentes : `^test-secret-key(-[0-9]+)?$`, `^(secret|test-admin)-token$`, `^0123456789abcdef$` (ce dernier couvre le faux positif préexistant de `internal/config/turnstile_test.go`). Chaque entrée porte un commentaire nommant le fichier qui l'utilise.

Rationale : l'allowlist gitleaks apparie la *valeur* détectée, pas le fichier ; c'est ce que font déjà les entrées ARN/`REDACTED` du même fichier. Un vrai secret collé dans un test redevient détectable. Coût : ajouter un nouveau littéral factice demande une entrée — c'est le bon coût, il force à regarder.

Vérification : `gitleaks detect --config .gitleaks.toml --no-git` doit rester à zéro finding ; un test négatif (ajouter temporairement un faux `AKIA…` dans un `_test.go`, vérifier que gitleaks le voit, retirer) prouve que la couverture est revenue.

### D6 — Un seul middleware de rate-limit paramétré

`rateLimitMiddleware(rl *middleware.RateLimiter, auditAction, message string) func(http.Handler) http.Handler` dans `internal/identity/routes.go` ; les trois fonctions existantes deviennent des appels. Les messages et actions d'audit sont conservés à l'identique — ce sont des chaînes journalisées, un changement serait visible dans l'observabilité.

### D7 — Un hook de confirmation de mot de passe

`site/src/hooks/usePasswordConfirmation({ password, confirm, minLength })` retourne `{ tooShort, mismatch, hint }`. `ResetPassword.jsx` et `ChangePassword.jsx` l'utilisent ; `MIN_PASSWORD_LENGTH` vit dans le hook. Le JSX de l'indicateur de robustesse reste dans chaque page (il diffère légèrement en libellé).

### D8 — Le manifest dit ce que les tests font, et les tests s'appellent comme le manifest

Les projets Playwright de `site/playwright.config.js` sont renommés `support-desktop`, `support-iphone`, `support-ipad`. Le schéma du manifest impose la forme `<cible>-<appareil>` (motif `^x-y$`, et le gate vérifie que chaque `device` est couvert par un suffixe de projet) ; `required_projects` du manifest 040 était donc conforme au schéma, et c'est la configuration Playwright qui ne suivait pas la convention. Les captures d'écran suivent automatiquement (`change-password-${testInfo.project.name}.png`) et les gardes « desktop seulement » du fichier de test passent de `project.name === 'desktop'` à `project.name.endsWith('-desktop')`. Chaque entrée de `coverage_must_test` devient le titre exact d'un `test(...)` Playwright, pour que l'appariement du gate cesse de produire des avertissements. Le test manquant (« accès direct à une autre page ramène à /change-password ») est écrit : indicateur posé, `page.goto('/admin')`, assertion sur l'URL finale **sans qu'aucune requête `/api/` n'ait été émise** (interception qui échoue le test si elle est atteinte).

### D9 — Ce qui était « hors périmètre » est entériné, pas retiré

La case « Afficher les mots de passe » reste : elle existe déjà sur `ResetPassword.jsx`, l'homogénéité vaut mieux que la lettre du spec. Le rate-limit du changement reste keyé par IP, comme `resetLimiter` : un attaquant qui tourne les IP ne peut de toute façon réussir qu'en connaissant le mot de passe temporaire. Les deux sont ajoutés comme scénarios, pour que le prochain relecteur ne les signale pas à nouveau.

## Risks / Trade-offs

- **L'indicateur persisté peut rester posé à tort** si le changement réussit côté serveur mais que le client ne l'efface pas (fermeture d'onglet pendant la réponse). Symptôme : redirection vers `/change-password` bien que le serveur accepte le compte. Atténuation : `ChangePassword.jsx`, à son montage, si l'indicateur est posé, tente `GET /api/profile` ; un `200` prouve que le serveur ne verrouille plus et efface l'indicateur. Coût : un appel au montage de cette seule page.
- **Deux mécanismes de verrou** au lieu d'un. Assumé et documenté (D2) : ils couvrent deux moments différents.
- **Une enveloppe oubliée sur une future route protégée** laisse cette route sans garde structurel — mais toujours avec le garde réactif. La régression serait partielle, pas totale.

## Migration Plan

Aucune migration. Déploiement frontend seul (`support_site_version` sur un nouveau tag), déploiement backend pour la factorisation du rate-limit (comportement identique). Ordre indifférent. Retour arrière : redéployer le tag précédent ; l'indicateur `adminPasswordChangeRequired` éventuellement présent dans un storage est ignoré par l'ancien code.

## Open Questions

Aucune.
