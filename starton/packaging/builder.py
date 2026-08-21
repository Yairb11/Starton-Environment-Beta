"""Run the whole build: freeze the editor, then link it from the Desktop.

This is the only module in the project that prints. It is a build tool driven
from a terminal and is never frozen into the shipped executable, so writing
progress to stdout is safe here in a way it would not be anywhere else.
"""

import sys

from starton.packaging import executable, shortcut


def _prepare_output():
    """Make stdout able to carry the paths this build reports.

    The Desktop folder is often named in the user's own language, and those
    characters cannot survive the legacy code page Python falls back to when
    its output is piped into another program rather than shown in a console.
    Switching the stream to UTF-8 keeps the reported paths readable instead of
    ending the build with an encoding error after it has already succeeded.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def build():
    """Build ``SetupGUI.exe`` and place a shortcut to it on the Desktop.

    Progress and the resulting paths are printed as the build runs. Failures
    are reported as a single readable line rather than a traceback, since the
    interesting detail is almost always further up in PyInstaller's own output.

    Returns:
        int: ``0`` when the executable and the shortcut were both created,
        ``1`` if either step failed.
    """
    _prepare_output()
    print(f"Building {executable.executable_path().name} from {executable.ENTRY_POINT} ...")
    try:
        built = executable.build_executable()
        link = shortcut.create_desktop_shortcut(built, executable.icon_path())
    except (OSError, RuntimeError) as error:
        print(f"\nBuild failed: {error}")
        return 1

    print("\nBuild finished.")
    print(f"  Executable: {built}")
    print(f"  Shortcut:   {link}")
    return 0
