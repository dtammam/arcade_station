"""
Games Updater for Arcade Station.

Add, update, remove and list games without re-running the installer or editing
config files by hand. Each change is written to both files that define a game:

- config/installed_games.toml, which says how a game ID launches, and
- src/pegasus-fe/config/metafiles/metadata.pegasus.txt, the Pegasus menu.

Both documents are validated and built in memory before either is written, each
write is atomic, and if the menu write fails the games file is restored to what
it was. Pegasus reads the menu when it starts, so restart Arcade Station to see
a change.

Usage (from the repository root, with the Arcade Station virtual environment):

    python src/arcade_station/tools/games_updater.py list
    python src/arcade_station/tools/games_updater.py add --name "Metal Slug" --rom mslug
    python src/arcade_station/tools/games_updater.py add --name "SF III" --path "C:\\Games\\sf3.exe"
    python src/arcade_station/tools/games_updater.py update sf_iii --args=-fullscreen
    python src/arcade_station/tools/games_updater.py remove metal_slug
"""

import argparse
import os
import sys
import tomllib
from pathlib import Path

# Add the parent directory of 'arcade_station' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from arcade_station.core.common import games_config, pegasus_menu  # pylint: disable=wrong-import-position
from arcade_station.core.common.core_functions import log_message  # pylint: disable=wrong-import-position

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GAMES_FILE = REPO_ROOT / "config" / "installed_games.toml"
DEFAULT_MENU_FILE = REPO_ROOT / "src" / "pegasus-fe" / "config" / "metafiles" / "metadata.pegasus.txt"

LIMITATION = """\
Note: the installer remains the owner of these files. Re-running the installer's
game setup rebuilds both from the wizard's own list, so a game added here and
not also entered in the wizard is dropped by a later full reconfigure.

Values starting with '-' must be attached with '=', e.g. --args=-fullscreen.
"""

# CLI option name -> installed_games.toml key.
FIELD_OPTIONS = {
    "name": "display_name",
    "path": "path",
    "rom": "rom",
    "state": "state",
    "banner": "banner",
    "launch_args": "args",
}


def build_parser():
    """
    Build the command-line parser.

    Returns:
        argparse.ArgumentParser: The configured parser.
    """
    parser = argparse.ArgumentParser(
        prog="games_updater",
        description="Add, update, remove and list Arcade Station games.",
        epilog=LIMITATION,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--file", type=Path, default=DEFAULT_GAMES_FILE,
                        help="installed_games.toml to edit (default: %(default)s)")
    parser.add_argument("--menu-file", type=Path, default=DEFAULT_MENU_FILE,
                        help="Pegasus metadata.pegasus.txt to edit (default: %(default)s)")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="show configured games")

    add = commands.add_parser("add", help="add a game", epilog=LIMITATION,
                              formatter_class=argparse.RawDescriptionHelpFormatter)
    add.add_argument("--name", required=True, help="display name shown in the menu")
    target = add.add_mutually_exclusive_group(required=True)
    target.add_argument("--path", help="executable for a PC game")
    target.add_argument("--rom", help="ROM name for a MAME game")
    add.add_argument("--id", dest="game_id",
                     help="game ID (default: generated from --name)")
    add.add_argument("--banner", help="marquee/banner image path")
    add.add_argument("--args", dest="launch_args", help="launch arguments for a PC game")
    add.add_argument("--state", help="MAME save state to load (default: o)")

    update = commands.add_parser("update", help="change fields of a game (its ID never changes)",
                                 epilog=LIMITATION,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    update.add_argument("game_id", help="ID of the game to change")
    update.add_argument("--name", help="new display name")
    update.add_argument("--path", help="new executable path")
    update.add_argument("--rom", help="new ROM name")
    update.add_argument("--banner", help="new banner image path")
    update.add_argument("--args", dest="launch_args", help="new launch arguments")
    update.add_argument("--state", help="new MAME save state")
    update.add_argument("--clear", action="append", default=[],
                        choices=["name", "banner", "args", "state"],
                        help="remove an optional field (repeatable)")

    remove = commands.add_parser("remove", help="remove a game")
    remove.add_argument("game_id", help="ID of the game to remove")
    return parser


def _fields(options):
    """Collect the entry fields given on the command line."""
    return {
        key: getattr(options, option)
        for option, key in FIELD_OPTIONS.items()
        if getattr(options, option, None) is not None
    }


def _save(games_path, config, menu_path, menu):
    """
    Write the games file, then the menu, restoring the games file on failure.

    Raises:
        GamesConfigError: If either write fails. When the menu write fails the
            games file has been put back as it was.
    """
    previous = games_path.read_bytes() if games_path.exists() else None
    games_config.write_games(games_path, config)
    try:
        pegasus_menu.write_menu(menu_path, menu)
    except Exception as error:
        try:
            if previous is None:
                games_path.unlink()
            else:
                games_config.atomic_write_bytes(games_path, previous)
        except Exception as restore_error:
            raise games_config.GamesConfigError(
                f"Menu update failed ({error}) and {games_path} could not be restored "
                f"({restore_error}); the two files may now disagree"
            ) from error
        raise games_config.GamesConfigError(
            f"Menu update failed ({error}); {games_path} was restored, nothing changed"
        ) from error


def _warn_if_default_game(games_path, game_id):
    """Warn when removing the game Arcade Station launches at startup."""
    default_config = games_path.parent / "default_config.toml"
    try:
        with default_config.open("rb") as handle:
            default_game = tomllib.load(handle).get("default_game", {}).get("default_game")
    except (OSError, tomllib.TOMLDecodeError, AttributeError):
        return
    if default_game == game_id:
        print(f"Warning: '{game_id}' is the default game launched at startup; "
              f"change default_game in {default_config}.", file=sys.stderr)


def cmd_list(options):
    """Print the configured games and whether each has a menu entry."""
    games = games_config.load_games(options.file)["games"]
    if not games:
        print("No games configured.")
        return 0
    in_menu = {block.game_id for block in pegasus_menu.load_menu(options.menu_file).blocks}
    rows = [("ID", "TYPE", "NAME", "TARGET", "MENU")]
    for game_id, entry in games.items():
        kind = games_config.entry_kind(entry)
        if kind == "string":
            name, target = "", entry
        else:
            name = entry.get("display_name", "")
            target = entry.get("rom" if kind == "mame" else "path", "")
        rows.append((game_id, kind, name, str(target), "yes" if game_id in in_menu else "no"))
    widths = [max(len(row[i]) for row in rows) for i in range(4)]
    for row in rows:
        print("  ".join(cell.ljust(width) for cell, width in zip(row, widths)) + "  " + row[4])
    return 0


def cmd_add(options):
    """Add a game to both files."""
    config = games_config.load_games(options.file)
    menu = pegasus_menu.load_menu(options.menu_file)
    game_id = options.game_id or games_config.new_game_id(config, options.name)
    if not options.game_id and not games_config.validate_game_id(game_id):
        raise games_config.ValidationError(
            f"Could not make a valid ID from the name {options.name!r} (got {game_id!r}); "
            "pass one with --id using lowercase letters, digits and underscores"
        )
    config = games_config.add_game(config, game_id, _fields(options))
    menu = pegasus_menu.upsert_game_block(menu, game_id, config["games"][game_id])
    _save(options.file, config, options.menu_file, menu)
    log_message(f"Games updater added '{game_id}'", "GAME")
    print(f"Added '{game_id}'. Restart Arcade Station to see it in the menu.")
    return 0


def cmd_update(options):
    """Change fields of a game in both files."""
    changes = _fields(options)
    for option in options.clear:
        key = FIELD_OPTIONS["launch_args" if option == "args" else option]
        if key in changes:
            raise games_config.ValidationError(f"Cannot both set and clear '{option}'")
        changes[key] = None
    if not changes:
        raise games_config.ValidationError("Nothing to update: give at least one field to change")

    config = games_config.update_game(
        games_config.load_games(options.file), options.game_id, changes
    )
    menu = pegasus_menu.upsert_game_block(
        pegasus_menu.load_menu(options.menu_file), options.game_id,
        config["games"][options.game_id], changed=changes.keys(),
    )
    _save(options.file, config, options.menu_file, menu)
    log_message(f"Games updater changed {sorted(changes)} for '{options.game_id}'", "GAME")
    print(f"Updated '{options.game_id}'. Restart Arcade Station to see the change.")
    return 0


def cmd_remove(options):
    """Remove a game from both files."""
    config = games_config.remove_game(games_config.load_games(options.file), options.game_id)
    menu, removed = pegasus_menu.remove_game_blocks(
        pegasus_menu.load_menu(options.menu_file), options.game_id
    )
    _save(options.file, config, options.menu_file, menu)
    log_message(f"Games updater removed '{options.game_id}'", "GAME")
    print(f"Removed '{options.game_id}'. Restart Arcade Station to update the menu.")
    if not removed:
        print(f"Note: '{options.game_id}' had no menu entry.", file=sys.stderr)
    _warn_if_default_game(options.file, options.game_id)
    return 0


COMMANDS = {"list": cmd_list, "add": cmd_add, "update": cmd_update, "remove": cmd_remove}


def main(argv=None):
    """
    Run the games updater.

    Args:
        argv: Arguments to parse; defaults to sys.argv[1:].

    Returns:
        int: 0 on success, 1 on an error (argparse exits with 2 on bad usage).
    """
    options = build_parser().parse_args(argv)
    try:
        return COMMANDS[options.command](options)
    except (games_config.GamesConfigError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
