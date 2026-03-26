#!/usr/bin/env bash
# setup.sh — Initialize the agent pack in a new or existing repo.
# Run from the project root after copying these files in.

set -euo pipefail

echo "=== Agent Pack Setup ==="

# Ensure we're in a git repo
if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "Not a git repo. Run 'git init' first."
  exit 1
fi

# Set hooks path
git config core.hooksPath hooks
echo "✓ Git hooks path set to hooks/"

# Make hooks executable
chmod +x hooks/pre-commit hooks/pre-push
echo "✓ Git hooks made executable"

# Make session-start hook executable
chmod +x .claude/hooks/session-start.sh
echo "✓ SessionStart hook made executable"

# Initialize state
mkdir -p .state/inbox
[ ! -f .state/feature-state.json ] && echo '{}' > .state/feature-state.json
touch .state/inbox/.gitkeep
echo "✓ State directory initialized"

# Verify structure
echo ""
echo "=== Verification ==="

CHECKS=(
  "CLAUDE.md"
  ".claude/agents/engineering-manager.md"
  ".claude/agents/product-manager.md"
  ".claude/agents/principal-engineer.md"
  ".claude/agents/software-developer.md"
  ".claude/agents/build-specialist.md"
  ".claude/agents/quality-assurance.md"
  ".claude/commands/commit-only.md"
  ".claude/commands/commit-and-push.md"
  ".claude/hooks/session-start.sh"
  ".claude/settings.json"
  ".state/feature-state.json"
  "docs/index.md"
  "docs/CONTRIBUTING.md"
  "docs/ARCHITECTURE.md"
  "docs/RELIABILITY.md"
  "docs/PLANS.md"
  "docs/exec-plans/tech-debt-tracker.md"
  "hooks/pre-commit"
  "hooks/pre-push"
)

PASS=0
FAIL=0

for f in "${CHECKS[@]}"; do
  if [ -e "$f" ]; then
    echo "  ✓ $f"
    PASS=$((PASS + 1))
  else
    echo "  ✗ $f — MISSING"
    FAIL=$((FAIL + 1))
  fi
done

echo ""
echo "$PASS passed, $FAIL failed"

if [ "$FAIL" -eq 0 ]; then
  echo ""
  echo "=== Ready ==="
  echo "Open Claude Code and describe a feature. The engineering-manager"
  echo "agent should activate and walk you through the pipeline."
  echo ""
  echo "All placeholders have been filled and hooks configured for Python."
  echo "Run '/kickoff' in Claude Code to start your first feature."
fi
