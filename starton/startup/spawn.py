"""Start the boot-time runner on demand, the same way Windows does.

The editor uses this to open the saved environment without a reboot. Running
the real entry point in its own process, with the same ``pythonw`` command the
start-up batch file uses, means what the user sees is exactly what they will
get on the next boot - and the editor's event loop keeps running while apps
open, which can take a while.
"""

import shutil
import subprocess

from starton import config

PYTHON_COMMAND = "pythonw"

CREATE_NO_WINDOW = 0x08000000


def is_available():
    """Report whether the interpreter the start-up entry relies on is present.

    Returns:
        bool: ``True`` when ``pythonw`` can be found on the PATH.
    """
    return shutil.which(PYTHON_COMMAND) is not None


def run_environment():
    """Launch the saved environment in a detached process.

    Returns:
        subprocess.Popen: The started process.

    Raises:
        FileNotFoundError: If ``pythonw`` is not on the PATH, which also means
            the start-up entry could never have worked.
    """
    entry_point = config.project_root() / config.STARTUP_ENTRY_POINT
    return subprocess.Popen(
        [PYTHON_COMMAND, str(entry_point)],
        creationflags=CREATE_NO_WINDOW,
        cwd=str(config.project_root()),
    )
