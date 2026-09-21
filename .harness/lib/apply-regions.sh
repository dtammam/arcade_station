#!/usr/bin/env bash
# apply-regions.sh TEMPLATE [LOCAL]  ->  merged result on stdout
#
# The v2 update model (see lib/regions.md). Emits TEMPLATE, except that every
# `keep` region present in LOCAL is preserved verbatim from LOCAL. Harness-owned
# regions always come from TEMPLATE. No text merge, no checksums, no network.
#
#   - Fresh install (no LOCAL, or LOCAL has no region markers): TEMPLATE as-is.
#   - Update: harness regions refreshed from TEMPLATE; `keep` regions kept local.
#
# Region markers (comment style is ignored, only the tokens matter):
#   ... region:start id=<id>[ keep] ...
#   ... region:end id=<id> ...
set -uo pipefail

TEMPLATE="${1:-}"
LOCAL="${2:-}"

[ -n "$TEMPLATE" ] && [ -f "$TEMPLATE" ] || { echo "apply-regions: no template: $TEMPLATE" >&2; exit 2; }

# Fresh install, or a local file that isn't region-managed: template wins whole.
if [ -z "$LOCAL" ] || [ ! -f "$LOCAL" ] || ! grep -q 'region:start id=' "$LOCAL"; then
  cat "$TEMPLATE"
  exit 0
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# Pass 1 — extract LOCAL's keep-region bodies, one file per id.
awk -v dir="$tmp" '
  function id_of(s,   a){ sub(/.*id=/,"",s); split(s,a,/[ >]/); return a[1] }
  /region:start id=/ && /keep/ { cur=id_of($0); cap=1; next }
  /region:end id=/   { if (cap && id_of($0)==cur) { cap=0; cur="" }; next }
  cap { print >> (dir "/" cur) }
' "$LOCAL"

# Pass 2 — emit TEMPLATE; substitute LOCAL body inside any keep region we saved.
awk -v dir="$tmp" '
  function id_of(s,   a){ sub(/.*id=/,"",s); split(s,a,/[ >]/); return a[1] }
  /region:start id=/ {
    print
    cid=id_of($0)
    if ($0 ~ /keep/) {
      f=dir "/" cid; got=0
      while ((getline line < f) > 0) { print line; got=1 }
      close(f)
      if (got) { skip=1; skipid=cid }
    }
    next
  }
  /region:end id=/ { if (skip && id_of($0)==skipid) { skip=0; skipid="" }; print; next }
  skip { next }
  { print }
' "$TEMPLATE"
