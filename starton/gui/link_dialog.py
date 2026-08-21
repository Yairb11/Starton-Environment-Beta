"""The popup for editing a saved link's name and address.

Constants:
    FIELD_WIDTH: Width of the dialog, wide enough for a realistic URL without
        the fields having to scroll.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from starton.gui import styles
from starton.models import Link

FIELD_WIDTH = 420


class LinkDialog(QDialog):
    """A name field and a URL field over SAVE and CANCEL.

    The dialog refuses to close on values the save file could not hold, so a
    link that has been edited is always a link that can be read back.
    """

    def __init__(self, link, parent=None):
        """Fill the fields from the link being edited.

        Args:
            link (Link): The link whose values the fields start at.
            parent (QWidget, optional): Qt parent. Defaults to ``None``.
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Link")
        self.setStyleSheet(styles.INFO_PANEL)
        self.setMinimumWidth(FIELD_WIDTH)

        self.name_input = self._build_input(link.get_name(), "Link Name (e.g., GitHub)")
        self.link_input = self._build_input(link.get_link(), "https://...")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        layout.addLayout(self._build_fields())
        layout.addLayout(self._build_buttons())

    def _build_input(self, text, placeholder):
        """Create one pre-filled field.

        Args:
            text (str): Value the field starts at.
            placeholder (str): Hint shown once the field is emptied.

        Returns:
            QLineEdit: The field.
        """
        field = QLineEdit(text)
        field.setPlaceholderText(placeholder)
        field.setStyleSheet(styles.LINK_INPUT)
        return field

    def _build_fields(self):
        """Lay the two labelled fields out in a grid.

        Returns:
            QGridLayout: The field grid.
        """
        fields_layout = QGridLayout()
        fields_layout.setSpacing(8)
        for row, (text, field) in enumerate(
            (("Name:", self.name_input), ("Link:", self.link_input))
        ):
            label = QLabel(text)
            label.setStyleSheet(styles.LABEL)
            fields_layout.addWidget(label, row, 0)
            fields_layout.addWidget(field, row, 1)
        return fields_layout

    def _build_buttons(self):
        """Build the CANCEL and SAVE row.

        Returns:
            QHBoxLayout: The button row.
        """
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setStyleSheet(styles.DELETE_BTN)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("SAVE")
        save_btn.setStyleSheet(styles.SAVE_BTN)
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        return buttons_layout

    def get_values(self):
        """Return the edited name and address.

        Returns:
            tuple: ``(name, link)``, both stripped of surrounding whitespace.
        """
        return self.name_input.text().strip(), self.link_input.text().strip()

    def accept(self):
        """Close with the edit, unless the values could not be saved."""
        problem = Link.problem(*self.get_values())
        if problem:
            QMessageBox.warning(self, "Missing Info", problem)
            return
        super().accept()
