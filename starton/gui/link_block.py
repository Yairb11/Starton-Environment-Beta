"""One saved link, as shown in the editor's link list."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMenu,
    QPushButton,
    QVBoxLayout,
)

from starton.gui import styles
from starton.gui.elided_label import ElidedLabel


class LinkBlock(QFrame):
    """A card showing a link's name above its clickable URL.

    Text too long for the card is cut rather than allowed to widen it, so the
    list never scrolls sideways. The pencil button and the bin button, and the
    right-click menu behind them, edit and remove the link.

    Signals:
        edit_requested: Emitted with this block when the user edits it.
        delete_requested: Emitted with this block when the user removes it.
    """

    edit_requested = pyqtSignal(object)
    delete_requested = pyqtSignal(object)

    def __init__(self, link):
        """Build the card for one link.

        Args:
            link (Link): The link to display.
        """
        super().__init__()
        self.link = link
        self.setStyleSheet(styles.LINK_FRAME)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addLayout(self._build_text(), stretch=1)
        layout.addWidget(self._build_edit_button())
        layout.addWidget(self._build_delete_button())

    def _apply_enabled_style(self):
        """Dim the card's text if the link was switched off in the save file.

        Nothing in the editor switches links off any more, but a file edited
        by hand still can, and a link that will not open should not look
        identical to one that will.
        """
        self.name_lbl.setStyleSheet(
            styles.LINK_NAME if self.link.is_enabled() else styles.LINK_NAME_DISABLED
        )

    def _build_text(self):
        """Lay out the link's name above its URL.

        Returns:
            QVBoxLayout: The text column.
        """
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.name_lbl = ElidedLabel(self.link.get_name())

        self.url_lbl = ElidedLabel(self.link.get_link(), url=self.link.get_link())
        self.url_lbl.setOpenExternalLinks(True)
        self.url_lbl.setStyleSheet(styles.LINK_URL)

        text_layout.addWidget(self.name_lbl)
        text_layout.addWidget(self.url_lbl)
        self._apply_enabled_style()
        return text_layout

    def refresh(self):
        """Show the link's current values, after it has been edited."""
        self.name_lbl.set_content(self.link.get_name())
        self.url_lbl.set_content(self.link.get_link(), url=self.link.get_link())
        self._apply_enabled_style()

    def _build_edit_button(self):
        """Create the pencil button.

        Returns:
            QPushButton: The edit button.
        """
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(28, 28)
        edit_btn.setToolTip("Edit name and URL")
        edit_btn.setStyleSheet(styles.LINK_EDIT_BTN)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self))
        return edit_btn

    def _build_delete_button(self):
        """Create the bin button.

        Returns:
            QPushButton: The delete button.
        """
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setToolTip("Delete URL")
        delete_btn.setStyleSheet(styles.LINK_DELETE_BTN)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self))
        return delete_btn

    def _show_context_menu(self, position):
        """Show the right-click menu offering an edit or deletion.

        Args:
            position (QPoint): Where the user right-clicked, in widget
                coordinates.
        """
        context_menu = QMenu(self)
        context_menu.setStyleSheet(styles.CONTEXT_MENU)
        edit_action = QAction("✏️ Edit Link", self)
        edit_action.triggered.connect(lambda: self.edit_requested.emit(self))
        context_menu.addAction(edit_action)
        delete_action = QAction("🗑️ Delete Link", self)
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self))
        context_menu.addAction(delete_action)
        context_menu.exec(self.mapToGlobal(position))

    def get_link(self):
        return self.link
