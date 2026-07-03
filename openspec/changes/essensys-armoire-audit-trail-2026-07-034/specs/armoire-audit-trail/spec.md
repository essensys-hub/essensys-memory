# armoire-audit-trail

Journal d'audit append-only par armoire (`machine_id`) : actions domotiques, modifications de configuration et changements d'état. Lecture read-only pour utilisateurs autorisés ; écriture réservée aux composants backend. Aligné sur les trois périmètres [[Deployment Perimeters]].

## ADDED Requirements

### Requirement: Persistance canonique par armoire

Le système MUST persister les événements d'audit domotique dans **immudb** (source de vérité immuable) et MUST projeter une copie queryable dans la table PostgreSQL OVH `armoire_audit_events`, indexée par `machine_id`, distincte de `audit_logs` et `portal_audit_log`.

#### Scenario: Append immudb avant projection PG

- **WHEN** un writer service enregistre un événement valide via `essensys-audit-collector`
- **THEN** `essensys-audit-service` append l'événement dans immudb sous la clé `armoire/{machine_id}/event/{event_id}`
- **AND** une projection est insérée dans `armoire_audit_events` avec les mêmes champs métier
- **AND** la ligne PG MUST NOT être modifiable via API utilisateur

#### Scenario: Insertion événement avec machine_id

- **WHEN** la projection PostgreSQL est appliquée
- **THEN** une ligne existe dans `armoire_audit_events` avec `machine_id`, `event_id` UUID unique, `occurred_at`, `event_type`, `subject_type`, `subject_key`

#### Scenario: Idempotence event_id

- **WHEN** un ingest gateway envoie un `event_id` déjà présent
- **THEN** la réponse est `409 Conflict` ou ignore silencieux (`ON CONFLICT DO NOTHING`)
- **AND** aucun doublon n'existe en base

### Requirement: Service audit dédié (`essensys-audit-service`)

Le système MUST déployer `essensys-audit-service` sur la gateway LAN et sur OVH comme **seul** composant autorisé à écrire dans immudb.

#### Scenario: Append via audit-service LAN

- **WHEN** `essensys-server-backend` émet un événement via `audit-collector`
- **THEN** le collector envoie `POST /v1/audit/append` à l'instance locale `essensys-audit-service`
- **AND** l'événement est persisté dans immudb gateway avant toute projection PostgreSQL locale

#### Scenario: Append via audit-service OVH

- **WHEN** `essensys-user-portal-backend` ou un ingest gateway relay émet un événement
- **THEN** `essensys-audit-service` OVH append dans immudb cloud
- **AND** projette vers `armoire_audit_events` PostgreSQL OVH

#### Scenario: Accès immudb direct interdit

- **WHEN** un backend tente une connexion immudb sans passer par `essensys-audit-service`
- **THEN** l'authentification immudb MUST échouer (credentials réservés audit-service)

### Requirement: Collecteur inter-services (`essensys-audit-collector`)

Le système MUST fournir un collecteur unique que tous les services producteurs utilisent pour émettre des événements d'audit normalisés.

#### Scenario: Collecte inject LAN

- **WHEN** `POST /api/admin/inject` réussit sur `essensys-server-backend`
- **THEN** le backend appelle `collector.Emit` avec `event_type=USER_ACTION`
- **AND** le collector applique dedup et transmet à `essensys-audit-service`

#### Scenario: Collecte legacyiot armoire seule

- **WHEN** un delta `MyStatus` whitelisté est détecté sur OVH
- **THEN** `internal/legacyiot` appelle `collector.Emit` avec `event_type=STATE_CHANGE`
- **AND** l'événement atteint immudb OVH via audit-service cloud

#### Scenario: Buffer si audit-service indisponible

- **WHEN** `essensys-audit-service` est injoignable depuis la gateway
- **THEN** le collector MUST insérer l'événement dans `audit_outbox` PostgreSQL
- **AND** MUST rejouer vers audit-service au retour du service

### Requirement: Reconstruction PostgreSQL depuis immudb

Le système MUST permettre de reconstruire intégralement la projection PostgreSQL à partir d'immudb.

#### Scenario: Rebuild machine complète

- **WHEN** un opérateur exécute `audit-rebuild --source immudb --target postgres --machine-id M`
- **THEN** toutes les clés `armoire/M/event/*` sont lues depuis immudb en ordre transaction
- **AND** `armoire_audit_events` (ou projection locale gateway) est recréée sans perte par rapport à immudb

#### Scenario: Dry-run rebuild

- **WHEN** `audit-rebuild` est lancé avec `--dry-run`
- **THEN** le rapport liste les divergences PG vs immudb sans modifier PostgreSQL

### Requirement: Vérification d'intégrité cryptographique

Le système MUST détecter toute falsification en comparant immudb (preuve Merkle) et la projection PostgreSQL.

#### Scenario: Vérification intégrité OK

- **WHEN** `audit-integrity-check` ou `GET /api/admin/audit/integrity?machine_id=M` s'exécute
- **AND** PG et immudb sont cohérents
- **THEN** la réponse indique `status=ok` avec nombre d'événements vérifiés

#### Scenario: Divergence détectée

- **WHEN** une ligne PG a un `event_hash` différent de la valeur immudb `VerifiedGet`
- **THEN** un `SECURITY_ALERT` est enregistré avec `subject_key=security:audit_integrity_mismatch`
- **AND** la métrique `audit_integrity_mismatch_total` est incrémentée

### Requirement: Console admin audit et immudb

Le système MUST exposer une interface d'administration distincte du journal utilisateur pour superviser `essensys-audit-service`, immudb et la projection PostgreSQL.

#### Scenario: Accès admin cloud

- **WHEN** un `admin_global` ouvre `/admin/audit`
- **THEN** la page affiche l'état des services, l'intégrité PG ↔ immudb et les actions rebuild / export preuve
- **AND** aucun contrôle d'édition d'événements n'est proposé

#### Scenario: Accès admin LAN

- **WHEN** un `lan_admin` ouvre `/settings/audit-admin`
- **THEN** la même console est affichée pour l'instance gateway locale
- **AND** un `lan_user` reçoit `403 Forbidden`

#### Scenario: Rebuild dry-run

- **WHEN** l'admin lance un rebuild dry-run pour `machine_id=M`
- **THEN** le rapport liste les lignes PG qui seraient recréées depuis immudb sans modifier la base

### Requirement: Recherche utilisateur avancée

Le système MUST permettre aux utilisateurs autorisés de filtrer et rechercher le journal d'audit de leur armoire.

#### Scenario: Recherche plein texte

- **WHEN** un `user` lié envoie `GET /api/portal/audit/events?q=chauffage`
- **THEN** seuls les événements dont acteur, sujet ou détail contient « chauffage » sont retournés

#### Scenario: Filtres combinés

- **WHEN** l'utilisateur filtre par `event_type=USER_ACTION` et plage date 7 jours
- **THEN** l'IHM appelle l'API avec les query params correspondants
- **AND** le tableau et le graphique d'activité reflètent le même filtre

#### Scenario: Détail événement avec preuve

- **WHEN** l'utilisateur sélectionne une ligne du tableau
- **THEN** un panneau détail affiche les métadonnées incluant le statut de vérification immudb

### Requirement: Interdiction écriture utilisateur

Le système MUST NOT exposer de route HTTP permettant à un JWT utilisateur ou cookie session LAN de créer, modifier ou supprimer un événement `armoire_audit_events`.

#### Scenario: POST audit avec JWT utilisateur cloud

- **WHEN** un client envoie `POST /api/portal/audit/events` ou `POST /api/gateway/audit/events` avec un JWT utilisateur
- **THEN** la réponse est `403 Forbidden`

#### Scenario: POST audit avec cookie lan_user

- **WHEN** un client LAN envoie `POST /api/audit/events` avec session cookie
- **THEN** la réponse est `403 Forbidden`

#### Scenario: Ingest gateway autorisé

- **WHEN** la gateway envoie `POST /api/gateway/audit/events` avec token gateway valide et headers MAC
- **THEN** la réponse est `201 Created` pour un nouvel `event_id`

### Requirement: RBAC lecture cloud

Le système MUST autoriser la lecture du journal d'une armoire `M` selon le rôle cloud suivant.

#### Scenario: admin_global lit toute armoire

- **WHEN** un `admin_global` authentifié envoie `GET /api/portal/audit/events?machine_id=M`
- **THEN** la réponse est `200 OK` avec les événements de `M`

#### Scenario: user lié lit journal complet de son armoire

- **WHEN** un `user` avec `linked_machine_id = M` envoie `GET /api/portal/audit/events?machine_id=M`
- **THEN** la réponse est `200 OK` avec **tous** les événements de `M` (pas seulement ceux où `actor_id` = user)
- **AND** ce comportement est distinct de `GET /api/admin/audit` (audit plateforme inchangé)

#### Scenario: user tente autre armoire

- **WHEN** un `user` lié à `M1` demande `machine_id=M2`
- **THEN** la réponse est `403 Forbidden`
- **AND** un événement `SECURITY_ALERT` est enregistré

#### Scenario: guest_local refusé

- **WHEN** un `guest_local` tente `GET /api/portal/audit/events`
- **THEN** la réponse est `403 Forbidden`

#### Scenario: Résolution machine_id armoire seule

- **WHEN** un `user` a `linked_armoire_id = M` et pas de gateway éligible
- **THEN** l'authorizer MUST traiter `M` comme armoire liée pour la lecture audit

### Requirement: RBAC lecture LAN

Le système MUST autoriser la lecture audit sur la gateway locale pour `lan_admin` et `lan_user` uniquement.

#### Scenario: lan_user lit journal armoire locale

- **WHEN** un `lan_user` authentifié envoie `GET /api/audit/events`
- **THEN** la réponse est `200 OK` avec les événements de l'armoire locale de la gateway

#### Scenario: lan_guest refusé

- **WHEN** un `lan_guest` envoie `GET /api/audit/events`
- **THEN** la réponse est `403 Forbidden`
- **AND** un `SECURITY_ALERT` est enregistré

### Requirement: Déduplication STATE_CHANGE

Le système MUST NOT insérer un événement `STATE_CHANGE` si `new_value` est identique à la dernière `new_value` stockée pour le même `(machine_id, subject_type, subject_key)` après normalisation.

#### Scenario: Valeur inchangée ignorée

- **WHEN** un writer détecte `exchange:613` passant de `"64"` à `"64"`
- **THEN** aucune nouvelle ligne n'est insérée

#### Scenario: Transition réelle enregistrée

- **WHEN** `exchange:613` passe de `"0"` à `"64"`
- **THEN** un événement `STATE_CHANGE` est inséré avec `old_value=0` et `new_value=64`

#### Scenario: Oscillation A-B-A

- **WHEN** les valeurs successives sont `A`, `B`, `A`
- **THEN** trois événements sont stockés

#### Scenario: USER_ACTION jamais dédupliqué

- **WHEN** deux injects identiques `exchange:590` sont exécutés
- **THEN** deux événements `USER_ACTION` distincts sont stockés (sauf idempotence `action_guid` cloud relay)

### Requirement: Whitelist indices auditables

Le système MUST appliquer la déduplication `STATE_CHANGE` uniquement aux indices table d'échange listés dans la whitelist documentée (`internal/audit/whitelist.go`).

#### Scenario: Indice hors whitelist ignoré pour STATE_CHANGE

- **WHEN** un indice de télémétrie hors whitelist change
- **THEN** aucun événement `STATE_CHANGE` n'est produit

### Requirement: Outbox gateway et sync offline

Le système MUST bufferiser les événements non livrables à OVH dans `audit_outbox` (PostgreSQL gateway) et MUST les synchroniser de façon idempotente au retour du service.

#### Scenario: WAN indisponible

- **WHEN** OVH est injoignable depuis la gateway
- **THEN** l'événement est inséré dans `audit_outbox` avec `sync_status=pending`

#### Scenario: Sync batch réussi

- **WHEN** le job cloudsync envoie `POST /api/gateway/audit/batch` avec des événements pending
- **THEN** les lignes OVH sont créées sans doublon
- **AND** les lignes outbox passent à `sync_status=synced`

#### Scenario: Lecture LAN hors ligne

- **WHEN** un `lan_user` lit l'audit alors que OVH est coupé
- **THEN** `GET /api/audit/events` retourne les événements locaux incluant ceux `pending_sync`
- **AND** les entrées non sync sont marquées `pending_sync: true` dans la réponse JSON

### Requirement: Périmètre armoire seule WAN

Le système MUST enregistrer les événements domotique pour les installations sans gateway locale via les handlers `internal/legacyiot` sur OVH uniquement.

#### Scenario: MyStatus delta armoire seule

- **WHEN** le firmware envoie `POST /api/mystatus` sur OVH pour une armoire liée sans gateway
- **THEN** les `STATE_CHANGE` whitelistés sont évalués et persistés dans `armoire_audit_events`
- **AND** aucune écriture n'est attendue dans `audit_outbox` gateway

### Requirement: Intégrité append-only et hash chain

Le système MUST empêcher UPDATE/DELETE sur `armoire_audit_events` via triggers PostgreSQL, MUST conserver l'historique complet dans immudb (append-only), et MUST calculer `prev_hash` / `event_hash` (SHA-256) par `machine_id` à l'append immudb (recopiés en projection PG).

#### Scenario: immudb append-only

- **WHEN** une tentative de suppression ou modification d'une clé immudb existante est effectuée
- **THEN** l'opération MUST échouer (immudb ne supporte pas UPDATE/DELETE applicatif)

#### Scenario: Tentative UPDATE SQL projection

- **WHEN** un rôle applicatif tente `UPDATE armoire_audit_events`
- **THEN** la base rejette l'opération

#### Scenario: Chaîne cohérente après ingest

- **WHEN** trois événements sont appendés pour la même `machine_id`
- **THEN** chaque `event_hash` dépend du `event_hash` précédent pour cette machine
- **AND** `VerifiedGet` immudb valide chaque entrée

### Requirement: IHM lecture seule jumelle

Les frontends `essensys-server-frontend` et `essensys-user-portal-frontend` MUST exposer une page `/settings/audit` en lecture seule, synchronisée entre jumeaux, intégrée à la **navigation utilisateur**.

#### Scenario: Entrée sidebar utilisateur

- **WHEN** un `lan_user`, `lan_admin` (LAN) ou `user` / `admin_*` lié (cloud) est authentifié
- **THEN** la sidebar affiche l'entrée « Journal d'activité » pointant vers `/settings/audit`
- **AND** l'entrée est absente pour `lan_guest` ou utilisateur non lié

#### Scenario: Carte Paramètres

- **WHEN** l'utilisateur autorisé ouvre `/settings`
- **THEN** une `ControlCard` « Journal d'activité domotique » affiche le statut charte et un lien vers `/settings/audit`

#### Scenario: Pas de contrôle d'édition

- **WHEN** la page audit est rendue pour un rôle lecteur autorisé
- **THEN** aucun bouton créer/modifier/supprimer n'est affiché
- **AND** aucun champ de formulaire éditable n'est présent

#### Scenario: Filtres lecture

- **WHEN** l'utilisateur applique un filtre date ou `event_type`
- **THEN** seul `GET` API est appelé avec les query params correspondants

#### Scenario: Accès dashboard rapide

- **WHEN** l'utilisateur autorisé consulte `/dashboard`
- **THEN** une carte « Journal d'activité » permet d'accéder à `/settings/audit` en un clic

### Requirement: Taxonomie événements minimale

Le système MUST supporter les `event_type` suivants : `USER_ACTION`, `CONFIG_CHANGE`, `STATE_CHANGE`, `AUTH_EVENT`, `SECURITY_ALERT`, `SYSTEM`.

#### Scenario: AUTH_EVENT trusted device

- **WHEN** un appareil est appairé ou révoqué ([[Trusted Devices LAN]])
- **THEN** un `AUTH_EVENT` est enregistré avec `subject_key` approprié

#### Scenario: SECURITY_ALERT accès refusé

- **WHEN** un rôle non autorisé tente de lire l'audit
- **THEN** un `SECURITY_ALERT` avec `subject_key=security:audit_denied` est enregistré

### Requirement: Couverture tests backend

Le package `internal/audit` MUST atteindre au minimum **85 %** de couverture de tests sur les modules dedup, authorizer, hashchain, writer et sync.

#### Scenario: Tests dedup table-driven

- **WHEN** `go test ./internal/audit/... -cover` est exécuté en CI
- **THEN** la couverture globale du package est ≥ 85 %
- **AND** au moins 10 cas dedup sont couverts

#### Scenario: Test POST utilisateur refusé

- **WHEN** les tests API simulent un JWT user sur route ingest
- **THEN** le test exige `403 Forbidden`

### Requirement: Non-régression audit plateforme

Le système MUST NOT modifier le comportement de `GET /api/admin/audit` (table `audit_logs` auth plateforme).

#### Scenario: Admin audit plateforme inchangé

- **WHEN** un `admin_global` appelle `GET /api/admin/audit`
- **THEN** le filtre historique par `user_id` pour rôle `user` reste inchangé
- **AND** la nouvelle route `/api/portal/audit/events` est distincte

### Requirement: Charte RGPD obligatoire avant accès audit

Le système MUST exiger la signature de la charte « collecte et journal d'audit domotique » (version courante) avant tout accès au journal d'audit armoire.

#### Scenario: Premier accès cloud sans charte signée

- **WHEN** un `user` lié envoie `GET /api/portal/audit/events` sans acceptation enregistrée
- **THEN** la réponse est `403 Forbidden` avec code `audit_charter_required`
- **AND** le corps inclut `charter_version` et URL de la charte

#### Scenario: Acceptation charte cloud

- **WHEN** l'utilisateur envoie `POST /api/portal/audit/charter/accept` avec `charter_version` courante
- **THEN** une ligne est insérée dans `user_audit_charter_acceptances` avec `user_id`, `version`, `accepted_at`, `ip_address`
- **AND** les accès ultérieurs `GET /api/portal/audit/events` sont autorisés si RBAC OK

#### Scenario: Premier accès LAN sans charte

- **WHEN** un `lan_user` ouvre `/settings/audit` sans acceptation LAN enregistrée
- **THEN** une modal bloquante affiche la charte et MUST empêcher la lecture tant que non acceptée

#### Scenario: Ré-consentement après bump version

- **WHEN** `audit_charter_version` est incrémentée en configuration
- **AND** l'utilisateur a signé une version antérieure
- **THEN** l'accès audit est à nouveau bloqué jusqu'à nouvelle acceptation

### Requirement: Transparence et information RGPD

Le système MUST publier une charte lisible et MUST mettre à jour la politique de confidentialité pour couvrir l'audit domotique par armoire.

#### Scenario: Charte accessible publiquement

- **WHEN** un visiteur ouvre `https://www.essensys.fr/privacy/audit-charter`
- **THEN** le document liste finalités, données, durée 24 mois, droits et contact `support@essensys.fr`

#### Scenario: Lien depuis politique confidentialité

- **WHEN** un utilisateur consulte `/privacy`
- **THEN** une section « Journal d'audit domotique » renvoie vers la charte dédiée

### Requirement: Droit d'accès et export audit

Le système MUST permettre à un utilisateur autorisé d'exporter les événements d'audit de son armoire liée (droit d'accès RGPD).

#### Scenario: Export JSON cloud

- **WHEN** un `user` avec charte signée appelle `GET /api/portal/audit/export?format=json`
- **THEN** la réponse est `200 OK` avec un fichier JSON des événements de son `machine_id` liée

#### Scenario: Export refusé sans charte

- **WHEN** l'utilisateur tente export sans acceptation charte
- **THEN** la réponse est `403 Forbidden` avec `audit_charter_required`

### Requirement: Rétention et purge automatique

Le système MUST supprimer les événements de la **projection PostgreSQL** `armoire_audit_events` plus anciens que la durée de rétention configurée (défaut **24 mois**). immudb MUST conserver l'historique complet pour audit réglementaire.

#### Scenario: Purge job projection PG

- **WHEN** le job `audit_retention_purge` s'exécute
- **THEN** les lignes PG avec `occurred_at` antérieur à la fenêtre de rétention sont supprimées
- **AND** les entrées immudb correspondantes restent intactes
- **AND** un événement `SYSTEM` résume le nombre de lignes purgées en PG

### Requirement: Minimisation des données affichées

Le système MUST masquer les adresses IP en affichage IHM (masque `/24` ou équivalent) tout en conservant l'IP complète en base pour enquêtes `admin_global`.

#### Scenario: Affichage IP masquée

- **WHEN** un `lan_user` consulte une ligne d'audit avec `actor_ip=192.168.1.42`
- **THEN** l'IHM affiche `192.168.1.0/24` ou `192.168.1.x`

### Requirement: Anonymisation à la suppression de compte

Le système MUST anonymiser les références personnelles dans `armoire_audit_events` lors de la suppression d'un compte utilisateur cloud.

#### Scenario: Delete compte utilisateur

- **WHEN** un utilisateur exerce le droit à l'effacement et son compte est supprimé
- **THEN** les champs `actor_id` et `actor_ip` des événements concernés sont remplacés par une valeur pseudonymisée non réversible
- **AND** les événements techniques restent pour l'intégrité sécurité du foyer

