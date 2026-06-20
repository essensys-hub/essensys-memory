# essensys-api-doc

> Documentation de l'API legacy Essensys (protocole HTTP du firmware ↔ serveur `mon.essensys.fr`), publiée sous forme de site MkDocs Material bilingue FR/EN.

**Catégorie :** Documentation / Site
**Stack :** MkDocs + thème Material, plugins i18n (FR/EN) + Mermaid2, Python 3.9, GitHub Pages
**Statut :** Actif — publié sur `https://rhinosys.github.io/essensys-api-doc/` (remote `github.com/rhinosys/essensys-api-doc`, branche `main`)

## Rôle dans l'architecture Essensys
Ce dépôt documente l'**API/protocole legacy** par lequel le contrôleur embarqué BP_MQX_ETH dialogue avec le serveur Essensys d'origine. Il sert de référence de rétro-ingénierie : c'est la spécification à partir de laquelle le backend moderne (gateway / Anti-Corruption Layer) doit reproduire une compatibilité 100 % avec le protocole legacy. Il documente aussi la **table de référence des indices** (clés/valeurs) pilotant les domaines fonctionnels (chauffage, cumulus, arrosage, prises de sécurité…).

## Format et API documentées
- **Format : ce n'est PAS de l'OpenAPI/Swagger.** La documentation est rédigée à la main en Markdown sous `docs/API/`, accompagnée d'un référentiel structuré en **JSON propriétaire** (`reference.json` — racine `essensys`, chaque indice avec `default` / `Description` / `Attribut`) et de tables Markdown clé→valeur.
- **API documentées** (protocole HTTP legacy du firmware, en-têtes HTTP Basic + matricule chiffré) :
  - `GET /api/serverinfos` — informations serveur.
  - `GET /api/mystatus` — état courant de l'installation.
  - `POST/GET /api/myactions` — commandes/actions utilisateur.
  - Table de référence des indices fonctionnels : Chauffage zones jour/nuit/SdB (clés 349-352), Cumulus (353), Arrosage (363), Prises de sécurité (440), etc., avec leurs valeurs codées.
- Les données brutes ayant servi à la rétro-ingénierie sont conservées : captures **Wireshark** (`data/WireShark/`, `.pcapng` + dumps `serverinfos`/`mystatus`/`myactions`) et un extracteur Python (`py/wireshark_http_extractor.py`).

## Contenu / structure
- `mkdocs.yml` — config du site (thème Material, i18n FR/EN, Mermaid, onglets de navigation, CSS custom + termynal).
- `docs/index.fr.md` / `index.en.md` — accueil bilingue.
- `docs/API/` — cœur documentaire :
  - `specification.fr.md` (table de référence clés/valeurs), `reference.json` (référentiel JSON), `ref-essensys.ori.MD`.
  - `ActualArchitecture.md` / `NewArchitecture.md` (architecture actuelle vs cible), `ProcessChrone.md`, diagrammes `.drawio`.
- `docs/dev.env.install.md` — mise en place de l'environnement de dev MkDocs.
- `docs/images/` — visuels matériel (cumulus, disjoncteur, concentrateur, platine).
- `data/WireShark/` — captures réseau de référence ; `py/` — script d'extraction HTTP ; `doc_src/monEssensys.html` — page source d'origine.

## Build / Publication (générateur, hébergement)
- **Générateur :** MkDocs (thème Material). Dépendances dans `requirements.txt` (`mkdocs-material`, `mkdocs-static-i18n`, `mkdocs-mermaid2-plugin`, `mkdocs-encryptcontent-plugin`, etc.).
- **CI/CD :** GitHub Actions `.github/workflows/gh-deploy.yml` — sur push `main`, installe Python 3.9 + requirements et exécute `mkdocs gh-deploy --force`.
- **Hébergement :** GitHub Pages — `https://rhinosys.github.io/essensys-api-doc/`.
- Le plugin `encryptcontent` est présent dans les dépendances mais **commenté** dans `mkdocs.yml` (possibilité de protéger des pages par mot de passe, désactivée).

## Intégrations
- Référence directe pour `essensys-server-backend` / gateway lors de l'implémentation de l'ACL (compatibilité protocole legacy).
- Le `reference.json` et la table d'indices sont cohérents avec la `exchange-table` documentée dans `essensys-doc` (mêmes indices, ex. cumulus, chauffage).
- Captures Wireshark exploitables pour rejouer/valider les échanges legacy.

## Points d'attention
- Hébergé sous l'organisation **`rhinosys`** et non `essensys-hub` (les autres dépôts doc/site sont sous `essensys-hub`) — incohérence d'organisation à surveiller.
- Documentation rédigée manuellement : pas de spec machine-readable type OpenAPI → risque de désynchronisation avec le code et pas de validation automatique de schéma.
- Plusieurs pages portent la mention « Keys inconnue » / « Undef » : rétro-ingénierie **incomplète**, certains indices restent non documentés.
- Petites incohérences de formatage dans les tables Markdown (séparateurs `|` manquants sur certaines lignes de `specification.fr.md`).
- Workflow CI épinglé sur des actions anciennes (`actions/checkout@v2`, `setup-python@v2`, Python 3.9).
