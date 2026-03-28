"""Unit tests for arcade_station.core.common.core_functions pure/config functions."""

import io
import logging
import re
import tomllib
from unittest.mock import MagicMock, patch

import pytest

from arcade_station.core.common.core_functions import (
    convert_path_for_platform,
    determine_operating_system,
    load_game_config,
    load_installed_games,
    load_key_mappings_from_toml,
    load_mame_config,
    load_toml_config,
    log_message,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _bytes_open_cm(content: bytes) -> MagicMock:
    """Return a MagicMock that behaves as a binary-mode context manager.

    Args:
        content: Raw bytes to serve as file contents.

    Returns:
        MagicMock: A mock whose ``__enter__`` returns ``io.BytesIO(content)``
            so it can be used directly as the return value of a patched
            ``builtins.open``.
    """
    cm: MagicMock = MagicMock()
    cm.__enter__ = MagicMock(return_value=io.BytesIO(content))
    cm.__exit__ = MagicMock(return_value=False)
    return cm


# ---------------------------------------------------------------------------
# determine_operating_system
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("os_name", ["Windows", "Linux", "Darwin"])
def test_determine_operating_system_returns_platform_system(os_name: str) -> None:
    """Verify determine_operating_system returns whatever platform.system() reports.

    Args:
        os_name: The string that platform.system() is mocked to return.
    """
    with patch(
        "arcade_station.core.common.core_functions.platform.system",
        return_value=os_name,
    ):
        result = determine_operating_system()

    assert result == os_name


# ---------------------------------------------------------------------------
# convert_path_for_platform
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "input_path, mock_os, expected",
    [
        # Forward-slash path on Windows -> backslashes
        ("path/to/file", "Windows", "path\\to\\file"),
        # Backslash path on Linux -> forward slashes
        ("path\\to\\file", "Linux", "path/to/file"),
        # None input -> returns None unchanged (falsy early-return branch)
        (None, "Linux", None),
        # Empty string input -> returns empty string (same falsy branch as None)
        ("", "Windows", ""),
        # Backslash-only path on Windows -> stays as backslashes
        ("path\\to\\file", "Windows", "path\\to\\file"),
        # Forward-slash-only path on Darwin -> stays as forward slashes
        ("path/to/file", "Darwin", "path/to/file"),
    ],
)
def test_convert_path_for_platform(
    input_path: str | None,
    mock_os: str,
    expected: str | None,
) -> None:
    """Verify path-separator conversion for each platform and edge case.

    Args:
        input_path: The path string passed to the function under test.
        mock_os: The value that ``platform.system()`` is mocked to return.
        expected: The expected return value after conversion.
    """
    with patch(
        "arcade_station.core.common.core_functions.platform.system",
        return_value=mock_os,
    ):
        result = convert_path_for_platform(input_path)

    assert result == expected


# ---------------------------------------------------------------------------
# load_toml_config
# ---------------------------------------------------------------------------


def test_load_toml_config_valid_toml_returns_dict() -> None:
    """Verify that load_toml_config parses a valid TOML file into a dict.

    Patches ``builtins.open`` so no real filesystem access occurs.
    """
    toml_bytes = b'[section]\nkey = "value"\n'
    mock_cm = _bytes_open_cm(toml_bytes)

    with patch("builtins.open", return_value=mock_cm):
        result = load_toml_config("any_config.toml")

    assert result == {"section": {"key": "value"}}


def test_load_toml_config_missing_file_raises_file_not_found_error() -> None:
    """Verify that load_toml_config raises FileNotFoundError when the file is absent.

    Patches ``builtins.open`` to raise ``FileNotFoundError`` simulating a
    missing configuration file.
    """
    with patch("builtins.open", side_effect=FileNotFoundError("no such file")):
        with pytest.raises(FileNotFoundError):
            load_toml_config("missing.toml")


def test_load_toml_config_invalid_toml_raises_decode_error() -> None:
    """Verify that load_toml_config raises TOMLDecodeError for malformed TOML.

    Patches ``builtins.open`` to return a file object containing invalid TOML
    syntax, expecting tomllib to surface a TOMLDecodeError.
    """
    # This is not valid TOML: bare word without quotes or proper type
    invalid_bytes = b"= broken toml\n"
    mock_cm = _bytes_open_cm(invalid_bytes)

    with patch("builtins.open", return_value=mock_cm):
        with pytest.raises(tomllib.TOMLDecodeError):
            load_toml_config("bad.toml")


# ---------------------------------------------------------------------------
# load_key_mappings_from_toml
# ---------------------------------------------------------------------------


def test_load_key_mappings_from_toml_with_key_mappings_returns_entries() -> None:
    """Verify that key_mappings entries are returned when the TOML contains them.

    Mocks ``load_toml_config`` to return a config dict containing a
    ``key_mappings`` table with real entries.
    """
    fake_config = {"key_mappings": {"ctrl+f1": "launch_game.py", "ctrl+f2": "menu.py"}}

    with patch(
        "arcade_station.core.common.core_functions.load_toml_config",
        return_value=fake_config,
    ):
        result = load_key_mappings_from_toml("hotkeys.toml")

    assert result == {"ctrl+f1": "launch_game.py", "ctrl+f2": "menu.py"}


def test_load_key_mappings_from_toml_no_key_mappings_key_returns_empty_dict() -> None:
    """Verify that an empty dict is returned when the config has no key_mappings key.

    Mocks ``load_toml_config`` to return a config that contains an unrelated
    key, exercising the ``config.get("key_mappings", {})`` miss branch and the
    subsequent ``if not key_mappings`` branch.
    """
    fake_config = {"other": "data"}

    with patch(
        "arcade_station.core.common.core_functions.load_toml_config",
        return_value=fake_config,
    ):
        result = load_key_mappings_from_toml("hotkeys.toml")

    assert result == {}


# ---------------------------------------------------------------------------
# load_installed_games / load_game_config / load_mame_config
# ---------------------------------------------------------------------------


def test_load_installed_games_calls_load_toml_config_with_correct_filename() -> None:
    """Verify load_installed_games calls load_toml_config('pegasus_binaries.toml').

    Mocks ``load_toml_config`` and asserts it is called with the expected
    filename, confirming the function's internal wiring.
    """
    with patch(
        "arcade_station.core.common.core_functions.load_toml_config",
        return_value={},
    ) as mock_load:
        load_installed_games()

    mock_load.assert_called_once_with("pegasus_binaries.toml")


def test_load_game_config_calls_load_toml_config_with_correct_filename() -> None:
    """Verify load_game_config calls load_toml_config('installed_games.toml').

    Mocks ``load_toml_config`` and asserts it is called with the expected
    filename.
    """
    with patch(
        "arcade_station.core.common.core_functions.load_toml_config",
        return_value={},
    ) as mock_load:
        load_game_config()

    mock_load.assert_called_once_with("installed_games.toml")


def test_load_mame_config_calls_load_toml_config_with_correct_filename() -> None:
    """Verify load_mame_config delegates to load_toml_config with 'mame_config.toml'.

    Mocks ``load_toml_config`` and asserts it is called with the expected
    filename.
    """
    with patch(
        "arcade_station.core.common.core_functions.load_toml_config",
        return_value={},
    ) as mock_load:
        load_mame_config()

    mock_load.assert_called_once_with("mame_config.toml")


# ---------------------------------------------------------------------------
# log_message
# ---------------------------------------------------------------------------

_TIMESTAMP_PATTERN = re.compile(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]")


def test_log_message_with_prefix_formats_correctly(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify that log_message includes the prefix and message in the log output.

    Captures log records at INFO level and checks that the formatted entry
    contains ``[PREFIX]``, the message text, and a timestamp in the expected
    format ``[YYYY-MM-DD HH:MM:SS]``.
    """
    with caplog.at_level(logging.INFO):
        log_message("hello world", "MENU")

    assert len(caplog.records) >= 1
    combined = " ".join(r.getMessage() for r in caplog.records)
    assert "[MENU]" in combined
    assert "hello world" in combined
    assert _TIMESTAMP_PATTERN.search(combined) is not None


def test_log_message_without_prefix_omits_empty_brackets(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify that calling log_message with no prefix omits the ``[] `` bracket pattern.

    Captures log records at INFO level and asserts that the message text is
    present but the ``[] `` empty-prefix pattern is absent, confirming the
    correct branch of the if/else in log_message.
    """
    with caplog.at_level(logging.INFO):
        log_message("bare message")

    combined = " ".join(r.getMessage() for r in caplog.records)
    assert "bare message" in combined
    assert "[] " not in combined
