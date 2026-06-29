#!/usr/bin/env python3
"""Generate the ESSENSYS Open Knowledge Format bundle.

The generator is intentionally conservative:
- it uses wiki pages as the preferred source of synthesis;
- it records repository/code pointers instead of copying source code;
- it does not read secrets or arbitrary environment files;
- it preserves unknown frontmatter keys when regenerating existing concepts.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VAULT_ROOT = Path(__file__).resolve().parents[2]
ESSENSYS_ROOT = Path(os.environ.get("ESSENSYS_ROOT", VAULT_ROOT.parent))
OKF = VAULT_ROOT / "okf"
WIKI = VAULT_ROOT / "wiki"
INVENTORY = VAULT_ROOT / "output" / "okf-repository-inventory.json"
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
DATE = TIMESTAMP[:10]

GENERATED = "<!-- BEGIN GENERATED CONTENT -->"
END_GENERATED = "<!-- END GENERATED CONTENT -->"

LAYER_LABELS = {
    "firmware": "Firmware / armoire",
    "legacy": "Legacy",
    "gateway-lan": "Gateway / LAN",
    "cloud": "Cloud / portails",
    "infra": "Infrastructure",
    "documentation": "Documentation / mémoire",
    "tooling": "Outillage",
    "system": "Système",
}

SPECIAL_DESCRIPTIONS = {
    "essensys-server-frontend": "Interface web LAN React/TypeScript pour piloter la domotique via le backend local.",
    "essensys-user-portal-frontend": "Portail cloud React/TypeScript pour l'accès distant utilisateur sur mon.essensys.fr.",
    "essensys-server-backend": "Backend Go LAN qui expose l'API moderne et maintient la compatibilité legacy IoT.",
    "essensys-user-portal-backend": "Backend Go cloud/OVH pour portail distant, relais gateway et expansion d'ordres.",
    "essensys-memory": "Mémoire persistante ESSENSYS, wiki Obsidian et bundle OKF agent-friendly.",
    "client-essensys-legacy": "Client embarqué legacy BP_MQX_ETH compatible protocole HTTP historique.",
    "essensys-web-legacy": "Application web legacy ASP.NET MVC/Web API de la plateforme historique.",
}

BOARD_ROLES = {
    "essensys-board-SC944D": ("SC944D", "Carte maître de l'armoire : agrège l'état, dialogue serveur et orchestre les échanges."),
    "essensys-board-SC940": ("SC940", "Carte actionneurs pièce de vie : lampes, variateurs, volets et sorties domotiques."),
    "essensys-board-SC941C": ("SC941C", "Carte actionneurs pièce d'eau : éclairage, volets et périphériques zone PDE."),
    "essensys-board-SC942C": ("SC942C", "Carte actionneurs chambres : relais, lampes, volets et variateurs."),
    "essensys-board-SC945D": ("SC945D", "Écran / IHM tactile mural, consommateur de la table d'échange côté utilisateur."),
    "essensys-board-SC946D": ("SC946D", "Carte sirène d'alarme et génération sonore d'alerte."),
    "essensys-board-SC947-xB": ("SC947-xB", "Détecteur de fuite d'eau autonome relié à l'écosystème armoire."),
    "essensys-board-SC840B": ("SC840B", "Banc de test usine pour cartes actionneurs."),
    "essensys-board-SC841A": ("SC841A", "Banc de test usine pour cartes BP et fonctions d'armoire."),
    "essensys-board-SC843D": ("SC843D", "Module gradateur / dimmer d'éclairage."),
}

PORTALS = [
    {
        "slug": "lan-local-portal",
        "title": "LAN Local Portal",
        "description": "Portail local gateway pour pilotage domotique sur le LAN.",
        "repos": ["essensys-server-frontend", "essensys-server-backend", "essensys-control-plane"],
        "audience": "Utilisateur local, installateur, admin LAN",
        "deployment": "Gateway locale Raspberry/CM5",
        "roadmap": ["essensys-lan-iam-2026-06.017", "essensys-lan-mcu-panels-2026-06.025", "essensys-install-wizard-2026-06.016"],
    },
    {
        "slug": "cloud-user-portal",
        "title": "Cloud User Portal",
        "description": "Portail distant utilisateur sur mon.essensys.fr.",
        "repos": ["essensys-user-portal-frontend", "essensys-user-portal-backend"],
        "audience": "Utilisateur distant",
        "deployment": "OVH / mon.essensys.fr",
        "roadmap": ["essensys-remote-user-interface-2026-06.015", "essensys-cloud-sync-scheduler"],
    },
    {
        "slug": "support-site",
        "title": "Support Site",
        "description": "Portail de support et documentation publique ESSENSYS.",
        "repos": ["essensys-support-site"],
        "audience": "Clients, support, communauté",
        "deployment": "OVH public",
        "roadmap": ["essensys-doc-site", "essensys-doc-site-dns-2026-06.008"],
    },
    {
        "slug": "documentation-site",
        "title": "Documentation Site",
        "description": "Site central de documentation technique et utilisateur.",
        "repos": ["essensys-doc", "essensys-memory"],
        "audience": "Développeurs, installateurs, agents IA",
        "deployment": "Docusaurus/MkDocs selon change roadmap",
        "roadmap": ["essensys-doc-docusaurus-2026-06.021", "essensys-centralized-doc-maintenance"],
    },
    {
        "slug": "roadmap-site",
        "title": "Roadmap Site",
        "description": "Publication publique de la roadmap OpenSpec ESSENSYS.",
        "repos": ["essensys-memory"],
        "audience": "Équipe projet, agents, décideurs",
        "deployment": "Site statique public",
        "roadmap": ["essensys-roadmap-site-2026-06.005", "essensys-roadmap-queue-2026-06"],
    },
    {
        "slug": "admin-surfaces",
        "title": "Admin Surfaces",
        "description": "Surfaces d'administration utilisateurs, sécurité et installation.",
        "repos": ["essensys-server-frontend", "essensys-user-portal-frontend", "essensys-server-backend", "essensys-user-portal-backend"],
        "audience": "Administrateurs ESSENSYS et installateurs",
        "deployment": "LAN + Cloud",
        "roadmap": ["essensys-admin-user-forbid-delete-2026-06-027", "essensys-trusted-devices-2026-06.013"],
    },
    {
        "slug": "gateway-install-control",
        "title": "Gateway Install Control",
        "description": "Surfaces et playbooks de provisioning, installation et contrôle gateway.",
        "repos": ["essensys-raspberry-install", "essensys-raspberry-gateway", "essensys-ansible"],
        "audience": "Installateurs, ops, agents déploiement",
        "deployment": "Gateway locale + Ansible",
        "roadmap": ["essensys-gateway-nixos", "essensys-gateway-fleet-2026-06.019", "essensys-gateway-recovery-2026-06.018"],
    },
]


def slug_title(name: str) -> str:
    return " ".join(w.capitalize() for w in re.sub(r"[^A-Za-z0-9]+", " ", name).split())


def repo_to_wiki_file(name: str) -> Path:
    return WIKI / "entities" / f"{name.lower()}.md"


def read_first_paragraph(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    lines = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("|") or line.startswith("---"):
            if lines:
                break
            continue
        if line.strip().startswith(">"):
            return line.strip().lstrip("> ")[:220]
        lines.append(line.strip())
        if len(" ".join(lines)) > 220:
            break
    return (" ".join(lines) or fallback)[:260]


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, text[end + 5 :]


def frontmatter(data: dict[str, Any], existing: dict[str, str] | None = None) -> str:
    merged: dict[str, Any] = {}
    if existing:
        for k, v in existing.items():
            if k not in data:
                merged[k] = v
    merged.update(data)
    lines = ["---"]
    for k, v in merged.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            sv = str(v)
            if any(ch in sv for ch in [": ", "#", "[", "]", "{", "}"]):
                sv = json.dumps(sv, ensure_ascii=False)
            lines.append(f"{k}: {sv}")
    lines.append("---\n")
    return "\n".join(lines)


def write_concept(path: Path, fm: dict[str, Any], body: str) -> None:
    existing_fm: dict[str, str] = {}
    if path.exists():
        existing_fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter(fm, existing_fm) + body.rstrip() + "\n", encoding="utf-8")


def md_list(items: list[str]) -> str:
    return "\n".join(f"* {i}" for i in items) if items else "* TBD"


def load_inventory() -> dict[str, Any]:
    if not INVENTORY.exists():
        raise SystemExit(f"Missing {INVENTORY}; run discover_repositories.py first")
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


def repo_body(repo: dict[str, Any]) -> str:
    name = repo["name"]
    title = slug_title(name)
    wiki = repo_to_wiki_file(name)
    description = SPECIAL_DESCRIPTIONS.get(name) or read_first_paragraph(wiki, f"Dépôt ESSENSYS {title}.")
    layer = repo["layer"]
    era = repo["era"]
    pointers = [f"`{name}/{p}`" for p in repo.get("pointers", [])[:24]]
    rels = []
    if name == "essensys-server-frontend":
        rels += ["UI twin de [Essensys User Portal Frontend](/systems/essensys-user-portal-frontend.md).", "Consomme [Essensys Server Backend](/systems/essensys-server-backend.md)."]
    if name == "essensys-user-portal-frontend":
        rels += ["UI twin de [Essensys Server Frontend](/systems/essensys-server-frontend.md).", "Consomme [Essensys User Portal Backend](/systems/essensys-user-portal-backend.md)."]
    if name == "essensys-server-backend":
        rels += ["Backend twin de [Essensys User Portal Backend](/systems/essensys-user-portal-backend.md).", "Implémente [Legacy HTTP](/protocols/legacy-http.md) et [Table D Echange](/protocols/table-d-echange.md)."]
    if name == "essensys-user-portal-backend":
        rels += ["Backend twin de [Essensys Server Backend](/systems/essensys-server-backend.md).", "Relais cloud connecté au portail distant."]
    if name in BOARD_ROLES:
        rels += ["Détaillé dans [architecture armoire](/synthesis/armoire-architecture.md).", "Lié à [Table D Echange](/protocols/table-d-echange.md)."]
    if layer == "firmware":
        rels += ["Contraintes legacy : compatibilité firmware et non-régression protocolaire."]
    citation = f"../../wiki/entities/{wiki.name}" if wiki.exists() else "../../output/okf-repository-inventory.json"
    return f"""{GENERATED}
# Rôle

{description}

# Interfaces

* Couche : {LAYER_LABELS.get(layer, layer)}.
* Era : {era}.
* Dépôt local : `{name}`.
{md_list(rels) if rels else '* Interfaces détaillées à compléter lors d’un approfondissement ciblé.'}

# Dépendances

{md_list(rels)}

# Code pointers

{md_list(pointers)}

# Risques

* Ne pas inférer de changement fonctionnel depuis cette fiche : elle décrit l'état et les contrats connus.
* Toute zone legacy ou protocolaire doit être vérifiée contre firmware + backend avant modification.

# Citations

[1] [Inventory](../../output/okf-repository-inventory.json)
[2] [Wiki source]({citation})
{END_GENERATED}
"""


def generate_repositories(inventory: dict[str, Any]) -> list[str]:
    covered = []
    for repo in inventory["repositories"]:
        name = repo["name"]
        title = slug_title(name)
        wiki = repo_to_wiki_file(name)
        description = SPECIAL_DESCRIPTIONS.get(name) or read_first_paragraph(wiki, f"Dépôt ESSENSYS {title}.")
        write_concept(
            OKF / "systems" / f"{name}.md",
            {
                "type": "Repository",
                "title": title,
                "description": description,
                "resource": f"file://{ESSENSYS_ROOT / name}",
                "tags": ["essensys", "repository", repo["layer"], repo["era"]],
                "timestamp": TIMESTAMP,
                "repo": name,
                "layer": repo["layer"],
                "era": repo["era"],
                "source_wiki": f"../../wiki/entities/{wiki.name}" if wiki.exists() else None,
            },
            repo_body(repo),
        )
        covered.append(name)
    return covered


def generate_firmware(inventory: dict[str, Any]) -> list[str]:
    created = []
    for repo in inventory["repositories"]:
        if repo["name"] not in BOARD_ROLES:
            continue
        board, role = BOARD_ROLES[repo["name"]]
        slug = board.lower().replace("-", "-")
        wiki = repo_to_wiki_file(repo["name"])
        pointers = [f"`{repo['name']}/{p}`" for p in repo.get("pointers", [])]
        body = f"""{GENERATED}
# Rôle

{role}

# Position dans l'armoire

* [SC944D](/firmware/sc944d.md) joue le rôle de maître quand la fiche existe.
* Les cartes actionneurs et IHM participent à l'état partagé via [Table D Echange](/protocols/table-d-echange.md).
* Les backends modernes doivent préserver la compatibilité avec le comportement firmware legacy.

# Interfaces

* Dépôt : [{slug_title(repo['name'])}](/systems/{repo['name']}.md)
* Architecture : [Armoire Architecture](/synthesis/armoire-architecture.md)
* Protocole : [Legacy HTTP](/protocols/legacy-http.md) selon implication firmware.

# Code pointers

{md_list(pointers)}

# Risques

* Compatibilité firmware et protocole à préserver.
* Vérifier les constantes d'indices avant toute modification affectant scénarios, alarmes, lumières ou volets.

# Citations

[1] [Repository concept](/systems/{repo['name']}.md)
[2] [Wiki source](../../wiki/entities/{wiki.name})
{END_GENERATED}
"""
        write_concept(
            OKF / "firmware" / f"{slug}.md",
            {
                "type": "Firmware Board",
                "title": f"Essensys Board {board}",
                "description": role,
                "resource": f"file://{ESSENSYS_ROOT / repo['name']}",
                "tags": ["essensys", "firmware", "armoire", "legacy"],
                "timestamp": TIMESTAMP,
                "repo": repo["name"],
                "layer": "firmware",
                "era": "legacy",
            },
            body,
        )
        created.append(slug)
    return created


def generate_protocols() -> None:
    table_wiki = WIKI / "concepts" / "table-d-echange.md"
    dual_wiki = WIKI / "concepts" / "dual-protocol.md"
    write_concept(
        OKF / "protocols" / "table-d-echange.md",
        {
            "type": "Protocol Contract",
            "title": "Table D Echange",
            "description": "Contrat k/v armoire ↔ serveur au cœur du dialogue firmware, backend, écran et cloud.",
            "tags": ["essensys", "protocol", "firmware", "legacy", "armoire"],
            "timestamp": TIMESTAMP,
            "era": "migration",
            "source_wiki": "../../wiki/concepts/table-d-echange.md",
        },
        f"""{GENERATED}
# Rôle

La Table d'Échange est le contrat central armoire ↔ serveur : paires `k` (indice) / `v` (valeur) partagées entre firmware, écran, backends et interfaces.

# Indices critiques

| Indice | Sémantique |
|---|---|
| `590` | Trigger scénario : `0` aucun, `1` serveur / Mode B, `2`-`8` slots mémorisés / Mode A |
| `591-919` | Scénarios mémorisés, 8 slots × 41 octets |
| `605-610` | Masques éteindre éclairage PDV / CHB / PDE |
| `611-616` | Masques allumer éclairage PDV / CHB / PDE |
| `617-622` | Ouvrir / fermer volets par zone |
| `409-411` | État et contrôle alarme |
| `566-589` | Temps de course volets propagés vers cloud/gateway |

# Règles d'action

* `_de67f` doit rester en premier dans la réponse `/api/myactions` pour l'alarme chiffrée AES ou `null`.
* Les actions lumière/volet doivent envoyer le bloc complet `605-622` avec `590="1"` pour préserver le comportement firmware.
* Les actions multiples sur un même index fusionnent par OR bitwise.
* Les chemins web/backend et cloud doivent rester cohérents avec firmware et écran IHM.

# Mappings multi-repos

* Firmware maître : `essensys-board-SC944D/.../TableEchange.h`.
* Client legacy : `client-essensys-legacy/H/TableEchange.h`.
* Écran IHM : `IHM_ECHANGES.INC` dans [SC945D](/firmware/sc945d.md) quand disponible.
* Backend LAN : `essensys-server-backend/pkg/protocol/constants.go`, `internal/core/action_service.go`.
* Cloud twin : `essensys-user-portal-backend/internal/domain/order_expansion.go`.

# Risques

* Toute renumérotation ou changement de sémantique doit être propagé firmware + écran + serveur + portail cloud.
* Les contradictions entre sources doivent être conservées dans le rapport de couverture, pas masquées.

# Citations

[1] [Wiki source](../../wiki/concepts/table-d-echange.md)
[2] [Dual Protocol](/protocols/dual-protocol.md)
{END_GENERATED}
""",
    )
    write_concept(
        OKF / "protocols" / "legacy-http.md",
        {
            "type": "Protocol Contract",
            "title": "Legacy HTTP",
            "description": "Contrat HTTP historique entre firmware/client embarqué ESSENSYS et backend compatible.",
            "tags": ["essensys", "legacy", "http", "firmware", "compatibility"],
            "timestamp": TIMESTAMP,
            "era": "legacy",
        },
        f"""{GENERATED}
# Rôle

Legacy HTTP est le protocole historique figé utilisé par les clients embarqués ESSENSYS, notamment BP_MQX_ETH / SC944D, pour dialoguer avec le serveur.

# Endpoints gelés

| Endpoint | Rôle |
|---|---|
| `/api/serverinfos` | Informations serveur nécessaires au client embarqué |
| `/api/mystatus` | Remontée état armoire / client |
| `/api/myactions` | Récupération des actions pending côté firmware |
| `/api/done/{{guid}}` | Acquittement d'une action traitée |

# Particularités wire

* JSON non standard pouvant nécessiter normalisation.
* `Content-Type` historique avec forme non canonique.
* Basic Auth côté legacy.
* Payload alarme chiffré AES via `_de67f`.
* Réponse single-packet TCP à préserver.
* Flux critique : injection web/MCP/cloud → pending actions → `/api/myactions` → firmware → `/api/done/{{guid}}`.

# Compatibilité

Ces endpoints sont compatibility-critical. Ils ne doivent pas être modernisés, renommés ou reformattés sans campagne explicite de tests firmware et régression legacy.

# Liens

* [Table D Echange](/protocols/table-d-echange.md)
* [Dual Protocol](/protocols/dual-protocol.md)
* [Client Essensys Legacy](/systems/client-essensys-legacy.md)
* [Essensys Server Backend](/systems/essensys-server-backend.md)

# Citations

[1] [Dual Protocol wiki](../../wiki/concepts/dual-protocol.md)
[2] [Table D Echange wiki](../../wiki/concepts/table-d-echange.md)
{END_GENERATED}
""",
    )
    write_concept(
        OKF / "protocols" / "dual-protocol.md",
        {
            "type": "Architecture Pattern",
            "title": "Dual Protocol",
            "description": "Coexistence du protocole HTTP legacy IoT et de l'API REST moderne.",
            "tags": ["essensys", "protocol", "backend", "legacy", "modern"],
            "timestamp": TIMESTAMP,
            "source_wiki": "../../wiki/concepts/dual-protocol.md",
        },
        f"""{GENERATED}
# Rôle

Le Dual Protocol impose aux backends ESSENSYS de servir simultanément le protocole legacy IoT et les APIs REST modernes.

# Contrats

* Legacy IoT : endpoints figés, wire quirks, compatibilité firmware et [Table D Echange](/protocols/table-d-echange.md).
* Moderne : REST/JSON, sessions/JWT, APIs utilisateur, admin et gateway.

# Risque

Tout changement backend doit vérifier les deux chemins. Une amélioration REST ne doit pas casser le firmware legacy.

# Citations

[1] [Wiki source](../../wiki/concepts/dual-protocol.md)
[2] [Legacy HTTP](/protocols/legacy-http.md)
{END_GENERATED}
""",
    )


def generate_synthesis() -> None:
    board_links = [f"[{board}](/firmware/{board.lower()}.md)" for _, (board, _) in BOARD_ROLES.items()]
    write_concept(
        OKF / "synthesis" / "armoire-architecture.md",
        {
            "type": "Architecture Overview",
            "title": "Armoire Architecture",
            "description": "Vue OKF de l'architecture armoire ESSENSYS : cartes, firmware, table d'échange et protocoles.",
            "tags": ["essensys", "architecture", "armoire", "firmware", "legacy"],
            "timestamp": TIMESTAMP,
        },
        f"""{GENERATED}
# Vue d'ensemble

L'armoire ESSENSYS combine une carte maître, des cartes actionneurs, une IHM, des modules alarme/détection et des bancs de test. Elle dialogue avec les couches serveur par [Legacy HTTP](/protocols/legacy-http.md) et partage son état via [Table D Echange](/protocols/table-d-echange.md).

# Cartes

{md_list(board_links)}

# Flux architecture

```text
Utilisateur / portail → backend LAN/cloud → pending actions → Legacy HTTP → SC944D / armoire → Table d'Échange → cartes + IHM
```

# Contraintes

* Préserver les endpoints legacy et le format attendu par firmware.
* Vérifier les index table d'échange avant changement métier.
* Synchroniser les backends twins et UI twins pour éviter les dérives LAN/cloud.

# Citations

[1] [Platform Overview wiki](../../wiki/synthesis/platform-overview.md)
[2] [Table D Echange wiki](../../wiki/concepts/table-d-echange.md)
{END_GENERATED}
""",
    )


def generate_roadmap() -> int:
    changes_dir = WIKI / "roadmap" / "changes"
    count = 0
    for p in sorted(changes_dir.glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        fm, body = parse_frontmatter(text)
        title_m = re.search(r"^#\s+(.+)$", body, re.M)
        title = title_m.group(1).strip() if title_m else slug_title(p.stem)
        status = fm.get("status", "TBD")
        host = fm.get("host_repo", "TBD")
        year = "2026" if "2026" in p.stem or "2026" in text else ("2025" if "2025" in p.stem or "2025" in text else "TBD")
        desc = read_first_paragraph(p, f"Roadmap OpenSpec {title}.")
        body_out = f"""{GENERATED}
# Rôle

{desc}

# État roadmap

| Champ | Valeur |
|---|---|
| Statut | {status} |
| Dépôt hôte | {host} |
| Horizon année | {year} |
| Source | `wiki/roadmap/changes/{p.name}` |

# Liens architecture

* [Feature Lifecycle](/processes/feature-lifecycle.md)
* [ESSENSYS Platform Overview](/synthesis/platform-overview.md)

# Citations

[1] [Roadmap source](../../wiki/roadmap/changes/{p.name})
{END_GENERATED}
"""
        write_concept(
            OKF / "roadmap" / f"{p.stem}.md",
            {
                "type": "Roadmap Change",
                "title": title,
                "description": desc[:180],
                "tags": ["essensys", "roadmap", "openspec", status, year],
                "timestamp": TIMESTAMP,
                "status": status,
                "host_repo": host,
                "horizon_year": year,
            },
            body_out,
        )
        count += 1
    return count


def generate_portals() -> list[str]:
    slugs = []
    for portal in PORTALS:
        repo_links = [f"[{slug_title(r)}](/systems/{r}.md)" for r in portal["repos"]]
        roadmap_links = []
        for r in portal["roadmap"]:
            target = OKF / "roadmap" / f"{r}.md"
            if target.exists():
                roadmap_links.append(f"[{slug_title(r)}](/roadmap/{r}.md)")
            else:
                roadmap_links.append(f"{r} (source à vérifier)")
        write_concept(
            OKF / "portals" / f"{portal['slug']}.md",
            {
                "type": "Portal",
                "title": portal["title"],
                "description": portal["description"],
                "tags": ["essensys", "portal", "2025", "2026"],
                "timestamp": TIMESTAMP,
                "deployment": portal["deployment"],
                "horizon_year": "2025/2026",
            },
            f"""{GENERATED}
# Rôle

{portal['description']}

# Audience et déploiement

| Champ | Valeur |
|---|---|
| Audience | {portal['audience']} |
| Déploiement | {portal['deployment']} |
| Horizon | 2025/2026 lorsque sourcé par roadmap, sinon TBD par item |

# Dépôts

{md_list(repo_links)}

# Roadmap liée

{md_list(roadmap_links)}

# APIs et sécurité

* Les portails LAN/cloud doivent respecter [Dual Protocol](/protocols/dual-protocol.md) quand ils touchent les chemins backend.
* Les surfaces admin/utilisateur doivent rester alignées avec [Feature Lifecycle](/processes/feature-lifecycle.md) et les gates sécurité.
* Les états de déploiement doivent rester source-backed ; tout état non sourcé est un gap à remonter.

# Citations

[1] [Roadmap index](../../wiki/roadmap/index.md)
[2] [Platform overview](../../wiki/synthesis/platform-overview.md)
{END_GENERATED}
""",
        )
        slugs.append(portal["slug"])
    return slugs


def generate_processes() -> None:
    # keep richer process pages synced with OKF tree if they already exist
    fl = WIKI / "concepts" / "feature-lifecycle.md"
    write_concept(
        OKF / "processes" / "feature-lifecycle.md",
        {
            "type": "Process",
            "title": "Feature Lifecycle",
            "description": "Chaîne Jira SCRUM → OpenSpec → Git/CI → docs → déploiement.",
            "tags": ["essensys", "process", "jira", "openspec", "ci"],
            "timestamp": TIMESTAMP,
            "source_wiki": "../../wiki/concepts/feature-lifecycle.md",
        },
        f"""{GENERATED}
# Rôle

Le lifecycle ESSENSYS relie idée, Jira SCRUM, OpenSpec, issues/tâches, commits/PR, tests, gates sécurité, documentation, et déploiements local + OVH.

# Obligations

* OpenSpec décrit les changements.
* Les manifests `features/<id>.json` sont source de vérité quand présents.
* Les gates sécurité sont bloquants par défaut.
* Les docs et la mémoire doivent être mises à jour continuellement.

# Citations

[1] [Wiki source](../../wiki/concepts/feature-lifecycle.md)
{END_GENERATED}
""",
    )


def write_indexes(counts: dict[str, int]) -> None:
    sections = {
        "systems": "actifs, dépôts et services structurants de la plateforme ESSENSYS",
        "firmware": "cartes armoire, firmware et contraintes embarquées",
        "protocols": "contrats legacy, table d'échange et protocoles",
        "roadmap": "changes OpenSpec et roadmap 2025/2026",
        "portals": "portails LAN, cloud, support, documentation, roadmap et admin",
        "processes": "processus lifecycle, sécurité, installation et déploiement",
        "synthesis": "vues transverses et architectures synthétiques",
        "references": "sources externes et formats",
    }
    root_lines = ["---", 'okf_version: "0.1"', "---", "", "# ESSENSYS Open Knowledge Format Memory", ""]
    for d, desc in sections.items():
        root_lines.append(f"* [{slug_title(d)}]({d}/) - {desc} ({counts.get(d, 0)} concepts).")
    root_lines += ["", "# Entry Points", "", "* [Armoire Architecture](synthesis/armoire-architecture.md) - architecture armoire, cartes et flux legacy.", "* [Table D Echange](protocols/table-d-echange.md) - contrat k/v firmware ↔ serveur.", "* [Legacy HTTP](protocols/legacy-http.md) - endpoints historiques gelés.", "* [Repository Inventory](systems/) - fiches de tous les dépôts ESSENSYS."]
    (OKF / "index.md").write_text("\n".join(root_lines) + "\n", encoding="utf-8")

    for d in sections:
        dirp = OKF / d
        dirp.mkdir(parents=True, exist_ok=True)
        lines = [f"# {slug_title(d)}", ""]
        for p in sorted(dirp.glob("*.md")):
            if p.name in {"index.md", "log.md"}:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            fm, _ = parse_frontmatter(text)
            title = fm.get("title", slug_title(p.stem)).strip('"')
            desc = fm.get("description", "OKF concept").strip('"')
            lines.append(f"* [{title}]({p.name}) - {desc}")
        (dirp / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_logs_and_wiki() -> None:
    log = OKF / "log.md"
    existing = log.read_text(encoding="utf-8") if log.exists() else "# OKF Bundle Update Log\n"
    entry = f"\n## {DATE}\n* **Update**: Applied `essensys-okf-discovery-2026-06-029`; generated repository, firmware, protocol, roadmap, portal, process and synthesis concepts.\n"
    if "essensys-okf-discovery-2026-06-029" not in existing:
        log.write_text(existing.rstrip() + entry, encoding="utf-8")
    wiki_log = WIKI / "log.md"
    if wiki_log.exists():
        wt = wiki_log.read_text(encoding="utf-8")
        wentry = f"\n## [{DATE}] update | OKF discovery applied\nGénération de la base OKF complète pour `essensys-okf-discovery-2026-06-029` : dépôts, armoire, protocoles legacy, roadmap, portails et rapport de couverture.\n"
        if "OKF discovery applied" not in wt:
            wiki_log.write_text(wt.rstrip() + wentry, encoding="utf-8")


def main() -> int:
    inventory = load_inventory()
    covered = generate_repositories(inventory)
    firmware = generate_firmware(inventory)
    generate_protocols()
    generate_synthesis()
    generate_processes()
    roadmap_count = generate_roadmap()
    portals = generate_portals()
    counts = {}
    for d in ["systems", "firmware", "protocols", "roadmap", "portals", "processes", "synthesis", "references"]:
        counts[d] = len([p for p in (OKF / d).glob("*.md") if p.name not in {"index.md", "log.md"}])
    write_indexes(counts)
    update_logs_and_wiki()
    summary = {
        "generated": TIMESTAMP,
        "repositories_covered": covered,
        "repository_count": len(covered),
        "firmware_concepts": firmware,
        "roadmap_count": roadmap_count,
        "portals": portals,
        "concept_counts": counts,
    }
    out = VAULT_ROOT / "output" / "okf-generation-summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
