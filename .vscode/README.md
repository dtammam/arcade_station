# VS Code Configuration

## Tasks (`tasks.json`)

### Claude CLI path

The agent tasks (Run Product Manager, Run Principal Engineer, etc.) use an
absolute path to the `claude` binary (e.g., `/home/coder/.local/bin/claude`).

This is intentional: VS Code task shells are non-login and non-interactive,
so they don't source `~/.profile` or `~/.bashrc`. The `claude` binary is
typically installed to `~/.local/bin/`, which is not on PATH in these shells.

**If tasks fail with "claude: command not found"**, update the `command` field
in each agent task to match your `claude` install location:

```bash
which claude  # find your install path
```

### Virtual environment tasks

Two "Activate .venv" tasks are provided — one for Windows, one for Linux/macOS.
Use the one matching your host OS. The venv must be created first:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
pip install -r requirements.txt
pip install -r requirements-dev.txt
```
