# Safely commit and push to origin with all quality gates enforced.

## Input

$ARGUMENTS is the commit message. If empty, draft one from the diff.

## Procedure

1. Reject generic messages ("update", "fix", "changes").
2. Run `git status` and `git diff --staged` to understand changes.
3. Stage files explicitly by path (never `git add .` or `git add -A`).
4. Commit using HEREDOC format:

git commit -m "$(cat <<'EOF'
$ARGUMENTS

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

5. Push to origin: `git push -u origin <current-branch>`.
6. If any step fails, stop and report the error. Never force-push.

## Rules

- Do NOT use `git add .` or `git add -A`.
- Do NOT use `--no-verify`, `--no-gpg-sign`, or `--force`.
- Stop on failure. Do not retry blindly.
