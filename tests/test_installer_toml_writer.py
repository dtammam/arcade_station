"""Characterization tests for the installer's fallback TOML writer.

InstallationManager._write_toml prefers tomli_w and falls back to hand-rolled
writing when it is unavailable. Only the fallback is exercised here, because it
is the path that can emit syntactically invalid TOML: it previously interpolated
values straight into a quoted string, so a Windows path or an argument
containing a quoted URL produced a file that tomllib refused to parse.
"""
import tomllib

import pytest

from installer.config.installation import InstallationManager

ARGS_VALUE = (
    '--start-fullscreen "https://example.com/watch.html'
    '?v=abc&ctx=%7B%22sort%22:%22release-date%22%7D"'
)


@pytest.fixture(name="manager", scope="module")
def fixture_manager():
    """An InstallationManager used only for its TOML writing helpers."""
    return InstallationManager()


def write_and_reload(manager, tmp_path, data):
    """Write data through the fallback writer and parse the result back."""
    target = tmp_path / "out.toml"
    manager._write_toml_manually(str(target), data)  # pylint: disable=protected-access
    with target.open("rb") as handle:
        return tomllib.load(handle)


@pytest.mark.characterization
def test_launch_arguments_survive_embedded_quotes(manager, tmp_path):
    """An args value wrapping a URL in double quotes round-trips byte for byte."""
    result = write_and_reload(manager, tmp_path, {"games": {"demo": {"args": ARGS_VALUE}}})
    assert result["games"]["demo"]["args"] == ARGS_VALUE


@pytest.mark.characterization
def test_windows_backslashes_in_non_path_keys_round_trip(manager, tmp_path):
    """logdirectory keeps its backslashes; they are escaped, not rewritten.

    'logdirectory' does not match the path-like key heuristic, so the value is
    preserved as given rather than converted to forward slashes.
    """
    raw = r"C:\Games\arcade_station\config\logs"
    result = write_and_reload(manager, tmp_path, {"logging": {"logdirectory": raw}})
    assert result["logging"]["logdirectory"] == raw


@pytest.mark.characterization
def test_path_like_keys_are_rewritten_to_forward_slashes(manager, tmp_path):
    """Existing behavior: keys containing path/banner/rom/state get slash conversion.

    This is pinned as-is. It is why 'path' values never carry backslashes into
    the emitted config, and any change to the heuristic should fail here first.
    """
    result = write_and_reload(
        manager, tmp_path, {"games": {"demo": {"path": r"C:\Program Files\App\app.exe"}}}
    )
    assert result["games"]["demo"]["path"] == "C:/Program Files/App/app.exe"


@pytest.mark.characterization
def test_booleans_are_lowercased(manager, tmp_path):
    """TOML requires lowercase booleans; Python's str() would emit True/False."""
    result = write_and_reload(manager, tmp_path, {"default_game": {"default_game_start": True}})
    assert result["default_game"]["default_game_start"] is True


@pytest.mark.characterization
def test_default_game_section_round_trips(manager, tmp_path):
    """The section the installer now emits parses back to what went in."""
    data = {"default_game": {"default_game_start": False, "default_game": "itgmania"}}
    assert write_and_reload(manager, tmp_path, data)["default_game"] == data["default_game"]
