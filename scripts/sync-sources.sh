#!/usr/bin/env bash
# Sync architecture docs and OpenSpec manifest from ESSENSYS monorepo into raw/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ESSENSYS_ROOT="${ESSENSYS_ROOT:-$(cd "$VAULT_ROOT/.." && pwd)}"

ARCH_SRC="$ESSENSYS_ROOT/docs/architecture"
ARCH_DST="$VAULT_ROOT/raw/architecture"
MANIFEST_DIR="$VAULT_ROOT/raw/openspec-index"
MANIFEST_FILE="$MANIFEST_DIR/manifest.json"
LOG_FILE="$VAULT_ROOT/wiki/log.md"
DATE="$(date +%Y-%m-%d)"

echo "ESSENSYS_ROOT=$ESSENSYS_ROOT" >&2

# --- Architecture docs ---
if [[ ! -d "$ARCH_SRC" ]]; then
  echo "ERROR: $ARCH_SRC not found" >&2
  exit 1
fi

mkdir -p "$ARCH_DST"
rsync -a --delete "$ARCH_SRC/" "$ARCH_DST/"
echo "Synced architecture docs → raw/architecture/" >&2

# --- MIGRATION_PLAN.md ---
if [[ -f "$ESSENSYS_ROOT/MIGRATION_PLAN.md" ]]; then
  mkdir -p "$VAULT_ROOT/raw/plans"
  cp "$ESSENSYS_ROOT/MIGRATION_PLAN.md" "$VAULT_ROOT/raw/plans/MIGRATION_PLAN.md"
  echo "Copied MIGRATION_PLAN.md → raw/plans/" >&2
fi

# --- OpenSpec manifest ---
mkdir -p "$MANIFEST_DIR"

export ESSENSYS_ROOT VAULT_ROOT
python3 << 'PYEOF'
import json, os, glob, re
from datetime import date

essensys_root = os.environ["ESSENSYS_ROOT"]
vault_root = os.environ["VAULT_ROOT"]
changes = []

def parse_openspec_yaml(path):
    meta = {}
    try:
        with open(path) as f:
            for line in f:
                m = re.match(r"^(\w+):\s*(.+)$", line.strip())
                if m:
                    meta[m.group(1)] = m.group(2).strip()
    except Exception:
        pass
    return meta

for openspec_yaml in glob.glob(os.path.join(essensys_root, "*", "openspec", "changes", "*", ".openspec.yaml")):
    change_dir = os.path.dirname(openspec_yaml)
    change_name = os.path.basename(change_dir)
    repo = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(change_dir))))
    rel_path = os.path.relpath(change_dir, essensys_root)

    meta = parse_openspec_yaml(openspec_yaml)
    has_proposal = os.path.isfile(os.path.join(change_dir, "proposal.md"))
    has_design = os.path.isfile(os.path.join(change_dir, "design.md"))
    has_tasks = os.path.isfile(os.path.join(change_dir, "tasks.md"))

    spec_count = len(glob.glob(os.path.join(change_dir, "specs", "**", "spec.md"), recursive=True))

    changes.append({
        "change": change_name,
        "repo": repo,
        "path": rel_path,
        "created": str(meta.get("created", "")),
        "schema": meta.get("schema", "spec-driven"),
        "artifacts": {
            "proposal": has_proposal,
            "design": has_design,
            "tasks": has_tasks,
            "spec_count": spec_count,
        },
    })

changes.sort(key=lambda c: (c["repo"], c["change"]))
manifest = {
    "generated": str(date.today()),
    "essensys_root": essensys_root,
    "changes": changes,
}

out = os.path.join(vault_root, "raw", "openspec-index", "manifest.json")
with open(out, "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")
print(f"Wrote {len(changes)} OpenSpec changes → raw/openspec-index/manifest.json", flush=True)
PYEOF

# --- Log entry ---
mkdir -p "$(dirname "$LOG_FILE")"
{
  echo ""
  echo "## [$DATE] sync | Sources synchronized"
  echo "Architecture docs from \`docs/architecture/\` and OpenSpec manifest regenerated."
  echo "ESSENSYS_ROOT: \`$ESSENSYS_ROOT\`"
} >> "$LOG_FILE"

echo "Done." >&2
