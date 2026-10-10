# support-report-tracking Specification

## Purpose
Permettre à un utilisateur Essensys connecté de retrouver les signalements qu'il a envoyés et de suivre leur avancement, sans compte GitHub.

## Requirements

### Requirement: Liste de ses propres signalements
Le système SHALL fournir à l'utilisateur connecté la liste de ses signalements, du plus récent au plus ancien, avec pour chacun : la référence, le type, le titre, la date d'envoi et l'état. Un utilisateur MUST NOT voir les signalements d'un autre compte.

#### Scenario: Liste d'un utilisateur
- **WHEN** un utilisateur connecté ouvre « Mes signalements » dans Mon profil
- **THEN** il voit ses signalements, du plus récent au plus ancien

#### Scenario: Isolation entre comptes
- **WHEN** l'utilisateur A demande la liste
- **THEN** aucun signalement de l'utilisateur B n'y figure

#### Scenario: Sans session
- **WHEN** la liste est demandée sans session valide
- **THEN** le système répond 401

#### Scenario: Aucun signalement
- **WHEN** l'utilisateur n'a encore rien signalé
- **THEN** la page indique qu'il n'y a aucun signalement et propose d'en créer un

### Requirement: États d'un signalement
Chaque signalement SHALL avoir l'un des états suivants : « en attente d'envoi » (issue pas encore créée), « ouvert » (issue créée et ouverte), « résolu » (issue fermée comme terminée), « clos » (issue fermée pour une autre raison). L'état affiché MUST refléter l'état de l'issue GitHub avec un retard d'au plus 15 minutes.

#### Scenario: Issue fermée par un mainteneur
- **WHEN** un mainteneur ferme l'issue comme terminée
- **THEN** le signalement apparaît « résolu » dans « Mes signalements » au plus tard 15 minutes après

### Requirement: Lien vers l'issue publique
Pour un bug, la liste SHALL proposer un lien vers l'issue publique sur GitHub. Pour un incident, elle MUST NOT exposer l'adresse du dépôt privé.

#### Scenario: Bug avec lien
- **WHEN** l'utilisateur consulte un bug à l'état « ouvert »
- **THEN** un lien ouvre l'issue publique dans un nouvel onglet

#### Scenario: Incident sans lien
- **WHEN** l'utilisateur consulte un incident
- **THEN** seuls la référence et l'état sont affichés, sans lien vers GitHub
