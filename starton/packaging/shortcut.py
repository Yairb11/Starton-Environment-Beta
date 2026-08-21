"""Put a shortcut to the built executable on the Windows Desktop.

The shortcut points back at ``SetupGUI.exe`` where it was built, inside the
project folder, rather than the executable itself being copied to the Desktop.
That distinction matters: a frozen build treats the folder it sits in as the
project root, so an executable living on the Desktop would create a second,
empty ``info`` folder there and register a start-up entry pointing at an
``OnSetup.py`` that does not exist. A shortcut resolves to the real path and
leaves the project folder in charge.

The ``.lnk`` itself is written by :mod:`starton.packaging.windows_shell`.

Constants:
    SHORTCUT_NAME: Name shown under the Desktop icon, without ``.lnk``.
    SHORTCUT_DESCRIPTION: Tooltip Windows shows when hovering the shortcut.
"""

from starton.packaging import windows_shell

SHORTCUT_NAME = "Starton Environment"

SHORTCUT_DESCRIPTION = "Starton Environment - design your startup environment"


def shortcut_path():
    """Return where the Desktop shortcut belongs.

    Returns:
        Path: ``<Desktop>/Starton Environment.lnk``.
    """
    return windows_shell.desktop_dir() / f"{SHORTCUT_NAME}.lnk"


def create_desktop_shortcut(target, icon):
    """Create - or replace - the Desktop shortcut to the executable.

    Args:
        target (Path): The executable the shortcut should open.
        icon (Path): Icon file for the shortcut.

    Returns:
        Path: The shortcut that was written.

    Raises:
        OSError: If the Desktop cannot be found or the shortcut not saved.
    """
    return windows_shell.create_shortcut(
        shortcut_path(),
        target,
        icon=icon,
        description=SHORTCUT_DESCRIPTION,
        working_directory=target.parent,
    )
