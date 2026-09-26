## Purpose

Garantit qu'un déploiement du backend cloud ne peut pas rendre une configuration que le binaire refusera au démarrage, et que les secrets n'ont qu'une source.

## ADDED Requirements

### Requirement: Source unique des secrets

Le système de déploiement SHALL lire tout secret de production depuis le coffre SOPS et depuis lui seul.

#### Scenario: Aucune copie en clair

- **WHEN** le dépôt `essensys-ansible` et le poste opérateur sont inspectés
- **THEN** aucun fichier en clair ne porte une clé également présente dans le coffre SOPS

#### Scenario: Playbook rendant une configuration

- **WHEN** un playbook ciblant l'hôte de production rend un fichier de configuration
- **THEN** le rôle `sops_load` est le premier rôle de ce playbook

### Requirement: Parité avec la validation du binaire

Le système de déploiement SHALL exiger, avant tout contact avec l'hôte, chaque variable que le binaire exige au démarrage en production.

#### Scenario: Clé manquante dans le coffre

- **WHEN** une clé requise est absente ou vide dans le coffre
- **THEN** le play échoue avant la première tâche sur l'hôte, en nommant la clé

#### Scenario: Clé présente mais absente du fichier rendu

- **WHEN** le coffre porte la clé mais le template ne la reporte pas (erreur de nom, `default('')`)
- **THEN** le play échoue avant d'écrire le fichier sur l'hôte, en nommant la variable du fichier

#### Scenario: Seuil de longueur

- **WHEN** une variable requise est présente avec moins de 16 caractères
- **THEN** le play échoue, avec le même seuil que `config.Validate()`

#### Scenario: Nouvelle exigence côté binaire

- **WHEN** `config.Validate()` gagne une nouvelle variable obligatoire
- **THEN** la liste des clés requises côté Ansible doit être mise à jour, et un commentaire y renvoie explicitement

### Requirement: Aucun playbook nuisible

Le dépôt SHALL ne contenir aucun playbook qui déploie un rôle invalide dans la topologie courante.

#### Scenario: Rôle legacy

- **WHEN** le mode consolidé est actif
- **THEN** aucun playbook ne déploie le rôle `backend` legacy sur l'hôte de production
