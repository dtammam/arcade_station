"""Tests for the launch-argument feature.

An earlier version of this file asserted only against tomllib and shlex, so it
passed even with the feature deleted from launch_game.py entirely. Both review
seats reproduced that. These tests import the project code and drive it, so a
regression in the launch path fails here.

The TOML-format cases at the bottom are kept because the config contract is real
- an entry written as `path = "x.exe" --flag` is what took every game down - but
they are labelled for what they are: assertions about the file format, not about
the launcher.
"""
import shlex
import subprocess
import tomllib

import pytest

from arcade_station.core.common import core_functions
from arcade_station.core.common.core_functions import (
    quote_powershell_literal,
    redact_urls_for_log,
)
from arcade_station.launchers import launch_game as launch_game_module

ARGS_VALUE = '--start-fullscreen "https://example.com/watch.html?v=abc&ctx=%7B%22sort%22:%22x%22%7D"'


@pytest.fixture(name="captured_launch")
def fixture_captured_launch(monkeypatch):
    """Drive launch_game() with a synthetic config, capturing the launch call.

    Everything with a side effect outside the process is stubbed: the frontend
    is not killed, no marquee is drawn, nothing sleeps, and no process starts.
    """
    captured = {}

    def fake_start(file_path, working_dir=None, arguments=None):
        captured["file_path"] = file_path
        captured["working_dir"] = working_dir
        captured["arguments"] = arguments
        return True

    def fake_popen(command, *args, **kwargs):
        captured["command"] = command

        class _Proc:  # pylint: disable=too-few-public-methods
            pid = 4242

        return _Proc()

    monkeypatch.setattr(launch_game_module, "start_process_with_powershell", fake_start)
    monkeypatch.setattr(launch_game_module.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(
        launch_game_module,
        "log_message",
        lambda message, *a, **k: captured.setdefault("logs", []).append(str(message)),
    )
    monkeypatch.setattr(launch_game_module, "load_toml_config",
                        lambda _name: {"dynamic_marquee": {"enabled": False}})
    monkeypatch.setattr(launch_game_module, "kill_pegasus", lambda: None)
    monkeypatch.setattr(launch_game_module, "force_window_focus", lambda: None)
    monkeypatch.setattr(launch_game_module, "set_process_priority", lambda *a, **k: True)
    monkeypatch.setattr(launch_game_module.time, "sleep", lambda _s: None)
    monkeypatch.setattr(launch_game_module.os.path, "exists", lambda _p: True)
    monkeypatch.setattr(launch_game_module.os, "chdir", lambda _p: None)

    def run(entry, platform_name="Windows"):
        monkeypatch.setattr(launch_game_module.platform, "system", lambda: platform_name)
        monkeypatch.setattr(launch_game_module, "load_game_config",
                            lambda: {"games": {"demo": entry}})
        captured.clear()
        launch_game_module.launch_game("demo")
        return captured

    return run


def test_args_reach_the_windows_launch_call(captured_launch):
    """A configured 'args' value is forwarded to the PowerShell launcher."""
    result = captured_launch({"path": "C:/app/demo.exe", "args": ARGS_VALUE})
    assert result["arguments"] == ARGS_VALUE
    assert result["file_path"] == "C:/app/demo.exe"


def test_entry_without_args_passes_empty_string(captured_launch):
    """Entries with no 'args' must behave exactly as they did before the feature.

    start_process_with_powershell omits the -Arguments parameter entirely when
    the value is falsy, so this is what preserves the original behavior.
    """
    result = captured_launch({"path": "C:/app/demo.exe"})
    assert result["arguments"] == ""


def test_args_are_shlex_split_on_non_windows(captured_launch):
    """The POSIX path splits args and appends them to the executable."""
    result = captured_launch({"path": "/opt/app/demo", "args": ARGS_VALUE}, platform_name="Linux")
    command = result["command"]
    # Length first, so a dropped split fails as an assertion rather than IndexError.
    assert len(command) == 3, f"expected executable + 2 split args, got {command!r}"
    assert command[0] == "/opt/app/demo"
    assert command[1] == "--start-fullscreen"
    assert command[2].startswith("https://example.com/")


def test_non_windows_entry_without_args_is_bare_command(captured_launch):
    """No args means the command is the executable alone, not a one-element split."""
    result = captured_launch({"path": "/opt/app/demo"}, platform_name="Linux")
    assert result["command"] == ["/opt/app/demo"]


def test_rom_entries_never_reach_the_binary_launcher(captured_launch):
    """MAME entries branch away before the args handling is consulted."""
    result = captured_launch({"rom": "ddrmax", "state": "o"})
    assert "arguments" not in result


class TestPowerShellQuoting:
    """quote_powershell_literal is what keeps a config value from becoming code."""

    def test_plain_value_is_wrapped(self):
        assert quote_powershell_literal("--flag") == "'--flag'"

    def test_single_quote_is_doubled(self):
        """PowerShell escapes ' by doubling it; anything else ends the string."""
        assert quote_powershell_literal("it's") == "'it''s'"

    def test_injection_payload_is_neutralised(self):
        payload = "--x '; Write-Output PWNED; '"
        quoted = quote_powershell_literal(payload)
        assert quoted == "'--x ''; Write-Output PWNED; '''"
        assert quoted.startswith("'") and quoted.endswith("'")

    def test_real_argument_value_is_unchanged_apart_from_wrapping(self):
        """The documented filetube-style value contains no single quotes."""
        assert quote_powershell_literal(ARGS_VALUE) == f"'{ARGS_VALUE}'"

    @pytest.mark.skipif(not hasattr(subprocess, "CREATE_NO_WINDOW"),
                        reason="requires Windows PowerShell")
    def test_payload_does_not_execute_in_real_powershell(self):
        """End-to-end: PowerShell binds the payload as data, not as code."""
        payload = "--x '; Write-Output PWNED-MARKER; '"
        stub = ("function Take { param([string]$Arguments) "
                "Write-Output \"ARGS=[$Arguments]\" }; Take -Arguments ")
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", stub + quote_powershell_literal(payload)],
            capture_output=True, text=True, check=False,
        )
        echoed = [ln for ln in result.stdout.splitlines() if ln.startswith("ARGS=[")]
        others = [ln for ln in result.stdout.splitlines() if not ln.startswith("ARGS=[")]
        assert echoed == [f"ARGS=[{payload}]"]
        assert not any("PWNED-MARKER" in line for line in others)


class TestConfigFileFormat:
    """Assertions about the TOML file format itself, not about the launcher.

    These pin why the documented entry shape is what it is. They exercise
    tomllib rather than project code, and are grouped here so that is explicit.
    """

    GOOD = (
        '[games.demo]\n'
        'path = "C:/app/demo.exe"\n'
        f"args = '{ARGS_VALUE}'\n"
    )
    BROKEN = '[games.demo]\npath = "C:/app/demo.exe" --start-fullscreen "https://example.com/"\n'

    def test_arguments_appended_to_path_are_a_parse_error(self):
        """The original filetube entry shape; it rejects the whole document."""
        with pytest.raises(tomllib.TOMLDecodeError):
            tomllib.loads(self.BROKEN)

    def test_documented_form_parses_and_keeps_the_quoted_url(self):
        entry = tomllib.loads(self.GOOD)["games"]["demo"]
        assert entry["args"] == ARGS_VALUE
        assert shlex.split(entry["args"])[0] == "--start-fullscreen"


class TestLogRedaction:
    """Launch arguments reach the log, so a URL query string must not.

    'args' is hand-edited and routinely holds a URL. Before the feature existed
    this log line always received None, so nothing was written; now it receives
    whatever the entry declares, on every launch, into a file that persists.
    """

    def test_query_string_is_removed_but_the_url_is_still_identifiable(self):
        """The diagnosable part survives; the part that could hold a token does not."""
        redacted = redact_urls_for_log(ARGS_VALUE)
        assert "v=abc" not in redacted
        assert "%22sort%22" not in redacted
        assert "https://example.com/watch.html?<redacted>" in redacted
        assert redacted.startswith("--start-fullscreen")

    def test_a_credential_bearing_query_string_does_not_survive(self):
        """The case this exists for."""
        assert "s3cr3t" not in redact_urls_for_log(
            "--url https://example.com/stream?token=s3cr3t"
        )

    def test_arguments_without_a_url_are_untouched(self):
        """A bare '?' is a wildcard or a batch parameter, not a query string."""
        assert redact_urls_for_log("--kiosk --profile C:/Users/x/AppData") == (
            "--kiosk --profile C:/Users/x/AppData"
        )
        assert redact_urls_for_log("/select ?foo") == "/select ?foo"

    def test_none_passes_through(self):
        """Entries without 'args' hand None to the launcher; that must not become 'None'."""
        assert redact_urls_for_log(None) is None

    def test_the_full_powershell_command_is_redacted_too(self):
        """The constructed command embeds the same value, so it needs the same treatment."""
        command = f"Start-ProcessSilently -Arguments {quote_powershell_literal(ARGS_VALUE)}"
        assert "v=abc" not in redact_urls_for_log(command)

    def test_launch_game_does_not_log_the_query_string_either(self, captured_launch):
        """The launcher logs the args itself, two frames before the helper sees them.

        The first version of this fix redacted only inside
        start_process_with_powershell, which left launch_game's own two log
        lines writing the value verbatim. Driving launch_game end to end is the
        only way to catch that, so this test does.
        """
        secret = '--start-fullscreen "https://example.com/watch.html?token=s3cr3t&v=abc"'
        result = captured_launch({"path": "C:/app/demo.exe", "args": secret})
        written = "\n".join(result.get("logs", []))
        assert written, "precondition: launch_game should have logged something"
        assert "s3cr3t" not in written, "credential reached the log from launch_game"
        assert "v=abc" not in written
        assert result["arguments"] == secret, (
            "redaction must apply to the log only - the launched process still "
            "needs the real arguments"
        )

    def test_the_launcher_actually_calls_it(self, monkeypatch):
        """Wiring, not availability.

        The tests above prove the helper works. This one proves it is reached:
        without it they would all still pass with both call sites deleted.
        """
        logged = []
        monkeypatch.setattr(
            core_functions, "log_message", lambda message, *a, **k: logged.append(str(message))
        )

        class _Proc:  # pylint: disable=too-few-public-methods
            pid = 4242

        monkeypatch.setattr(
            core_functions.subprocess, "Popen", lambda *a, **k: _Proc()
        )
        core_functions.start_process_with_powershell(
            "C:/app/demo.exe", arguments=ARGS_VALUE
        )
        written = "\n".join(logged)
        assert written, "precondition: the launcher should have logged something"
        assert "v=abc" not in written, "query string reached the log"
        assert "%22sort%22" not in written
        assert "<redacted>" in written
