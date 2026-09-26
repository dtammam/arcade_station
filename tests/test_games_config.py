"""Tests for the validated installed_games.toml write path (games_config).

A malformed installed_games.toml stops every game from launching, so these pin
the guarantees the games updater relies on: input is validated before anything
is written, every write round-trips through tomllib, and a failed write leaves
the original file byte-identical with no temporary file behind. Every test
works on a copy under tmp_path; the real config directory is never touched.
"""
import os
import sys
import tomllib

import pytest

from arcade_station.core.common import games_config as gc

SEED = (
    'title = "kept"\n'
    "\n"
    "[games.itgmania]\n"
    'path = "C:\\\\Games\\\\ITG\\\\itgmania.exe"\n'
    'banner = ""\n'
    "\n"
    "[games.not_itg]\n"
    'display_name = "Not ITG"\n'
    'path = "C:\\\\Games\\\\NotITG.exe"\n'
    'banner = ""\n'
    'args = "--windowed"\n'
    'custom = "hand-edited"\n'
    "\n"
    "[games.mslug]\n"
    'display_name = "Metal Slug"\n'
    'rom = "mslug"\n'
    'state = "o"\n'
    'banner = ""\n'
)

ARGS_VALUE = '--start-fullscreen "https://example.com/watch?v=abc&ctx=%7B%22a%22%7D"'


@pytest.fixture(name="games_file")
def fixture_games_file(tmp_path):
    """A seeded installed_games.toml in a temporary directory."""
    path = tmp_path / "installed_games.toml"
    path.write_text(SEED, encoding="utf-8")
    return path


def temp_files(directory):
    """Leftover temporary files from atomic writes."""
    return [name for name in os.listdir(directory) if name.endswith(".tmp")]


# --- loading ---------------------------------------------------------------

def test_load_missing_file_gives_empty_games_table(tmp_path):
    """A fresh install with no file yet can still have games added."""
    assert gc.load_games(tmp_path / "missing.toml") == {"games": {}}


def test_load_refuses_invalid_toml_and_leaves_it_alone(tmp_path):
    """An already-broken file is reported, never overwritten."""
    path = tmp_path / "installed_games.toml"
    path.write_bytes(b'[games.x]\npath = "unterminated\n')
    with pytest.raises(gc.GamesConfigError, match="not valid TOML"):
        gc.load_games(path)
    assert path.read_bytes() == b'[games.x]\npath = "unterminated\n'


def test_load_refuses_non_table_games(tmp_path):
    """A 'games' key that is not a table is not something we can edit."""
    path = tmp_path / "installed_games.toml"
    path.write_text('games = "nope"\n', encoding="utf-8")
    with pytest.raises(gc.GamesConfigError, match="not a table"):
        gc.load_games(path)


# --- add ---------------------------------------------------------------------

def test_add_binary_game_fills_installer_defaults(games_file):
    """A new PC game gets the empty banner the installer always writes."""
    config = gc.add_game(gc.load_games(games_file), "sf3", {"display_name": "SF3", "path": "C:\\sf3.exe"})
    assert config["games"]["sf3"] == {"display_name": "SF3", "path": "C:\\sf3.exe", "banner": ""}


def test_add_mame_game_defaults_state(games_file):
    """A new MAME game gets state 'o', as the installer writes it."""
    config = gc.add_game(gc.load_games(games_file), "kof98", {"display_name": "KOF 98", "rom": "kof98"})
    assert config["games"]["kof98"] == {
        "display_name": "KOF 98", "rom": "kof98", "banner": "", "state": "o",
    }


def test_add_rejects_duplicate_id(games_file):
    """An existing game is never silently replaced by add."""
    with pytest.raises(gc.ValidationError, match="already exists"):
        gc.add_game(gc.load_games(games_file), "mslug", {"rom": "other"})


def test_new_game_id_avoids_existing_ids(games_file):
    """Generated IDs reuse the installer's rules and skip taken IDs."""
    config = gc.load_games(games_file)
    assert gc.new_game_id(config, "Metal Slug") == "metal_slug"
    config = gc.add_game(config, "metal_slug", {"rom": "mslug2"})
    assert gc.new_game_id(config, "Metal Slug") == "metal_slug_1"


def test_operations_do_not_modify_their_input(games_file):
    """add/update/remove return new documents; the loaded one is unchanged."""
    config = gc.load_games(games_file)
    snapshot = tomllib.loads(SEED)
    gc.add_game(config, "new", {"path": "x"})
    gc.update_game(config, "not_itg", {"display_name": "Changed"})
    gc.remove_game(config, "mslug")
    assert config == snapshot


# --- validation --------------------------------------------------------------

@pytest.mark.parametrize(
    ("game_id", "entry", "message"),
    [
        ("Bad-ID", {"path": "x"}, "Invalid game ID"),
        ("", {"path": "x"}, "Invalid game ID"),
        ("abc\n", {"path": "x"}, "Invalid game ID"),
        ("ok", {"display_name": "No target"}, "'path' .* must not be empty"),
        ("ok", {"path": "   "}, "'path' .* must not be empty"),
        ("ok", {"rom": ""}, "'rom' .* must not be empty"),
        ("ok", {"path": "x", "args": ["-a", "-b"]}, "'args' .* must be a string"),
        ("ok", {"path": "x", "state": "o"}, "Unsupported key"),
        ("ok", {"rom": "r", "path": "x"}, "Unsupported key"),
        ("ok", {"rom": "r", "args": "-x"}, "Unsupported key"),
        ("ok", {"path": "x", "display_name": " "}, "'display_name' .* must not be empty"),
        ("ok", {"path": "x", "display_name": "A\ngame: Injected"}, "single line"),
        ("ok", {"path": "x", "display_name": "A\rB"}, "single line"),
        ("ok", {"path": "x", "display_name": "A\u2028B"}, "single line"),
        ("ok", {"path": "x", "display_name": "Trailing\n"}, "single line"),
        ("ok", {"path": "x", "banner": "C:\\a.png\ngame: X"}, "single line"),
    ],
)
def test_add_rejects_invalid_entries(games_file, game_id, entry, message):
    """Each rejected shape raises before any document is produced."""
    with pytest.raises(gc.ValidationError, match=message):
        gc.add_game(gc.load_games(games_file), game_id, entry)


# --- update ------------------------------------------------------------------

def test_update_changes_fields_and_keeps_hand_edited_keys(games_file):
    """Keys outside the schema already on an entry are preserved, not rejected."""
    config = gc.update_game(gc.load_games(games_file), "not_itg", {"display_name": "NotITG"})
    assert config["games"]["not_itg"]["display_name"] == "NotITG"
    assert config["games"]["not_itg"]["custom"] == "hand-edited"
    assert config["games"]["not_itg"]["args"] == "--windowed"


def test_update_clears_optional_key(games_file):
    """None removes an optional key such as args."""
    config = gc.update_game(gc.load_games(games_file), "not_itg", {"args": None})
    assert "args" not in config["games"]["not_itg"]


def test_update_cannot_clear_required_key(games_file):
    """Clearing path would leave an entry launch_game cannot start."""
    with pytest.raises(gc.ValidationError, match="required"):
        gc.update_game(gc.load_games(games_file), "not_itg", {"path": None})


def test_update_rejects_unknown_game(games_file):
    """update never creates a game."""
    with pytest.raises(gc.ValidationError, match="No game"):
        gc.update_game(gc.load_games(games_file), "ghost", {"display_name": "x"})


def test_update_refuses_bare_string_entry(tmp_path):
    """A hand-edited string entry is not rewritten into another shape."""
    path = tmp_path / "installed_games.toml"
    path.write_text('[games]\nlegacy = "C:\\\\legacy.exe"\n', encoding="utf-8")
    with pytest.raises(gc.ValidationError, match="string entry"):
        gc.update_game(gc.load_games(path), "legacy", {"display_name": "x"})


def test_update_rejects_switching_game_type_implicitly(games_file):
    """Adding a rom to a PC game would silently turn it into a MAME game."""
    with pytest.raises(gc.ValidationError, match="Unsupported key"):
        gc.update_game(gc.load_games(games_file), "itgmania", {"rom": "itg"})


# --- remove ------------------------------------------------------------------

def test_remove_game(games_file):
    """remove drops exactly one game."""
    config = gc.remove_game(gc.load_games(games_file), "mslug")
    assert set(config["games"]) == {"itgmania", "not_itg"}


def test_remove_unknown_game_is_rejected(games_file):
    """Removing a missing ID is an error, not a silent no-op."""
    with pytest.raises(gc.ValidationError, match="No game"):
        gc.remove_game(gc.load_games(games_file), "ghost")


def test_remove_bare_string_entry(tmp_path):
    """String entries can still be removed."""
    path = tmp_path / "installed_games.toml"
    path.write_text('[games]\nlegacy = "C:\\\\legacy.exe"\n', encoding="utf-8")
    assert gc.remove_game(gc.load_games(path), "legacy") == {"games": {}}


# --- writing -----------------------------------------------------------------

def test_write_round_trips_windows_paths_and_quoted_args(games_file):
    """Backslashes and embedded quotes are stored exactly as entered."""
    config = gc.add_game(
        gc.load_games(games_file), "web",
        {"display_name": "Web", "path": r"C:\Program Files\Browser\browser.exe", "args": ARGS_VALUE},
    )
    gc.write_games(games_file, config)
    with games_file.open("rb") as handle:
        reloaded = tomllib.load(handle)
    assert reloaded == config
    assert reloaded["games"]["web"]["path"] == r"C:\Program Files\Browser\browser.exe"
    assert reloaded["games"]["web"]["args"] == ARGS_VALUE
    assert reloaded["title"] == "kept"
    assert temp_files(games_file.parent) == []


def test_write_creates_missing_file(tmp_path):
    """The first game on a fresh install creates the file."""
    path = tmp_path / "installed_games.toml"
    gc.write_games(path, gc.add_game(gc.load_games(path), "a", {"path": "x"}))
    assert gc.load_games(path)["games"]["a"]["path"] == "x"


def test_serialization_failure_leaves_original_intact(games_file, monkeypatch):
    """If serialization breaks, nothing on disk changes."""
    before = games_file.read_bytes()
    monkeypatch.setattr(gc.tomli_w, "dumps", lambda *_a, **_k: 'games = "broken')
    with pytest.raises(gc.GamesConfigError, match="not valid TOML"):
        gc.write_games(games_file, gc.remove_game(gc.load_games(games_file), "mslug"))
    assert games_file.read_bytes() == before
    assert temp_files(games_file.parent) == []


def test_round_trip_mismatch_is_not_written(games_file, monkeypatch):
    """A document that parses back differently is refused."""
    before = games_file.read_bytes()
    monkeypatch.setattr(gc.tomllib, "loads", lambda _text: {"games": {}})
    with pytest.raises(gc.GamesConfigError, match="did not parse back identically"):
        gc.write_games(games_file, gc.load_games(games_file))
    assert games_file.read_bytes() == before


def test_locked_file_leaves_original_intact(games_file, monkeypatch):
    """os.replace failing (a file open on Windows) removes the temp file."""
    before = games_file.read_bytes()

    def locked(*_args):
        raise PermissionError(13, "The process cannot access the file")

    monkeypatch.setattr(gc.os, "replace", locked)
    with pytest.raises(gc.GamesConfigError, match="open in another program"):
        gc.write_games(games_file, gc.remove_game(gc.load_games(games_file), "mslug"))
    assert games_file.read_bytes() == before
    assert temp_files(games_file.parent) == []


def test_interrupted_write_leaves_original_intact(games_file, monkeypatch):
    """A failure while writing the temp file never reaches the target."""
    before = games_file.read_bytes()

    def interrupted(_fd):
        raise KeyboardInterrupt

    monkeypatch.setattr(gc.os, "fsync", interrupted)
    with pytest.raises(KeyboardInterrupt):
        gc.write_games(games_file, gc.remove_game(gc.load_games(games_file), "mslug"))
    assert games_file.read_bytes() == before
    assert temp_files(games_file.parent) == []


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits")
def test_write_keeps_file_permissions(games_file):
    """The replaced file keeps the original's permission bits."""
    games_file.chmod(0o640)
    gc.write_games(games_file, gc.load_games(games_file))
    assert games_file.stat().st_mode & 0o777 == 0o640


@pytest.mark.skipif(sys.platform == "win32", reason="symlinks need privileges on Windows")
def test_write_through_symlink_keeps_the_link(tmp_path, games_file):
    """A symlinked config stays a symlink; its target is what changes."""
    link = tmp_path / "link.toml"
    link.symlink_to(games_file)
    gc.write_games(link, gc.remove_game(gc.load_games(link), "mslug"))
    assert link.is_symlink()
    assert "mslug" not in gc.load_games(games_file)["games"]


def test_installer_game_id_rule_rejects_trailing_newline():
    """'$' matches before a final newline; the shared rule must not."""
    from installer.utils.game_id import validate_game_id  # pylint: disable=import-outside-toplevel
    assert validate_game_id("abc")
    assert not validate_game_id("abc\n")


def test_update_tolerates_non_string_hand_edited_key(tmp_path):
    """A preserved hand-edited key is not type-checked or rejected."""
    path = tmp_path / "installed_games.toml"
    path.write_text('[games.a]\npath = "x"\npriority = 5\n', encoding="utf-8")
    config = gc.update_game(gc.load_games(path), "a", {"display_name": "A"})
    assert config["games"]["a"]["priority"] == 5


def test_update_cannot_set_a_key_outside_the_schema(games_file):
    """Only keys already present are preserved; setting one is still rejected."""
    with pytest.raises(gc.ValidationError, match="Unsupported key"):
        gc.update_game(gc.load_games(games_file), "not_itg", {"custom": "changed"})


def test_nan_does_not_make_the_file_unwritable(tmp_path):
    """TOML allows nan, and nan != nan must not fail the round-trip check."""
    path = tmp_path / "installed_games.toml"
    path.write_text('threshold = nan\n[games.a]\npath = "x"\n', encoding="utf-8")
    gc.write_games(path, gc.add_game(gc.load_games(path), "b", {"path": "y"}))
    assert set(gc.load_games(path)["games"]) == {"a", "b"}


def test_failed_cleanup_never_hides_the_original_error(games_file, monkeypatch):
    """If deleting the temp file fails once, it is retried and the error kept."""
    before = games_file.read_bytes()
    real_unlink = os.unlink
    unlink_calls = []

    def locked(*_args):
        raise PermissionError(13, "Access is denied")

    def unlink_fails_once(name):
        unlink_calls.append(name)
        if len(unlink_calls) == 1:
            raise PermissionError(13, "Access is denied")
        real_unlink(name)

    monkeypatch.setattr(gc.os, "replace", locked)
    monkeypatch.setattr(gc.os, "unlink", unlink_fails_once)
    with pytest.raises(gc.GamesConfigError, match="open in another program or read-only"):
        gc.write_games(games_file, gc.load_games(games_file))
    assert games_file.read_bytes() == before
    assert temp_files(games_file.parent) == []


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits")
def test_new_file_follows_umask(tmp_path):
    """A first-time file gets normal permissions, not mkstemp's 0600."""
    old = os.umask(0o022)
    try:
        path = tmp_path / "installed_games.toml"
        gc.write_games(path, gc.add_game(gc.load_games(path), "a", {"path": "x"}))
    finally:
        os.umask(old)
    assert path.stat().st_mode & 0o777 == 0o644
