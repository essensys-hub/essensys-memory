# Prompt ruflo : build complet SC944D (BP) en Docker local — `essensys-gcc`

Tu es l'agent **`ruflo-core:coder`** (implémentation). Ta mission n'est **pas** de concevoir (pas d'OpenSpec ici) mais d'**exécuter jusqu'au bout, en local, un build Docker complet** du firmware **SC944D** (carte BP, MCF52259 ColdFire) dans le dépôt `~/ESSENSYS/essensys-gcc`, et de corriger toute erreur rencontrée jusqu'à obtenir un build vert reproductible sur cette machine.

> Pas de GitHub Actions ici. Le dépôt a déjà souffert d'itérations à l'aveugle sur des tags CI (voir `PIPELINE_SUMMARY.md`, cinq tentatives `fw-v001-0000` → `fw-v001-0004`) — la leçon retenue est : **valider en local avant de retoucher aux workflows**. N'ouvre, ne modifie, ne pousse **aucun** fichier sous `.github/workflows/` dans le cadre de ce prompt.

> ⚠️ **Contexte d'exécution ruflo.** Tu tournes comme sous-agent, potentiellement en arrière-plan, **sans TTY et sans droits d'admin**. Tu ne peux **pas** démarrer Docker Desktop ni faire `sudo`. Tu **ne committes ni ne pushes rien** — tu restes sur la copie de travail et tu rapportes. Utilise toujours des **chemins absolus** (ton cwd n'est pas garanti être `essensys-gcc`).

---

## 0. Préconditions — vérifier AVANT toute action (échouer vite si non remplies)

Exécute d'abord ces contrôles. Si l'un échoue, **arrête-toi et rends la main** avec un message clair — n'essaie pas de contourner.

```bash
GCC_DIR=/Users/nrineau/ESSENSYS/essensys-gcc

# P1 — Docker daemon joignable ? (l'agent NE PEUT PAS le démarrer lui-même)
docker version --format '{{.Server.Version}}' \
  || { echo "BLOQUÉ: Docker daemon non démarré. Demander à l'utilisateur de lancer Docker Desktop, puis relancer."; exit 1; }

# P2 — Submodule mqx présent (non vide) ?
test -f "$GCC_DIR/mqx/mqx/source/psp/coldfire/psp_comp.h" \
  || { echo "BLOQUÉ: submodule mqx absent. Voir §2 (init contrôlée)."; exit 1; }
```

> **P1 est le blocage le plus fréquent** : Docker Desktop se démarre à la main (action GUI), l'agent ne peut pas le faire. Si `docker version` échoue, le bon comportement est de **s'arrêter et le signaler**, pas de boucler.

---

## 0 bis. État constaté (vérifié le 2026-07-28 sur la copie de travail)

| Fait vérifié | Détail |
|---|---|
| Dépôt | `/Users/nrineau/ESSENSYS/essensys-gcc` est son propre repo git ; **pas** de repo git au niveau `ESSENSYS/` |
| Submodule `mqx` | **Déjà initialisé et déjà patché** : `git -C mqx diff --stat` montre les 4 fichiers du patch (`asm_mac.h`, `dispatch.S`, `ipsum.S`, `psp_prv.inc`) modifiés en local, et `git -C mqx apply --reverse --check ../bp/patches/0001-mqx-gcc-compat.patch` réussit. **NE PAS** lancer `git submodule update` aveuglément : cela réinitialiserait mqx au SHA enregistré et **effacerait le patch**, alors que le marqueur `bp/.mqx_patched` empêcherait sa ré-application → build sur sources non patchées. Voir §2. |
| Marqueur patch | `bp/.mqx_patched` **existe déjà** (vide) → la cible Make `patch` sera **skippée**. C'est cohérent tant que le patch reste appliqué dans mqx. Si (et seulement si) tu réinitialises mqx, supprime ce marqueur pour forcer la ré-application. |
| `bp/Makefile` | `APP_SRC = main.c` — **application minimale de validation** (57 lignes) ; les sources métier réelles (`Alarme.c`, `Chauffage.c`, `FilPilote.c`, … de `essensys-board-SC944D`) ne sont **pas** intégrées. Hors périmètre : on valide la **chaîne de build**, pas le firmware fonctionnel. |
| Dockerfile | Multi-stage : `toolchain-builder` compile `m68k-elf-gcc` 14.2.0 via crosstool-NG 1.26.0 (**long : 30-60 min au premier build**, ensuite cache Docker), stage final `essensys-builder` copie la toolchain + installe XC8 (skippable via `--build-arg SKIP_XC8=1`). |
| Pièges déjà connus (mémoire `sc944d-ci-pipeline`) | `gcov` n'est pas un paquet apt (fourni par gcc) ; `bp/main.c` minimal existe déjà ; `ba/Makefile` ne doit erreurer que sur un `BOARD` invalide, pas vide (commit `94091de`). |
| Dernier run CI (`job_info.json`) | Échec `Compile firmware BP` sur un SHA ancien (`24ee65c`, mars 2026), **antérieur** aux correctifs (`git log` va jusqu'à `94091de`). État obsolète, à revérifier en local. |

---

## 1. Objectif

Obtenir, **en local, dans Docker, sans toucher au CI**, un build **BP (SC944D)** qui se termine avec :

- `bp/build/bp/BP_MQX_ETH-<VERSION>.elf`
- `bp/build/bp/BP_MQX_ETH-<VERSION>.s19`
- `bp/build/bp/BP_MQX_ETH-<VERSION>.map`
- Rapport de taille (`m68k-elf-size`) affiché sans erreur

Secondaire (si le temps le permet et si BP passe) : lancer aussi `make test` (tests unitaires host GCC, pas besoin de Docker) et `make build-ba` (nécessite l'image avec XC8, plus lourde) pour valider `make all` de bout en bout — mais **BP est la priorité explicite de ce prompt**, ne bloque pas dessus pour courir après BA.

### Non-objectifs

- Intégrer les sources applicatives réelles du firmware (Alarme, Chauffage, etc.) — hors périmètre.
- Modifier `.github/workflows/*` ou déclencher un run CI (tag `fw-v*`).
- Toucher au protocole HTTP / à `Tb_Echange[]` / aux contraintes immuables du firmware (cf. `prompt.md` §"Contraintes immutables").
- Publier/pousser une image Docker sur `ghcr.io`.

---

## 2. Procédure recommandée

Toujours en chemins absolus (`GCC_DIR=/Users/nrineau/ESSENSYS/essensys-gcc`).

```bash
GCC_DIR=/Users/nrineau/ESSENSYS/essensys-gcc

# 1. Submodules — init CONTRÔLÉE, pas aveugle.
#    Sur la copie actuelle, mqx est déjà présent ET déjà patché (cf. §0 bis).
#    Ne lance `git submodule update` QUE si mqx est réellement absent :
if [ ! -f "$GCC_DIR/mqx/mqx/source/psp/coldfire/psp_comp.h" ]; then
  git -C "$GCC_DIR" submodule update --init --recursive
  rm -f "$GCC_DIR/bp/.mqx_patched"          # force la ré-application du patch au prochain build
fi
# Si mqx est présent : vérifie que le patch est bien appliqué, ne le ré-applique pas à l'aveugle :
git -C "$GCC_DIR/mqx" apply --reverse --check "$GCC_DIR/bp/patches/0001-mqx-gcc-compat.patch" \
  && echo "patch MQX déjà appliqué (OK)" \
  || echo "ATTENTION: état patch MQX inattendu — inspecter avant de builder"

# 2. Image Docker — commence SANS XC8 pour itérer vite sur BP uniquement.
#    ⚠️ Premier build = 30-60 min (crosstool-NG). Au-delà d'un budget de tour d'agent :
#    lance-le en tâche détachée/arrière-plan et attends sa fin AVANT l'étape 3,
#    ou réutilise une image déjà présente (`docker images essensys-builder`).
docker build --build-arg SKIP_XC8=1 -t essensys-builder "$GCC_DIR"

# 3. Build BP seul dans le conteneur (chemin absolu, pas $(pwd))
docker run --rm -v "$GCC_DIR":/workspace essensys-builder \
  make -C /workspace build-bp VERSION=local-dev

# alternative équivalente via l'orchestrateur build.sh embarqué dans l'image :
docker run --rm -v "$GCC_DIR":/workspace essensys-builder build.sh bp
```

Vérifie ensuite les artefacts :

```bash
ls -la "$GCC_DIR"/bp/build/bp/BP_MQX_ETH*
docker run --rm -v "$GCC_DIR":/workspace essensys-builder \
  m68k-elf-size /workspace/bp/build/bp/BP_MQX_ETH-local-dev.elf
```

Si tout est vert et qu'il reste du budget, enchaîne :

```bash
make -C "$GCC_DIR" test                          # tests host, hors Docker
docker build -t essensys-builder "$GCC_DIR"      # image complète avec XC8 (plus longue)
docker run --rm -v "$GCC_DIR":/workspace essensys-builder make -C /workspace all
```

> **Note bind-mount :** le build écrit dans `bp/build/` monté depuis l'hôte. Sur macOS/Docker Desktop l'ownership est remappé (pas de fichiers root-owned gênants) ; si un jour ce prompt tourne sous Docker Linux natif, prévoir `--user "$(id -u):$(id -g)"`.

---

## 3. Boucle de debug attendue

Ceci est un travail d'**exécution itérative**, pas de lecture passive de logs CI. À chaque échec :

1. Reproduis l'erreur en local (le message d'erreur `docker run` fait foi, pas une hypothèse).
2. Identifie la cause précise (chemin manquant, symbole non résolu, flag GCC incompatible, patch MQX qui échoue, section linker en conflit, etc.).
3. Corrige le fichier concerné (`bp/Makefile`, `bp/compat/*`, `bp/patches/0001-mqx-gcc-compat.patch`, `bp/intflash.ld`, `Dockerfile`) — **jamais** en modifiant les contraintes du §"Ce qu'il ne faut pas faire" ci-dessous.
4. Reconstruis uniquement ce qui est nécessaire (le cache Docker + les `.d` de dépendances Make évitent de tout refaire).
5. Documente le piège rencontré et sa correction (voir §5).

Points d'attention hérités des tentatives précédentes (à vérifier en priorité si erreur) :
- **`build.sh bp` ≠ `make build-bp` — divergence importante.** `build.sh` patche `psp_comp.h` (ajout de la branche `#elif defined(__GNUC__)` via `sed`) **avant** d'appeler `make`, alors que `make build-bp` ne le fait **pas** (la cible Make `patch` n'applique que `0001-mqx-gcc-compat.patch`, qui ne touche pas `psp_comp.h`). Vérifié : `grep __GNUC__ mqx/mqx/source/psp/coldfire/psp_comp.h` est actuellement **vide**. Donc si tu passes par `make build-bp` directement, `psp_comp.h` ne sera pas patché et le build peut casser sur MQX. **Recommandation : utilise `build.sh bp` comme point d'entrée** (il enchaîne patch psp_comp.h + `make`), ou patche `psp_comp.h` manuellement avant un `make` direct.
- Le patch `0001-mqx-gcc-compat.patch` (asm_mac.h, dispatch.S, ipsum.S, psp_prv.inc) est appliqué **une fois** via le marqueur `bp/.mqx_patched`. Sur la copie actuelle il est **déjà appliqué** (cf. §0 bis). Ne le ré-applique que si tu as réinitialisé mqx — dans ce cas, `rm bp/.mqx_patched` pour forcer la ré-application.
- Endianness **big-endian** native ColdFire — toute erreur de link étrange sur des structures packées mérite une vérification `-fpack-struct`/attributs plutôt qu'un contournement silencieux.
- Flags obligatoires déjà dans `bp/Makefile` : `-mcpu=52259 -msoft-float -ffreestanding -nostdlib` — ne les retire pas pour "faire passer" un lien, cherche la vraie cause (cf. §"Contraintes").

---

## 4. Ce qu'il ne faut pas faire

- Ne pas modifier `.github/workflows/*.yml` ni pousser de tag `fw-v*`.
- Ne pas changer le comportement fonctionnel du firmware — ce prompt valide une **chaîne de compilation**, pas le firmware métier.
- Ne pas toucher au layout mémoire du bootloader (`intflash.ld`, sections `.APP_JUMP`/`.APP_CRC`/`.APP_VERSION`) sauf si l'erreur de build le justifie explicitement et que c'est documenté.
- Ne pas ajouter de dépendance apt fantaisiste sans vérifier qu'elle existe réellement dans `debian:bookworm-slim` (rappel : `gcov` n'est pas un paquet séparé, piège déjà rencontré).
- Ne pas committer/pousser sans validation explicite — reste sur la copie de travail locale, rapporte l'état avant tout commit.
- Ne pas inventer de registres périphériques ou de HAL absents du firmware actuel (cf. `prompt.md`).

---

## 5. Mise à jour mémoire (obligatoire si nouveau piège trouvé)

Si un nouveau problème de build est découvert et corrigé (au-delà de ceux déjà listés en §0 bis), ajoute-le au fichier mémoire persistant :

`/Users/nrineau/.claude/projects/-Users-nrineau-ESSENSYS/memory/sc944d-ci-pipeline.md`

dans la section « Pièges rencontrés », avec la cause **et** la correction — pas seulement dans ce prompt.

## 5 bis. Condition d'arrêt (anti-spin)

Tu as pour consigne de « corriger jusqu'au vert », mais **pas** de tourner indéfiniment. Arrête-toi et rends la main avec un rapport si l'un de ces cas survient :

- Docker daemon injoignable (précondition P1) — action utilisateur requise.
- **3 tentatives de correction** consécutives sur la **même** erreur de compilation/link sans progrès.
- Une correction exigerait de violer le §4 (toucher au layout bootloader, aux contraintes immuables, aux workflows CI, ou d'intégrer les sources métier).
- Le premier `docker build` dépasse largement l'attendu (> ~75 min) ou échoue sur le stage toolchain — signale-le, ne relance pas en boucle.

---

## 6. Definition of Done

- [ ] Préconditions §0 vertes (Docker joignable, submodule mqx présent et patché).
- [ ] `docker build --build-arg SKIP_XC8=1 -t essensys-builder "$GCC_DIR"` termine sans erreur.
- [ ] `make -C /workspace build-bp VERSION=local-dev` (dans le conteneur) termine sans erreur.
- [ ] `bp/build/bp/BP_MQX_ETH-local-dev.elf`, `.s19` et `.map` existent et sont non vides.
- [ ] Rapport de taille (`m68k-elf-size`) affiché, sans dépassement de la Flash 512 Ko / SRAM 64 Ko.
- [ ] Aucun fichier sous `.github/workflows/` modifié.
- [ ] Rapport final : liste des fichiers modifiés, causes des erreurs rencontrées et corrections apportées, taille finale du binaire, et — le cas échéant — statut de `make test` / `make build-ba`.

### Point de départ pour l'agent

> Commence par les **préconditions §0** (Docker joignable ? mqx présent ?). Si Docker n'est pas démarré, arrête-toi et demande à l'utilisateur de lancer Docker Desktop. Puis suis la §2 (init submodule **contrôlée**, pas aveugle — mqx est déjà patché ici), construis l'image **sans XC8** pour itérer vite sur BP, et privilégie `build.sh bp` comme entrée. Ne lance `make all` (BA/XC8) qu'une fois BP vert. Logue chaque commande et sa **sortie brute** — pas de résumé optimiste sans la sortie réelle à l'appui. Respecte la condition d'arrêt §5 bis.
