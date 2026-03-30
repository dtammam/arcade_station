# Safely stage and commit without pushing. All quality gates enforced.

## Required input

- Commit message provided as $ARGUMENTS.
- Reject generic messages (update, fix, wip).
- If no message provided, ask for one.

## Workflow

1. Run git status and git diff to understand what will be staged.
2. Stage changes by file (prefer explicit paths over git add .).
3. Commit using HEREDOC format with co-author trailer.

## Failure handling

If the commit fails — stop. Do not retry blindly. Do not amend.
Read the error. Fix the root cause. Re-run from step 1.
Never use --no-verify.

If the same failure repeats, add it to docs/exec-plans/tech-debt-tracker.md.
