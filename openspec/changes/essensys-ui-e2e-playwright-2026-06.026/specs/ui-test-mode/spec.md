# ui-test-mode

Mode test Essensys : valider les écritures domotique **sans** enqueue vers l'armoire SC944D ; lire et comparer les valeurs **reçues** sur la table d'échange.

## ADDED Requirements

### Requirement: Activation dry-run sur écritures API

Les endpoints d'écriture domotique MUST accepter le mode test lorsque `X-Essensys-Test-Mode: dry-run` **ou** `test_mode=dry_run` est présent.

Endpoints concernés (minimum) :

- `POST /api/admin/inject` (local)
- `POST /api/portal/inject` (portail)
- `POST /api/scenarios/{slot}/launch`, `PUT /api/scenarios/{slot}`, `POST /api/scenarios/{slot}/restore`
- Équivalents `/api/portal/scenarios/*`
- `POST /api/web/actions`, `POST /api/portal/web/actions`

#### Scenario: Inject dry-run valide sans enqueue

- **WHEN** le client envoie `POST /api/admin/inject?test_mode=dry_run` avec `{"k":590,"v":"2"}`
- **THEN** la réponse est `200` avec `dry_run: true` et `status: "test_ok"`
- **AND** aucune entrée n'est ajoutée à la file firmware (`DequeueActions` inchangé)

#### Scenario: Inject dry-run rejete param invalide

- **WHEN** le client envoie un index hors plage ou batch > 30 params en dry-run
- **THEN** la réponse est `422` avec `status: "test_failed"` et un message explicite
- **AND** aucune action n'est enqueue

#### Scenario: Launch scénario dry-run

- **WHEN** le client envoie `POST /api/scenarios/2/launch?test_mode=dry_run`
- **THEN** la réponse contient `validated_params` incluant l'index trigger 590 et la valeur slot
- **AND** la file firmware reste vide

### Requirement: Lecture exchange sans effet de bord

`GET /api/admin/exchange` et `GET /api/portal/exchange` MUST rester en lecture seule et MUST NOT être modifiés par le mode test.

#### Scenario: Snapshot exchange pour assertion test

- **WHEN** le backend a reçu des valeurs via `POST /api/mystatus` (firmware)
- **AND** le test appelle `GET /api/admin/exchange?keys=349,350,351,352`
- **THEN** la réponse liste les k/v connus du cache
- **AND** le mode test dry-run n'a pas modifié ces valeurs

### Requirement: UI mode test visible

Le frontend MUST afficher un indicateur persistant lorsque le mode test est actif.

#### Scenario: Bannière mode test

- **WHEN** l'utilisateur active le mode test (settings ou `?test=1`)
- **THEN** une bannière indique qu'aucune commande n'est envoyée à l'armoire
- **AND** toutes les écritures API incluent le header dry-run

#### Scenario: Verdict affiché après action

- **WHEN** l'utilisateur lance un scénario en mode test
- **AND** le backend répond `test_ok`
- **THEN** l'UI affiche un message de succès de **test** (pas « envoyé à l'armoire »)

### Requirement: Parité jumeaux local / portail

Le comportement mode test MUST être équivalent entre `essensys-server-frontend` + `essensys-server-backend` et `essensys-user-portal-frontend` + `essensys-user-portal-backend`, à l'exception des préfixes URL (`/api/admin` vs `/api/portal`).

#### Scenario: Portail dry-run sans forward gateway

- **WHEN** `POST /api/portal/scenarios/2/launch?test_mode=dry_run` avec JWT valide
- **THEN** le hub valide et répond `test_ok`
- **AND** aucune requête n'est forwardée vers la gateway du client
