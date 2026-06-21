#!/usr/bin/env bash
# Update wiki/roadmap/ from raw/openspec-index/manifest.json
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ESSENSYS_ROOT="${ESSENSYS_ROOT:-$(cd "$VAULT_ROOT/.." && pwd)}"
MANIFEST="$VAULT_ROOT/raw/openspec-index/manifest.json"
ROADMAP_DIR="$VAULT_ROOT/wiki/roadmap"
CHANGES_DIR="$ROADMAP_DIR/changes"
INDEX="$ROADMAP_DIR/index.md"
DATE="$(date +%Y-%m-%d)"

if [[ ! -f "$MANIFEST" ]]; then
  echo "ERROR: $MANIFEST not found — run scripts/sync-sources.sh first" >&2
  exit 1
fi

mkdir -p "$CHANGES_DIR"

export VAULT_ROOT ESSENSYS_ROOT DATE MANIFEST CHANGES_DIR INDEX
python3 << 'PYEOF'
import json, os, re

vault_root = os.environ["VAULT_ROOT"]
essensys_root = os.environ["ESSENSYS_ROOT"]
date = os.environ["DATE"]
manifest_path = os.environ["MANIFEST"]
changes_dir = os.environ["CHANGES_DIR"]
index_path = os.environ["INDEX"]

with open(manifest_path) as f:
    manifest = json.load(f)

def slug_to_title(name):
    return " ".join(w.capitalize() for w in name.replace("-", " ").split())

def read_excerpt(proposal_path, lines=5):
    if not os.path.isfile(proposal_path):
        return "_No proposal yet_"
    with open(proposal_path) as f:
        content = f.read()
    # Skip frontmatter-like headers, get first paragraph after ## Why
    m = re.search(r"## Why\s*\n+(.*?)(?:\n##|\Z)", content, re.DOTALL)
    if m:
        text = m.group(1).strip()
        return text[:500] + ("…" if len(text) > 500 else "")
    return content.strip()[:300] + "…"

def infer_status(artifacts, change_dir):
    tasks_path = os.path.join(change_dir, "tasks.md")
    if os.path.isfile(tasks_path):
        with open(tasks_path) as f:
            content = f.read()
        unchecked = content.count("- [ ]")
        checked = content.count("- [x]")
        if unchecked == 0 and checked > 0:
            return "completed"
        if checked > 0:
            return "active"
    if artifacts.get("proposal"):
        return "active"
    return "planned"

active, planned, completed = [], [], []

for entry in manifest.get("changes", []):
    change = entry["change"]
    repo = entry["repo"]
    rel = entry["path"]
    change_dir = os.path.join(essensys_root, rel)
    artifacts = entry.get("artifacts", {})
    status = infer_status(artifacts, change_dir)

    proposal_path = os.path.join(change_dir, "proposal.md")
    excerpt = read_excerpt(proposal_path)

    page_path = os.path.join(changes_dir, f"{change}.md")
    repo_entity = f"[[{slug_to_title(repo)}]]" if repo != "essensys-memory" else "[[ESSENSYS Memory]]"

    with open(page_path, "w") as f:
        f.write("---\n")
        f.write(f"tags: [roadmap, openspec]\n")
        f.write(f"sources: [manifest.json]\n")
        f.write(f"created: {entry.get('created') or date}\n")
        f.write(f"updated: {date}\n")
        f.write(f"status: {status}\n")
        f.write(f"host_repo: {repo}\n")
        f.write("---\n\n")
        f.write(f"# {slug_to_title(change)}\n\n")
        f.write(f"**Host repo:** {repo_entity}\n")
        f.write(f"**Path:** `{rel}`\n")
        f.write(f"**Status:** {status}\n")
        f.write(f"**OpenSpec created:** {entry.get('created', '—')}\n\n")
        f.write("## Why\n\n")
        f.write(excerpt + "\n\n")
        f.write("## Artifacts\n\n")
        f.write(f"- Proposal: {'✓' if artifacts.get('proposal') else '—'}\n")
        f.write(f"- Design: {'✓' if artifacts.get('design') else '—'}\n")
        f.write(f"- Tasks: {'✓' if artifacts.get('tasks') else '—'}\n")
        f.write(f"- Specs: {artifacts.get('spec_count', 0)}\n\n")
        f.write("## Source files\n\n")
        for fname in ["proposal.md", "design.md", "tasks.md"]:
            src = os.path.join(rel, fname)
            if os.path.isfile(os.path.join(essensys_root, src)):
                f.write(f"- `{src}`\n")

    item = f"- [[{slug_to_title(change)}]] — {repo} ({status})"
    if status == "completed":
        completed.append(item)
    elif status == "active":
        active.append(item)
    else:
        planned.append(item)

with open(index_path, "w") as f:
    f.write("---\n")
    f.write("tags: [roadmap, openspec, index]\n")
    f.write(f"updated: {date}\n")
    f.write("---\n\n")
    f.write("# Roadmap OpenSpec\n\n")
    f.write("Index des changes OpenSpec connus du monorepo ESSENSYS. ")
    f.write("Regénérer via `scripts/update-roadmap.sh` après sync.\n\n")
    f.write(f"**Dernière mise à jour:** {date} · **Changes:** {len(manifest.get('changes', []))}\n\n")
    f.write("## Active\n\n")
    f.write("\n".join(active) if active else "_Aucun_\n")
    f.write("\n\n## Planned\n\n")
    f.write("\n".join(planned) if planned else "_Aucun_\n")
    f.write("\n\n## Completed\n\n")
    f.write("\n".join(completed) if completed else "_Aucun_\n")
    f.write("\n\n## Roadmap produit\n\n")
    f.write("- [[Product Roadmap Rubric]] — découpage phases, gate Phase 0 doc/install\n")
    f.write("- [[Product Roadmap]] — priorités Now / Next / Later (`wiki/synthesis/product-roadmap.md`)\n")
    f.write("\n")

print(f"Updated {len(manifest.get('changes', []))} change pages + index", flush=True)
PYEOF

LOG_FILE="$VAULT_ROOT/wiki/log.md"
{
  echo ""
  echo "## [$DATE] roadmap | OpenSpec index updated"
  echo "Regenerated \`wiki/roadmap/index.md\` and change pages from manifest."
} >> "$LOG_FILE"

echo "Done." >&2
