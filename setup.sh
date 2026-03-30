#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Agent Pack Installer
# ============================================================================
# Installs the Claude Code agent framework into the current (or specified) repo.
#
# Usage:
#   ./setup.sh                  # install into current directory
#   ./setup.sh /path/to/repo    # install into specified repo
#
# What it does:
#   1. Copies agent definitions, commands, scripts, VS Code tasks, state files
#   2. Creates template docs if they don't exist (won't overwrite)
#   3. Installs git hooks (symlinks to hooks/ directory)
#   4. Makes scripts executable
#   5. Creates CLAUDE.md.template (you rename to CLAUDE.md and customize)
#
# What it does NOT do:
#   - Overwrite existing CLAUDE.md, docs/CONTRIBUTING.md, docs/ARCHITECTURE.md,
#     or docs/RELIABILITY.md — your project-specific content is preserved
#   - Install any runtime dependencies
#   - Modify your build system
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-.}"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: $TARGET_DIR is not a directory."
  exit 1
fi

# Resolve to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo "Installing agent-pack into: $TARGET_DIR"
echo ""

# --------------------------------------------------------------------------
# Helper: copy a directory, creating it if needed
# --------------------------------------------------------------------------
copy_dir() {
  local src="$1" dst="$2"
  mkdir -p "$dst"
  cp -r "$src"/* "$dst"/ 2>/dev/null || true
  # Also copy hidden files
  cp -r "$src"/.* "$dst"/ 2>/dev/null || true
}

# --------------------------------------------------------------------------
# Helper: copy file only if target doesn't exist (safe for user content)
# --------------------------------------------------------------------------
copy_if_missing() {
  local src="$1" dst="$2"
  if [[ -f "$dst" ]]; then
    echo "  SKIP (exists): $dst"
  else
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    echo "  CREATED: $dst"
  fi
}

# --------------------------------------------------------------------------
# 1. Agent definitions
# --------------------------------------------------------------------------
echo "[1/7] Agent definitions (.claude/agents/)"
mkdir -p "$TARGET_DIR/.claude/agents"
for f in "$SCRIPT_DIR/.claude/agents/"*.md; do
  fname="$(basename "$f")"
  cp "$f" "$TARGET_DIR/.claude/agents/$fname"
  echo "  INSTALLED: .claude/agents/$fname"
done

# --------------------------------------------------------------------------
# 2. Slash commands
# --------------------------------------------------------------------------
echo ""
echo "[2/7] Slash commands (.claude/commands/)"
mkdir -p "$TARGET_DIR/.claude/commands"
for f in "$SCRIPT_DIR/.claude/commands/"*.md; do
  fname="$(basename "$f")"
  cp "$f" "$TARGET_DIR/.claude/commands/$fname"
  echo "  INSTALLED: .claude/commands/$fname"
done

# --------------------------------------------------------------------------
# 3. CLI scripts for mobile workflow
# --------------------------------------------------------------------------
echo ""
echo "[3/7] CLI scripts (scripts/)"
mkdir -p "$TARGET_DIR/scripts"
for f in "$SCRIPT_DIR/scripts/"*.sh; do
  fname="$(basename "$f")"
  cp "$f" "$TARGET_DIR/scripts/$fname"
  chmod +x "$TARGET_DIR/scripts/$fname"
  echo "  INSTALLED: scripts/$fname"
done

# --------------------------------------------------------------------------
# 4. VS Code tasks
# --------------------------------------------------------------------------
echo ""
echo "[4/7] VS Code tasks (.vscode/tasks.json)"
if [[ -f "$TARGET_DIR/.vscode/tasks.json" ]]; then
  echo "  WARNING: .vscode/tasks.json already exists."
  echo "  Agent tasks saved to .vscode/tasks.agent-pack.json for manual merge."
  cp "$SCRIPT_DIR/.vscode/tasks.json" "$TARGET_DIR/.vscode/tasks.agent-pack.json"
else
  mkdir -p "$TARGET_DIR/.vscode"
  cp "$SCRIPT_DIR/.vscode/tasks.json" "$TARGET_DIR/.vscode/tasks.json"
  echo "  INSTALLED: .vscode/tasks.json"
fi

# --------------------------------------------------------------------------
# 5. State directory
# --------------------------------------------------------------------------
echo ""
echo "[5/7] State directory (.state/)"
mkdir -p "$TARGET_DIR/.state/inbox"
copy_if_missing "$SCRIPT_DIR/.state/feature-state.json" "$TARGET_DIR/.state/feature-state.json"
copy_if_missing "$SCRIPT_DIR/.state/inbox/.gitkeep" "$TARGET_DIR/.state/inbox/.gitkeep"
copy_if_missing "$SCRIPT_DIR/.state/.gitignore" "$TARGET_DIR/.state/.gitignore"

# --------------------------------------------------------------------------
# 6. Template docs (won't overwrite existing)
# --------------------------------------------------------------------------
echo ""
echo "[6/7] Template docs (docs/)"
mkdir -p "$TARGET_DIR/docs/exec-plans/active"
mkdir -p "$TARGET_DIR/docs/exec-plans/completed"
copy_if_missing "$SCRIPT_DIR/docs/index.md" "$TARGET_DIR/docs/index.md"
copy_if_missing "$SCRIPT_DIR/docs/CONTRIBUTING.md" "$TARGET_DIR/docs/CONTRIBUTING.md"
copy_if_missing "$SCRIPT_DIR/docs/ARCHITECTURE.md" "$TARGET_DIR/docs/ARCHITECTURE.md"
copy_if_missing "$SCRIPT_DIR/docs/RELIABILITY.md" "$TARGET_DIR/docs/RELIABILITY.md"
copy_if_missing "$SCRIPT_DIR/docs/exec-plans/tech-debt-tracker.md" "$TARGET_DIR/docs/exec-plans/tech-debt-tracker.md"
copy_if_missing "$SCRIPT_DIR/docs/exec-plans/active/.gitkeep" "$TARGET_DIR/docs/exec-plans/active/.gitkeep"
copy_if_missing "$SCRIPT_DIR/docs/exec-plans/completed/.gitkeep" "$TARGET_DIR/docs/exec-plans/completed/.gitkeep"

# --------------------------------------------------------------------------
# 7. Git hooks
# --------------------------------------------------------------------------
echo ""
echo "[7/7] Git hooks"
mkdir -p "$TARGET_DIR/hooks"
for f in "$SCRIPT_DIR/hooks/"*; do
  fname="$(basename "$f")"
  cp "$f" "$TARGET_DIR/hooks/$fname"
  chmod +x "$TARGET_DIR/hooks/$fname"
  echo "  INSTALLED: hooks/$fname"
done

# Symlink hooks into .git/hooks if this is a git repo
if [[ -d "$TARGET_DIR/.git" ]]; then
  git -C "$TARGET_DIR" config core.hooksPath hooks
  echo "  CONFIGURED: git core.hooksPath -> hooks/"
else
  echo "  NOTE: Not a git repo — hooks installed but not linked. Run 'git config core.hooksPath hooks' after git init."
fi

# --------------------------------------------------------------------------
# CLAUDE.md template
# --------------------------------------------------------------------------
echo ""
if [[ -f "$TARGET_DIR/CLAUDE.md" ]]; then
  echo "CLAUDE.md already exists — template saved as CLAUDE.md.template"
  cp "$SCRIPT_DIR/CLAUDE.md.template" "$TARGET_DIR/CLAUDE.md.template"
else
  cp "$SCRIPT_DIR/CLAUDE.md.template" "$TARGET_DIR/CLAUDE.md"
  echo "CREATED: CLAUDE.md (from template — customize the TODO sections)"
fi

# --------------------------------------------------------------------------
# Done
# --------------------------------------------------------------------------
echo ""
echo "============================================"
echo "  Agent pack installed successfully!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Edit CLAUDE.md — fill in the TODO placeholders with your project's commands"
echo "  2. Edit docs/CONTRIBUTING.md — add your coding standards"
echo "  3. Edit docs/ARCHITECTURE.md — document your system design"
echo "  4. Edit docs/RELIABILITY.md — define performance budgets"
echo "  5. Edit hooks/pre-commit and hooks/pre-push — add your quality checks"
echo "  6. Run: /kickoff <your feature description>"
echo ""
echo "See SEED.md for the full onboarding process."
echo "See README.md for agent framework documentation."
