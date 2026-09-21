#!/usr/bin/env bash
# SessionStart hook — inject only git-derived and marker-derived facts, never
# stored state. Anything that can silently rot does not belong here.
set -uo pipefail

root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$root" || exit 0

branch="$(git branch --show-current 2>/dev/null || true)"
echo "Branch: ${branch:-(detached)}"

# Active plan(s) and their real status, read from the doc markers themselves.
# Spine files: flat active/*.md (legacy) + active/<slug>/plan.md (v2.1 directories).
# A plain glob is non-recursive and misses the directory shape — use find.
plans=()
while IFS= read -r p; do plans+=("$p"); done < <(
  { find docs/exec-plans/active -maxdepth 1 -type f -name '*.md' 2>/dev/null
    find docs/exec-plans/active -mindepth 2 -type f -name 'plan.md' 2>/dev/null; } | sort -u )
if [ "${#plans[@]}" -gt 0 ]; then
  echo "Active plans (${#plans[@]}):"
  for p in "${plans[@]}"; do
    name="$(basename "$p")"; [ "$name" = plan.md ] && name="$(basename "$(dirname "$p")")"
    status="$(grep -m1 '^status:' "$p" 2>/dev/null | sed 's/^status:[[:space:]]*//')"
    next="$(grep -m1 '^next:' "$p" 2>/dev/null | sed 's/^next:[[:space:]]*//')"
    echo "  - $name: ${status:-no status}${next:+ — next: $next}"
  done
fi

# Marker health — report, never block. Stale markers surface here first.
if [ -x .harness/lib/check-markers.sh ]; then
  .harness/lib/check-markers.sh docs/exec-plans 2>&1 | sed 's/^/  /' || true
fi
