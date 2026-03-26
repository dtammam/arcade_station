# Close out the feature, commit, push, create a PR, and optionally walk through a release.

## What this does

Invokes the engineering-manager agent to:
1. Set the feature stage to "done" in `.state/feature-state.json`
2. Move the exec plan from `docs/exec-plans/active/` to `docs/exec-plans/completed/`
3. Update CLAUDE.md's "Active work" section
4. Summarize: what was built, artifacts produced, any tech debt created
5. Reset the state file to `{}` for the next feature

Then the main session will:
6. Stage, commit, and push all changes
7. Create a pull request targeting `main`
8. Ask the user if they want to tag a release

## Input

$ARGUMENTS is not typically needed.

## Procedure

1. Invoke the engineering-manager agent with this instruction:

   "Run the Done stage ONLY. Mark the feature as complete: update the
   state file, move the exec plan to completed, update CLAUDE.md's
   active work section. Summarize what was built. Do NOT remind the
   user about committing — that will be handled automatically."

2. Relay the engineering-manager's summary to the user.

3. After the EM finishes, automatically run the commit + push + PR flow:
   - Run `git status` and `git diff` to see all changes
   - Stage all relevant files by explicit path (not `git add .`)
   - Commit with a descriptive message using HEREDOC format and co-author trailer
   - Push to origin
   - Create a pull request targeting `main` using `gh pr create`

4. After the PR is created, ask the user:

   "Would you like to tag a release? If yes, provide the version (e.g., v1.2.0)
   and I'll create the tag and push it — the release workflow will build
   binaries and create a GitHub Release automatically."

   If yes: run `git tag <version>` and `git push origin <version>`.
   If no: done.

---

## ▶ WHAT HAPPENS

This command handles everything end-to-end: archive → commit → push → PR → optional release.

## ✅ WHEN DONE

The feature is closed. The PR is open. Merge when ready. Run **`/kickoff`** to start the next feature.

---

## Rules

- Only run this after `/accept` has passed.
- If tech debt was created during implementation, it must be recorded in
  `docs/exec-plans/tech-debt-tracker.md` before closing.
- Never use `--no-verify`. Never force-push.
- If the commit fails, stop and fix the root cause.
