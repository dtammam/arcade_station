---
name: Python 3.12 not available in dev environment
description: Dev environment runs Python 3.11 (Debian 12) but project requires 3.12.9 — needs dedicated provisioning task
type: project
---

The dev environment (Debian 12) ships Python 3.11, not the required 3.12.9. The hygiene initiative is proceeding on 3.11 without issues — black, flake8, mypy, pytest all work fine. The version mismatch produces a cosmetic warning but doesn't block anything.

**Why:** Installing 3.12 requires building from source or pyenv/deadsnakes, which is an infrastructure change that carries risk if done ad-hoc mid-initiative.

**How to apply:** Track as a follow-on task after the hygiene initiative completes. Scope: "Provision Python 3.12 in the dev environment, recreate venv, confirm all tools work under 3.12." Do not attempt mid-initiative.
