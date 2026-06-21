#!/usr/bin/env bash
# Régénère les surfaces publiques roadmap + blog depuis la queue OpenSpec.
# Appelé après update-roadmap.sh et toute modification visible utilisateur.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ESSENSYS_ROOT="${ESSENSYS_ROOT:-$(cd "$VAULT_ROOT/.." && pwd)}"
DATE="$(date +%Y-%m-%d)"

export VAULT_ROOT ESSENSYS_ROOT DATE

echo "== publish-roadmap-public ($DATE) =="

cd "$VAULT_ROOT"
ESSENSYS_ROOT="$ESSENSYS_ROOT" ./scripts/update-roadmap.sh

if [[ -x "$SCRIPT_DIR/build-roadmap-site.sh" ]]; then
  "$SCRIPT_DIR/build-roadmap-site.sh"
else
  echo "WARN: build-roadmap-site.sh absent — copie snapshot queue (stub Phase 2)"
  mkdir -p content/roadmap/generated
  cp wiki/roadmap/openspec-queue-2026-06.md content/roadmap/generated/queue-snapshot.md
fi

if [[ -x "$SCRIPT_DIR/prepare-blog.sh" ]]; then
  "$SCRIPT_DIR/prepare-blog.sh"
else
  echo "WARN: prepare-blog.sh absent — blog non copié vers support-site (stub Phase 4)"
fi

python3 "$SCRIPT_DIR/lint-wiki.py"

echo ""
echo "DoD prod (après deploy Ansible / CI) :"
echo "  curl -sI https://roadmap.essensys.fr | head -1"
echo "  curl -sI https://mon.essensys.fr/blog | head -1"
echo "Done."
