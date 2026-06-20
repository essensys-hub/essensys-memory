#!/usr/bin/env bash
# Copy critical protocol/firmware docs into raw/protocol/ (immutable snapshots)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ESSENSYS_ROOT="${ESSENSYS_ROOT:-$(cd "$VAULT_ROOT/.." && pwd)}"
DST="$VAULT_ROOT/raw/protocol"
DATE="$(date +%Y-%m-%d)"
LOG="$VAULT_ROOT/wiki/log.md"

mkdir -p "$DST"

copy_if() {
  local src="$1" rel="$2"
  if [[ -f "$src" ]]; then
    mkdir -p "$(dirname "$DST/$rel")"
    cp "$src" "$DST/$rel"
    echo "  $rel" >&2
  fi
}

echo "Syncing protocol docs → raw/protocol/" >&2

copy_if "$ESSENSYS_ROOT/client-essensys-legacy/docs/protocol/exchange-table.md" "exchange-table.md"
copy_if "$ESSENSYS_ROOT/client-essensys-legacy/docs/protocol/http-legacy-protocol.md" "http-legacy-protocol.md"
copy_if "$ESSENSYS_ROOT/client-essensys-legacy/docs/protocol/tcp-single-packet.md" "tcp-single-packet.md"
copy_if "$ESSENSYS_ROOT/essensys-server-backend/docs/MCP_DEVICE_INDEX_REFERENCE.md" "mcp-device-index-reference.md"
copy_if "$ESSENSYS_ROOT/essensys-server-backend/docs/ARCHITECTURE_DUAL_PROTOCOL.md" "architecture-dual-protocol.md"
copy_if "$ESSENSYS_ROOT/essensys-server-backend/pkg/protocol/constants.go" "constants.go"

TABLE_H="$ESSENSYS_ROOT/essensys-board-SC944D/SC944D/Prog/099-37/BP_MQX_ETH/H/TableEchange.h"
copy_if "$TABLE_H" "TableEchange.h"

{
  echo ""
  echo "## [$DATE] sync | Protocol docs"
  echo "Copied legacy protocol + TableEchange.h + MCP index reference to \`raw/protocol/\`."
} >> "$LOG"

echo "Done." >&2
