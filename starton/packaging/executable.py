"""Freeze the editor into a single console-less ``SetupGUI.exe``.

PyInstaller is driven in-process through :mod:`PyInstaller.__main__` rather
than as a subprocess, so the build inherits the interpreter and environment it
was started with instead of guessing at one.

The executable is written to the repository root, not to ``dist``. That is
deliberate: :func:`starton.config.project_root` resolves to the folder the
frozen executable sits in, and everything else - the ``info`` folder, the
start-up batch file - hangs off that. Building anywhere else would hand the
shipped application the wrong idea of where the project lives.

Constants:
    EXECUTABLE_NAME: Base name of the executable, without its extension.
    ENTRY_POINT: Script PyInstaller freezes, relative to the project root.
    ICON_PATH: Executable icon, relative to the project root.
    WORK_DIR_PREFIX: Prefix for the throwaway directory PyInstaller works in.
"""

import shutil
import tempfile
from pathlib import Path

from starton import config

EXECUTABLE_NAME = "SetupGUI"

ENTRY_POINT = "GUI.py"

ICON_PATH = Path("icons") / "SetupGUIIcon.ico"

WORK_DIR_PREFIX = "starton-build-"


def entry_point_path():
    """Return the script that becomes the executable.

    Returns:
        Path: ``<project root>/GUI.py``.
    """
    return config.project_root() / ENTRY_POINT


def icon_path():
    """Return the icon baked into the executable and the Desktop shortcut.

    Returns:
        Path: ``<project root>/icons/SetupGUIIcon.ico``.
    """
    return config.project_root() / ICON_PATH


def executable_path():
    """Return where the finished executable lands.

    Returns:
        Path: ``<project root>/SetupGUI.exe``.
    """
    return config.project_root() / f"{EXECUTABLE_NAME}.exe"


def _pyinstaller_arguments(work_dir):
    """Assemble the PyInstaller command line.

    ``--windowed`` is what keeps a console window from appearing behind the
    editor. It is safe here only because no module in the ``starton`` package
    writes to stdout or stderr, which a windowed build sets to ``None``.

    Both ``--workpath`` and ``--specpath`` point at the same throwaway
    directory, so the generated ``build`` tree and ``SetupGUI.spec`` are
    cleaned up together and never appear in the repository.

    Args:
        work_dir (Path): Scratch directory for PyInstaller's intermediate
            files and the generated spec file.

    Returns:
        list[str]: Arguments ready for :func:`PyInstaller.__main__.run`.
    """
    return [
        str(entry_point_path()),
        "--name",
        EXECUTABLE_NAME,
        "--onefile",
        "--windowed",
        "--icon",
        str(icon_path()),
        "--distpath",
        str(config.project_root()),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(work_dir),
        "--noconfirm",
        "--clean",
    ]


def build_executable():
    """Freeze the editor and return the executable that was produced.

    Returns:
        Path: The finished ``SetupGUI.exe``.

    Raises:
        FileNotFoundError: If the entry point or the icon is missing.
        RuntimeError: If PyInstaller fails, or reports success without
            leaving an executable behind.
    """
    import PyInstaller.__main__

    for required in (entry_point_path(), icon_path()):
        if not required.exists():
            raise FileNotFoundError(f"Required file is missing: {required}")

    work_dir = Path(tempfile.mkdtemp(prefix=WORK_DIR_PREFIX))
    try:
        PyInstaller.__main__.run(_pyinstaller_arguments(work_dir))
    except SystemExit as stop:
        if stop.code:
            raise RuntimeError(f"PyInstaller exited with code {stop.code}") from stop
    except Exception as error:
        raise RuntimeError(f"PyInstaller failed: {error}") from error
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    built = executable_path()
    if not built.exists():
        raise RuntimeError(f"PyInstaller reported success but {built} is missing")
    return built
