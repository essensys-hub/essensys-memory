#!/usr/bin/env python3
"""Ingest raw/architecture/repos/*.md into wiki/entities/*.md"""
import os
import re
import glob
from datetime import date

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(VAULT, "raw", "architecture", "repos")
ENT_DIR = os.path.join(VAULT, "wiki", "entities")
INDEX = os.path.join(VAULT, "wiki", "index.md")
LOG = os.path.join(VAULT, "wiki", "log.md")
TODAY = str(date.today())

LEGACY_REPOS = {
    "client-essensys-legacy", "essensys-web-legacy",
    "essensys-board-SC944D", "essensys-board-SC945D",
}
MODERN_REPOS = {
    "essensys-server-backend", "essensys-server-frontend",
    "essensys-user-portal-backend", "essensys-user-portal-frontend",
    "essensys-raspberry-gateway", "essensys-control-plane",
}
MIGRATION_REPOS = {
    "essensys-raspberry-install", "essensys-ansible",
    "essensys-support-site", "essensys-homeassitant",
}


def repo_to_title(name: str) -> str:
    parts = name.replace("-", " ").split()
    return " ".join(p.upper() if len(p) <= 3 and p.isalpha() else p.capitalize() for p in parts)


def infer_era(repo: str, content: str) -> str:
    if repo in LEGACY_REPOS or "legacy" in content.lower()[:800]:
        if repo in MIGRATION_REPOS:
            return "migration"
        if "legacy" in content.lower()[:500] or repo in LEGACY_REPOS:
            return "legacy"
    if repo in MODERN_REPOS:
        return "modern"
    if repo in MIGRATION_REPOS:
        return "migration"
    if "stub" in content.lower()[:600]:
        return "modern"
    if "firmware" in content.lower()[:400] or "board" in repo:
        return "legacy" if "legacy" in content.lower() else "modern"
    return "modern"


def extract_field(content: str, label: str) -> str:
    m = re.search(rf"\*\*{re.escape(label)} :\*\*\s*(.+)", content)
    return m.group(1).strip() if m else ""


def extract_blockquote(content: str) -> str:
    m = re.search(r"^> (.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def extract_section(content: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, content, re.DOTALL)
    return m.group(1).strip() if m else ""


def infer_tags(repo: str, category: str, era: str) -> list:
    tags = ["entity", "repo"]
    if era:
        tags.append(era)
    cat = category.lower()
    if "firmware" in cat or "board" in repo:
        tags.extend(["firmware", "hardware"])
    elif "backend" in cat or "backend" in repo:
        tags.append("backend")
    elif "frontend" in cat or "frontend" in repo:
        tags.append("frontend")
    elif "infra" in cat or repo in ("essensys-ansible", "essensys-nginx", "essensys-traefik"):
        tags.append("infra")
    elif "legacy" in cat:
        tags.append("legacy")
    elif "outillage" in cat or "ia" in cat:
        tags.append("tooling")
    return list(dict.fromkeys(tags))


def related_links(repo: str) -> list:
    links = ["[[Platform Overview]]"]
    related = {
        "essensys-server-backend": ["[[Dual Protocol]]", "[[Table D Echange]]", "[[Essensys Server Frontend]]", "[[Essensys Redis]]"],
        "essensys-server-frontend": ["[[Essensys Server Backend]]", "[[Table D Echange]]"],
        "essensys-user-portal-backend": ["[[Cloud Relay]]", "[[Essensys User Portal Frontend]]", "[[Essensys Server Backend]]"],
        "essensys-user-portal-frontend": ["[[Essensys User Portal Backend]]", "[[Essensys Server Frontend]]"],
        "essensys-raspberry-gateway": ["[[Essensys Raspberry Install]]", "[[Essensys Gateway Dual Nic]]", "[[Client Essensys Legacy]]"],
        "client-essensys-legacy": ["[[Dual Protocol]]", "[[Table D Echange]]", "[[Essensys Web Legacy]]", "[[Essensys Server Backend]]"],
        "essensys-web-legacy": ["[[Client Essensys Legacy]]", "[[Migration Legacy To Modern]]"],
        "essensys-board-SC944D": ["[[Table D Echange]]", "[[Essensys Board SC945D]]", "[[Client Essensys Legacy]]"],
        "essensys-board-SC945D": ["[[Table D Echange]]", "[[Essensys Board SC944D]]"],
        "essensys-memory": ["[[Roadmap OpenSpec]]", "[[Essensys Second Brain]]"],
        "essensys-mcp": ["[[Essensys Memory]]", "[[Essensys Server Backend]]"],
    }
    return related.get(repo, links)


def convert_wikilinks_in_text(text: str) -> str:
    def repl(m):
        path = m.group(1)
        if path.startswith("repos/"):
            name = path.replace("repos/", "").replace(".md", "")
            return f"[[{repo_to_title(name)}]]"
        return m.group(0)
    return re.sub(r"`([^`]+\.md)`", repl, text)


def ingest_repo(src_path: str) -> tuple[str, str]:
    repo = os.path.basename(src_path).replace(".md", "")
    with open(src_path) as f:
        content = f.read()

    title = repo_to_title(repo)
    blockquote = extract_blockquote(content)
    category = extract_field(content, "Catégorie")
    stack = extract_field(content, "Stack")
    status = extract_field(content, "Statut")
    era = infer_era(repo, content)
    tags = infer_tags(repo, category, era)

    role = extract_section(content, "Rôle dans l'architecture Essensys")
    attention = extract_section(content, "Points d'attention")
    structure = extract_section(content, "Structure du dépôt")
    integrations = extract_section(content, "Intégrations")

    # Truncate long sections
    def trunc(s, n=2000):
        return s[:n] + "\n\n_… voir source complète dans raw/_" if len(s) > n else s

    related = related_links(repo)
    related_md = "\n".join(f"- {l}" for l in related)

    out = f"""---
tags: [{", ".join(tags)}]
sources: [{repo}.md]
created: {TODAY}
updated: {TODAY}
era: {era}
repo: {repo}
---

# {title}

> {blockquote}

| | |
|---|---|
| **Catégorie** | {category or "—"} |
| **Stack** | {stack or "—"} |
| **Statut** | {status or "—"} |
| **Era** | {era} |

## Rôle

{convert_wikilinks_in_text(trunc(role, 1500)) if role else "_Voir fiche architecture._"}

## Intégrations

{convert_wikilinks_in_text(trunc(integrations, 1200)) if integrations else "_Non documenté._"}

## Structure

{trunc(structure, 800) if structure else "_Voir dépôt source._"}

## Points d'attention

{convert_wikilinks_in_text(trunc(attention, 1200)) if attention else "_Aucun point notable._"}

## Liens

{related_md}

## Source

`raw/architecture/repos/{repo}.md`
"""
    out_path = os.path.join(ENT_DIR, f"{repo}.md")
    with open(out_path, "w") as f:
        f.write(out)
    return repo, title


def update_index(entries: list[tuple[str, str, str]]):
    """entries: (repo, title, one_line_summary)"""
    with open(os.path.join(VAULT, "raw", "architecture", "README.md")) as f:
        arch_readme = f.read()

    entities_lines = []
    for repo, title, _ in sorted(entries, key=lambda x: x[0]):
        src = os.path.join(SRC_DIR, f"{repo}.md")
        with open(src) as f:
            bq = extract_blockquote(f.read())
        summary = bq[:110] + ("…" if len(bq) > 110 else "")
        entities_lines.append(f"- [[{title}]] — {summary}")

    concepts = """- [[Dual Protocol]] — deux protocoles HTTP legacy IoT vs REST moderne sur le backend Go
- [[Table D Echange]] — contrat k/v armoire ↔ serveur, propagation firmware/écran/cloud
- [[Cloud Relay]] — pilotage distant cloud via polling sortant NAT traversal
- [[Gateway Exchange]] — endpoints /api/gateway/exchange et pending-actions"""

    synthesis = """- [[Platform Overview]] — vue d'ensemble domotique Essensys (4 couches, 40 dépôts)
- [[Migration Legacy To Modern]] — migration ASP.NET/MQX → Go/React/Raspberry"""

    roadmap = "- [[Roadmap OpenSpec]] — index des changes OpenSpec (gateway, brain, …)"

    index = f"""# Index

Master catalog of all wiki pages. Updated on every ingest.

## Sources

- [[Architecture README]] — vue d'ensemble 40 dépôts (`raw/architecture/README.md`)
- [[Migration Plan Source]] — plan migration legacy (`raw/plans/MIGRATION_PLAN.md`)

## Entities

{chr(10).join(entities_lines)}

## Concepts

{concepts}

## Synthesis

{synthesis}

## Roadmap

{roadmap}

## Timeline

Historique Git par dépôt dans `wiki/timeline/` (regénérer via `scripts/extract-git-history.sh`).
"""
    with open(INDEX, "w") as f:
        f.write(index)


def main():
    os.makedirs(ENT_DIR, exist_ok=True)
    entries = []
    for src in sorted(glob.glob(os.path.join(SRC_DIR, "*.md"))):
        repo, title = ingest_repo(src)
        entries.append((repo, title, ""))
        print(f"  {repo} → wiki/entities/{repo}.md")

    update_index(entries)

    with open(LOG, "a") as f:
        f.write(f"\n## [{TODAY}] ingest | Phase 2 architecture repos\n")
        f.write(f"Ingested {len(entries)} repo fiches from `raw/architecture/repos/` → `wiki/entities/`.\n")

    print(f"\nDone: {len(entries)} entities, index updated.")


if __name__ == "__main__":
    main()
