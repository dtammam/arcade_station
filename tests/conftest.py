"""Shared pytest fixtures for the arcade_station test suite."""

from pathlib import Path

import pytest


@pytest.fixture
def toml_config_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory with a minimal TOML configuration.

    Creates a ``config/`` subdirectory inside ``tmp_path`` and writes a
    minimal ``games.toml`` file into it.  Tests that need to redirect
    ``load_toml_config`` lookups should patch ``builtins.open`` directly,
    since that function computes its path from ``__file__`` rather than
    reading an environment variable.

    Args:
        tmp_path: pytest built-in fixture providing a per-test temporary
            directory that is cleaned up automatically after the test.

    Returns:
        Path: The temporary config directory (``tmp_path / "config"``)
        containing the minimal TOML files.
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Write a minimal valid TOML file for tests that need a real config file.
    (config_dir / "games.toml").write_text("[games]\n", encoding="utf-8")

    return config_dir
