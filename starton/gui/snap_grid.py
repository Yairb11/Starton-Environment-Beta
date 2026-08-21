"""A picker shaped like a screen, for choosing where a window sits.

The nine regions are laid out the way they appear on the monitor - corners in
the corners, halves along the edges, full screen in the middle - and each cell
is a small drawing of the monitor with the window on it. Picking a window state
is one click on the picture you want, and every option is visible at once.

The custom-size button below the grid is a toggle rather than a tenth option:
switching it on hides the nine cells, leaving the editor showing nothing but the
width and height boxes, and switching it off brings the picker back.

Constants:
    CUSTOM_BTN_HEIGHT: Height of the custom-size toggle, kept short so the
        picker above it stays the thing the eye lands on.
    UNSELECTED_INSET: Margin an unselected cell is inset by inside its slot.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QPushButton, QVBoxLayout, QWidget

from starton.geometry import CUSTOM_TITLE, REGION_GRID
from starton.gui import styles
from starton.gui.mini_canvas import MiniCanvas

CUSTOM_BTN_HEIGHT = 26

UNSELECTED_INSET = 12


class SnapGrid(QWidget):
    """Nine region previews plus a custom-size button.

    Signals:
        region_selected: Emitted with a region name when a cell is clicked.
        custom_selected: Emitted when the custom-size button is clicked.
    """

    region_selected = pyqtSignal(str)
    custom_selected = pyqtSignal()

    def __init__(self, monitor, parent=None):
        """Build the grid and the custom-size button.

        Args:
            monitor: Monitor the cells are drawn to the shape of.
            parent (QWidget, optional): Qt parent. Defaults to ``None``.
        """
        super().__init__(parent)
        self.cells = {}
        self.frames = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self._build_grid(monitor))
        layout.addWidget(self._build_custom_button())

    def _build_grid(self, monitor):
        """Lay the nine regions out in the shape of a screen.

        The grid lives in a widget of its own so the custom-size toggle can
        hide all nine cells with one call.

        Args:
            monitor: Monitor the cells are drawn to the shape of.

        Returns:
            QWidget: The grid of region previews.
        """
        self.grid_widget = QWidget()
        grid = QGridLayout(self.grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(4)
        for row, region_row in enumerate(REGION_GRID):
            for column, region in enumerate(region_row):
                cell = MiniCanvas(region, monitor)
                cell.clicked.connect(self.region_selected.emit)
                self.cells[region] = cell
                grid.addWidget(self._inset(cell, region), row, column)
        return self.grid_widget

    def _inset(self, cell, region):
        """Wrap a cell so an unselected one can sit smaller in its slot.

        The grid keeps uniform slots; the chosen cell fills its own, and the
        rest are inset from theirs. Doing it with margins rather than by
        resizing the slots means the grid never reflows as the choice moves
        around.

        Args:
            cell (MiniCanvas): The cell to wrap.
            region (str): The region the cell shows.

        Returns:
            QWidget: The wrapper holding the cell.
        """
        frame = QWidget()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(UNSELECTED_INSET, 0, UNSELECTED_INSET, 0)
        frame_layout.addWidget(cell, 0, Qt.AlignmentFlag.AlignVCenter)
        self.frames[region] = frame_layout
        return frame

    def _build_custom_button(self):
        """Create the button that switches to an explicit pixel size.

        Returns:
            QPushButton: The custom-size button.
        """
        self.custom_btn = QPushButton(CUSTOM_TITLE)
        self.custom_btn.setFixedHeight(CUSTOM_BTN_HEIGHT)
        self.custom_btn.setToolTip("Type an exact width and height instead of picking a region")
        self.custom_btn.setStyleSheet(styles.SNAP_CELL)
        self.custom_btn.clicked.connect(self.custom_selected.emit)
        return self.custom_btn

    def set_monitor(self, monitor):
        """Redraw every cell against a different monitor.

        Args:
            monitor: The monitor the app now sits on.
        """
        for cell in self.cells.values():
            cell.set_monitor(monitor)

    def set_selected(self, region):
        """Highlight the cell for a region, leaving every other one small.

        Args:
            region (str | None): Region to highlight, or ``None`` to leave the
                whole picker unhighlighted, as a custom size does.
        """
        for name, cell in self.cells.items():
            is_chosen = name == region
            cell.set_selected(is_chosen)
            inset = 0 if is_chosen else UNSELECTED_INSET
            self.frames[name].setContentsMargins(inset, 0, inset, 0)

    def set_custom_open(self, is_open):
        """Swap between the region picker and a custom size.

        Args:
            is_open (bool): ``True`` to hide the nine cells and show the
                custom-size button as the chosen one.
        """
        self.grid_widget.setVisible(not is_open)
        self.custom_btn.setStyleSheet(
            styles.SNAP_CELL_SELECTED if is_open else styles.SNAP_CELL
        )

    def is_selected(self, region):
        """Report whether a cell is currently showing as the chosen one.

        Args:
            region (str): Region to check.

        Returns:
            bool: ``True`` when that cell is drawn large and blue.
        """
        return self.cells[region].is_selected
