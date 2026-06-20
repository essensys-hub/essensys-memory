#!/usr/bin/env bash
# Install post-merge git hook in essensys-memory to refresh brain after pull/merge
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK="$VAULT_ROOT/.git/hooks/post-merge"

if [[ ! -d "$VAULT_ROOT/.git" ]]; then
  echo "ERROR: not a git repo: $VAULT_ROOT" >&2
  exit 1
fi

cat > "$HOOK" << 'HOOKEOF'
#!/usr/bin/env bash
# ESSENSYS-BRAIN — refresh timeline after merge/pull (fast path)
VAULT_ROOT="$(git rev-parse --show-toplevel)"
export ESSENSYS_ROOT="${ESSENSYS_ROOT:-$(cd "$VAULT_ROOT/.." && pwd)}"
if [[ -x "$VAULT_ROOT/scripts/extract-git-history.sh" ]]; then
  "$VAULT_ROOT/scripts/extract-git-history.sh" >/dev/null 2>&1 || true
fi
HOOKEOF

chmod +x "$HOOK"
echo "Installed post-merge hook → $HOOK"
echo "For full refresh after local work: ./scripts/refresh-all.sh"
