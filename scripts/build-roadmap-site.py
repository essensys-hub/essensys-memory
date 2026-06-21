#!/usr/bin/env python3
"""Generate static roadmap site from OpenSpec manifest + change proposals."""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
ESSENSYS_ROOT = Path(os.environ.get("ESSENSYS_ROOT", VAULT.parent))
MANIFEST = VAULT / "raw/openspec-index/manifest.json"
OUT = VAULT / "content/roadmap/site"


def slug_to_title(name: str) -> str:
    return " ".join(w.capitalize() for w in name.replace("-", " ").split())


def infer_status(change_dir: Path) -> str:
    tasks = change_dir / "tasks.md"
    if not tasks.is_file():
        return "planned"
    text = tasks.read_text()
    unchecked = text.count("- [ ]")
    checked = text.count("- [x]")
    if unchecked == 0 and checked > 0:
        return "completed"
    if checked > 0:
        return "active"
    return "planned"


def read_why(proposal: Path) -> str:
    if not proposal.is_file():
        return "_Pas de proposal._"
    m = re.search(r"## Why\s*\n+(.*?)(?:\n##|\Z)", proposal.read_text(), re.DOTALL)
    if not m:
        return "_—_"
    return m.group(1).strip()[:800]


def roadmap_id_from_yaml(change_dir: Path) -> str:
    y = change_dir / ".openspec.yaml"
    if y.is_file():
        m = re.search(r"roadmap_id:\s*(\S+)", y.read_text())
        if m:
            return m.group(1)
    return ""


def page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(title)} — Essensys Roadmap</title>
  <link rel="stylesheet" href="/style.css"/>
</head>
<body>
  <header><a href="/">← Roadmap Essensys</a></header>
  <main>{body}</main>
  <footer><p>Source : essensys-memory OpenSpec — généré automatiquement</p></footer>
</body>
</html>"""


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    entries = []
    for e in manifest.get("changes", []):
        change = e["change"]
        rel = e["path"]
        change_dir = ESSENSYS_ROOT / rel
        rid = roadmap_id_from_yaml(change_dir)
        status = infer_status(change_dir)
        why = read_why(change_dir / "proposal.md")
        entries.append({
            "change": change,
            "title": slug_to_title(change),
            "roadmap_id": rid,
            "status": status,
            "repo": e.get("repo", "essensys-memory"),
            "why": why,
        })

    def sort_key(x):
        rid = x["roadmap_id"] or "9999"
        return rid

    entries.sort(key=sort_key)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "style.css").write_text("""
body { font-family: system-ui, sans-serif; max-width: 960px; margin: 0 auto; padding: 1rem 1.5rem; line-height: 1.5; color: #1a1a1a; }
header { margin-bottom: 1.5rem; padding-bottom: .5rem; border-bottom: 1px solid #ddd; }
header a { color: #0d9488; text-decoration: none; font-weight: 600; }
h1 { color: #0f766e; }
h2 { margin-top: 2rem; color: #115e59; }
table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
th, td { text-align: left; padding: .5rem .75rem; border-bottom: 1px solid #e5e7eb; }
.badge { display: inline-block; padding: .15rem .5rem; border-radius: 4px; font-size: .85rem; font-weight: 600; }
.badge-active { background: #fef3c7; color: #92400e; }
.badge-completed { background: #d1fae5; color: #065f46; }
.badge-planned { background: #e0e7ff; color: #3730a3; }
.change-detail pre { white-space: pre-wrap; background: #f9fafb; padding: 1rem; border-radius: 6px; }
footer { margin-top: 3rem; font-size: .85rem; color: #6b7280; }
""")

    for status in ("active", "completed", "planned"):
        section = [e for e in entries if e["status"] == status]
        if not section:
            continue
        for e in section:
            slug = e["change"]
            body = f"""<h1>{html.escape(e['title'])}</h1>
<p><span class="badge badge-{status}">{status}</span>
{f' · ID <strong>{html.escape(e["roadmap_id"])}</strong>' if e['roadmap_id'] else ''}</p>
<p><strong>Dépôt :</strong> {html.escape(e['repo'])}</p>
<h2>Pourquoi</h2>
<div class="change-detail"><pre>{html.escape(e['why'])}</pre></div>
"""
            (OUT / f"{slug}.html").write_text(page(e["title"], body))

    def row(e):
        st = e["status"]
        rid = e["roadmap_id"] or "—"
        return f'<tr><td>{html.escape(rid)}</td><td><a href="/{html.escape(e["change"])}.html">{html.escape(e["title"])}</a></td><td><span class="badge badge-{st}">{st}</span></td></tr>'

    sections = ""
    labels = {"active": "En cours", "completed": "Terminés", "planned": "À venir"}
    for status in ("active", "completed", "planned"):
        rows = [e for e in entries if e["status"] == status]
        if not rows:
            continue
        sections += f"<h2>{labels[status]}</h2><table><thead><tr><th>ID</th><th>Change</th><th>Statut</th></tr></thead><tbody>"
        sections += "".join(row(e) for e in rows)
        sections += "</tbody></table>"

    index_body = f"<h1>Roadmap produit Essensys</h1><p>OpenSpec — changes publics (en cours, passés, à venir).</p>{sections}"
    (OUT / "index.html").write_text(page("Roadmap", index_body))
    print(f"build-roadmap-site: {len(entries)} changes → {OUT}")

if __name__ == "__main__":
    main()
