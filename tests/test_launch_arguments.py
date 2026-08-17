"""Characterization tests for the launch-argument config contract.

These pin the exact failure that motivated the feature: an entry written as

    path = "C:/.../msedge.exe" --start-fullscreen "https://..."

is not valid TOML. A key takes one value, so the trailing text is a parse error
that rejects the entire file and stops every game from launching. Splitting the
executable and its arguments into 'path' and 'args' is what makes it legal.
"""
import shlex
import tomllib

import pytest

GOOD_ENTRY = """
[games.filetube]
display_name = "filetube"
path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
args = '--start-fullscreen "https://example.com/watch.html?v=abc&ctx=%7B%22sort%22:%22x%22%7D"'
banner = "C:/banners/filetube.png"
"""

BROKEN_ENTRY = """
[games.filetube]
path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --start-fullscreen "https://example.com/"
"""

BASIC_STRING_ENTRY = """
[games.filetube]
args = "--start-fullscreen "https://example.com/""
"""


@pytest.mark.characterization
def test_arguments_appended_to_path_are_a_parse_error():
    """The original form fails, and it fails for the whole document."""
    with pytest.raises(tomllib.TOMLDecodeError):
        tomllib.loads(BROKEN_ENTRY)


@pytest.mark.characterization
def test_basic_string_cannot_hold_unescaped_quotes():
    """A double-quoted TOML string cannot wrap a value that itself uses quotes.

    This is why the documented form uses a literal (single-quoted) string.
    """
    with pytest.raises(tomllib.TOMLDecodeError):
        tomllib.loads(BASIC_STRING_ENTRY)


@pytest.mark.characterization
def test_split_path_and_args_entry_parses():
    """The documented form parses and keeps the quoted URL intact."""
    entry = tomllib.loads(GOOD_ENTRY)["games"]["filetube"]
    assert entry["path"].endswith("msedge.exe")
    assert entry["args"].startswith("--start-fullscreen ")
    assert '"https://example.com/watch.html' in entry["args"]


@pytest.mark.characterization
def test_percent_encoding_is_preserved_verbatim():
    """%22 and friends must not be unescaped or reinterpreted on the way through."""
    args = tomllib.loads(GOOD_ENTRY)["games"]["filetube"]["args"]
    assert "%7B%22sort%22:%22x%22%7D" in args


@pytest.mark.characterization
def test_shlex_split_yields_flag_and_url():
    """The non-Windows launch path splits args with shlex before Popen.

    shlex strips the surrounding quotes, so the URL arrives as a single argv
    entry even though it contains characters a naive split would break on.
    """
    args = tomllib.loads(GOOD_ENTRY)["games"]["filetube"]["args"]
    parts = shlex.split(args)
    assert parts[0] == "--start-fullscreen"
    assert len(parts) == 2
    assert parts[1].startswith("https://example.com/")
    assert '"' not in parts[1]
