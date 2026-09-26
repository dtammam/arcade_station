"""Tests for surgical edits to the Pegasus menu file (pegasus_menu).

Pegasus builds its menu from metadata.pegasus.txt, which the installer writes.
The games updater edits one game's block at a time, so these pin that every
other byte of the file survives: other games' blocks, comments, blocks this
module does not recognise, CRLF line endings, and a missing final newline.
"""
import pytest

from arcade_station.core.common import pegasus_menu as pm
from arcade_station.core.common.games_config import GamesConfigError

PY = "C:/Repositories/arcade_station/.venv/Scripts/pythonw.exe"
LAUNCHER = "C:/Repositories/arcade_station/src/arcade_station/launchers/launch_game.py"

# Shaped like _generate_pegasus_metadata output, plus a comment, a hand-edited
# block with its own launch command, and no final newline.
SAMPLE = f"""collection: arcade_station
shortname: arcade_station

game: ITGMania
file: not\\using\\files\\to\\launch\\games\\ITGMania
sortBy: a
launch:
    "{PY}"
    "{LAUNCHER}"
    "itgmania"
assets.box_front: ../../../../assets/images/banners/itgmania.png

# my own emulator entry
game: Handmade
file: C:/roms/handmade.bin
launch: "C:/emu/emu.exe" "{{file.path}}"

game: Not ITG
file: not\\using\\files\\to\\launch\\games\\Not ITG
sortBy: b
launch:
    "{PY}"
    "{LAUNCHER}"
    "not_itg"


game: Metal Slug
file: not\\using\\files\\to\\launch\\games\\Metal Slug
sortBy: m
launch:
    "{PY}"
    "{LAUNCHER}"
    "mslug"
assets.box_front: ../../../../assets/images/banners/arcade_station.png"""


@pytest.fixture(name="menu_file", params=["lf", "crlf"])
def fixture_menu_file(request, tmp_path):
    """The sample menu written with LF or CRLF line endings."""
    path = tmp_path / "metadata.pegasus.txt"
    text = SAMPLE if request.param == "lf" else SAMPLE.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))
    return path


def block_text(menu, game_id):
    """The rendered text of one game's block."""
    block = next(b for b in menu.blocks if b.game_id == game_id)
    return "".join(block.lines)


def test_load_and_render_is_identity(menu_file):
    """Loading and rendering an untouched file reproduces it byte for byte."""
    assert pm.render(pm.load_menu(menu_file)) == menu_file.read_bytes()


def test_blocks_are_identified_by_launch_id(menu_file):
    """Installer-shaped blocks get their launch ID; others stay opaque."""
    menu = pm.load_menu(menu_file)
    assert [b.game_id for b in menu.blocks] == [None, "itgmania", None, "not_itg", "mslug"]


def test_new_binary_block_matches_installer_format(menu_file):
    """A new game is appended in the installer's format; old bytes are a prefix."""
    original = menu_file.read_bytes()
    menu = pm.upsert_game_block(
        pm.load_menu(menu_file), "street_fighter_iii",
        {"display_name": "Street Fighter III", "path": "C:\\sf3.exe", "banner": "C:\\art\\sf3.png"},
    )
    rendered = pm.render(menu)
    newline = menu.newline
    expected_block = (
        "game: Street Fighter III\n"
        "file: not\\using\\files\\to\\launch\\games\\Street Fighter III\n"
        "sortBy: n\n"
        "launch: \n"
        f'    "{PY}" \n'
        f'    "{LAUNCHER}" \n'
        '    "street_fighter_iii"\n'
        "assets.box_front: C:/art/sf3.png\n"
        "\n\n"
    ).replace("\n", newline)
    assert rendered.startswith(original)
    assert rendered[len(original):] == f"{newline}{newline}{expected_block}".encode()


def test_binary_without_banner_has_no_asset_line(menu_file):
    """The installer omits assets.box_front for a PC game with no banner."""
    menu = pm.upsert_game_block(pm.load_menu(menu_file), "plain", {"path": "x", "banner": ""})
    assert "assets.box_front" not in block_text(menu, "plain")
    assert block_text(menu, "plain").startswith("game: Plain")


def test_mame_without_banner_uses_default_art(menu_file):
    """A MAME game with no banner gets the installer's default image."""
    menu = pm.upsert_game_block(
        pm.load_menu(menu_file), "kof98", {"display_name": "KOF 98", "rom": "kof98", "banner": ""}
    )
    assert f"assets.box_front: {pm.DEFAULT_MAME_BANNER}" in block_text(menu, "kof98")


def test_rename_rewrites_only_title_lines(menu_file):
    """A display name change touches game: and file: lines of one block."""
    menu = pm.load_menu(menu_file)
    before = pm.render(menu).decode()
    updated = pm.upsert_game_block(
        menu, "not_itg", {"display_name": "NotITG", "path": "x"}, changed={"display_name"}
    )
    after = pm.render(updated).decode()
    assert after == before.replace("game: Not ITG", "game: NotITG").replace(
        "games\\Not ITG", "games\\NotITG"
    )


def test_path_only_change_leaves_existing_block_alone(menu_file):
    """Fields that are not in the menu do not rewrite it."""
    menu = pm.load_menu(menu_file)
    updated = pm.upsert_game_block(menu, "itgmania", {"path": "D:\\new.exe", "banner": ""}, changed={"path"})
    assert pm.render(updated) == pm.render(menu)


def test_banner_change_rewrites_asset_line(menu_file):
    """A new banner replaces the asset line with forward slashes."""
    menu = pm.upsert_game_block(
        pm.load_menu(menu_file), "itgmania", {"path": "x", "banner": "D:\\art\\itg.png"}, changed={"banner"}
    )
    text = block_text(menu, "itgmania")
    assert "assets.box_front: D:/art/itg.png" in text
    assert "itgmania.png" not in text


def test_clearing_binary_banner_removes_asset_line(menu_file):
    """An empty banner on a PC game drops the asset line, like the installer."""
    menu = pm.upsert_game_block(
        pm.load_menu(menu_file), "itgmania", {"path": "x", "banner": ""}, changed={"banner"}
    )
    assert "assets.box_front" not in block_text(menu, "itgmania")


def test_banner_added_to_block_without_asset_line(menu_file):
    """A banner on a block that had none is inserted after the launch value."""
    menu = pm.upsert_game_block(
        pm.load_menu(menu_file), "not_itg", {"path": "x", "banner": "C:/a.png"}, changed={"banner"}
    )
    lines = block_text(menu, "not_itg").splitlines()
    assert lines[lines.index('    "not_itg"') + 1] == "assets.box_front: C:/a.png"


def test_remove_deletes_only_that_block(menu_file):
    """Removing a game leaves the rest of the file byte-identical."""
    menu = pm.load_menu(menu_file)
    updated, removed = pm.remove_game_blocks(menu, "not_itg")
    assert removed == 1
    kept = [b for b in menu.blocks if b.game_id != "not_itg"]
    expected = "".join(menu.preamble) + "".join("".join(b.lines) for b in kept)
    assert pm.render(updated) == expected.encode()


def test_remove_missing_game_reports_zero(menu_file):
    """No block for the ID is reported, not an error."""
    menu = pm.load_menu(menu_file)
    updated, removed = pm.remove_game_blocks(menu, "ghost")
    assert removed == 0
    assert pm.render(updated) == pm.render(menu)


def test_opaque_blocks_are_never_removed(menu_file):
    """A hand-edited block with no parsable ID survives any removal."""
    menu = pm.load_menu(menu_file)
    for game_id in ("itgmania", "not_itg", "mslug"):
        menu, _ = pm.remove_game_blocks(menu, game_id)
    assert "game: Handmade" in pm.render(menu).decode()
    assert "# my own emulator entry" in pm.render(menu).decode()


def test_crlf_file_stays_crlf(tmp_path):
    """Every line written into a CRLF file ends in CRLF."""
    path = tmp_path / "metadata.pegasus.txt"
    path.write_bytes(SAMPLE.replace("\n", "\r\n").encode())
    menu = pm.upsert_game_block(pm.load_menu(path), "new_game", {"display_name": "New", "path": "x"})
    menu = pm.upsert_game_block(menu, "not_itg", {"display_name": "Renamed", "path": "x"}, changed={"display_name"})
    rendered = pm.render(menu)
    assert rendered.count(b"\n") == rendered.count(b"\r\n")


def test_missing_file_starts_from_installer_header(tmp_path):
    """With no menu file yet, the header is created and launch paths derived."""
    path = tmp_path / "metadata.pegasus.txt"
    menu = pm.upsert_game_block(pm.load_menu(path), "sf", {"display_name": "SF", "path": "x"},
                                repo_root="R")
    text = pm.render(menu).decode()
    assert text.startswith("collection: arcade_station")
    assert "launch_game.py" in text and '"sf"' in text


def test_non_utf8_file_is_refused(tmp_path):
    """A file we cannot decode is left alone."""
    path = tmp_path / "metadata.pegasus.txt"
    path.write_bytes(b"game: \xff\n")
    with pytest.raises(GamesConfigError, match="UTF-8"):
        pm.load_menu(path)


def test_upsert_does_not_modify_input(menu_file):
    """Documents are copied, not mutated."""
    menu = pm.load_menu(menu_file)
    before = pm.render(menu)
    pm.upsert_game_block(menu, "new", {"path": "x"})
    pm.upsert_game_block(menu, "not_itg", {"display_name": "X", "path": "x"})
    pm.remove_game_blocks(menu, "mslug")
    assert pm.render(menu) == before


def test_write_menu_round_trips(menu_file):
    """write_menu stores exactly what render produces."""
    menu = pm.upsert_game_block(pm.load_menu(menu_file), "new", {"path": "x"})
    pm.write_menu(menu_file, menu)
    assert menu_file.read_bytes() == pm.render(menu)


def test_comment_above_a_block_belongs_to_that_block(tmp_path):
    """Removing a game takes its own leading comment, not the next game's."""
    path = tmp_path / "metadata.pegasus.txt"
    path.write_text(
        f'game: A\nlaunch: \n    "{PY}" \n    "{LAUNCHER}" \n    "a"\n\n'
        f'# B is the cabinet favourite\ngame: B\nlaunch: \n    "{PY}" \n    "{LAUNCHER}" \n    "b"\n',
        encoding="utf-8",
    )
    menu = pm.load_menu(path)
    assert pm.render(menu) == path.read_bytes()
    without_a, _ = pm.remove_game_blocks(menu, "a")
    assert pm.render(without_a).decode().startswith("# B is the cabinet favourite\ngame: B")
    without_b, _ = pm.remove_game_blocks(menu, "b")
    assert "favourite" not in pm.render(without_b).decode()
