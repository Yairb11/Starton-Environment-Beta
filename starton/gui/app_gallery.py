"""The opening screen: every saved app as a card waiting to be picked.

Shown in place of the app editor while nothing is selected, so the panel opens
on what there is to choose from rather than on an instruction to choose.

Constants:
    COLUMNS: How many cards sit side by side.
    BROKEN_MARK: Put beside an app whose path is not on this machine.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from starton import monitors
from starton.gui import styles
from starton.gui.elided_label import ElidedLabel

COLUMNS = 2

BROKEN_MARK = "⚠"


class AppCard(QFrame):
    """One saved app, as a card that selects it when clicked.

    The name and the path are elided rather than wrapped, so a deeply nested
    path cannot widen the card and push the grid past the panel.

    Signals:
        chosen: Emitted with this card's app when the user clicks it.
    """

    chosen = pyqtSignal(object)

    def __init__(self, app, screen_number):
        """Build the card for one app.

        Args:
            app (App): The app to show.
            screen_number (int): Which monitor it opens on, counting from one.
        """
        super().__init__()
        self.app = app
        self.is_broken = not app.path_exists()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(self._resting_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)
        layout.addLayout(self._build_name_row())
        layout.addWidget(self._build_meta(screen_number))
        layout.addWidget(self._build_path())

    def _resting_style(self):
        """Pick the border the card wears while the cursor is elsewhere.

        Returns:
            str: A style sheet, red-bordered when the path is missing.
        """
        return styles.APP_CARD_BROKEN if self.is_broken else styles.APP_CARD

    def _build_name_row(self):
        """Lay out the app's name beside its broken-path marker.

        Returns:
            QHBoxLayout: The name row.
        """
        name_layout = QHBoxLayout()
        name_layout.setSpacing(4)

        name_lbl = ElidedLabel(self.app.get_name())
        name_lbl.setStyleSheet(styles.APP_CARD_NAME)
        name_layout.addWidget(name_lbl, stretch=1)

        if self.is_broken:
            broken_lbl = QLabel(BROKEN_MARK)
            broken_lbl.setToolTip("This path is not on this PC")
            broken_lbl.setStyleSheet(styles.APP_CARD_META)
            name_layout.addWidget(broken_lbl)
        return name_layout

    def _build_meta(self, screen_number):
        """Build the line naming the monitor the app opens on.

        Args:
            screen_number (int): Which monitor, counting from one.

        Returns:
            QLabel: The monitor line.
        """
        meta_lbl = QLabel(f"Screen {screen_number}")
        meta_lbl.setStyleSheet(styles.APP_CARD_META)
        return meta_lbl

    def _build_path(self):
        """Build the elided path line.

        Returns:
            ElidedLabel: The path line.
        """
        path_lbl = ElidedLabel(self.app.get_app_path())
        path_lbl.setStyleSheet(styles.APP_CARD_META)
        return path_lbl

    def enterEvent(self, event):
        """Outline the card in blue as the cursor arrives.

        Args:
            event (QEnterEvent): The Qt enter event.
        """
        super().enterEvent(event)
        self.setStyleSheet(styles.APP_CARD_HOVER)

    def leaveEvent(self, event):
        """Put the resting border back as the cursor leaves.

        Args:
            event (QEvent): The Qt leave event.
        """
        super().leaveEvent(event)
        self.setStyleSheet(self._resting_style())

    def mousePressEvent(self, event):
        """Select this card's app on a left click.

        Args:
            event (QMouseEvent): The Qt mouse event.
        """
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.chosen.emit(self.app)


class AppGallery(QWidget):
    """A grid of every saved app, offered instead of an empty editor.

    Deliberately a plain widget rather than a scroll area: it is placed inside
    the editor's own scroll area, and nesting the two would leave the panel
    with two scroll bars fighting over one list.

    Signals:
        app_chosen: Emitted with the app whose card was clicked.
        add_requested: Emitted when the user asks for a new app.
    """

    app_chosen = pyqtSignal(object)
    add_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Build the empty gallery, ready to be filled by :meth:`set_apps`.

        Args:
            parent (QWidget, optional): Qt parent. Defaults to ``None``.
        """
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)

        self.hint_lbl = QLabel("Select an app to edit")
        self.hint_lbl.setStyleSheet(styles.GALLERY_HINT)
        self.hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(8)

        self.empty_lbl = QLabel("No apps yet")
        self.empty_lbl.setStyleSheet(styles.GALLERY_EMPTY)
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.hint_lbl)
        layout.addWidget(self.empty_lbl)
        layout.addWidget(self.grid_widget)
        layout.addStretch()
        layout.addWidget(self._build_add_button())

    def _build_add_button(self):
        """Create the button offering a new app.

        Returns:
            QPushButton: The add button.
        """
        add_btn = QPushButton("➕  Add an app")
        add_btn.setToolTip("Add an app (Ctrl+N)")
        add_btn.setStyleSheet(styles.GALLERY_ADD_BTN)
        add_btn.clicked.connect(self.add_requested.emit)
        return add_btn

    def set_apps(self, apps, screens):
        """Rebuild the grid from the saved apps.

        Args:
            apps (list | None): Every saved app, or ``None`` when none exist.
            screens (list): Every connected monitor, used to name the one each
                app opens on.
        """
        self._clear_grid()
        has_apps = bool(apps)
        self.empty_lbl.setVisible(not has_apps)
        self.grid_widget.setVisible(has_apps)
        self.hint_lbl.setText(
            "Select an app to edit" if has_apps else "Nothing saved yet"
        )
        for index, app in enumerate(apps or []):
            card = AppCard(app, self._screen_number(app, screens))
            card.chosen.connect(self.app_chosen.emit)
            self.grid_layout.addWidget(card, index // COLUMNS, index % COLUMNS)

    def _clear_grid(self):
        """Throw away the cards currently in the grid."""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    @staticmethod
    def _screen_number(app, screens):
        """Work out which monitor an app opens on, counting from one.

        A saved position can land on no monitor at all once a screen is
        unplugged, where the lookup answers ``-1`` and would name the last
        monitor by Python's indexing. Such an app falls back to the first.

        Args:
            app (App): The app to place.
            screens (list): Every connected monitor.

        Returns:
            int: The monitor's number, counting from one.
        """
        index = monitors.find_screen_index(screens, app.get_pos())
        return (0 if index < 0 else index) + 1
