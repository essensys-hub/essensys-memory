## 1. Catalogue, vecteurs de test et parité (essensys-user-portal-backend) (#51)

- [ ] 1.1 Extraire des tables d'indices actuelles le `catalog.json` canonique (types, clés, pièces, patrons, noms d'origine) dans `internal/names/` ; vérifier par un test qui reconstruit chacun des libellés actuels à l'identique
- [ ] 1.2 Écrire les vecteurs de test communs `names_vectors.json` (résolution : nom forcé, hérité, d'origine ; validation : longueur en points de code, espaces, NFC, caractères interdits, balises) ; vérifier qu'ils passent en Go
- [ ] 1.3 Ajouter à `essensys-feature-lifecycle` le script de parité qui compare le catalogue et les vecteurs de tous les dépôts ; vérifier en modifiant une clé dans une seule copie (le script échoue) puis en la rétablissant (il passe)

## 2. Cloud : stockage, API, droits, audit et synchronisation (essensys-user-portal-backend) (#52)

- [ ] 2.1 Ajouter la migration idempotente `018` (`custom_names`, compteur de révision par installation) et le stockage (lire depuis une révision, écrire avec nouvelle révision, rétablir par pierre tombale) ; vérifier par des tests de stockage (révision croissante, rétablissement visible dans les changements, migration rejouée deux fois)
- [ ] 2.2 Implémenter la règle de nom affiché et la validation sur les vecteurs communs ; vérifier par le passage de tous les vecteurs
- [ ] 2.3 Ajouter `GET`, `PUT` et `DELETE` `/api/names` avec `ETag`, 304, `since` et `can_rename` ; vérifier par des tests de routes (première lecture, 304, changements depuis une révision, nom invalide, clé inconnue)
- [ ] 2.4 Réserver l'écriture aux rôles `admin_local` et `admin_global` liés à la machine, isoler chaque installation et limiter le débit ; vérifier par des tests (utilisateur ordinaire refusé, autre installation refusée, 429 en rafale)
- [ ] 2.5 Ajouter `GET /api/gateway/names` et `POST /api/gateway/names/sync` pour la gateway authentifiée ; vérifier par des tests (gateway en retard, changement venu de la gateway, deux modifications simultanées qui convergent, gateway d'une autre installation refusée)
- [ ] 2.6 Journaliser chaque changement dans l'audit (auteur, objet, ancien et nouveau nom, origine) et purger les noms à la suppression de l'installation ; vérifier par des tests, et par l'absence de nom dans les journaux techniques

## 3. Gateway : stockage, API réseau local et synchronisation (essensys-server-backend) (#16)

- [ ] 3.1 Ajouter le stockage par fichier `names.json` (écriture atomique, `local_rev`, `cloud_rev`, `pending`) ; vérifier par des tests (redémarrage, coupure simulée pendant l'écriture, fichier absent au premier démarrage)
- [ ] 3.2 Ajouter l'API réseau local `/api/names` (lecture, écriture, rétablissement, `ETag`, `can_rename`) avec la même validation ; vérifier par des tests (administrateur autorisé, utilisateur ordinaire refusé, nom invalide, clé inconnue)
- [ ] 3.3 Étendre `cloudsync` : envoi des changements en attente, reprise de l'état fusionné, reprise après coupure et redémarrage ; vérifier par des tests avec un cloud simulé (du cloud vers la gateway, de la gateway vers le cloud, trois modifications faites hors ligne puis envoyées, conflit)
- [ ] 3.4 Prouver qu'aucun indice ni commande n'est écrit ; vérifier par un test qui renomme chaque objet du catalogue et compare la table d'échange avant et après

## 4. Installation CM5 (essensys-ansible) (#13)

- [ ] 4.1 Faire créer `names.json` avec le propriétaire du service et le mode `0640` par le rôle `raspberry_backend`, garantir qu'une mise à jour le conserve et l'inclure dans les sauvegardes de configuration ; vérifier par un dry-run `--check --diff`, puis par un déploiement de test qui garde un nom déjà saisi

## 5. Installation Raspberry Pi 4 (essensys-raspberry-install) (#19)

- [ ] 5.1 Faire créer le stockage des noms par `install.sh` et conserver le fichier lors d'une mise à jour ; vérifier par une installation puis une mise à jour sur une machine de test, avec un nom conservé

## 6. Portail cloud (essensys-user-portal-frontend) (#38)

- [ ] 6.1 Migrer les manifests du dépôt vers le bloc `github` et mettre son schéma à jour (les blocs `jira` et `confluence` sont refusés à partir du 2026-11-09) ; vérifier par `validate_feature_manifests.py` sans avertissement
- [ ] 6.2 Ajouter au portail cloud, qui n'en a pas, l'infrastructure Playwright (configuration, projets `remote-desktop`, `remote-iphone` et `remote-ipad`, mode `no-armoire`, serveur de test) et rapatrier le spec de noms du jumeau ; vérifier par un test de fumée sur les trois projets et par `check_feature_gate.py --strict` dans la CI du dépôt
- [ ] 6.3 Ajouter le hook `useNames` (référentiel, cache, rafraîchissement toutes les 30 s avec `ETag`) et `displayName` sur les vecteurs communs ; vérifier par des tests unitaires (résolution, validation, 304, serveur sans les noms)
- [ ] 6.4 Ajouter l'écran « Noms » dans les Réglages (catégories, origine, feuille de modification, compteur, rétablissement, aperçu d'une pièce, masqué pour un utilisateur ordinaire) ; vérifier par des tests Playwright
- [ ] 6.5 Remplacer les libellés codés en dur par `displayName` dans les pages éclairage, volets, chauffage, prises de sécurité, chauffe-eau, arrosage, scénarios et éditeur de scénarios, et dans les confirmations ; vérifier par des tests Playwright qui renomment une pièce et contrôlent chaque page
- [ ] 6.6 Faire passer les scénarios de noms sur desktop, iPhone et iPad ; vérifier par la matrice Playwright en mode `no-armoire`

## 7. Portail local (essensys-server-frontend) (#9)

- [ ] 7.1 Migrer les manifests du dépôt vers le bloc `github` et mettre son schéma à jour (échéance du 2026-11-09) ; vérifier par `validate_feature_manifests.py` sans avertissement
- [ ] 7.2 Reporter à l'identique les tâches 6.3 à 6.6 sur le portail local, jumeau du portail cloud, contre l'API du réseau local ; vérifier par les mêmes scénarios Playwright, et par la parité des textes avec le portail cloud

## 8. Qualité et déploiement (essensys-feature-lifecycle) (#42)

- [ ] 8.1 Écrire le test de bout en bout de synchronisation (cloud, gateway et clients simulés : nom saisi sur chaque environnement, coupure et redémarrage de la gateway) et les tests `NR-*` listés par la spec de qualité ; vérifier par leur passage sans armoire réelle (`NO_ARMOIRE=1`)
- [ ] 8.2 Déployer dans l'ordre cloud, gateway CM5 puis Raspberry Pi 4, portails, apps, avec un `/checkup` vert avant chaque PR ; vérifier par un renommage réel d'une pièce depuis un compte administrateur de test, vu sur les quatre clients en moins d'une minute
- [ ] 8.3 Mettre à jour le guide utilisateur et les README des portails et des apps avec la fonction « Noms » et ses droits ; vérifier par la présence de la section et de captures sur #41
