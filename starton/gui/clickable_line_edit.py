"""A read-only line edit that reports clicks."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLineEdit


class ClickableLineEdit(QLineEdit):
    """A line edit the user picks a value into instead of typing one.

    The field is read only, so clicking it can mean "open a picker" rather than
    "place a caret". It is used for the app path, where clicking the text opens
    a folder browser.

    Signals:
        clicked: Emitted on every left click.
    """

    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        """Create the field read only, with a pointing-hand cursor."""
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        """Emit :attr:`clicked` for left clicks.

        Args:
            event: The Qt mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
