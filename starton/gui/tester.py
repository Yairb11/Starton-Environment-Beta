"""Open one app in the background so the editor can preview a single window.

Launching an app and waiting for its window takes up to ten seconds, which
would freeze the editor if it ran on the main thread. The work happens on a
worker thread instead; it touches only ``os.startfile`` and the ctypes calls
in :mod:`starton.startup.window_manager`, never a Qt widget. The monitor
measurements it needs are taken on the main thread and handed over as values.
"""

from PyQt6.QtCore import QThread, pyqtSignal

from starton.startup import runner


class AppTester(QThread):
    """Launches one app and places its window, off the main thread.

    Signals:
        finished_test: Emitted with an error message when the launch failed,
            or an empty string when it worked.
    """

    finished_test = pyqtSignal(str)

    def __init__(self, app, screens, work_areas, parent=None):
        """Capture everything the worker needs before it starts.

        Args:
            app (App): The app to launch, as currently edited in the panel.
            screens (list): Every connected monitor.
            work_areas (list): Usable area of each monitor, taskbar excluded.
            parent (QObject, optional): Qt parent. Defaults to ``None``.
        """
        super().__init__(parent)
        self.app = app
        self.screens = screens
        self.work_areas = work_areas

    def run(self):
        """Launch the app and report how it went."""
        try:
            runner.launch_and_place(self.app, self.screens, self.work_areas)
        except OSError as error:
            self.finished_test.emit(str(error))
            return
        self.finished_test.emit("")
