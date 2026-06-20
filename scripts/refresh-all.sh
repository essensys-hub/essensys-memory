#!/usr/bin/env bash
# Full brain refresh: sync, timeline, roadmap, qmd index, lint
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export ESSENSYS_ROOT="${ESSENSYS_ROOT:-$(cd "$VAULT_ROOT/.." && pwd)}"

echo "=== ESSENSYS-BRAIN refresh ===" >&2
echo "ESSENSYS_ROOT=$ESSENSYS_ROOT" >&2

"$SCRIPT_DIR/sync-sources.sh"
"$SCRIPT_DIR/sync-protocol-docs.sh"
"$SCRIPT_DIR/extract-git-history.sh"
"$SCRIPT_DIR/update-roadmap.sh"

if command -v qmd &>/dev/null; then
  "$SCRIPT_DIR/index-qmd.sh"
else
  echo "WARN: qmd not installed — skip index" >&2
fi

python3 "$SCRIPT_DIR/lint-wiki.py"

echo "=== Refresh complete ===" >&2
