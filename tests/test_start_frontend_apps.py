"""Characterization tests for start_frontend_apps.py — the boot-to-game path.

AGENTS.md flags this module at zero coverage and warns: "A green suite means
'the pinned behavior didn't move,' not 'this is safe.'" These tests pin the
CURRENT behavior of the startup orchestration — quirks included, such as the
fixed 5-second Pegasus sleep that is a delay and not a readiness check — so a
future refactor of the boot path has something to fail against. They assert what
the code does today, not what it ideally should do.

Every side effect outside the process is stubbed: no processes are launched, no
marquee is drawn, nothing sleeps for real, and the virtual environment on disk is
never mutated.
"""
import os

import pytest

from arcade_station import start_frontend_apps as sfa
from arcade_station.launchers import launch_game as launch_game_module

pytestmark = pytest.mark.characterization


@pytest.fixture(autouse=True)
def _silence_logging(monkeypatch):
    """log_message writes to a persistent file; keep the suite from touching it."""
    monkeypatch.setattr(sfa, "log_message", lambda *a, **k: None)


class _Proc:  # pylint: disable=too-few-public-methods
    """Stand-in for a launched process; only .pid is read by the module."""
    pid = 4242


# ---------------------------------------------------------------------------
# setup_virtual_environment
# ---------------------------------------------------------------------------
def test_setup_venv_true_when_already_in_a_venv(monkeypatch):
    """sys.prefix != sys.base_prefix short-circuits to success without touching disk."""
    monkeypatch.setattr(sfa.sys, "prefix", "/somewhere/.venv")
    monkeypatch.setattr(sfa.sys, "base_prefix", "/usr")
    assert sfa.setup_virtual_environment() is True


def test_setup_venv_false_when_venv_missing(monkeypatch):
    """Not in a venv and no .venv on disk returns False."""
    monkeypatch.setattr(sfa.sys, "prefix", "/usr")
    monkeypatch.setattr(sfa.sys, "base_prefix", "/usr")
    monkeypatch.setattr(sfa.os.path, "exists", lambda _p: False)
    assert sfa.setup_virtual_environment() is False


def test_setup_venv_activates_on_linux(monkeypatch):
    """Linux path prepends .venv/bin to PATH, sets VIRTUAL_ENV, drops PYTHONHOME."""
    monkeypatch.setattr(sfa.sys, "prefix", "/usr")
    monkeypatch.setattr(sfa.sys, "base_prefix", "/usr")
    monkeypatch.setattr(sfa, "determine_operating_system", lambda: "Linux")
    monkeypatch.setattr(sfa.os.path, "exists", lambda _p: True)
    env = {"PATH": "/bin", "PYTHONHOME": "/old"}
    monkeypatch.setattr(sfa.os, "environ", env)

    assert sfa.setup_virtual_environment() is True
    assert env["VIRTUAL_ENV"].endswith(".venv")
    assert env["PATH"].startswith(os.path.join(env["VIRTUAL_ENV"], "bin"))
    assert "PYTHONHOME" not in env


def test_setup_venv_activates_on_windows(monkeypatch):
    """Windows path prepends .venv/Scripts to PATH and sets VIRTUAL_ENV."""
    monkeypatch.setattr(sfa.sys, "prefix", "/usr")
    monkeypatch.setattr(sfa.sys, "base_prefix", "/usr")
    monkeypatch.setattr(sfa, "determine_operating_system", lambda: "Windows")
    monkeypatch.setattr(sfa.os.path, "exists", lambda _p: True)
    env = {"PATH": "C:\\Windows"}
    monkeypatch.setattr(sfa.os, "environ", env)

    assert sfa.setup_virtual_environment() is True
    assert env["VIRTUAL_ENV"].endswith(".venv")
    assert env["PATH"].startswith(os.path.join(env["VIRTUAL_ENV"], "Scripts"))


def test_setup_venv_false_when_activation_script_missing(monkeypatch):
    """.venv exists but its activate script does not — returns False."""
    monkeypatch.setattr(sfa.sys, "prefix", "/usr")
    monkeypatch.setattr(sfa.sys, "base_prefix", "/usr")
    monkeypatch.setattr(sfa, "determine_operating_system", lambda: "Linux")
    # The venv dir exists; the activate script inside it does not.
    monkeypatch.setattr(sfa.os.path, "exists", lambda p: "activate" not in p)
    monkeypatch.setattr(sfa.os, "environ", {"PATH": "/bin"})
    assert sfa.setup_virtual_environment() is False


def test_setup_venv_swallows_exceptions_and_returns_false(monkeypatch):
    """Any error during setup is caught and reported as False, never raised."""
    monkeypatch.setattr(sfa.sys, "prefix", "/usr")
    monkeypatch.setattr(sfa.sys, "base_prefix", "/usr")

    def boom():
        raise RuntimeError("disk gone")

    monkeypatch.setattr(sfa, "determine_operating_system", boom)
    monkeypatch.setattr(sfa.os.path, "exists", lambda _p: True)
    assert sfa.setup_virtual_environment() is False


# ---------------------------------------------------------------------------
# prepare_system
# ---------------------------------------------------------------------------
def test_prepare_system_kills_processes_and_returns_true(monkeypatch):
    """Kills from the canonical TOML, then returns True."""
    called = {}
    monkeypatch.setattr(sfa, "kill_processes_from_toml",
                        lambda name: called.setdefault("toml", name))
    monkeypatch.setattr(sfa.time, "sleep", lambda _s: None)

    assert sfa.prepare_system() is True
    assert called["toml"] == "processes_to_kill.toml"


def test_prepare_system_returns_false_on_error(monkeypatch):
    """A failure while killing processes is caught and reported as False."""
    def boom(_name):
        raise OSError("cannot kill")

    monkeypatch.setattr(sfa, "kill_processes_from_toml", boom)
    monkeypatch.setattr(sfa.time, "sleep", lambda _s: None)
    assert sfa.prepare_system() is False


# ---------------------------------------------------------------------------
# start_conditional_scripts
# ---------------------------------------------------------------------------
@pytest.fixture(name="conditional_env")
def fixture_conditional_env(monkeypatch):
    """Drive start_conditional_scripts with per-file configs, capturing launches."""
    launched = []
    osd_calls = []

    monkeypatch.setattr(sfa, "launch_script",
                        lambda script, identifier=None: (launched.append(identifier), _Proc())[1])
    monkeypatch.setattr(sfa, "launch_osd", lambda: (osd_calls.append(True), True)[1])

    def run(configs, os_type="Windows"):
        monkeypatch.setattr(sfa, "determine_operating_system", lambda: os_type)
        monkeypatch.setattr(sfa, "load_toml_config", lambda name: configs.get(name, {}))
        launched.clear()
        osd_calls.clear()
        sfa.start_conditional_scripts()
        return {"launched": launched, "osd": osd_calls}

    return run


def test_conditional_launches_nothing_when_all_disabled(conditional_env):
    """Empty configs launch no services."""
    result = conditional_env({})
    assert result["launched"] == []
    assert result["osd"] == []


def test_conditional_launches_vpn_when_enabled(conditional_env):
    result = conditional_env({"utility_config.toml": {"vpn": {"enabled": True}}})
    assert "connect_vpn" in result["launched"]


def test_conditional_launches_osd_on_windows(conditional_env):
    result = conditional_env({"utility_config.toml": {"osd": {"enabled": True}}},
                             os_type="Windows")
    assert result["osd"] == [True]


def test_conditional_skips_osd_off_windows(conditional_env):
    """OSD is Windows-only; enabled on Linux it must not launch."""
    result = conditional_env({"utility_config.toml": {"osd": {"enabled": True}}},
                             os_type="Linux")
    assert result["osd"] == []


def test_conditional_launches_itgmania_monitor(conditional_env):
    result = conditional_env({
        "display_config.toml": {
            "dynamic_marquee": {"enabled": True, "itgmania_display_enabled": True}
        }
    })
    assert "monitor_itgmania" in result["launched"]


def test_conditional_launches_icloud_only_on_windows(conditional_env):
    cfg = {"screenshot_config.toml": {"icloud_upload": {"enabled": True}}}
    assert "manage_icloud" in conditional_env(cfg, os_type="Windows")["launched"]
    assert "manage_icloud" not in conditional_env(cfg, os_type="Linux")["launched"]


def test_conditional_swallows_config_errors(monkeypatch):
    """A failure loading config is caught; the function returns without raising."""
    def boom(_name):
        raise ValueError("bad toml")

    monkeypatch.setattr(sfa, "load_toml_config", boom)
    assert sfa.start_conditional_scripts() is None


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
@pytest.fixture(name="main_env")
def fixture_main_env(monkeypatch):
    """Stub every seam main() touches; capture the launch sequence and game launch."""
    calls = {"launched": [], "game": None, "conditional": 0, "image": 0}

    monkeypatch.setattr(sfa.sys, "argv", ["start_frontend_apps.py"])
    monkeypatch.setattr(sfa, "setup_virtual_environment", lambda: True)
    monkeypatch.setattr(sfa, "prepare_system", lambda: True)
    monkeypatch.setattr(sfa, "display_image_from_config",
                        lambda **k: calls.__setitem__("image", calls["image"] + 1))
    monkeypatch.setattr(sfa, "launch_script",
                        lambda script, identifier=None: (calls["launched"].append(identifier), _Proc())[1])
    monkeypatch.setattr(sfa, "start_conditional_scripts",
                        lambda: calls.__setitem__("conditional", calls["conditional"] + 1))
    monkeypatch.setattr(sfa.time, "sleep", lambda _s: None)
    monkeypatch.setattr(launch_game_module, "launch_game",
                        lambda name: calls.__setitem__("game", name))

    def set_default_config(cfg):
        monkeypatch.setattr(sfa, "load_toml_config", lambda name: cfg)

    calls["set_default_config"] = set_default_config
    return calls


def test_main_startup_sequence_without_default_game(main_env):
    """The boot sequence runs its services and launches no game when disabled."""
    main_env["set_default_config"]({"default_game": {"default_game_start": False}})
    sfa.main()

    assert main_env["image"] == 1
    assert main_env["conditional"] == 1
    # key_listener before the Pegasus reset launcher, in that order.
    assert main_env["launched"] == ["key_listener", "kill_all_and_reset_pegasus"]
    assert main_env["game"] is None


def test_main_launches_default_game_when_configured(main_env):
    """default_game_start + a named game launches that game after the boot sequence."""
    main_env["set_default_config"]({
        "default_game": {"default_game_start": True, "default_game": "pump"}
    })
    sfa.main()
    assert main_env["game"] == "pump"


def test_main_skips_launch_when_default_game_unset(main_env):
    """default_game_start enabled but no game name launches nothing."""
    main_env["set_default_config"]({
        "default_game": {"default_game_start": True, "default_game": ""}
    })
    sfa.main()
    assert main_env["game"] is None


def test_main_shell_mode_keeps_alive_until_interrupt(main_env, monkeypatch):
    """--shell-mode enters the keep-alive loop and exits cleanly on interrupt."""
    main_env["set_default_config"]({"default_game": {"default_game_start": False}})
    monkeypatch.setattr(sfa.sys, "argv", ["start_frontend_apps.py", "--shell-mode"])

    def interrupt(_s):
        raise KeyboardInterrupt

    # The keep-alive loop's only sleep; raising here is the interrupt the loop
    # is written to catch. Must not propagate: main() returns cleanly.
    monkeypatch.setattr(sfa.time, "sleep", interrupt)
    sfa.main()
