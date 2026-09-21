#!/usr/bin/env bash
# check-markers.sh — enforce the state-as-document marker contract.
#
# Flags stale, misfiled, sha-less, merged-but-unreleased, and self-contradictory
# markers so document-state cannot rot silently. See lib/harness-markers.md.
#
# Usage:   check-markers.sh [plans_dir]     (default: docs/exec-plans)
# Exit:    0 = clean, 1 = issues found, 2 = usage/setup error.
#
# Scans a plan's SPINE only — flat `active/*.md` (legacy) and `<slug>/plan.md`
# (v2.1 directories) — never research/*.md or design.md siblings.
set -uo pipefail

PLANS_DIR="${1:-docs/exec-plans}"
ISSUES=0

command -v git >/dev/null 2>&1 || { echo "check-markers: git not found" >&2; exit 2; }
[ -d "$PLANS_DIR" ] || { echo "check-markers: no such directory: $PLANS_DIR" >&2; exit 2; }

flag() { printf '  ✗ %s: %s\n' "$1" "$3"; ISSUES=$((ISSUES + 1)); }

# The default branch, and a ref that reflects what's actually merged (prefer origin).
default_branch() {
  local d
  d="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@')"
  [ -n "$d" ] && { echo "$d"; return; }
  for c in main master; do git show-ref --verify --quiet "refs/heads/$c" && { echo "$c"; return; }; done
  echo main
}
DEFAULT="$(default_branch)"
if git show-ref --verify --quiet "refs/remotes/origin/$DEFAULT"; then DEFAULT_REF="origin/$DEFAULT"; else DEFAULT_REF="$DEFAULT"; fi

# One field from the YAML frontmatter (the block between the first two `---` lines),
# tolerating a leading comment line before the block. Body text is never matched.
fm_field() { # fm_field <file> <field>
  awk -v f="$2" 'BEGIN{n=0}
    /^---[[:space:]]*$/ { n++; if (n==2) exit; next }
    n==1 && $0 ~ ("^" f ":[[:space:]]*") { sub("^" f ":[[:space:]]*", ""); print; exit }' "$1"
}
is_shipped() { case "$1" in Shipped*|Abandoned*) return 0;; *) return 1;; esac; }   # belongs in completed/

# Spine files for a given active|completed dir: flat *.md + nested plan.md, no siblings.
spines() { # spines <active|completed>
  { find "$PLANS_DIR/$1" -maxdepth 1 -type f -name '*.md' 2>/dev/null
    find "$PLANS_DIR/$1" -mindepth 2 -type f -name 'plan.md' 2>/dev/null; } | sort -u
}

# ---- active plans -----------------------------------------------------------
while IFS= read -r file; do
  [ -f "$file" ] || continue
  status="$(fm_field "$file" status)"

  # 0. anchor enum: the frontmatter anchor must be outcome|spec|tdd (first token),
  #    so a misused field (e.g. "docs-and-content (slim gate)") can't ship clean.
  anchor="$(fm_field "$file" anchor)"
  case "${anchor%% *}" in
    ""|outcome|spec|tdd) : ;;
    *) flag "$file" "-" "invalid anchor '$anchor' — must be outcome|spec|tdd" ;;
  esac

  # 1. terminal status (frontmatter only — not prose) still under active/.
  if is_shipped "$status"; then
    flag "$file" "-" "terminal status '$status' still under active/ — move to completed/"
  fi

  # 2. bound approval markers: sha exists, and the reviewed CODE is unchanged
  #    since it (plans dir excluded so a plan's own bookkeeping never counts).
  while IFS= read -r line; do
    sha="$(printf '%s' "$line" | grep -oE '@[0-9a-f]{7,40}' | head -n1 | tr -d '@')"
    [ -n "$sha" ] || continue
    if ! git cat-file -e "${sha}^{commit}" 2>/dev/null; then
      flag "$file" "$line" "approval marker references unknown commit @$sha"; continue
    fi
    if ! git diff --quiet "$sha" -- . ":(exclude)$PLANS_DIR" 2>/dev/null; then
      flag "$file" "$line" "stale approval @$sha — reviewed code changed since; re-gate"
    fi
  done < <(grep -En '(Approved|APPROVED)[^@]*@[0-9a-f]{7,40}' "$file" 2>/dev/null || true)

  # 3. sha-less approvals.
  while IFS= read -r line; do
    printf '%s' "$line" | grep -qE '@[0-9a-f]{7,40}' && continue
    flag "$file" "$line" "approval marker has no @<sha> — bind it to the reviewed commit"
  done < <(grep -En '^[[:space:]]*(status|design):[[:space:]]*Approved|Gate:[[:space:]]*APPROVED' "$file" 2>/dev/null || true)

  # 4. merged but not released: the latest Gate: APPROVED @sha is already on the
  #    default branch, but status isn't terminal/parked → the work shipped and
  #    /release never ran. (Ancestor check; squash-merged shas won't resolve —
  #    that gap is covered by making /release the flow's mandatory close.)
  case "$status" in
    Shipped*|Abandoned*|Parked*) : ;;
    *)
      asha="$(grep -oE 'Gate:[[:space:]]*APPROVED[^@]*@[0-9a-f]{7,40}' "$file" | tail -1 | grep -oE '[0-9a-f]{7,40}' | tail -1)"
      if [ -n "${asha:-}" ] && git cat-file -e "${asha}^{commit}" 2>/dev/null \
         && git merge-base --is-ancestor "$asha" "$DEFAULT_REF" 2>/dev/null; then
        flag "$file" "-" "approved work @$asha is already in '$DEFAULT' but plan not Shipped — run /release"
      fi ;;
  esac
done < <(spines active)

# ---- completed plans: frozen, so no staleness — only self-consistency -------
while IFS= read -r file; do
  [ -f "$file" ] || continue
  status="$(fm_field "$file" status)"

  # A completed v2 plan must carry a terminal status. Legacy docs with no
  # frontmatter status are pre-v2 history and are skipped.
  if [ -n "$status" ] && ! is_shipped "$status"; then
    flag "$file" "-" "completed plan has non-terminal status '$status' — should be Shipped/Abandoned"
  fi

  # Frontmatter gate: must not contradict the last Gate: verdict in the body.
  fm_gate="$(fm_field "$file" gate)"
  last_gate="$(grep -oE 'Gate:[[:space:]]*(APPROVED|CHANGES)' "$file" | tail -1 | grep -oE 'APPROVED|CHANGES')"
  if [ -n "$last_gate" ] && [ -n "$fm_gate" ]; then
    case "$fm_gate" in
      *"$last_gate"*|*pending*) : ;;
      *) flag "$file" "-" "frontmatter 'gate: $fm_gate' contradicts the body's last verdict ($last_gate)" ;;
    esac
  fi
done < <(spines completed)

if [ "$ISSUES" -eq 0 ]; then
  echo "check-markers: clean ($PLANS_DIR)"
  exit 0
fi
echo "check-markers: $ISSUES issue(s) found" >&2
exit 1
