from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal

class ClickableLineEdit(QLineEdit):
    """Extension to QLineEdit widget that makes the QLineEdit readonly
    And on click it does some custom function

    Attributes:
        clicked (pyqtSignal): Stores the custom function
    """
    clicked = pyqtSignal()
    def __init__(self, *args, **kwargs):
        """Initializes the QLineEdit to readonly
        """
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    def mousePressEvent(self, event):
        """Runs the function that is stored on clicked when we press the left button on the mouse

        Args:
            event: the event information
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)