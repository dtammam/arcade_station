#!/usr/bin/env bash
set -euo pipefail

AGENT="quality-assurance"
INBOX=".state/inbox/${AGENT}.md"

if [[ ! -f "$INBOX" ]] || [[ ! -s "$INBOX" ]]; then
  echo "Error: ${INBOX} does not exist or is empty."
  echo "Run the appropriate slash command in Session 1 first (e.g. /review)."
  exit 1
fi

exec claude --dangerously-skip-permissions --agent "$AGENT" "@${INBOX}"
