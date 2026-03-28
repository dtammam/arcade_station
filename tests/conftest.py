"""Shared pytest fixtures for the arcade_station test suite."""

from pathlib import Path

import pytest


@pytest.fixture
def toml_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide a temporary directory with a minimal TOML configuration.

    Creates a ``config/`` subdirectory inside ``tmp_path``, writes a minimal
    ``games.toml`` file into it, and sets the ``ARCADE_STATION_CONFIG_DIR``
    environment variable so tests can redirect config lookups to the temp
    directory.

    Args:
        tmp_path: pytest built-in fixture providing a per-test temporary
            directory that is cleaned up automatically after the test.
        monkeypatch: pytest built-in fixture for safely patching attributes
            and environment variables within a test's scope.

    Returns:
        Path: The temporary config directory (``tmp_path / "config"``)
        containing the minimal TOML files.
    """
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    # Write a minimal valid TOML file for tests that need a real config file.
    (config_dir / "games.toml").write_text("[games]\n", encoding="utf-8")

    # Point the well-known env var at the temp dir so modules that honour it
    # will resolve configs from the temporary location instead of the real one.
    monkeypatch.setenv("ARCADE_STATION_CONFIG_DIR", str(config_dir))

    return config_dir
