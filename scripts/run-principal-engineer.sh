#!/usr/bin/env bash
set -euo pipefail

AGENT="principal-engineer"
INBOX=".state/inbox/${AGENT}.md"

if [[ ! -f "$INBOX" ]] || [[ ! -s "$INBOX" ]]; then
  echo "Error: ${INBOX} does not exist or is empty."
  echo "Run the appropriate slash command in Session 1 first (e.g. /design)."
  exit 1
fi

exec claude --dangerously-skip-permissions --agent "$AGENT" "@${INBOX}"
