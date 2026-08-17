"""Tests how a reconfigure treats settings the wizard cannot collect.

_generate_config_files rebuilds the games table from scratch on every run, so
any key the wizard has no field for is dropped unless it is explicitly carried
forward. Both review seats reproduced this: an installed_games.toml holding a
documented 'args' value came back without it, and default_config.toml came back
with default_game_start reset to false.

Carrying settings forward is not unconditional, and this module's title should
not be read as a guarantee that a reconfigure preserves everything. Answering
no on the Game Setup page sets skip_games, which discards the entire games
table - behaviour that predates this work and is not changed here. What is
guaranteed is that the boot-to-game pointer is never emitted dangling: when the
game it names is gone, for that reason or any other, the setting is dropped.

Both paths are covered below, run against the real method.
"""
import tomllib

import pytest

from installer.config.installation import InstallationManager

ARGS_VALUE = '--start-fullscreen "https://example.com/watch.html?v=abc&ctx=%7B%22sort%22:%22x%22%7D"'


@pytest.fixture(name="manager")
def fixture_manager():
    """An InstallationManager used only for config generation."""
    return InstallationManager()


@pytest.fixture(name="seeded_config_dir")
def fixture_seeded_config_dir(tmp_path):
    """A config directory holding hand-edited settings the wizard cannot collect."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "installed_games.toml").write_text(
        "[games.demo]\n"
        'display_name = "demo"\n'
        'path = "C:/app/demo.exe"\n'
        f"args = '{ARGS_VALUE}'\n"
        'banner = "C:/banners/demo.png"\n',
        encoding="utf-8",
    )
    (config_dir / "default_config.toml").write_text(
        '[logging]\nlogdirectory = "C:/logs"\n\n'
        '[paths]\npegasus_base_path = "../../../pegasus-fe"\n\n'
        '[default_game]\ndefault_game_start = true\ndefault_game = "demo"\n',
        encoding="utf-8",
    )
    return config_dir


def reconfigure(manager, config_dir, tmp_path):
    """Run generation the way a reconfigure does: wizard data with no args field."""
    wizard_config = {
        "install_path": str(tmp_path),
        "log_dir": str(tmp_path / "logs"),
        # Exactly what BinaryGameEntry.get_data() returns - note no 'args'.
        "binary_games": {
            "demo": {
                "id": "demo",
                "display_name": "demo",
                "path": "C:/app/demo.exe",
                "banner": "C:/banners/demo.png",
            }
        },
    }
    manager._generate_config_files(wizard_config, str(config_dir))  # pylint: disable=protected-access
    with (config_dir / "installed_games.toml").open("rb") as handle:
        games = tomllib.load(handle)
    with (config_dir / "default_config.toml").open("rb") as handle:
        defaults = tomllib.load(handle)
    return games, defaults


def test_hand_edited_args_survive_a_reconfigure(manager, seeded_config_dir, tmp_path):
    """The wizard cannot supply 'args', so it must be carried over."""
    games, _ = reconfigure(manager, seeded_config_dir, tmp_path)
    entry = games["games"]["demo"]
    assert "args" in entry, "reconfigure dropped the hand-edited args key"
    assert entry["args"] == ARGS_VALUE


def test_reconfigure_still_applies_wizard_fields(manager, seeded_config_dir, tmp_path):
    """Preservation must not shadow values the wizard does manage."""
    games, _ = reconfigure(manager, seeded_config_dir, tmp_path)
    entry = games["games"]["demo"]
    assert entry["path"] == "C:/app/demo.exe"
    assert entry["display_name"] == "demo"


def test_default_game_setting_survives_a_reconfigure(manager, seeded_config_dir, tmp_path):
    """Boot-to-game has no wizard page, so a rebuild must not reset it."""
    _, defaults = reconfigure(manager, seeded_config_dir, tmp_path)
    assert defaults["default_game"]["default_game_start"] is True
    assert defaults["default_game"]["default_game"] == "demo"


def test_absent_prior_config_yields_safe_defaults(manager, tmp_path):
    """A fresh install has nothing to preserve and must not fail."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    _, defaults = reconfigure(manager, config_dir, tmp_path)
    assert defaults["default_game"]["default_game_start"] is False
    assert defaults["default_game"]["default_game"] == ""


def test_default_game_dropped_when_its_game_is_gone(manager, seeded_config_dir, tmp_path):
    """Preserving the pointer must not outlive the game it points at.

    The seeded config boots into 'demo'. Reconfiguring without demo in the
    wizard payload rebuilds the games table without it, so the setting has
    nothing left to resolve to and must not be written out.
    """
    wizard_config = {
        "install_path": str(tmp_path),
        "log_dir": str(tmp_path / "logs"),
        "binary_games": {
            "other": {
                "id": "other",
                "display_name": "other",
                "path": "C:/app/other.exe",
                "banner": "",
            }
        },
    }
    manager._generate_config_files(wizard_config, str(seeded_config_dir))  # pylint: disable=protected-access
    with (seeded_config_dir / "installed_games.toml").open("rb") as handle:
        games = tomllib.load(handle)["games"]
    with (seeded_config_dir / "default_config.toml").open("rb") as handle:
        defaults = tomllib.load(handle)["default_game"]
    assert "demo" not in games, "precondition: the rebuild should have dropped demo"
    assert defaults["default_game_start"] is False
    assert defaults["default_game"] == ""


def test_default_game_dropped_when_game_setup_is_skipped(manager, seeded_config_dir, tmp_path):
    """The skip_games path discards every game, so the pointer cannot survive it.

    Answering no on the Game Setup page sets skip_games, which leaves the games
    table empty. Before this guard the boot-to-game setting was still preserved
    verbatim, emitting a config that pointed into an empty table.
    """
    wizard_config = {
        "install_path": str(tmp_path),
        "log_dir": str(tmp_path / "logs"),
        "skip_games": True,
    }
    manager._generate_config_files(wizard_config, str(seeded_config_dir))  # pylint: disable=protected-access
    with (seeded_config_dir / "installed_games.toml").open("rb") as handle:
        games = tomllib.load(handle)["games"]
    with (seeded_config_dir / "default_config.toml").open("rb") as handle:
        defaults = tomllib.load(handle)["default_game"]
    assert games == {}, "precondition: skip_games leaves the table empty"
    assert defaults["default_game_start"] is False
    assert defaults["default_game"] == ""


def test_wizard_supplied_args_take_precedence(manager, seeded_config_dir, tmp_path):
    """If a future wizard page collects args, its value wins over the old one."""
    wizard_config = {
        "install_path": str(tmp_path),
        "log_dir": str(tmp_path / "logs"),
        "binary_games": {
            "demo": {
                "id": "demo",
                "display_name": "demo",
                "path": "C:/app/demo.exe",
                "banner": "",
                "args": "--kiosk",
            }
        },
    }
    manager._generate_config_files(wizard_config, str(seeded_config_dir))  # pylint: disable=protected-access
    with (seeded_config_dir / "installed_games.toml").open("rb") as handle:
        entry = tomllib.load(handle)["games"]["demo"]
    assert entry["args"] == "--kiosk"
