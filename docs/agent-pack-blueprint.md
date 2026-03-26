# Agent Pack Blueprint

A reusable, multi-agent SDLC system for Claude Code. This document explains the architecture, how to implement it in a new project, and how to use it day-to-day.

## What this is

A set of Claude Code agents and slash commands that implement a full software development lifecycle (SDLC) inside your editor. Each stage of the lifecycle is handled by a specialist agent — a Product Manager gathers requirements, a Principal Engineer designs the solution, a Software Developer implements it, and so on.

The system is designed so that:
- **Every agent's output is directly visible to you** — no intermediary summaries
- **You control every stage transition** — nothing auto-progresses
- **Each agent runs in its own session** — isolated context, clean separation of concerns
- **State is tracked in a JSON file** — easy to inspect, debug, or reset

## Architecture

### Agents

| Agent | Role | Model | Tools |
|-------|------|-------|-------|
| **Engineering Manager** | State manager + router. Reads state, updates it, writes prompts for specialists, tells you what to run next. Never writes application code. | opus | Read, Write, Edit, Glob, Grep |
| **Product Manager** | Two modes: Discovery (gather requirements, write exec plan) and Acceptance (validate delivered work against criteria). | sonnet | Read, Write, Edit, Glob, Grep |
| **Principal Engineer** | Reads requirements + codebase, produces technical design (approach, risks, alternatives). Does not write implementation code. | opus | Read, Write, Edit, Glob, Grep, Bash |
| **Software Developer** | Implements ONE task at a time. Writes code + tests, runs quality checks, reports what changed. | sonnet | Read, Write, Edit, Bash, Glob, Grep |
| **Build Specialist** | Runs build, test, lint, format checks. Reports pass/fail. Never fixes code. | haiku | Read, Bash, Glob, Grep |
| **Quality Assurance** | Reviews code for correctness, security, performance, standards. Reports findings. Never fixes code. | sonnet | Read, Bash, Glob, Grep |

### Slash commands

Each command maps to one stage of the lifecycle:

| Command | Stage | What happens |
|---------|-------|-------------|
| `/kickoff` | Bootstrap | Initialize state, summarize project context |
| `/discover` | Discovery | Route to PM for requirements + exec plan |
| `/design` | Design | Route to PE for technical design |
| `/tasks` | Task breakdown | EM splits design into implementable tasks |
| `/implement` | Implementation | Route to SDE for ONE task |
| `/verify` | Verification | Route to build specialist for quality gates |
| `/review` | Code review | Route to QA for code review (optional) |
| `/accept` | Acceptance | Route to PM to validate acceptance criteria |
| `/done` | Closure | Archive, commit, push, create PR, optional release |
| `/commit-only` | Utility | Stage and commit |
| `/commit-and-push` | Utility | Stage, commit, push |

### Workflow

```
/kickoff → /discover → /design → /tasks → /implement → /verify → /accept → /done
                                              ↑            |
                                              └── (next) ──┘

Optional at any point: /review (code review)
```

### State management

All state lives in `.state/feature-state.json`:

```json
{
  "feature_id": "short-kebab-case-slug",
  "feature_name": "Human-readable feature name",
  "stage": "bootstrap|discovery|design|tasks|implementation|verification|acceptance|done",
  "created_at": "YYYY-MM-DD",
  "updated_at": "YYYY-MM-DD",
  "tasks": [
    {
      "id": 1,
      "title": "Task title",
      "description": "What to do",
      "files": ["file1.rs", "file2.rs"],
      "definition_of_done": "When X is true",
      "status": "pending|done"
    }
  ],
  "completed_tasks": [1, 2],
  "artifacts": {
    "requirements": "docs/exec-plans/active/YYYY-MM-DD-slug.md",
    "design": "docs/exec-plans/active/YYYY-MM-DD-slug.md",
    "exec_plan": "docs/exec-plans/active/YYYY-MM-DD-slug.md"
  },
  "history": [
    { "timestamp": "YYYY-MM-DD HH:MM", "stage": "bootstrap", "note": "Feature initiated" }
  ]
}
```

### Routing mechanism

The Engineering Manager doesn't invoke agents directly. Instead:

1. EM writes a self-contained prompt to `.state/inbox/<agent-name>.md`
2. EM tells you which VS Code task to run
3. You run the task via **Terminal → Run Task…**
4. The task spawns a fresh Claude Code session that reads the inbox file
5. The specialist works autonomously and outputs directly in your terminal

This keeps specialist output transparent and avoids context window pollution.

## How to implement in a new project

### Step 1: Copy the file structure

```
your-project/
├── .claude/
│   ├── agents/
│   │   ├── engineering-manager.md
│   │   ├── product-manager.md
│   │   ├── principal-engineer.md
│   │   ├── software-developer.md
│   │   ├── build-specialist.md
│   │   └── quality-assurance.md
│   ├── commands/
│   │   ├── kickoff.md
│   │   ├── discover.md
│   │   ├── design.md
│   │   ├── tasks.md
│   │   ├── implement.md
│   │   ├── verify.md
│   │   ├── review.md
│   │   ├── accept.md
│   │   ├── done.md
│   │   ├── commit-only.md
│   │   └── commit-and-push.md
│   └── hooks/
│       └── session-start.sh      (optional: context injector)
├── .vscode/
│   └── tasks.json
├── .state/
│   ├── feature-state.json        (initialized as {})
│   └── inbox/
│       └── .gitkeep
├── docs/
│   ├── exec-plans/
│   │   ├── active/               (current exec plans)
│   │   ├── completed/            (archived exec plans)
│   │   └── tech-debt-tracker.md
│   ├── ARCHITECTURE.md
│   ├── CONTRIBUTING.md
│   └── RELIABILITY.md            (optional: performance budgets)
└── CLAUDE.md
```

### Step 2: Configure your project

1. **CLAUDE.md** — Set up the main session instructions. The key section is the "What YOU do" block that tells the main session to route through the EM. Customize the reference docs, quality gates, and commands sections for your project's toolchain.

2. **`.gitignore`** — Add these lines:

   ```
   .state/feature-state.json
   .state/inbox/*.md
   !.state/inbox/.gitkeep
   ```

3. **`.vscode/tasks.json`** — The tasks file is generic. Just ensure `claude` is on your PATH. If you installed Claude Code elsewhere, update the command path.

4. **Agents** — The agents are project-agnostic. They read your project's `CONTRIBUTING.md`, `ARCHITECTURE.md`, and `RELIABILITY.md` to understand standards. Write those docs and the agents will follow them.

5. **Commands** — The commands are project-agnostic. No changes needed unless you want to customize the workflow (e.g., add a `/deploy` stage).

### Step 3: Write your project docs

The agents derive project-specific behavior from these docs:

| Doc | Purpose | Who reads it |
|-----|---------|-------------|
| `CONTRIBUTING.md` | Design principles, coding standards, quality gates | PM, PE, SDE, QA |
| `ARCHITECTURE.md` | System design, module layout, layer boundaries | PE, QA |
| `RELIABILITY.md` | Performance budgets, invariants, SLOs | PE, SDE, QA |

The better these docs are, the better the agents perform. Start with something minimal and iterate.

### Step 4: Initialize state

```sh
mkdir -p .state/inbox
echo '{}' > .state/feature-state.json
touch .state/inbox/.gitkeep
```

### Step 5: Optional — session-start hook

The `session-start.sh` hook injects context (branch, uncommitted changes, active feature) at the start of every conversation. Example:

```bash
#!/usr/bin/env bash
set -euo pipefail

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
UNCOMMITTED=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

STATE_FILE=".state/feature-state.json"
if [ -f "$STATE_FILE" ] && [ -s "$STATE_FILE" ]; then
  FEATURE=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('feature_name','none'))" 2>/dev/null || echo "none")
else
  FEATURE="none"
fi

cat <<EOF
## Session context (auto-injected)
- **Branch:** $BRANCH
- **Uncommitted changes:** $UNCOMMITTED file(s)
- **Active feature:** $FEATURE
EOF
```

Configure it in `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/session-start.sh" }
        ]
      }
    ]
  }
}
```

## How to use day-to-day

### Starting a feature

```
You: /kickoff Add dark mode support
     → Review summary
You: /discover
     → Run "Run Product Manager" task
     → PM writes exec plan
You: /design
     → Run "Run Principal Engineer" task
     → PE writes design
You: /tasks
     → Review task breakdown
```

### Implementing

```
You: /implement
     → Run "Run Software Developer" task
     → SDE implements task 1
You: /implement
     → Run "Run Software Developer" task
     → SDE implements task 2
You: /verify
     → Run "Run Build Specialist" task
     → All green
```

### Closing out

```
You: /review          (optional)
     → Run "Run Quality Assurance" task
You: /accept
     → Run "Run Product Manager" task
     → All criteria pass
You: /done
     → Archives plan, commits, pushes, creates PR
     → Asks about release tagging
```

### Tips

- **Skip stages for trivial changes.** If you're fixing a typo, you don't need the full pipeline. Use `/kickoff` → `/tasks` (with "keep it to one task") → `/implement` → `/done`.
- **Run `/review` when it matters.** It's optional but catches things the build specialist can't — logic errors, security issues, naming problems.
- **The state file is your friend.** If something gets confused, read `.state/feature-state.json` to see where things stand. You can edit it manually if needed.
- **Reset with `echo '{}' > .state/feature-state.json`** if you need a clean slate.
- **Each agent is independent.** If one fails or gives bad output, re-run just that VS Code task. You don't need to restart the whole pipeline.

## Design decisions

**Why VS Code tasks instead of direct agent invocation?**
Direct invocation would require the main session to relay all specialist output, polluting the context window and losing fidelity. VS Code tasks give each specialist its own terminal with full output visibility.

**Why one task per `/implement` invocation?**
Smaller units of work are easier to verify, review, and roll back. If a task fails, you know exactly what broke.

**Why separate Discovery and Acceptance for the PM?**
The PM writes the contract (requirements) and then independently validates it was met. This avoids the bias of having the implementer judge their own work.

**Why is the EM an advisor, not a delegator?**
Keeping the user in the loop at every transition prevents runaway agents and gives you control over the pace and direction of work.
