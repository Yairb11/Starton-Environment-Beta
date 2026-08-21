"""A small picture of one monitor with a window drawn on it.

Nine of these make up the window-state picker, one per region, so every state
is visible at once and each one is shaped like the monitor the app actually
sits on.

The chosen state is drawn large and in blue; the rest sit much smaller and grey
around it, so the panel shows at a glance which one is set without having to
read a label. Hovering one of the small ones outlines its monitor in blue, and
that outline is the only thing marking the cell: the widget itself has no
border, so nothing is drawn twice.

Constants:
    SCALE: Pixels of real screen per pixel of drawing. The result is scaled
        again to fit the widget, so this only sets the working resolution.
    SELECTED_HEIGHT, UNSELECTED_HEIGHT: Cell heights by state. The drawing
        keeps the monitor's aspect ratio inside whichever height applies, so a
        portrait screen shows a tall narrow picture rather than a stretched
        one.
    BORDER_WIDTH: Thickness of the outline drawn around the monitor.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsView

from starton.geometry import region_rect
from starton.gui import styles

SCALE = 10

SELECTED_HEIGHT = 86

UNSELECTED_HEIGHT = 40

BORDER_WIDTH = 2


class MiniCanvas(QGraphicsView):
    """One region, drawn on a thumbnail of a monitor.

    Signals:
        clicked: Emitted with the region name when the cell is clicked.
    """

    clicked = pyqtSignal(str)

    def __init__(self, region, monitor):
        """Draw the preview for one region.

        Args:
            region (str): Region the window occupies, from
                :data:`starton.geometry.REGIONS`.
            monitor: Monitor to draw the window on.
        """
        super().__init__()
        self.region = region
        self.monitor = monitor
        self.is_selected = False
        self.is_hovered = False
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setFixedHeight(UNSELECTED_HEIGHT)
        self.setStyleSheet(styles.MINI_CANVAS)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(region.replace("_", " ").title())
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._draw()

    def set_monitor(self, monitor):
        """Redraw the preview against a different monitor.

        Args:
            monitor: The monitor to preview, which changes the aspect ratio.
        """
        self.monitor = monitor
        self._draw()

    def set_selected(self, is_selected):
        """Grow and colour this cell, or shrink it back to grey.

        Args:
            is_selected (bool): Whether this is the chosen region.
        """
        if is_selected == self.is_selected:
            return
        self.is_selected = is_selected
        self.setFixedHeight(SELECTED_HEIGHT if is_selected else UNSELECTED_HEIGHT)
        self._draw()

    def enterEvent(self, event):
        """Outline the monitor in blue while the cursor is over the cell.

        Args:
            event: The Qt enter event.
        """
        self.is_hovered = True
        self._draw()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Drop the hover outline once the cursor leaves.

        Args:
            event: The Qt leave event.
        """
        self.is_hovered = False
        self._draw()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Report a click so the picker can select this region.

        Args:
            event: The Qt mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.region)
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        """Keep the drawing fitted whenever the cell changes size.

        Args:
            event: The Qt resize event.
        """
        super().resizeEvent(event)
        self._fit()

    def _draw(self):
        """Draw the monitor and the window sitting on it.

        The scene is emptied first: the preview is redrawn whenever the app
        moves to another monitor, and without this the old rectangles pile up
        behind the new ones.
        """
        if not self.monitor:
            return
        self.scene.clear()
        monitor_view = QGraphicsRectItem(
            0, 0, self.monitor.width // SCALE, self.monitor.height // SCALE
        )
        if self.is_selected:
            border_color = styles.MONITOR_BORDER_CHOSEN
        elif self.is_hovered:
            border_color = styles.MONITOR_BORDER_HOVER
        else:
            border_color = styles.MONITOR_BORDER
        monitor_view.setBrush(QBrush(QColor(styles.MONITOR_FILL)))
        monitor_view.setPen(QPen(QColor(border_color), BORDER_WIDTH))

        x, y, width, height = region_rect(
            self.region, 0, 0, self.monitor.width, self.monitor.height
        )
        app_view = QGraphicsRectItem(
            x // SCALE, y // SCALE, width // SCALE, height // SCALE
        )
        window_color = styles.APP_DEFAULT if self.is_selected else styles.APP_UNCHOSEN
        app_view.setBrush(QBrush(QColor(window_color)))
        app_view.setPen(QPen(QColor(styles.MONITOR_BORDER), 1))

        self.scene.addItem(monitor_view)
        self.scene.addItem(app_view)
        self._fit()

    def _fit(self):
        """Scale the drawing to fill the cell without distorting the monitor.

        Qt warns and misbehaves when asked to fit an empty rectangle, which
        happens on the first layout pass before the cell has a size.
        """
        bounds = self.scene.itemsBoundingRect()
        if bounds.isEmpty():
            return
        self.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)
