"""A drop-down for jumping straight to any saved app.

Constants:
    EMPTY_TEXT: Shown, greyed out, when nothing has been saved yet.
    PLACEHOLDER_TEXT: Shown while no app is selected.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox

from starton.gui import styles

EMPTY_TEXT = "No apps yet"

PLACEHOLDER_TEXT = "Select an app"


class AppPicker(QComboBox):
    """A combo box naming every saved app, showing the selected one.

    Each row carries its :class:`App` as item data rather than being matched
    back by name, so renaming an app cannot point the picker at the wrong one.

    Signals:
        app_chosen: Emitted with the app the user picked.
    """

    app_chosen = pyqtSignal(object)

    def __init__(self, parent=None):
        """Build the combo box.

        Args:
            parent (QWidget, optional): Qt parent. Defaults to ``None``.
        """
        super().__init__(parent)
        self.setStyleSheet(styles.APP_COMBO)
        self.setPlaceholderText(PLACEHOLDER_TEXT)
        self.setToolTip("Jump to an app")
        self.activated.connect(self._on_activated)

    def set_apps(self, apps, current_app):
        """Rebuild the list and show whichever app is selected.

        Signals are blocked while the rows are replaced: clearing a combo box
        moves its current index, and an unblocked rebuild would report that as
        a choice the user never made.

        Args:
            apps (list | None): Every saved app, or ``None`` when none exist.
            current_app (App | None): The app to show, or ``None`` to fall back
                to the placeholder.
        """
        self.blockSignals(True)
        self.clear()
        if not apps:
            self.addItem(EMPTY_TEXT)
            self.model().item(0).setEnabled(False)
        for app in apps or []:
            self.addItem(app.get_name(), app)
        self.setCurrentIndex(self._index_of(current_app))
        self.blockSignals(False)

    def _index_of(self, current_app):
        """Find a row by identity rather than by equality.

        Two apps can render identically while one of them is being edited, and
        matching on equality would let the picker settle on the other one.

        Args:
            current_app (App | None): The app to look for.

        Returns:
            int: Its row, or ``-1`` when it is not listed, which shows the
            placeholder instead.
        """
        for index in range(self.count()):
            if self.itemData(index) is current_app:
                return index
        return -1

    def _on_activated(self, index):
        """Report the app behind the row the user clicked.

        Args:
            index (int): The row activated.
        """
        chosen = self.itemData(index)
        if chosen is not None:
            self.app_chosen.emit(chosen)
