#!/usr/bin/env bash
# Index essensys-memory wiki with qmd for local semantic search
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COLLECTION="wiki"

cd "$VAULT_ROOT"

if ! command -v qmd &>/dev/null; then
  echo "ERROR: qmd not installed (npm i -g @tobilu/qmd)" >&2
  exit 1
fi

if [[ ! -f "$VAULT_ROOT/.qmd/index.sqlite" ]] && [[ ! -d "$VAULT_ROOT/.qmd" ]]; then
  qmd init >&2 2>/dev/null || qmd init >&2
fi

if ! qmd collection list 2>/dev/null | grep -q "^wiki\b"; then
  qmd collection add wiki "$COLLECTION" >&2 || qmd collection add wiki >&2
  echo "Added collection wiki" >&2
fi

qmd update -c "$COLLECTION" >&2

QMD_FORCE_CPU=1 qmd embed -c "$COLLECTION" 2>&1 || qmd embed -c "$COLLECTION" 2>&1 || echo "WARN: embed skipped" >&2

qmd status >&2
echo "qmd index ready. Search: qmd query -c $COLLECTION 'your question'" >&2
