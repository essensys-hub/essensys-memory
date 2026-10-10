## Purpose

Permettre à un utilisateur Essensys connecté de signaler un bug logiciel ou un incident sur son installation sans compte GitHub, tout en protégeant ses données personnelles : les dépôts publics ne reçoivent jamais d'information qui l'identifie.

## ADDED Requirements

### Requirement: Signalement réservé aux comptes connectés
Le système SHALL accepter un signalement uniquement d'un utilisateur authentifié par une session valide du portail. Une requête sans session valide MUST être refusée sans créer d'issue.

#### Scenario: Requête sans session
- **WHEN** une requête de signalement arrive sans jeton de session, ou avec un jeton expiré ou invalide
- **THEN** le système répond 401 et ne crée aucune issue

#### Scenario: Mot de passe temporaire non changé
- **WHEN** l'utilisateur connecté doit encore changer son mot de passe temporaire
- **THEN** le système refuse le signalement avec la même réponse que les autres routes du portail qui exigent ce changement

#### Scenario: Visiteur sur le site
- **WHEN** un visiteur non connecté ouvre la page du formulaire
- **THEN** le site l'invite à se connecter et ne montre pas le formulaire

### Requirement: Contenu du formulaire
Le formulaire SHALL demander : le type (Bug logiciel ou Incident sur mon installation), l'application concernée (portail web, app iPhone, app Android, gateway locale, autre), la version si connue, le mode de connexion (cloud ou réseau local), un titre, ce qui se passe, ce qui était attendu, et, pour un bug, les étapes pour reproduire. Le système MUST rejeter un signalement dont le type, le titre ou la description manque, ou dont un champ dépasse sa longueur maximale (titre 120 caractères, chaque texte libre 4 000 caractères).

#### Scenario: Signalement complet
- **WHEN** un utilisateur connecté envoie un signalement Bug avec tous les champs obligatoires remplis
- **THEN** le système l'enregistre, crée l'issue et répond avec la référence du signalement

#### Scenario: Champ obligatoire manquant
- **WHEN** le titre ou la description est vide
- **THEN** le système répond 400 en nommant le champ, et le site affiche l'erreur à côté de ce champ

#### Scenario: Champ trop long
- **WHEN** la description dépasse 4 000 caractères
- **THEN** le système répond 400 et ne crée aucune issue

### Requirement: Avertissement sur les données personnelles
Le formulaire SHALL afficher, avant les champs de texte libre et sans action de l'utilisateur, l'avertissement : « Ne saisissez jamais votre adresse postale, votre mot de passe ni aucun code d'accès. Les bugs sont publiés sur GitHub de façon anonyme. »

#### Scenario: Avertissement visible
- **WHEN** l'utilisateur connecté ouvre le formulaire, sur ordinateur ou sur mobile
- **THEN** l'avertissement est visible au-dessus du premier champ de texte libre, sans défilement horizontal

### Requirement: Refus des contenus sensibles
Le système MUST refuser un signalement dont le titre ou un texte libre contient un motif qui ressemble à un mot de passe déclaré (par exemple « mot de passe : … », « password= »), à un jeton ou une clé (jeton JWT, clé d'API, clé privée), à une adresse postale (numéro, type de voie et nom de voie, ou code postal à cinq chiffres suivi d'une ville) ou à une adresse email. La réponse MUST indiquer le champ et la catégorie détectée, sans recopier le texte détecté. Le contenu refusé MUST NOT être enregistré ni journalisé.

#### Scenario: Mot de passe dans la description
- **WHEN** la description contient « mon mot de passe : Soleil2026 »
- **THEN** le système répond 422 avec le champ `description` et la catégorie `password`, et n'enregistre rien

#### Scenario: Adresse postale dans la description
- **WHEN** la description contient « 12 rue des Lilas 69400 Limas »
- **THEN** le système répond 422 avec la catégorie `postal_address`

#### Scenario: Texte technique légitime
- **WHEN** la description contient « l'écran Volets affiche 25 s puis se fige »
- **THEN** le signalement est accepté

#### Scenario: Message affiché à l'utilisateur
- **WHEN** le site reçoit un refus pour contenu sensible
- **THEN** il affiche sous le champ concerné un message qui demande de retirer l'information, sans effacer la saisie

### Requirement: Limite de signalements par compte
Le système SHALL limiter chaque compte à 5 signalements par période glissante de 24 heures. Au-delà, il MUST répondre 429 sans créer d'issue, et indiquer quand un nouveau signalement sera possible.

#### Scenario: Sixième signalement
- **WHEN** un compte a déjà créé 5 signalements dans les dernières 24 heures et en envoie un sixième
- **THEN** le système répond 429 et ne crée aucune issue

#### Scenario: Comptes indépendants
- **WHEN** un compte a atteint la limite
- **THEN** un autre compte peut toujours signaler

### Requirement: Routage et anonymisation
Un signalement de type Bug SHALL créer une issue de type Bug dans le dépôt public `essensys-hub/essensys-support-site`. Un signalement de type Incident SHALL créer une issue dans le dépôt privé `essensys-hub/essensys-support`. Les deux issues SHALL être ajoutées au Project #6. Une issue créée dans un dépôt public MUST NOT contenir le nom, l'email, l'identifiant de compte, l'identifiant d'armoire ou de passerelle, ni l'adresse IP de l'utilisateur. Elle porte seulement une référence pseudonyme stable `U-` suivie de caractères dérivés du compte, non réversibles sans la base du portail.

#### Scenario: Bug public anonymisé
- **WHEN** un utilisateur crée un signalement Bug
- **THEN** l'issue publique contient le titre, les champs du formulaire et la référence `U-…`, et ne contient ni email, ni nom, ni identifiant d'armoire

#### Scenario: Même référence pour un même compte
- **WHEN** un même utilisateur crée deux signalements
- **THEN** les deux issues portent la même référence `U-…`

#### Scenario: Incident privé
- **WHEN** un utilisateur crée un signalement Incident
- **THEN** l'issue est créée dans le dépôt privé et n'apparaît dans aucun dépôt public

### Requirement: Indisponibilité de GitHub
Si la création de l'issue échoue (GitHub indisponible, droits insuffisants, quota atteint), le système SHALL conserver le signalement avec l'état « en attente d'envoi », répondre avec succès à l'utilisateur, et réessayer plus tard. Un signalement en attente MUST compter dans la limite par compte.

#### Scenario: GitHub répond 5xx
- **WHEN** GitHub répond une erreur serveur à la création de l'issue
- **THEN** l'utilisateur reçoit la référence de son signalement avec l'état « en attente d'envoi », et l'issue est créée lors d'une nouvelle tentative

### Requirement: Accès depuis la page d'accueil
Pour un utilisateur connecté, les cartes « Bug logiciel » et « Incident production » de la page d'accueil SHALL ouvrir le formulaire avec le type correspondant déjà choisi, au lieu des modèles d'issue GitHub.

#### Scenario: Carte Incident
- **WHEN** un utilisateur connecté clique sur la carte « Incident production »
- **THEN** le formulaire s'ouvre avec le type Incident sélectionné
