"""
Surgical edits to the Pegasus menu file (metadata.pegasus.txt).

Pegasus builds its game menu from metadata.pegasus.txt, not from
installed_games.toml: each menu entry's launch command runs launch_game.py with
a game ID, and installed_games.toml only says how that ID launches. The
installer regenerates the whole file from its wizard input; this module instead
edits one game's block at a time so every other block stays byte-identical.

The file is a list of 'name: value' lines. A value continues onto following
lines that start with whitespace, and every entry belongs to the last 'game:'
or 'collection:' line above it. A game block here runs from a column-0 'game:'
line to the next column-0 'game:' or 'collection:' line. Its game ID is the last
quoted token of its 'launch:' value, as the installer writes it:

    launch:
        "<python>"
        "<...>/launch_game.py"
        "<game id>"

Blocks without that shape are treated as opaque and never edited or removed.

Functions take paths as arguments and never resolve the real menu location
themselves; callers decide which file is edited.
"""

import copy
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from arcade_station.core.common.games_config import (
    GamesConfigError,
    atomic_write_bytes,
    entry_kind,
)
# games_config has put the installer package on sys.path.
from installer.utils.game_id import get_display_name  # pylint: disable=wrong-import-order

MENU_HEADER = "collection: arcade_station\nshortname: arcade_station\n\n"
FILE_PREFIX = "not\\using\\files\\to\\launch\\games\\"
DEFAULT_MAME_BANNER = "../../../../assets/images/banners/arcade_station.png"
REPO_ROOT = Path(__file__).resolve().parents[4]

_SECTION_START = re.compile(r"(?i)(game|collection)\s*:")
_GAME_LINE = re.compile(r"(?i)game\s*:")
_FILE_LINE = re.compile(r"(?i)file\s*:")
_SORT_LINE = re.compile(r"(?i)sort[_-]?by\s*:\s*(.*?)\s*$")
_LAUNCH_LINE = re.compile(r"(?i)launch\s*:(.*)$")
_ASSET_LINE = re.compile(r"(?i)assets\.box_front\s*:")
_QUOTED = re.compile(r'"([^"]*)"')
_GAME_ID = re.compile(r"^[a-z0-9_]+$")


@dataclass
class Block:
    """One section of the menu file: its original lines and parsed game ID.

    Attributes:
        lines: The section's lines, each with its own line ending.
        game_id: ID from the launch command, or None if the block is opaque.
        launch_tokens: Quoted tokens of the launch value, when parsed.
    """

    lines: list
    game_id: str = None
    launch_tokens: list = field(default_factory=list)


@dataclass
class MenuDocument:
    """A parsed menu file.

    Attributes:
        preamble: Lines before the first 'game:' or 'collection:' line.
        blocks: The file's sections, in order.
        newline: Line ending used for any line this module writes.
    """

    preamble: list
    blocks: list
    newline: str


def _split_lines(text):
    """Split text on '\\n' only, keeping each line's ending, as Pegasus reads it."""
    return re.findall(r"[^\n]*\n|[^\n]+$", text)


def _value_lines(lines, start):
    """Return the index just past a value's continuation lines."""
    end = start + 1
    while end < len(lines) and lines[end][:1] in (" ", "\t"):
        end += 1
    return end


def _split_leading_comments(lines):
    """
    Split off the comment lines at the end of a block that introduce the next.

    A '#' comment directly above a 'game:' line describes that game, so it
    moves (with anything after it) to the next block. Blank lines before the
    first such comment stay where they are, as separation.

    Returns:
        tuple: (lines kept in this block, lines moved to the next block).
    """
    start = len(lines)
    while start > 0 and (not lines[start - 1].strip() or lines[start - 1].lstrip().startswith("#")):
        start -= 1
    trailing = lines[start:]
    first_comment = next(
        (i for i, line in enumerate(trailing) if line.lstrip().startswith("#")), None
    )
    if first_comment is None:
        return lines, []
    cut = start + first_comment
    return lines[:cut], lines[cut:]


def _parse_block(lines):
    """Build a Block, identifying its game ID from the launch value."""
    block = Block(lines=lines)
    title_index = next(i for i, line in enumerate(lines) if _SECTION_START.match(line))
    if not _GAME_LINE.match(lines[title_index]):
        return block
    for index, line in enumerate(lines):
        match = _LAUNCH_LINE.match(line)
        if not match:
            continue
        end = _value_lines(lines, index)
        value = match.group(1) + "".join(lines[index + 1:end])
        tokens = _QUOTED.findall(value)
        if (
            len(tokens) >= 3
            and tokens[-2].replace("\\", "/").endswith("launchers/launch_game.py")
            and _GAME_ID.match(tokens[-1])
        ):
            block.game_id = tokens[-1]
            block.launch_tokens = tokens
        break
    return block


def load_menu(path):
    """
    Load a Pegasus menu file for editing.

    Args:
        path: Path to metadata.pegasus.txt.

    Returns:
        MenuDocument: The parsed file. A missing file yields the installer's
            header with no games.

    Raises:
        GamesConfigError: If the file is not valid UTF-8.
    """
    path = Path(path)
    if path.exists():
        try:
            text = path.read_bytes().decode("utf-8")
        except UnicodeDecodeError as error:
            raise GamesConfigError(f"{path} is not valid UTF-8; refusing to modify it") from error
        newline = "\r\n" if "\r\n" in text else "\n"
    else:
        newline = os.linesep
        text = MENU_HEADER.replace("\n", newline)

    preamble, blocks, current = [], [], None
    for line in _split_lines(text):
        if _SECTION_START.match(line):
            leading = []
            if current is not None:
                current, leading = _split_leading_comments(current)
                blocks.append(_parse_block(current))
            current = leading + [line]
        elif current is None:
            preamble.append(line)
        else:
            current.append(line)
    if current is not None:
        blocks.append(_parse_block(current))
    return MenuDocument(preamble=preamble, blocks=blocks, newline=newline)


def render(menu):
    """
    Serialize a menu document to bytes.

    Args:
        menu: The document to serialize.

    Returns:
        bytes: UTF-8 file contents. Untouched blocks are reproduced exactly.
    """
    parts = list(menu.preamble)
    for block in menu.blocks:
        parts.extend(block.lines)
    return "".join(parts).encode("utf-8")


def write_menu(path, menu):
    """
    Atomically replace the menu file with a document.

    Args:
        path: Path to metadata.pegasus.txt.
        menu: The document to write.

    Raises:
        GamesConfigError: If the file cannot be replaced.
    """
    atomic_write_bytes(path, render(menu))


def _title(game_id, entry):
    """Menu title for a game: its display name, else one derived from the ID."""
    return entry.get("display_name") or get_display_name(game_id)


def _asset_value(entry):
    """The assets.box_front value the installer would write, or '' for none."""
    banner = entry.get("banner", "").replace("\\", "/")
    if not banner and entry_kind(entry) == "mame":
        return DEFAULT_MAME_BANNER
    return banner


def _launch_paths(menu, repo_root):
    """Python and launcher strings: copied from an existing block if possible."""
    for block in menu.blocks:
        if block.game_id is not None:
            return block.launch_tokens[-3], block.launch_tokens[-2]
    python = os.path.join(repo_root, ".venv", "Scripts", "pythonw.exe") if os.name == "nt" \
        else os.path.join(repo_root, ".venv", "bin", "python")
    launcher = os.path.join(repo_root, "src", "arcade_station", "launchers", "launch_game.py")
    return python, launcher


def _next_sort_key(menu):
    """The letter after the highest single-letter sortBy, so new games go last."""
    keys = []
    for block in menu.blocks:
        for line in block.lines:
            match = _SORT_LINE.match(line)
            if match and len(match.group(1)) == 1:
                keys.append(match.group(1))
    return chr(ord(max(keys)) + 1) if keys else "a"


def _new_block_lines(menu, game_id, entry, repo_root):
    """Lines for a new block, in the installer's format and the file's newline."""
    title = _title(game_id, entry)
    python, launcher = _launch_paths(menu, repo_root)
    asset = _asset_value(entry)
    text = (
        f"game: {title}\n"
        f"file: {FILE_PREFIX}{title}\n"
        f"sortBy: {_next_sort_key(menu)}\n"
        "launch: \n"
        f'    "{python}" \n'
        f'    "{launcher}" \n'
        f'    "{game_id}"\n'
    )
    # The installer ends a binary block with an optional asset line and a blank
    # line pair, and a MAME block with an asset line and one blank line.
    if entry_kind(entry) == "mame":
        text += f"assets.box_front: {asset}\n\n"
    else:
        text += (f"assets.box_front: {asset}\n" if asset else "") + "\n\n"
    return _split_lines(text.replace("\n", menu.newline))


def _ending(line, newline):
    """The line ending of an existing line, or the file's newline if it has none."""
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return newline


def _rewrite_block(block, game_id, entry, changed, newline):
    """Rewrite the title and/or asset lines of an existing block in place."""
    lines = list(block.lines)
    if "display_name" in changed:
        title = _title(game_id, entry)
        for index, line in enumerate(lines):
            if _GAME_LINE.match(line):
                lines[index] = f"game: {title}{_ending(line, newline)}"
            elif _FILE_LINE.match(line):
                lines[index] = f"file: {FILE_PREFIX}{title}{_ending(line, newline)}"
    if "banner" in changed:
        asset = _asset_value(entry)
        asset_index = next((i for i, line in enumerate(lines) if _ASSET_LINE.match(line)), None)
        if asset_index is not None:
            end = _value_lines(lines, asset_index)
            ending = _ending(lines[end - 1], newline)
            lines[asset_index:end] = [f"assets.box_front: {asset}{ending}"] if asset else []
        elif asset:
            launch_index = next(i for i, line in enumerate(lines) if _LAUNCH_LINE.match(line))
            end = _value_lines(lines, launch_index)
            if not lines[end - 1].endswith("\n"):
                lines[end - 1] += newline
            lines.insert(end, f"assets.box_front: {asset}{newline}")
    return Block(lines=lines, game_id=block.game_id, launch_tokens=block.launch_tokens)


def upsert_game_block(menu, game_id, entry, changed=None, repo_root=REPO_ROOT):
    """
    Return a copy of the menu with one game's block added or updated.

    If blocks for the ID exist, only the lines for the changed fields are
    rewritten ('game:' and 'file:' for display_name, 'assets.box_front:' for
    banner); sortBy and launch are kept. Otherwise a new block is appended.

    Args:
        menu: The parsed menu.
        game_id: ID of the game.
        entry: The game's table from installed_games.toml.
        changed: Keys that changed. None means all menu fields.
        repo_root: Root used for launch paths when no existing block has them.

    Returns:
        MenuDocument: The updated menu. The input is not modified.
    """
    if not isinstance(entry, dict):
        raise GamesConfigError(f"'{game_id}' is not a table and cannot be shown in the menu")
    changed = {"display_name", "banner"} if changed is None else set(changed)
    updated = copy.deepcopy(menu)
    matched = False
    for index, block in enumerate(updated.blocks):
        if block.game_id == game_id:
            updated.blocks[index] = _rewrite_block(block, game_id, entry, changed, updated.newline)
            matched = True
    if not matched:
        tail = updated.blocks[-1].lines if updated.blocks else updated.preamble
        # Existing text is kept as an exact prefix: a missing final line ending
        # is added so the new 'game:' starts its own line, then a blank line.
        if tail and not tail[-1].endswith("\n"):
            tail[-1] += updated.newline
        if tail and tail[-1].strip():
            tail.append(updated.newline)
        updated.blocks.append(_parse_block(_new_block_lines(updated, game_id, entry, repo_root)))
    return updated


def remove_game_blocks(menu, game_id):
    """
    Return a copy of the menu without any block for a game.

    Args:
        menu: The parsed menu.
        game_id: ID of the game.

    Returns:
        tuple: (MenuDocument, int) — the updated menu and how many blocks were
            removed. The input is not modified.
    """
    kept = [copy.deepcopy(block) for block in menu.blocks if block.game_id != game_id]
    removed = len(menu.blocks) - len(kept)
    return MenuDocument(preamble=list(menu.preamble), blocks=kept, newline=menu.newline), removed
