## Purpose

Donner aux utilisateurs connectés d'Essensys un guide du portail mon.essensys.fr : une page par écran avec une capture annotée et des explications, toujours à jour, publiée sur www.essensys.fr.

## ADDED Requirements

### Requirement: Une page par écran
Le guide SHALL contenir une page « Premiers pas » et une page pour chacun des écrans suivants : Connexion et mots de passe, Tableau de bord, Éclairage, Volets et stores, Chauffage, Chauffe-eau, Arrosage, Scénarios, Sécurité, Notifications, Réglages, Profil et signalements. Chaque page MUST indiquer : à quoi sert l'écran, comment y accéder, le rôle de chaque bouton ou zone (numérotés en correspondance avec la capture), les messages d'erreur courants avec la conduite à tenir, et un lien vers « Signaler un problème ».

#### Scenario: Page complète
- **WHEN** on ouvre la page « Éclairage » du guide
- **THEN** elle affiche une capture de l'écran Éclairage, la liste numérotée des zones (pièces, éclairage principal, indirect, tout allumer, tout éteindre), les messages d'erreur courants et un lien vers le formulaire de signalement

#### Scenario: Aucun écran oublié
- **WHEN** on compare le sommaire du guide à la liste des écrans utilisateur du portail
- **THEN** chaque écran utilisateur a sa page, et l'écran d'administration `/admin/regression` n'en a pas

### Requirement: Captures reproductibles sans armoire
Les captures du guide SHALL être produites par une commande unique, qui exécute le portail et le site avec une API simulée. Cette commande MUST NOT envoyer de commande à une armoire ni contacter un backend réel. Les captures MUST NOT contenir de donnée personnelle réelle (nom, email, adresse, identifiant d'armoire ou de passerelle réels). Chaque écran SHALL être capturé au moins en desktop et en mobile.

#### Scenario: Régénération
- **WHEN** un mainteneur lance `npm run docs:screenshots` dans le dépôt du portail
- **THEN** toutes les captures du guide sont recréées, en desktop et en mobile, sans requête réseau vers mon.essensys.fr ni vers une passerelle

#### Scenario: Aucune donnée réelle
- **WHEN** on inspecte une capture du guide
- **THEN** les comptes, pièces et équipements affichés sont fictifs

### Requirement: Guide réservé aux comptes connectés
Les pages `/guide` et `/guide/<écran>` de www.essensys.fr SHALL afficher le guide seulement à un utilisateur connecté. Un visiteur MUST voir une invitation à se connecter, sans le contenu du guide, et revenir sur la page demandée après connexion.

#### Scenario: Visiteur
- **WHEN** un visiteur non connecté ouvre www.essensys.fr/guide/eclairage
- **THEN** il voit « Connectez-vous pour accéder au guide », un bouton de connexion, et aucune capture ni explication

#### Scenario: Retour après connexion
- **WHEN** ce visiteur se connecte depuis cette invitation
- **THEN** il arrive sur www.essensys.fr/guide/eclairage

#### Scenario: Utilisateur connecté
- **WHEN** un utilisateur connecté ouvre www.essensys.fr/guide
- **THEN** il voit le sommaire du guide et peut ouvrir chaque page

#### Scenario: Adresse inconnue
- **WHEN** un utilisateur connecté ouvre www.essensys.fr/guide/inexistant
- **THEN** il voit un message « Page du guide introuvable » et un lien vers le sommaire

### Requirement: Accès au guide
Pour un utilisateur connecté, le site SHALL proposer un lien vers le guide dans le menu, sur la page Support et sur la page Profil.

#### Scenario: Depuis le profil
- **WHEN** un utilisateur connecté ouvre son profil
- **THEN** un lien « Guide du portail » mène à www.essensys.fr/guide

### Requirement: Affichage lisible sur tous les appareils
Le guide SHALL être lisible sur ordinateur, iPhone et iPad, sans défilement horizontal. Les captures MUST s'adapter à la largeur de l'écran.

#### Scenario: Mobile
- **WHEN** un utilisateur connecté ouvre une page du guide sur un écran de 375 px de large
- **THEN** le texte et la capture tiennent dans la largeur, sans défilement horizontal

### Requirement: Source unique
Le contenu publié sur www.essensys.fr SHALL provenir de `docs/user-guide/` du dépôt du portail, à la version déployée. Aucune copie du texte du guide MUST être maintenue à la main dans le dépôt du site.

#### Scenario: Mise à jour
- **WHEN** une page du guide est modifiée dans le dépôt du portail, puis le site redéployé
- **THEN** la nouvelle version s'affiche sur www.essensys.fr sans modification du dépôt du site
