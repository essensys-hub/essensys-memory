## Purpose

Garantir que les noms personnalisés restent corrects, identiques sur tous les clients, synchronisés de bout en bout, et sans effet sur l'armoire.

## ADDED Requirements

### Requirement: Tests sans armoire
Tous les tests des noms SHALL s'exécuter sans armoire réelle, avec des serveurs simulés. Aucun test ne MUST envoyer de commande à une armoire.

#### Scenario: Suite des tests
- **WHEN** les tests des noms s'exécutent avec `NO_ARMOIRE=1`
- **THEN** aucune commande n'atteint une armoire réelle et tous les tests passent

### Requirement: Parité du catalogue
Les catalogues du cloud, de la gateway, des portails et des apps SHALL être identiques : mêmes types, clés, pièces, patrons et noms d'origine. Un test de non-régression MUST échouer dès qu'un catalogue diverge des autres.

#### Scenario: Divergence
- **WHEN** une clé du catalogue est modifiée dans un seul dépôt
- **THEN** le test de parité échoue

### Requirement: Non-régression
Des tests `NR-*` SHALL vérifier qu'un utilisateur sans droit d'administrateur ne peut jamais écrire un nom, côté cloud et côté gateway ; que les noms d'origine s'affichent quand l'API des noms est absente ; qu'un nom saisi ne peut jamais modifier un indice ni une commande ; que deux modifications simultanées convergent vers la même valeur ; et que les tests existants des tables d'indices restent verts.

#### Scenario: Écriture interdite
- **WHEN** un test écrit un nom avec un compte ordinaire sur le cloud puis sur la gateway
- **THEN** les deux écritures sont refusées

#### Scenario: Indices intacts
- **WHEN** un test renomme chaque objet du catalogue
- **THEN** les indices et masques de la table d'échange sont identiques à ceux d'avant

### Requirement: Synchronisation de bout en bout
Un test de bout en bout SHALL, avec un cloud simulé, une gateway simulée et des clients simulés, vérifier qu'un nom saisi sur chaque environnement apparaît sur les autres, y compris après une coupure et un redémarrage de la gateway.

#### Scenario: Aller-retour
- **WHEN** un nom est saisi sur le portail cloud, puis un autre sur la gateway, puis la gateway redémarre
- **THEN** les deux noms sont présents sur le cloud, la gateway et les clients

### Requirement: Tests d'application
Les portails SHALL passer leurs scénarios de noms avec Playwright sur desktop, iPhone et iPad. Les apps SHALL les passer sur émulateur Android et simulateur iOS.

#### Scenario: Matrice d'appareils
- **WHEN** la suite Playwright s'exécute
- **THEN** les scénarios de noms passent sur desktop, iPhone et iPad

### Requirement: Déploiement ordonné
Le déploiement SHALL suivre l'ordre cloud, gateway (CM5 puis Raspberry Pi 4), portails, apps. Les serveurs MUST rester utilisables par les clients qui ne connaissent pas les noms.

#### Scenario: Cloud seul déployé
- **WHEN** le cloud est déployé et pas encore les portails ni les apps
- **THEN** les clients actuels fonctionnent sans changement
