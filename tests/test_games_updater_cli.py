"""Tests for the games updater command line (tools/games_updater).

Each command edits two files: installed_games.toml (how a game launches) and the
Pegasus menu (whether it is listed). These run the real entry point against
copies under tmp_path, and pin that a failure writing the menu puts the games
file back rather than leaving the two disagreeing.
"""
import sys

import pytest

from arcade_station.core.common import games_config as gc
from arcade_station.core.common import pegasus_menu as pm
from arcade_station.tools import games_updater

PY = "C:/AS/.venv/Scripts/pythonw.exe"
LAUNCHER = "C:/AS/src/arcade_station/launchers/launch_game.py"

GAMES = (
    "[games.itgmania]\n"
    'path = "C:\\\\Games\\\\ITG\\\\itgmania.exe"\n'
    'banner = ""\n'
)
MENU = (
    "collection: arcade_station\r\nshortname: arcade_station\r\n\r\n"
    "game: ITGMania\r\nfile: not\\using\\files\\to\\launch\\games\\ITGMania\r\nsortBy: a\r\n"
    f'launch: \r\n    "{PY}" \r\n    "{LAUNCHER}" \r\n    "itgmania"\r\n'
    "assets.box_front: ../../../../assets/images/banners/itgmania.png\r\n\r\n"
)


@pytest.fixture(name="files")
def fixture_files(tmp_path):
    """Seeded copies of both files, and a runner bound to them."""
    games = tmp_path / "installed_games.toml"
    menu = tmp_path / "metadata.pegasus.txt"
    games.write_text(GAMES, encoding="utf-8")
    menu.write_bytes(MENU.encode("utf-8"))

    def run(*args):
        return games_updater.main(["--file", str(games), "--menu-file", str(menu), *args])

    return games, menu, run


def test_add_writes_both_files(files, capsys):
    """add puts the game in the games table and the menu."""
    games, menu, run = files
    assert run("add", "--name", "Metal Slug", "--rom", "mslug") == 0
    assert gc.load_games(games)["games"]["metal_slug"]["rom"] == "mslug"
    assert "metal_slug" in {b.game_id for b in pm.load_menu(menu).blocks}
    assert "Restart Arcade Station" in capsys.readouterr().out


def test_add_accepts_dash_leading_args_with_equals(files):
    """Launch arguments starting with '-' are passed as --args=VALUE."""
    games, _, run = files
    assert run("add", "--name", "Web", "--path", "C:\\b.exe", "--args=--kiosk \"https://x/?a=1\"") == 0
    assert gc.load_games(games)["games"]["web"]["args"] == '--kiosk "https://x/?a=1"'


def test_update_renames_in_both_files(files):
    """A rename changes display_name and the menu title, not the ID."""
    games, menu, run = files
    assert run("update", "itgmania", "--name", "ITG") == 0
    assert gc.load_games(games)["games"]["itgmania"]["display_name"] == "ITG"
    assert b"game: ITG\r\n" in menu.read_bytes()


def test_update_clear_removes_optional_field(files):
    """--clear removes a field from the entry."""
    games, _, run = files
    assert run("update", "itgmania", "--args=-x") == 0
    assert run("update", "itgmania", "--clear", "args") == 0
    assert "args" not in gc.load_games(games)["games"]["itgmania"]


def test_remove_updates_both_files(files):
    """remove takes the game out of the table and the menu."""
    games, menu, run = files
    assert run("remove", "itgmania") == 0
    assert gc.load_games(games)["games"] == {}
    assert "itgmania" not in menu.read_text(encoding="utf-8")


def test_remove_warns_about_default_game(files, capsys):
    """Removing the startup game says so."""
    games, _, run = files
    (games.parent / "default_config.toml").write_text(
        '[default_game]\ndefault_game = "itgmania"\ndefault_game_start = true\n', encoding="utf-8"
    )
    assert run("remove", "itgmania") == 0
    assert "default game launched at startup" in capsys.readouterr().err


def test_list_shows_games_and_menu_status(files, capsys):
    """list reports each game and whether it has a menu entry."""
    games, _, run = files
    gc.write_games(games, gc.add_game(gc.load_games(games), "orphan", {"path": "x"}))
    assert run("list") == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].split() == ["ID", "TYPE", "NAME", "TARGET", "MENU"]
    assert out[1].split()[-1] == "yes" and out[1].startswith("itgmania")
    assert out[2].split()[-1] == "no" and out[2].startswith("orphan")


@pytest.mark.parametrize(
    "args",
    [
        ("add", "--name", "Bad\ngame: X", "--path", "x"),
        ("add", "--name", "Pokémon", "--path", "x"),
        ("add", "--name", "ITGMania", "--path", "x", "--id", "itgmania"),
        ("add", "--name", "Mixed", "--path", "x", "--state", "o"),
        ("update", "ghost", "--name", "x"),
        ("update", "itgmania"),
        ("update", "itgmania", "--args=-x", "--clear", "args"),
        ("remove", "ghost"),
        ("add", "--name", "KOF", "--rom", "kof98", "--state", ""),
    ],
)
def test_rejected_commands_change_nothing(files, capsys, args):
    """Every rejected command exits 1 and leaves both files byte-identical."""
    games, menu, run = files
    before = (games.read_bytes(), menu.read_bytes())
    assert run(*args) == 1
    err = capsys.readouterr().err
    assert "Error:" in err
    if "Pokémon" in args:
        assert "--id" in err
    assert (games.read_bytes(), menu.read_bytes()) == before


def test_menu_failure_restores_games_file(files, monkeypatch, capsys):
    """If the menu cannot be written, the games file is put back as it was."""
    games, menu, run = files
    before = (games.read_bytes(), menu.read_bytes())

    def fail(*_args):
        raise gc.GamesConfigError("menu is locked")

    monkeypatch.setattr(pm, "write_menu", fail)
    assert run("add", "--name", "Metal Slug", "--rom", "mslug") == 1
    assert "was restored" in capsys.readouterr().err
    assert (games.read_bytes(), menu.read_bytes()) == before


def test_menu_failure_on_first_game_removes_new_games_file(tmp_path, monkeypatch):
    """With no games file before, a failed menu write leaves none behind."""
    games = tmp_path / "installed_games.toml"
    menu = tmp_path / "metadata.pegasus.txt"
    monkeypatch.setattr(pm, "write_menu", lambda *_a: (_ for _ in ()).throw(OSError("disk full")))
    code = games_updater.main(["--file", str(games), "--menu-file", str(menu),
                               "add", "--name", "A", "--path", "x"])
    assert code == 1
    assert not games.exists()


def test_default_paths_point_at_the_real_config():
    """Without --file/--menu-file the tool edits this install's own files."""
    options = games_updater.build_parser().parse_args(["list"])
    assert options.file == games_updater.REPO_ROOT / "config" / "installed_games.toml"
    assert options.menu_file.parts[-4:] == ("pegasus-fe", "config", "metafiles", "metadata.pegasus.txt")


def test_failed_restore_says_the_files_may_disagree(files, monkeypatch, capsys):
    """If the restore also fails, the error says so instead of claiming success."""
    _, _, run = files

    def fail_menu(*_args):
        raise gc.GamesConfigError("menu is locked")

    real_write = gc.atomic_write_bytes
    calls = []

    def fail_restore(path, data):
        # The first call is the games write itself; the second is the restore.
        calls.append(path)
        if len(calls) > 1:
            raise OSError("games file is locked too")
        real_write(path, data)

    monkeypatch.setattr(pm, "write_menu", fail_menu)
    monkeypatch.setattr(gc, "atomic_write_bytes", fail_restore)
    assert run("remove", "itgmania") == 1
    err = capsys.readouterr().err
    assert "could not be restored" in err and "may now disagree" in err


def test_update_of_a_launch_only_field_leaves_the_menu_alone(files):
    """Changing a path must not rewrite the installer's menu block."""
    _, menu, run = files
    before = menu.read_bytes()
    assert run("update", "itgmania", "--path", "D:\\ITG\\itgmania.exe") == 0
    assert menu.read_bytes() == before


def test_clear_name_falls_back_to_derived_title(files):
    """--clear name removes display_name and the menu shows the ID-derived title."""
    games, menu, run = files
    assert run("update", "itgmania", "--name", "ITG") == 0
    assert run("update", "itgmania", "--clear", "name") == 0
    assert "display_name" not in gc.load_games(games)["games"]["itgmania"]
    assert b"game: Itgmania\r\n" in menu.read_bytes()


def test_ctrl_c_during_menu_write_still_rolls_back(files, monkeypatch):
    """KeyboardInterrupt is not a process kill: the games file is restored."""
    games, menu, run = files
    before = (games.read_bytes(), menu.read_bytes())

    def interrupted(*_args):
        raise KeyboardInterrupt

    monkeypatch.setattr(pm, "write_menu", interrupted)
    with pytest.raises(KeyboardInterrupt):
        run("remove", "itgmania")
    assert (games.read_bytes(), menu.read_bytes()) == before


@pytest.mark.skipif(sys.platform == "win32", reason="symlinks need privileges on Windows")
def test_rollback_through_dangling_symlink_keeps_the_link(tmp_path, monkeypatch):
    """A failed first write removes the file it created, not the symlink."""
    link = tmp_path / "installed_games.toml"
    target = tmp_path / "real" / "games.toml"
    target.parent.mkdir()
    link.symlink_to(target)
    monkeypatch.setattr(pm, "write_menu", lambda *_a: (_ for _ in ()).throw(OSError("locked")))
    code = games_updater.main(["--file", str(link), "--menu-file", str(tmp_path / "m.txt"),
                               "add", "--name", "A", "--path", "x"])
    assert code == 1
    assert link.is_symlink() and not target.exists()


def test_list_tolerates_non_string_hand_edited_name(tmp_path, capsys):
    """A hand-edited display_name = 5 is shown, not a crash."""
    games = tmp_path / "installed_games.toml"
    games.write_text('[games.a]\npath = "x"\ndisplay_name = 5\n', encoding="utf-8")
    assert games_updater.main(["--file", str(games), "--menu-file", str(tmp_path / "m.txt"), "list"]) == 0
    assert "5" in capsys.readouterr().out


def test_mame_game_update_rename_and_banner_reach_both_files(files):
    """Acceptance 1: a MAME game is updated through the CLI in both files."""
    games, menu, run = files
    assert run("add", "--name", "Metal Slug", "--rom", "mslug") == 0
    assert run("update", "metal_slug", "--name", "Metal Slug X", "--state", "2",
               "--banner", "C:\\art\\mslugx.png") == 0
    assert gc.load_games(games)["games"]["metal_slug"] == {
        "display_name": "Metal Slug X", "rom": "mslug", "state": "2", "banner": "C:\\art\\mslugx.png",
    }
    block = next(b for b in pm.load_menu(menu).blocks if b.game_id == "metal_slug")
    text = "".join(block.lines)
    assert text.startswith("game: Metal Slug X\r\n")
    assert "assets.box_front: C:/art/mslugx.png\r\n" in text


def test_mame_game_remove_through_cli(files):
    """Acceptance 1: a MAME game is removed from both files."""
    games, menu, run = files
    assert run("add", "--name", "Metal Slug", "--rom", "mslug") == 0
    assert run("remove", "metal_slug") == 0
    assert "metal_slug" not in gc.load_games(games)["games"]
    assert "metal_slug" not in {b.game_id for b in pm.load_menu(menu).blocks}


def test_list_shows_a_mame_row(files, capsys):
    """Acceptance 1: list shows MAME games with their ROM."""
    _, _, run = files
    assert run("add", "--name", "Metal Slug", "--rom", "mslug") == 0
    capsys.readouterr()
    assert run("list") == 0
    row = next(line for line in capsys.readouterr().out.splitlines() if line.startswith("metal_slug"))
    assert row.split() == ["metal_slug", "mame", "Metal", "Slug", "mslug", "yes"]


def test_list_with_no_games(tmp_path, capsys):
    """An empty games table says so."""
    code = games_updater.main(["--file", str(tmp_path / "g.toml"), "--menu-file", str(tmp_path / "m.txt"), "list"])
    assert code == 0 and capsys.readouterr().out.strip() == "No games configured."


def test_list_shows_bare_string_entry(tmp_path, capsys):
    """A hand-edited string entry is listed with its path."""
    games = tmp_path / "g.toml"
    games.write_text('[games]\nlegacy = "C:\\\\legacy.exe"\n', encoding="utf-8")
    assert games_updater.main(["--file", str(games), "--menu-file", str(tmp_path / "m.txt"), "list"]) == 0
    row = capsys.readouterr().out.splitlines()[1].split()
    assert row == ["legacy", "string", "C:\\legacy.exe", "no"]


def test_mame_state_cannot_be_cleared_from_cli(files):
    """--clear state is not offered: argparse rejects it."""
    _, _, run = files
    with pytest.raises(SystemExit) as exited:
        run("update", "itgmania", "--clear", "state")
    assert exited.value.code == 2


@pytest.mark.skipif(sys.platform == "win32", reason="symlinks need privileges on Windows")
def test_default_game_warning_looks_beside_the_given_path(tmp_path, capsys):
    """With installed_games.toml symlinked elsewhere, default_config.toml is read beside the link."""
    config_dir, elsewhere = tmp_path / "config", tmp_path / "elsewhere"
    config_dir.mkdir()
    elsewhere.mkdir()
    (elsewhere / "games.toml").write_text(GAMES, encoding="utf-8")
    (config_dir / "installed_games.toml").symlink_to(elsewhere / "games.toml")
    (config_dir / "default_config.toml").write_text(
        '[default_game]\ndefault_game = "itgmania"\n', encoding="utf-8")
    menu = tmp_path / "m.txt"
    menu.write_bytes(MENU.encode())
    assert games_updater.main(["--file", str(config_dir / "installed_games.toml"),
                               "--menu-file", str(menu), "remove", "itgmania"]) == 0
    assert "default game launched at startup" in capsys.readouterr().err
