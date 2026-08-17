"""Characterization tests for configuration loading.

These pin the behavior the rest of the application depends on. They deliberately
assert structure rather than values: every file under config/ carries
skip-worktree, so a fresh clone sees near-empty defaults while a real install
sees personalized content. Anything asserted here has to hold for both.

The motivating failure: a single malformed entry in installed_games.toml makes
tomllib reject the whole file, so load_game_config raises and *every* game stops
launching, not just the broken one.
"""
import tomllib

import pytest

from arcade_station.core.common.core_functions import (
    load_game_config,
    load_toml_config,
)

CONFIG_FILES = ["default_config.toml", "display_config.toml", "installed_games.toml",
                "key_listener.toml", "mame_config.toml", "pegasus_binaries.toml",
                "processes_to_kill.toml", "screenshot_config.toml", "utility_config.toml"]


@pytest.mark.characterization
@pytest.mark.parametrize("name", CONFIG_FILES)
def test_shipped_config_parses(config_dir, name):
    """Every shipped config file is valid TOML.

    One malformed file takes down everything that reads it, so this is the
    cheapest high-value guard in the suite.
    """
    path = config_dir / name
    if not path.exists():
        pytest.skip(f"{name} not present in this checkout")
    with path.open("rb") as handle:
        assert isinstance(tomllib.load(handle), dict)


@pytest.mark.characterization
def test_load_toml_config_resolves_relative_to_package(config_dir):
    """load_toml_config locates config/ by walking up from its own module."""
    if not (config_dir / "default_config.toml").exists():
        pytest.skip("default_config.toml not present in this checkout")
    assert isinstance(load_toml_config("default_config.toml"), dict)


@pytest.mark.characterization
def test_load_toml_config_raises_for_missing_file():
    """A missing config file surfaces as FileNotFoundError, not a silent empty dict."""
    with pytest.raises(FileNotFoundError):
        load_toml_config("this_file_does_not_exist.toml")


@pytest.mark.characterization
def test_game_config_exposes_games_table():
    """load_game_config always yields a 'games' table, empty on a fresh clone."""
    assert isinstance(load_game_config().get("games"), dict)


@pytest.mark.characterization
def test_every_game_entry_is_rom_or_path_based():
    """launch_game branches on the presence of 'rom'; entries must supply one shape.

    A dict entry with neither key reaches the binary branch with an empty path
    and is logged as invalid rather than launched.
    """
    for name, entry in load_game_config().get("games", {}).items():
        if not isinstance(entry, dict):
            continue
        assert "rom" in entry or "path" in entry, f"{name} declares neither 'rom' nor 'path'"


@pytest.mark.characterization
def test_launch_arguments_are_strings_when_present():
    """'args' is handed to PowerShell and shlex as a single string, never a list."""
    for name, entry in load_game_config().get("games", {}).items():
        if isinstance(entry, dict) and "args" in entry:
            assert isinstance(entry["args"], str), f"{name} declares non-string 'args'"
