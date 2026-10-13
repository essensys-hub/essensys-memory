# Clé d'accès à distance du BP et exécution des actions : analyse du 2026-10-13

Version anonymisée. Les adresses IP, la MAC et les numéros de série de l'installation sont retirés.

## Contexte

Un boîtier principal (BP, SC944D, firmware 099-37) neuf a été installé sur une gateway CM5 (stack V.1.3.0) après l'incident foudre du 9 août 2026. C'est le premier BP posé depuis la fermeture d'Essensys et la disparition du serveur ASP.NET `mon.essensys.fr`.

Symptôme rapporté : « la gateway voit le BP mais aucune action n'est exécutée ». La page écran **Réglages → Accès à distance** montre une clé vide (8 groupes de tirets) et le voyant `CABLE > DHCP > DNS > SERVEUR` entièrement vert.

Question posée : la fonction « Réglage accès à distance » peut-elle empêcher les actions ?

Méthode :
- lecture du firmware 099-37 (identique à `client-essensys-legacy`, et identique aux archives 095-34 à 097-36 pour la clé), du programme écran SC945D, de l'ASP.NET legacy et du backend Go ;
- 7 lecteurs parallèles, puis chaque hypothèse vérifiée selon 3 angles (trace de code, déploiement réel, explication alternative) ;
- diagnostic SSH en lecture seule sur la gateway.

## Fonctionnement de la clé (firmware)

- **Génération.** L'ancien site générait une clé aléatoire de 32 chiffres par compte (`UserService.cs:229-233`, `rnd.Next(0,9)`, donc sans chiffre 9) et stockait son MD5 (`HashedPkey`). La « clef produit » collée sur le tableau ne servait qu'à l'inscription et n'est jamais envoyée au BP.
- **Saisie.** L'écran écrit 16 octets aux index **922 à 937** de la table d'échange, deux chiffres par octet (chiffre n° 1 dans les bits 0 à 3). Droits `_W` : écriture seule, aucune relecture possible. Les tirets de la page sont un gabarit fixe (`StpAAD.4FN`).
- **Persistance.** EEPROM SPI du BP (25AA02E48), adresses 0x00 à 0x0F, la même puce que le code alarme (0x10) et la MAC usine (0xFA). La clé est **perdue quand on change de BP**. Au démarrage, elle est mise à 0 (`main.c:786`), puis relue brute en EEPROM sans contrôle (`EepromAdresseMac.c:92-133`). Sur un BP neuf, l'EEPROM est probablement à 0xFF.
- **Prise en compte à chaud.** `main.c:378-383` appelle `vd_UpdateCleServeurDansEEPROM` à chaque tour de boucle. À chaque octet modifié, la fonction écrit l'EEPROM et rappelle `cryptage()` (`EepromAdresseMac.c:146-161`). Aucun redémarrage n'est nécessaire.
- **Calcul** (`Cryptage.c:70-105`) : 32 caractères `'0' + demi-octet` (bas, puis haut), MD5, « 16 hexa : 16 hexa », base64. Le résultat est envoyé **sans condition** dans l'en-tête `Authorization: Basic` des 7 requêtes HTTP.
- **Alarme distante.** La même chaîne sert à déchiffrer en AES l'ordre d'alarme distant `_de67f` (`www.c:1158-1245`) : la clé AES est la chaîne des 32 chiffres, et l'IV est dérivé du MD5.
- **Aucun test de validité.** Le firmware ne vérifie jamais la clé. Le traitement d'une action ne vérifie que les droits d'écriture de chaque index.

## Quand la clé bloquait les actions

1. **Serveur ASP.NET (historique).**
   - Le serveur contrôlait `HashedPkey && IsActive` et répondait 401 sinon.
   - Le BP exige « 200 OK » sur `serverinfos` (`Json.c:68-72`). Sans cela, il ne demande jamais ni `mystatus` ni `myactions`, et le voyant SERVEUR reste rouge.
   - C'est le sens de l'avertissement de la procédure v3 : « clé mal saisie → pas d'accès à distance ».
2. **Gateway CM5 (aujourd'hui) : aucun blocage.**
   - L'authentification legacy est désactivée (`auth.enabled: false`) et le LAN IAM est actif. Le middleware BasicAuth n'est donc pas monté. Même monté, il serait passif.
   - La file d'actions Redis est **globale** (`essensys:global:actions`).
   - Le backend renvoie toujours `_de67f: null`.
3. **Index 922 à 937 écrits par une action serveur.** Une telle action réécrirait l'identité du BP. Aucun composant ne les émet.

Le voyant SERVEUR vert suffit à écarter la clé : il prouve que `serverinfos`, `mystatus` (201) et `myactions` (200) aboutissent.

## Points corrigés pendant l'analyse

- `cryptage()` n'est pas calculé seulement au démarrage : il est rappelé à chaque changement de la clé.
- `GET /table_ref` ne vide pas la file : `RedisStore.DequeueActions` fait un `LRANGE 0 -1` sans retrait, et seul `/api/done` retire une action (`LREM`).

## Ordre des opérations côté BP

`www.c:945-990` : le BP écrit les valeurs reçues dans `Tb_Echange`, puis envoie `POST /api/done/{guid}`, et **seulement ensuite** la tâche BA transmet l'ordre par l'I2C.

Si le BA ne répond pas, l'ordre est libéré sans prévenir après plus de 20 essais (`ba.c:284-296`). Une fois ce compteur saturé, chaque nouvel ordre vers ce BA n'a plus droit qu'à un seul essai.

**Un acquittement « Action acknowledged » ne prouve donc pas l'exécution.**

Le BP neuf ne renvoie pas la configuration des BA au démarrage (`ba.c:127-135`).

## Diagnostic SSH du 2026-10-13 (lecture seule)

- Le BP a un bail DHCP sur le segment armoire. `Status Update (Version: V37)` arrive environ toutes les 2 s : 76 585 cycles en 48 h, sans aucun 401 ni 403.
- 13 `POST /api/admin/inject` le 2026-10-12 entre 15 h 53 et 16 h 44 ont produit **15 actions envoyées, 15 `POST /api/done` et 15 « Action acknowledged »**, chacune en 1 à 2 s. La file Redis est vide.
- Les 15 actions visaient toutes des sorties des BA **CHB** (index 607 et 613, bit 6) et **PDE** (609, 610, 615, 616). **Aucune ne visait le BA PDV.**
- `/table_ref` : **index 12 = 24 (0x18)**, soit BA CHB (0x12) et PDE (0x13) en défaut et BA PDV (0x11) répondant ; **index 10 = 0**, pas de mode secouru.

**Conclusion.** Les actions atteignent le BP et sont acquittées. Elles sont perdues en aval, sur l'I2C vers les deux BA en défaut depuis l'incident foudre. La clé d'accès à distance n'est pas en cause.

Test discriminant restant : envoyer une commande vers un BA PDV (lampe d'une pièce de vie) et constater l'effet.

## Valeurs de référence (algorithme de Cryptage.c)

| Clé | MD5 | Identifiant (16 premiers hexa) |
|---|---|---|
| 16 × 0x00 | cd9e459ea708a948d5c2f5a6ca8838cf | cd9e459ea708a948 |
| 16 × 0xFF (EEPROM vierge) | 33ee58c4205294452a09c59a8c3c2ba3 | 33ee58c420529445 |

L'algorithme est validé par le vecteur de test de l'ASP.NET (`AuthTest`).

## Suivi

- Ticket essensys-hub/essensys-doc#7 : procédure d'ajout ou de remplacement d'un BP, publiée dans `docs/install/ajout-bp.md`.
- Lien avec essensys-hub/essensys-board-SC944D#2 : diagnostic et remise en service de l'installation touchée.
