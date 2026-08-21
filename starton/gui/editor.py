"""Start the editor: load the saved environment and open the window.

Constants:
    QT_ENVIRONMENT: Qt is pinned to 96 DPI with scaling off. The editor works
        in raw pixel coordinates that have to match the ones the Win32 calls
        use at boot, and Qt's high-DPI scaling would silently rescale them.

        The platform entry declares the DPI awareness the process already has.
        ``python.exe`` ships a manifest marking itself system DPI aware, and
        Windows will not let that be changed once the process is running, so
        Qt's own attempt to switch to per-monitor awareness fails and is
        reported every launch. Asking for the awareness that is already in
        force stops Qt trying, and changes nothing about how the editor runs.
"""

import os
import sys

from PyQt6 import QtWidgets

from starton import monitors
from starton.gui.main_window import MainWindow
from starton.installer import prepare_environment
from starton.storage import SaveFile

QT_ENVIRONMENT = {
    "QT_ENABLE_HIGHDPI_SCALING": "0",
    "QT_AUTO_SCREEN_SCALE_FACTOR": "0",
    "QT_FONT_DPI": "96",
    "QT_QPA_PLATFORM": "windows:dpiawareness=1",
}


def run():
    """Open the editor full screen and block until the user closes it.

    The window state is set here rather than while the window is being built,
    so nothing that happens during construction can undo it. ``F11`` and
    ``Esc`` hand a normal window back.

    Returns:
        int: Qt's exit code, ready to hand to :func:`sys.exit`.
    """
    save_file = SaveFile(prepare_environment())
    screens = monitors.get_screens()
    apps, links = save_file.read_file()

    os.environ.update(QT_ENVIRONMENT)
    desktop_app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(screens, apps, links, save_file)
    window.showFullScreen()
    return desktop_app.exec()
