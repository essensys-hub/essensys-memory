> Ticket : [essensys-hub/essensys-feature-lifecycle#15](https://github.com/essensys-hub/essensys-feature-lifecycle/issues/15) — Feature ID `support-reports-2026-10-004`

## Why

Depuis essensys-hub/essensys-support-site#6, seuls les utilisateurs connectés voient les cartes « Bug logiciel » et « Incident production » sur www.essensys.fr. Mais ces cartes ouvrent les formulaires d'issue GitHub, qui exigent un compte GitHub : la plupart des utilisateurs Essensys n'en ont pas et ne peuvent donc rien signaler. Il faut un formulaire natif, sans compte GitHub, qui protège leurs données personnelles alors que les dépôts sont publics.

## What Changes

- Nouveau **formulaire de signalement** sur www.essensys.fr, réservé aux comptes connectés : type (Bug logiciel ou Incident sur mon installation), application concernée, version, mode de connexion (cloud ou réseau local), description, comportement attendu, étapes pour reproduire.
- **Avertissement** visible au-dessus des champs libres : ne jamais saisir d'adresse postale, de mot de passe ni de code d'accès.
- **Contrôle côté serveur** des contenus sensibles : un texte qui ressemble à un mot de passe, à un jeton ou à une adresse postale est refusé avec un message qui explique pourquoi.
- Nouveau **point d'entrée** `POST /api/support/reports` dans `essensys-user-portal-backend` : session obligatoire, limite par compte, création de l'issue GitHub au nom d'une **GitHub App Essensys**, ajout au Project #6.
- **Bugs** créés dans le dépôt public `essensys-support-site`, anonymisés : référence `U-xxxx` uniquement, ni nom, ni email, ni identifiant d'armoire.
- **Incidents** créés dans un dépôt **privé** `essensys-support`, visible des mainteneurs seulement.
- Nouvelle page **« Mes signalements »** dans Mon profil : liste, état, lien vers l'issue publique.
- Les cartes de la section « Signaler » de l'accueil ouvrent le formulaire au lieu des modèles GitHub. Les modèles d'issue GitHub restent disponibles pour les contributeurs.

## Capabilities

### New Capabilities
- `support-report-submission` : dépôt d'un signalement Bug/Incident par un utilisateur connecté, validation, avertissement et filtrage des données sensibles, limite par compte, routage public/privé et anonymisation.
- `support-report-tracking` : consultation par l'utilisateur de ses propres signalements et de leur état.

### Modified Capabilities
<!-- Aucune spec existante dans ce dépôt. -->

## Impact

- **essensys-user-portal-backend** : nouvelle table `support_reports`, nouveau module HTTP (création et liste), client GitHub App (JWT RS256, jeton d'installation), configuration et secrets nouveaux.
- **essensys-support-site** (`site/`) : pages formulaire et « Mes signalements », cartes de l'accueil, tests Playwright.
- **essensys-ansible** : variables d'environnement du backend et secrets SOPS de la GitHub App (`roles/cloud_backend`, `roles/sops_load`).
- **GitHub (action humaine, admin de l'org)** : création de la GitHub App (droits Issues lecture/écriture sur les deux dépôts, Projects lecture/écriture sur l'org) et du dépôt privé `essensys-support`.
- **Legacy IoT** : aucun impact. Ni le firmware SC944D, ni la table d'échange, ni les routes gateway ne changent.
- Wiki : [[Essensys User Portal Backend]], [[Essensys Support Site]], [[Essensys Ansible]].
