# Safely stage and commit without pushing. All quality gates enforced.

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

5. If the commit fails (e.g., pre-commit hook), fix the root cause and retry.
   Never use `--no-verify`.

## Rules

- Do NOT push. This is commit-only.
- Do NOT use `git add .` or `git add -A`.
- Do NOT use `--no-verify` or `--no-gpg-sign`.
- Stop on failure. Do not retry blindly.
