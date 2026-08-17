"""Shared pytest configuration for the Arcade Station test suite.

Runtime code inserts its own package roots onto sys.path before importing, so
the tests do the same rather than requiring the project to be pip-installed.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# 'src' provides the arcade_station package; 'install' provides the installer
# package used by the installer tests.
for _path in (REPO_ROOT / "src", REPO_ROOT / "install"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


@pytest.fixture(scope="session")
def repo_root():
    """Absolute path to the repository root."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def config_dir(repo_root):
    """Absolute path to the shipped config directory."""
    return repo_root / "config"
