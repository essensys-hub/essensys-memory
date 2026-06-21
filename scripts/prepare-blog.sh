#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ESSENSYS_ROOT="${ESSENSYS_ROOT:-$(cd "$VAULT_ROOT/.." && pwd)}"
SRC="$VAULT_ROOT/content/blog"
DEST="$ESSENSYS_ROOT/essensys-support-site/site/public/blog"
mkdir -p "$DEST"

python3 << PY
import json, re, shutil
from pathlib import Path

src = Path("$SRC")
dest = Path("$DEST")
posts = []
for fp in sorted(src.glob("*.md")):
    if fp.name == "README.md":
        continue
    text = fp.read_text()
    meta = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
            body = parts[2].strip()
    slug = fp.stem
    posts.append({
        "slug": slug,
        "title": meta.get("title", slug),
        "date": meta.get("date", ""),
        "roadmap_id": meta.get("roadmap_id", ""),
        "change": meta.get("change", ""),
        "tags": meta.get("tags", ""),
        "body": body,
    })
    shutil.copy2(fp, dest / fp.name)

(dest / "index.json").write_text(json.dumps({"posts": posts}, ensure_ascii=False, indent=2))
print(f"prepare-blog: {len(posts)} article(s) → {dest}")
PY
