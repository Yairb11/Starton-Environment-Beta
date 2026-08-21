"""Where Starton keeps its files, and what it writes into them.

The project ships two entry points at the repository root - ``SetupGUI.py``
(the editor) and ``OnSetup.py`` (the boot-time runner) - and both resolve
their paths through this module so they always agree.

Constants:
    INFO_DIR_NAME: Folder, relative to the project root, holding every
        generated file.
    LAUNCH_SCRIPT_NAME: Batch file copied into the Windows start-up folder.
    STARTUP_ENTRY_POINT: Entry point that batch file runs on every boot.
    STARTUP_FOLDER: Windows per-user start-up folder, unexpanded.
    EMPTY_SAVE_FILE: A brand new save file - both sections present but empty.
"""

import os
import sys
from pathlib import Path

INFO_DIR_NAME = "info"

LAUNCH_SCRIPT_NAME = "launch_apps.bat"

STARTUP_ENTRY_POINT = "OnSetup.py"

STARTUP_FOLDER = r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

EMPTY_SAVE_FILE = """<open_apps>
</open_apps>
<open_urls>
</open_urls>"""


def project_root():
    """Locate the folder holding the entry points and the ``info`` folder.

    Returns:
        Path: The folder ``SetupGUI.exe`` sits in when frozen by PyInstaller,
        otherwise the repository root.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.resolve()
    return Path(__file__).resolve().parents[1]


def info_dir():
    """Return the folder holding the save files and the launch script.

    Returns:
        Path: ``<project root>/info``.
    """
    return project_root() / INFO_DIR_NAME


def save_file_path(screens_connected, layout):
    """Build the save-file path for one monitor setup.

    Each monitor arrangement gets its own file, so plugging in a second screen
    gives you a separate environment instead of corrupting the first one.

    Args:
        screens_connected (int): Number of connected monitors.
        layout (str): Orientation signature from
            :func:`starton.monitors.layout_signature`.

    Returns:
        Path: ``<project root>/info/OnSetupInfo_2LL.txt`` and friends.
    """
    return info_dir() / f"OnSetupInfo_{screens_connected}{layout}.txt"


def startup_dir():
    """Return the Windows start-up folder for the current user.

    Returns:
        Path: The expanded start-up folder.
    """
    return Path(os.path.expandvars(STARTUP_FOLDER))


def launch_script_source():
    """Return the launch script Starton keeps inside its own folder.

    Returns:
        Path: ``<project root>/info/launch_apps.bat``.
    """
    return info_dir() / LAUNCH_SCRIPT_NAME


def launch_script_target():
    """Return the copy of the launch script Windows runs on boot.

    Returns:
        Path: ``<start-up folder>/launch_apps.bat``.
    """
    return startup_dir() / LAUNCH_SCRIPT_NAME


def launch_script_contents():
    """Build the batch file that starts the runner on boot.

    Returns:
        str: A batch script launching :data:`STARTUP_ENTRY_POINT` with
        ``pythonw`` so no console window appears.
    """
    return f'@echo off\nstart "" pythonw "{project_root() / STARTUP_ENTRY_POINT}"'
