## Purpose

Permet à un titulaire de compte portail Essensys de demander la réinitialisation de son mot de passe sans révéler à un tiers si une adresse email est enregistrée, et de recevoir un jeton de réinitialisation à usage unique et à durée de vie limitée.

## ADDED Requirements

### Requirement: Endpoint de demande de réinitialisation

Le système SHALL exposer `POST /api/auth/password/forgot` en accès public (sans JWT), acceptant un corps JSON `{ "email": string, "turnstile_token": string }`.

#### Scenario: Email correspondant à un compte actif

- **WHEN** un client soumet une adresse email correspondant à un compte `users` non interdit
- **THEN** le système crée un jeton de réinitialisation associé à ce compte
- **AND** déclenche l'envoi du courriel de réinitialisation
- **AND** répond `202 Accepted` avec le corps `{ "message": "Si un compte existe pour cette adresse, un email de réinitialisation a été envoyé." }`

#### Scenario: Email inconnu

- **WHEN** un client soumet une adresse email absente de la table `users`
- **THEN** le système ne crée aucun jeton et n'envoie aucun courriel
- **AND** répond `202 Accepted` avec un corps **strictement identique** à celui du cas « compte actif »

#### Scenario: Compte interdit

- **WHEN** un client soumet l'adresse d'un compte dont `forbidden_at` est renseigné
- **THEN** le système ne crée aucun jeton et n'envoie aucun courriel
- **AND** répond `202 Accepted` avec le même corps que les autres cas

#### Scenario: Email absent ou syntaxiquement invalide

- **WHEN** le champ `email` est vide, absent, ou ne contient pas de `@`
- **THEN** le système répond `400 Bad Request` avec `{ "error": "invalid_email" }`

### Requirement: Résistance à l'énumération de comptes

Le système MUST rendre indiscernables, du point de vue d'un appelant non authentifié, les réponses aux adresses existantes et inexistantes.

#### Scenario: Corps et code de réponse uniformes

- **WHEN** un attaquant compare les réponses obtenues pour une adresse existante et une adresse inexistante
- **THEN** le code HTTP, les en-têtes applicatifs et le corps JSON sont identiques

#### Scenario: Temps de réponse non discriminant

- **WHEN** un attaquant mesure la latence des deux cas sur au moins 20 requêtes
- **THEN** l'écart des médianes reste inférieur à 50 ms, le système effectuant un travail cryptographique équivalent (génération de jeton et/ou comparaison factice) dans les deux branches
- **AND** l'envoi du courriel est effectué de manière asynchrone afin de ne pas exposer la latence SMTP

### Requirement: Protection anti-automatisation

Le système SHALL protéger l'endpoint de demande par une vérification captcha Turnstile et par une limitation de débit par adresse IP.

#### Scenario: Jeton Turnstile manquant alors que le captcha est exigé

- **WHEN** la configuration serveur impose Turnstile et que `turnstile_token` est vide
- **THEN** le système répond `400 Bad Request` avec `{ "error": "captcha_required" }`
- **AND** ne crée aucun jeton de réinitialisation

#### Scenario: Jeton Turnstile refusé par Cloudflare

- **WHEN** la vérification du jeton auprès de Cloudflare échoue
- **THEN** le système répond `403 Forbidden` avec `{ "error": "captcha_failed" }`

#### Scenario: Captcha non configuré

- **WHEN** aucune clé secrète Turnstile n'est configurée sur le serveur
- **THEN** le système traite la demande sans vérification captcha, en s'appuyant uniquement sur la limitation de débit

#### Scenario: Dépassement de la limite de débit

- **WHEN** une même adresse IP effectue plus de 5 demandes en 1 heure
- **THEN** le système répond `429 Too Many Requests`
- **AND** journalise l'action d'audit `PASSWORD_RESET_BLOCKED_RATELIMIT` avec l'adresse IP

#### Scenario: Limite par compte

- **WHEN** plus de 3 jetons ont déjà été émis pour un même compte dans la dernière heure
- **THEN** le système n'émet pas de nouveau jeton et n'envoie pas de courriel
- **AND** répond malgré tout `202 Accepted` avec le corps uniforme

### Requirement: Émission du jeton de réinitialisation

Le système SHALL générer un jeton opaque imprévisible, le stocker sous forme hachée, et lui associer une expiration courte.

#### Scenario: Caractéristiques du jeton

- **WHEN** un jeton est émis
- **THEN** il contient au moins 256 bits d'entropie issus d'un générateur cryptographiquement sûr
- **AND** il est représenté sous une forme sûre pour une URL
- **AND** seul son empreinte SHA-256 est persistée, jamais sa valeur en clair

#### Scenario: Durée de validité

- **WHEN** un jeton est émis
- **THEN** son expiration est fixée à 60 minutes après l'émission

#### Scenario: Invalidation des jetons antérieurs

- **WHEN** un nouveau jeton est émis pour un compte possédant déjà des jetons non consommés
- **THEN** tous les jetons antérieurs de ce compte sont marqués comme invalidés et deviennent inutilisables

### Requirement: Traçabilité des demandes

Le système SHALL journaliser chaque demande de réinitialisation dans le journal d'audit, sans y inscrire la valeur du jeton.

#### Scenario: Demande aboutissant à l'émission d'un jeton

- **WHEN** un jeton est émis pour un compte
- **THEN** une entrée d'audit `PASSWORD_RESET_REQUESTED` est créée avec l'identifiant du compte, l'adresse email, l'adresse IP appelante et l'horodatage
- **AND** l'entrée ne contient ni le jeton en clair ni son empreinte

#### Scenario: Demande pour une adresse inconnue

- **WHEN** la demande porte sur une adresse inexistante
- **THEN** une entrée d'audit `PASSWORD_RESET_REQUESTED` est créée sans identifiant de compte, mentionnant que l'adresse est inconnue
- **AND** cette information n'est jamais renvoyée à l'appelant
