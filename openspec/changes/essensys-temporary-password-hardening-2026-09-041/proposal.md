## Why

La change `essensys-temporary-password-2026-09-040` a été livrée, mergée et déployée. La revue à deux axes (Standards + Spec) menée le 25/09 sur les deux PR (`essensys-user-portal-backend#20`, `essensys-support-site#2`) a relevé des écarts réels entre ce que la spec demandait et ce qui a été livré, ainsi que deux affaiblissements de posture introduits en passant. Aucun n'est un bug de sécurité exploitable ; plusieurs sont des promesses non tenues par le code ou par le manifest — ce qui, dans un lifecycle où `features/<id>.json` est « la source de vérité », est précisément ce que le processus est censé empêcher.

Les écarts, par gravité :

1. **Le verrou anti-navigation est réactif, pas structurel.** La tâche 7.5 de 040 demandait de « rediriger toute route protégée si le contexte utilisateur porte l'indicateur ». Ce qui a été livré dépend de ce qu'une page protégée fasse un `fetch` authentifié à son montage, qui remonte alors en `409` intercepté par `lib/passwordChangeGuard.js`. Une page qui ne fait aucun appel immédiat reste accessible. La tâche a été cochée sans que l'écart soit signalé.
2. **Le manifest frontend affirme des choses fausses.** `tests.ux_matrix.required_projects` nomme des projets Playwright (`support-desktop`…) qui n'existent pas dans `playwright.config.js` (`desktop`/`iphone`/`ipad`) — le schéma du manifest impose la forme `<cible>-<appareil>`, c'est donc la configuration Playwright qui ne suit pas la convention, mais le résultat est le même : un gate qui valide des noms qui ne correspondent à rien ; `tests.coverage_must_test` liste « accès direct à une autre page ramène à /change-password », scénario pour lequel aucun test n'existe. Le feature-gate a passé — il ne vérifie pas ces champs contre la réalité.
3. **`.gitleaks.toml` a été élargi au-delà du besoin.** L'entrée `_test\.go$` aveugle gitleaks sur tous les fichiers de test Go, présents et futurs, pour couvrir quatre littéraux factices identifiables par une regex de contenu. Signalé indépendamment par les deux axes de revue.
4. **`?return=` est perdu sur le chemin 409.** Un verrouillage en cours de session ramène vers `/admin` par défaut au lieu de la page d'origine ; seul le chemin login → changement préserve la destination.
5. **`design.md` (D6) dit « dans la transaction d'émission »** ; le code fait deux `UPDATE` séquentiels sans transaction. Le choix d'implémentation est défendable (le pire cas est un ancien lien de réinitialisation encore valide, pas une brèche) — le document ne le dit pas.
6. **Duplication introduite** : troisième clone du middleware de rate-limit dans `internal/identity/routes.go` ; validation de mot de passe recopiée de `ResetPassword.jsx` dans `ChangePassword.jsx`.

Cette change corrige les six points. Elle ne rouvre pas la conception de 040 : aucun endpoint, aucune colonne, aucun comportement serveur ne change.

## What Changes

- **Frontend `essensys-support-site`** : indicateur `adminPasswordChangeRequired` persisté (posé au login et par le garde 409, effacé au changement réussi et à la déconnexion) ; composant `RequirePasswordChange` enveloppant les routes `/admin` et `/profile` dans `App.jsx`, qui redirige **avant tout rendu** ; `passwordChangeGuard.js` construit `/change-password?return=<page courante>` au lieu de suivre `data.redirect` nu ; hook `usePasswordConfirmation` partagé par `ResetPassword.jsx` et `ChangePassword.jsx` ; test Playwright de navigation directe ; manifest corrigé et titres de tests alignés sur `coverage_must_test`.
- **Backend `essensys-user-portal-backend`** : `.gitleaks.toml` — remplacement de la règle de chemin `_test\.go$` par des regex de contenu ciblant les littéraux factices réels ; factorisation `rateLimitMiddleware(rl, auditAction, message)` remplaçant les trois clones de `internal/identity/routes.go`.
- **Spécification 040** : `design.md` D6 amendé pour décrire les deux écritures séquentielles et la raison pour laquelle c'est acceptable ; la case « Afficher les mots de passe » et le rate-limit par IP, signalés comme non demandés, sont entérinés par des scénarios ajoutés plutôt que retirés.

Aucun impact sur le protocole legacy IoT, la base de données, ni les endpoints.

## Capabilities

### New Capabilities
- `feature-manifest-truthfulness`: chaque affirmation d'un `features/<id>.json` (projets requis, couverture de test) doit correspondre à un artefact vérifiable — et le gate doit le vérifier

### Modified Capabilities
- `forced-password-change-ui`: le verrou devient structurel (garde de route sur indicateur persisté) en plus du garde réactif ; la destination d'origine est préservée sur le chemin 409 ; la bascule d'affichage des mots de passe est spécifiée
- `admin-temporary-password-issue`: le rate-limit du changement de mot de passe, keyé par IP, est spécifié comme tel (aligné sur `resetLimiter`) au lieu d'être laissé à l'interprétation

## Impact

- **Repos** : `essensys-support-site` (UI, e2e, manifest), `essensys-user-portal-backend` (`.gitleaks.toml`, `internal/identity/routes.go`), `essensys-memory` (amendement D6 de 040).
- **Fichiers frontend** : `site/src/App.jsx`, `site/src/components/RequirePasswordChange.jsx` (nouveau), `site/src/lib/passwordChangeGuard.js`, `site/src/lib/authState.js` (nouveau — lecture/écriture de l'indicateur), `site/src/hooks/usePasswordConfirmation.js` (nouveau), `site/src/pages/Login.jsx`, `site/src/pages/ChangePassword.jsx`, `site/src/pages/ResetPassword.jsx`, `site/src/pages/Admin.jsx` (déconnexion efface l'indicateur), `site/e2e/temporary-password.spec.js`, `features/essensys-temporary-password-2026-09-040.json`.
- **Fichiers backend** : `.gitleaks.toml`, `internal/identity/routes.go`.
- **Entités wiki liées** : [[Portal Authentication]], [[Essensys Support Site]], [[Essensys User Portal Backend]].
- **Non impacté** : migrations, `internal/admin`, `internal/middleware`, `internal/domain`, firmware, table d'échange.
