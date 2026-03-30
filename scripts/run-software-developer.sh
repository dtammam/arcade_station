#!/usr/bin/env bash
set -euo pipefail

AGENT="software-developer"
INBOX=".state/inbox/${AGENT}.md"

if [[ ! -f "$INBOX" ]] || [[ ! -s "$INBOX" ]]; then
  echo "Error: ${INBOX} does not exist or is empty."
  echo "Run the appropriate slash command in Session 1 first (e.g. /implement)."
  exit 1
fi

exec claude --dangerously-skip-permissions --agent "$AGENT" "@${INBOX}"
