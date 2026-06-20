#!/usr/bin/env bash
# Extract git commit history per repo into wiki/timeline/<repo>.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ESSENSYS_ROOT="${ESSENSYS_ROOT:-$(cd "$VAULT_ROOT/.." && pwd)}"
TIMELINE_DIR="$VAULT_ROOT/wiki/timeline"
COMMIT_LIMIT="${COMMIT_LIMIT:-100}"
DATE="$(date +%Y-%m-%d)"

mkdir -p "$TIMELINE_DIR"

count=0
for dir in "$ESSENSYS_ROOT"/*/; do
  repo_name="$(basename "$dir")"
  git_dir="$dir.git"

  if [[ ! -d "$git_dir" ]]; then
    continue
  fi

  out_file="$TIMELINE_DIR/${repo_name}.md"
  first_commit=""
  last_commit=""

  # Get repo metadata
  first_commit=$(git -C "$dir" log --reverse --format="%h %ad" --date=short 2>/dev/null | head -1 || true)
  last_commit=$(git -C "$dir" log -1 --format="%h %ad" --date=short 2>/dev/null || true)
  total=$(git -C "$dir" rev-list --count HEAD 2>/dev/null || echo "0")

  {
    echo "---"
    echo "tags: [timeline, git]"
    echo "repo: $repo_name"
    echo "updated: $DATE"
    echo "total_commits: $total"
    echo "shown_commits: $COMMIT_LIMIT"
    echo "---"
    echo ""
    echo "# Timeline — $repo_name"
    echo ""
    echo "**First commit:** ${first_commit:-unknown} · **Latest:** ${last_commit:-unknown} · **Total:** $total"
    echo ""
    echo "## Commits (newest first, limit $COMMIT_LIMIT)"
    echo ""

    git -C "$dir" log -"$COMMIT_LIMIT" \
      --format="- **%ad** \`%h\` — %s (%an)" \
      --date=short 2>/dev/null || echo "_No commits found_"
  } > "$out_file"

  echo "  $repo_name ($total commits)" >&2
  ((count++)) || true
done

# Log
LOG_FILE="$VAULT_ROOT/wiki/log.md"
{
  echo ""
  echo "## [$DATE] timeline | Git history extracted"
  echo "Generated $count timeline files in \`wiki/timeline/\` (limit=$COMMIT_LIMIT commits each)."
} >> "$LOG_FILE"

echo "Done: $count repos → wiki/timeline/" >&2
