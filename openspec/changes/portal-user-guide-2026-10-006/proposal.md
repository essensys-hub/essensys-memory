> Ticket : [essensys-hub/essensys-feature-lifecycle#26](https://github.com/essensys-hub/essensys-feature-lifecycle/issues/26) — Feature ID `portal-user-guide-2026-10-006`

## Why

Les utilisateurs du portail mon.essensys.fr n'ont aucun guide. Ils découvrent les écrans seuls (éclairage, volets, chauffage, scénarios…) et ne savent pas ce que fait chaque bouton ni quoi faire quand un message d'erreur s'affiche. Il faut un guide en français, une page par écran avec une capture annotée, publié sur www.essensys.fr pour les utilisateurs connectés. Il doit aussi se mettre à jour facilement quand l'interface change.

## What Changes

- **Rédaction** : un guide en Markdown dans `essensys-user-portal-frontend/docs/user-guide/`. Une page par écran, une page « Premiers pas » et un index qui fixe l'ordre et les titres.
- **Écrans couverts (12)** :
  - Connexion et mots de passe, Tableau de bord, Éclairage, Volets et stores ;
  - Chauffage, Chauffe-eau, Arrosage, Scénarios ;
  - Sécurité, Notifications, Réglages, Profil et signalements.
- **Captures automatiques** : une commande `npm run docs:screenshots` lance le portail en **mode démo** (`VITE_DEMO_MODE`, API simulée, aucune armoire pilotée) et photographie chaque écran avec Playwright, sur desktop et sur mobile. Les écrans du site (connexion, profil, signalement) sont capturés de la même façon, avec l'API simulée.
- **Publication sur www.essensys.fr** :
  - une page **`/guide`** (sommaire) et une page **`/guide/<écran>`** par écran ;
  - **réservées aux comptes connectés** : un visiteur voit « Connectez-vous pour accéder au guide » et revient sur la page demandée après connexion ;
  - liens depuis le menu, la page Support et le profil.
- **Une seule source** : au déploiement, le rôle Ansible `frontend` récupère `docs/user-guide/` du portail et le prépare pour le site, sur le modèle du blog alimenté par essensys-memory.

## Capabilities

### New Capabilities
- `portal-user-guide` : contenu, captures reproductibles et publication réservée aux connectés du guide utilisateur du portail.

### Modified Capabilities
<!-- Aucune. -->

## Impact

- **essensys-user-portal-frontend** :
  - `docs/user-guide/` (Markdown et images) ;
  - Playwright en dépendance de développement, script `docs:screenshots` ;
  - ajustements éventuels du mode démo pour avoir des données représentatives sur chaque écran.
- **essensys-support-site** : pages `/guide` et `/guide/:slug` (rendu Markdown, réservé aux connectés), liens dans le menu, la page Support et le profil, tests Playwright.
- **essensys-ansible** : rôle `frontend` (récupération et préparation du guide au build du site).
- **Legacy IoT** : aucun impact. Aucune armoire n'est pilotée, ni pour les captures ni pour les tests.
- Wiki : [[Essensys Support Site]], [[Essensys Ansible]].
