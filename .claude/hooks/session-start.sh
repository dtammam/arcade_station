#!/usr/bin/env bash
set -euo pipefail

# Inject repo context at the start of every Claude Code session.
# Must complete in <500ms — keep it fast.

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

# Active exec plans
ACTIVE_PLANS=""
if [ -d "docs/exec-plans/active" ]; then
  ACTIVE_PLANS=$(ls docs/exec-plans/active/*.md 2>/dev/null | xargs -I{} basename {} .md | paste -sd ", " - || echo "")
fi

# Tech debt count
DEBT_COUNT=0
if [ -f "docs/exec-plans/tech-debt-tracker.md" ]; then
  DEBT_COUNT=$(grep -c '^\- \[' docs/exec-plans/tech-debt-tracker.md 2>/dev/null || echo "0")
fi

# Feature state
STATE_FILE=".state/feature-state.json"
FEATURE="none"
STAGE=""
if [ -f "$STATE_FILE" ] && [ -s "$STATE_FILE" ]; then
  FEATURE=$(python3 -c "import json,sys; d=json.load(open('$STATE_FILE')); print(d.get('feature_name','none'))" 2>/dev/null || echo "none")
  STAGE=$(python3 -c "import json,sys; d=json.load(open('$STATE_FILE')); print(d.get('stage',''))" 2>/dev/null || echo "")
fi

cat <<EOF
## Session context (auto-injected)
- **Branch:** $BRANCH
- **Uncommitted changes:** $DIRTY file(s)
- **Active feature:** $FEATURE${STAGE:+ (stage: $STAGE)}
- **Active exec plans:**
EOF

if [ -n "$ACTIVE_PLANS" ]; then
  echo "$ACTIVE_PLANS" | tr ',' '\n' | while read -r plan; do
    plan=$(echo "$plan" | xargs)
    [ -n "$plan" ] && echo "  - \`$plan.md\`"
  done
else
  echo "  (none)"
fi

echo "- **Active tech debt items:** $DEBT_COUNT"
