"""
Validated read/write access to installed_games.toml.

This module is the safe write path for the games table. A single malformed
entry makes tomllib reject the whole file, which stops every game from
launching rather than just the one that is wrong, so every write here is:

1. built completely in memory,
2. serialized with tomli_w,
3. parsed back with tomllib and compared to what was intended, and only then
4. written to a temporary file in the same directory and swapped into place
   with os.replace, so the file on disk is always either the old valid
   document or the new valid document.

The schema matches what the installer generates
(install/installer/config/installation.py) and adds no keys of its own. The
installer remains the owner of the schema: it rebuilds the games table from its
own wizard input on every reconfigure, so a game added only through this module
is not carried over by a later full reconfigure.

Functions take the target file path as an argument and never resolve the real
config location themselves; callers decide which file is edited.
"""

import copy
import os
import stat
import sys
import tempfile
import tomllib
from pathlib import Path

import tomli_w

# Game ID rules live in the installer package, which ships alongside src in
# every install. Put it on sys.path the same way runtime modules add src.
_INSTALL_DIR = Path(__file__).resolve().parents[4] / "install"
if str(_INSTALL_DIR) not in sys.path:
    sys.path.insert(0, str(_INSTALL_DIR))

from installer.utils.game_id import generate_game_id, validate_game_id  # pylint: disable=wrong-import-position

BINARY_KEYS = frozenset({"display_name", "path", "banner", "args"})
MAME_KEYS = frozenset({"display_name", "rom", "state", "banner"})
OPTIONAL_KEYS = frozenset({"display_name", "banner", "args", "state"})
# Keys whose values are also written into the line-based Pegasus menu file.
MENU_KEYS = ("display_name", "banner")
DEFAULT_MAME_STATE = "o"


class GamesConfigError(Exception):
    """Raised when installed_games.toml cannot be read or safely written."""


class ValidationError(GamesConfigError):
    """Raised when a game ID or entry does not match the installer's schema."""


def entry_kind(entry):
    """
    Classify a game entry the same way launch_game does.

    Args:
        entry: A value from the games table.

    Returns:
        str: "mame" for a table with a 'rom' key, "binary" for any other
            table, and "string" for a bare path string (a hand-edited shape
            launch_game still accepts).
    """
    if isinstance(entry, dict):
        return "mame" if "rom" in entry else "binary"
    return "string"


def load_games(path):
    """
    Load an installed_games.toml file for editing.

    Args:
        path: Path to the installed_games.toml file.

    Returns:
        dict: The complete parsed document, including any top-level keys other
            than 'games' so they survive the next write. A missing file yields
            an empty games table.

    Raises:
        GamesConfigError: If the file is not valid TOML or its 'games' key is
            not a table. The file is left for the user to repair rather than
            being overwritten.
    """
    path = Path(path)
    if not path.exists():
        return {"games": {}}

    try:
        with path.open("rb") as handle:
            config = tomllib.load(handle)
    except tomllib.TOMLDecodeError as error:
        raise GamesConfigError(
            f"{path} is not valid TOML ({error}); refusing to modify it"
        ) from error

    games = config.setdefault("games", {})
    if not isinstance(games, dict):
        raise GamesConfigError(f"'games' in {path} is not a table; refusing to modify it")
    return config


def validate_entry(game_id, entry, preserved_keys=frozenset()):
    """
    Check a game ID and entry against the installer's schema.

    Args:
        game_id: Key of the game in the games table.
        entry: The game's table.
        preserved_keys: Keys already present on an existing entry that are
            outside the schema. They are left alone rather than rejected so an
            update never destroys a hand-edited value.

    Raises:
        ValidationError: Describing the first problem found.
    """
    if not isinstance(game_id, str) or not validate_game_id(game_id):
        raise ValidationError(
            f"Invalid game ID {game_id!r}: use only lowercase letters, digits and underscores"
        )
    if not isinstance(entry, dict):
        raise ValidationError(f"Entry for '{game_id}' must be a table")

    kind = entry_kind(entry)
    allowed = MAME_KEYS if kind == "mame" else BINARY_KEYS
    unknown = sorted(set(entry) - allowed - set(preserved_keys))
    if unknown:
        raise ValidationError(
            f"Unsupported key(s) for a {kind} game '{game_id}': {', '.join(unknown)}"
        )

    for key, value in entry.items():
        if key in preserved_keys:
            continue
        if not isinstance(value, str):
            raise ValidationError(
                f"'{key}' for '{game_id}' must be a string, got {type(value).__name__}"
            )

    required = "rom" if kind == "mame" else "path"
    if not entry.get(required, "").strip():
        raise ValidationError(f"'{required}' for '{game_id}' must not be empty")
    if "display_name" in entry and not entry["display_name"].strip():
        raise ValidationError(f"'display_name' for '{game_id}' must not be empty")

    # The Pegasus menu file is line-based: a line break inside one of these
    # values would start a new line there, which can inject a whole menu entry.
    # str.splitlines is the broadest definition of a line break Python has.
    for key in MENU_KEYS:
        if key in entry and key not in preserved_keys and len(f"x{entry[key]}x".splitlines()) != 1:
            raise ValidationError(f"'{key}' for '{game_id}' must be a single line")


def new_game_id(config, display_name):
    """
    Generate an unused game ID from a display name.

    Args:
        config: The parsed document from load_games.
        display_name: Name the ID is derived from.

    Returns:
        str: An ID that is not yet in the games table.
    """
    return generate_game_id(display_name, config["games"])


def add_game(config, game_id, entry):
    """
    Return a copy of config with a new game added.

    Fills in the same defaults the installer writes: an empty 'banner' when
    none is given, and state "o" for a MAME game.

    Args:
        config: The parsed document from load_games.
        game_id: ID for the new game.
        entry: The new game's table.

    Returns:
        dict: The updated document. The input is not modified.

    Raises:
        ValidationError: If the ID is taken or the entry is invalid.
    """
    if game_id in config["games"]:
        raise ValidationError(f"A game with ID '{game_id}' already exists")

    entry = dict(entry)
    entry.setdefault("banner", "")
    if entry_kind(entry) == "mame":
        entry.setdefault("state", DEFAULT_MAME_STATE)
    validate_entry(game_id, entry)

    updated = copy.deepcopy(config)
    updated["games"][game_id] = entry
    return updated


def update_game(config, game_id, changes):
    """
    Return a copy of config with fields of an existing game changed.

    Args:
        config: The parsed document from load_games.
        game_id: ID of the game to change.
        changes: Mapping of key to new value. A value of None removes an
            optional key.

    Returns:
        dict: The updated document. The input is not modified.

    Raises:
        ValidationError: If the game does not exist, is a bare string entry,
            or the result would be invalid.
    """
    games = config["games"]
    if game_id not in games:
        raise ValidationError(f"No game with ID '{game_id}'")
    current = games[game_id]
    if not isinstance(current, dict):
        raise ValidationError(
            f"'{game_id}' is a hand-edited string entry; edit it by hand or remove and re-add it"
        )

    kind = entry_kind(current)
    allowed = MAME_KEYS if kind == "mame" else BINARY_KEYS
    preserved = set(current) - allowed

    entry = dict(current)
    for key, value in changes.items():
        if value is None:
            if key not in OPTIONAL_KEYS:
                raise ValidationError(f"'{key}' is required and cannot be cleared")
            entry.pop(key, None)
        else:
            entry[key] = value
    validate_entry(game_id, entry, preserved_keys=preserved - set(changes))

    updated = copy.deepcopy(config)
    updated["games"][game_id] = entry
    return updated


def remove_game(config, game_id):
    """
    Return a copy of config with a game removed.

    Args:
        config: The parsed document from load_games.
        game_id: ID of the game to remove.

    Returns:
        dict: The updated document. The input is not modified.

    Raises:
        ValidationError: If the game does not exist.
    """
    if game_id not in config["games"]:
        raise ValidationError(f"No game with ID '{game_id}'")
    updated = copy.deepcopy(config)
    del updated["games"][game_id]
    return updated


def atomic_write_bytes(path, data):
    """
    Atomically replace a file with new contents.

    The data is written to a temporary file in the target's own directory (so
    the final rename stays on one volume and is atomic on Windows), flushed to
    disk, given the target's current permission bits, and moved over the target
    with os.replace. On any failure the original file is left exactly as it
    was and the temporary file is removed.

    Args:
        path: File to replace. A symlink is followed so the link itself is kept.
        data: The complete new contents, as bytes.

    Raises:
        GamesConfigError: If the file cannot be replaced (on Windows, typically
            because another process has it open).
    """
    path = Path(path).resolve()
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            os.chmod(tmp_name, stat.S_IMODE(path.stat().st_mode))
        os.replace(tmp_name, path)
    except BaseException as error:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        if isinstance(error, PermissionError):
            raise GamesConfigError(
                f"Could not replace {path}: it may be open in another program "
                "(close Arcade Station and try again)"
            ) from error
        raise


def write_games(path, config):
    """
    Atomically replace installed_games.toml with a verified document.

    The document is serialized, parsed back and compared before any file is
    touched, then written with atomic_write_bytes.

    Args:
        path: Path to the installed_games.toml file.
        config: The complete document to write.

    Raises:
        GamesConfigError: If the document does not survive a round trip, or
            the file cannot be replaced.
    """
    try:
        text = tomli_w.dumps(config)
    except (TypeError, ValueError) as error:
        raise GamesConfigError(f"Could not serialize games config: {error}") from error
    try:
        round_trip = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise GamesConfigError(
            f"Serialized games config is not valid TOML ({error}); not written"
        ) from error
    if round_trip != config:
        raise GamesConfigError("Serialized games config did not parse back identically; not written")

    atomic_write_bytes(path, text.encode("utf-8"))
