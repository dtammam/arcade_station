"""Regression test for the installer's reset-and-reinstall path.

InstallLocationPage.validate() calls shutil.rmtree twice, at the point where the
user chooses "Reset and reinstall at this location". The module imported shutil
only inside a nested function belonging to a *different* method, so both calls
raised NameError.

Neither call crashed the installer. Both sit inside `except Exception`, and
NameError is a subclass of Exception, so the failure surfaced as a dialog
reading "Could not delete {item}. Please close any programs using files in this
directory and try again" - blaming a file lock that was never there. Because
every real installation contains subdirectories, the loop failed on the first
one and validate() always returned False, meaning that dialog option could never
succeed.

This is a structural assertion rather than a behavioral one. Driving validate()
directly would require a live Tk root, the surrounding wizard's app state, and
three modal dialogs, none of which belong in a suite that has to run headless.
Asserting the import is present is the cheapest check that fails before the fix
and passes after it.
"""
import pytest


@pytest.mark.characterization
def test_shutil_is_importable_at_module_level():
    """shutil must resolve from module scope, not from one nested function.

    validate() and the nested patched_copy() both use shutil, so a local import
    inside the latter cannot cover the former.
    """
    from installer.ui.pages import install_location_page

    assert hasattr(install_location_page, "shutil"), (
        "install_location_page uses shutil.rmtree in validate(); without a "
        "module-level import those calls raise NameError and the reset option "
        "silently fails."
    )


@pytest.mark.characterization
def test_module_level_names_used_by_validate_are_present():
    """The names validate() depends on at module scope all resolve.

    Guards the same class of defect for the other imports that method relies on.
    """
    from installer.ui.pages import install_location_page

    for name in ("os", "shutil", "messagebox"):
        assert hasattr(install_location_page, name), f"missing module-level {name}"
