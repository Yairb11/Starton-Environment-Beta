"""The draggable rectangle standing in for one app window on the canvas.

Constants:
    RESIZE_MARGIN: How thick a resize grip is on screen. It is divided by the
        view's zoom before being used, so a grip stays the same size under the
        cursor however far the canvas is zoomed in.
    MIN_SIZE: Smallest rectangle a resize may produce, so an item can never be
        shrunk to the point where its grips are unreachable.
    DRAG_THRESHOLD: How far the mouse must travel before a drag counts as a
        real move. Below this a click is only a selection, and the window keeps
        the region it was snapped to.
    LABEL_PADDING: Gap between the rectangle's edge and its writing.
    LABEL_FONT_SIZE: Height of the app name written inside the rectangle.
    LABEL_MIN_WIDTH, LABEL_MIN_HEIGHT: Below this the rectangle is left blank
        rather than filled with text too clipped to read.
"""

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QAction, QBrush, QColor, QCursor, QFontMetricsF, QPen
from PyQt6.QtWidgets import QApplication, QGraphicsItem, QGraphicsRectItem, QMenu

from starton.gui import styles
from starton.gui.canvas_handles import cursor_for, handle_at, resize_rect

RESIZE_MARGIN = 12

MIN_SIZE = RESIZE_MARGIN + 8

DRAG_THRESHOLD = 5

LABEL_PADDING = 4

LABEL_FONT_SIZE = 11

LABEL_MIN_WIDTH = 46

LABEL_MIN_HEIGHT = 16


class InteractiveAppItem(QGraphicsRectItem):
    """One app window on the canvas: click to select, drag to move, grab any
    edge or corner to resize, right click to delete.

    ``QGraphicsRectItem`` is not a ``QObject`` and cannot carry Qt signals, so
    the item reports back through the callbacks its canvas hands it. Snapping
    works the same way: the item asks its canvas where the rectangle ought to
    go, because the canvas is the only thing that knows about the other
    windows and the monitors.
    """

    def __init__(
        self,
        x,
        y,
        width,
        height,
        app,
        z,
        bounds,
        scale=1,
        click_callback=None,
        pos_callback=None,
        size_callback=None,
        delete_callback=None,
        snap_callback=None,
        drag_end_callback=None,
    ):
        """Draw the rectangle for one app.

        Args:
            x (float): Left edge, in canvas coordinates.
            y (float): Top edge, in canvas coordinates.
            width (float): Rectangle width.
            height (float): Rectangle height.
            app (App): The app this rectangle stands for.
            z (int): Stacking order; higher rectangles sit in front.
            bounds (list): ``[min_x, max_x, min_y, max_y]`` the rectangle may
                not leave.
            scale (int): Desktop pixels per canvas pixel, used only to write
                the window's real size inside it.
            click_callback (optional): Called with the app when it is selected.
            pos_callback (optional): Called with ``(app, x, y, moved)`` while
                dragging.
            size_callback (optional): Called with ``(app, width, height)``
                while resizing.
            delete_callback (optional): Called with the app on delete.
            snap_callback (optional): Called with ``(item, rect, handle)`` and
                answers with the rectangle after snapping.
            drag_end_callback (optional): Called with the item once a drag or
                resize is over.
        """
        super().__init__(x, y, width, height)
        self.app = app
        self.bounds = bounds
        self.scale = scale
        self.click_callback = click_callback
        self.pos_callback = pos_callback
        self.size_callback = size_callback
        self.delete_callback = delete_callback
        self.snap_callback = snap_callback
        self.drag_end_callback = drag_end_callback
        self.is_moved = False
        self.is_selected = False
        self._handle = None

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setBrush(QBrush(QColor(styles.APP_DEFAULT)))
        self.setPen(QPen(Qt.GlobalColor.white, 1))
        self.setZValue(z)

    def get_app(self):
        return self.app

    def set_app(self, app):
        self.app = app

    def find_app_item(self, app):
        """Report whether this rectangle stands for a given app.

        Args:
            app (App): The app to compare against.

        Returns:
            bool: ``True`` when this item holds that app.
        """
        return self.app == app

    def set_color(self, is_selected):
        """Highlight or un-highlight the rectangle.

        Args:
            is_selected (bool): Whether this app is the selected one.
        """
        self.is_selected = is_selected
        color = styles.APP_SELECTED if is_selected else styles.APP_DEFAULT
        self.setBrush(QBrush(QColor(color)))

    def _hit_margin(self):
        """Measure a resize grip in item coordinates.

        Item coordinates shrink as the view zooms in, so a grip given a fixed
        size there would grow under the cursor until most of a zoomed-in window
        resized instead of dragging. Dividing by the zoom keeps it the same
        size on screen at every magnification.

        Returns:
            float: How thick the grips are for the current zoom.
        """
        views = self.scene().views() if self.scene() else []
        zoom = views[0].transform().m11() if views else 1.0
        return RESIZE_MARGIN / zoom if zoom else RESIZE_MARGIN

    def _handle_at(self, point):
        """Name the resize grip under a point.

        Args:
            point (QPointF): Position in item coordinates.

        Returns:
            str | None: The grip, or ``None`` when a press there would drag.
        """
        return handle_at(self.rect(), point, self._hit_margin())

    def _front_item_at(self, scene_pos):
        """Find the topmost app rectangle under a point.

        Args:
            scene_pos (QPointF): Position in scene coordinates.

        Returns:
            InteractiveAppItem | None: The frontmost item, if any.
        """
        for item in self.scene().items(scene_pos):
            if isinstance(item, InteractiveAppItem):
                return item
        return None

    def paint(self, painter, option, widget=None):
        """Draw the rectangle, then write which window it is inside it.

        Without this an environment is a row of identical blue boxes that have
        to be clicked one by one to be told apart.
        """
        super().paint(painter, option, widget)
        self._paint_label(painter)

    def _paint_label(self, painter):
        """Write the app's name and real size inside the rectangle.

        The two lines are dropped one at a time as the rectangle shrinks: a
        small window loses its size line, and a tiny one is left blank rather
        than filled with text clipped past the point of being readable.

        Args:
            painter (QPainter): The painter the item is being drawn with.
        """
        rect = self.rect().adjusted(
            LABEL_PADDING, LABEL_PADDING, -LABEL_PADDING, -LABEL_PADDING
        )
        if rect.width() < LABEL_MIN_WIDTH or rect.height() < LABEL_MIN_HEIGHT:
            return

        font = painter.font()
        font.setPixelSize(LABEL_FONT_SIZE)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(styles.APP_LABEL)))
        metrics = QFontMetricsF(font)
        alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        painter.drawText(
            rect,
            alignment,
            metrics.elidedText(
                self.app.get_name(), Qt.TextElideMode.ElideRight, rect.width()
            ),
        )

        line_height = metrics.height()
        if rect.height() < LABEL_MIN_HEIGHT + line_height:
            return
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QPen(QColor(styles.APP_LABEL_DIM)))
        painter.drawText(rect.adjusted(0, line_height, 0, 0), alignment, self._size_text())

    def _size_text(self):
        """Describe the window's size in the desktop pixels it will open at.

        The rectangle is the live truth during a drag, where the app's saved
        size is still whatever it was before the edit, so the text is measured
        from the rectangle rather than read off the model.

        Returns:
            str: The size, as ``"1920 x 1080"``.
        """
        rect = self.rect()
        return f"{int(rect.width() * self.scale)} x {int(rect.height() * self.scale)}"

    def hoverEnterEvent(self, event):
        if not self.is_selected:
            self.setBrush(QBrush(QColor(styles.APP_HOVER)))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.is_selected:
            self.setBrush(QBrush(QColor(styles.APP_DEFAULT)))
        super().hoverLeaveEvent(event)

    def hoverMoveEvent(self, event):
        self.setCursor(QCursor(cursor_for(self._handle_at(event.pos()))))
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        """Select the app, and decide whether this press drags or resizes.

        Presses are ignored unless this item is the frontmost one under the
        cursor, so clicking an overlapping window picks the one on top.
        """
        self.is_moved = False
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._front_item_at(event.scenePos()) is not self:
            return

        self._handle = self._handle_at(event.pos())
        if not self._handle:
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            self.setBrush(QBrush(QColor(styles.APP_SELECTED)))
            super().mousePressEvent(event)
        if self.click_callback:
            self.click_callback(self.app)

    def mouseMoveEvent(self, event):
        """Resize from a grip, or let Qt handle the drag."""
        if not self._handle:
            super().mouseMoveEvent(event)
            return
        rect = resize_rect(
            self.rect(), self._handle, event.pos(), MIN_SIZE, self.bounds
        )
        self._apply_resize(self._snapped_resize(rect))

    def _snapped_resize(self, rect):
        """Pull the edges being dragged onto whatever they line up with.

        Args:
            rect (QRectF): The rectangle the resize has produced.

        Returns:
            QRectF: The rectangle after snapping, or unchanged when snapping is
            off or nothing was close enough.
        """
        if not self.snap_callback or self._is_snapping_off():
            return rect
        return self.snap_callback(self, rect, self._handle)

    def _apply_resize(self, rect):
        """Take on a resized rectangle and report it.

        A grip on the top or left edge moves the window as well as resizing it,
        so the position is reported too. It is reported as a real move, because
        the panel ignores a position that did not travel far enough to count.

        Args:
            rect (QRectF): The rectangle to take on.
        """
        self.setRect(rect)
        if self.size_callback:
            self.size_callback(self.app, rect.width(), rect.height())
        if self.pos_callback and ("top" in self._handle or "left" in self._handle):
            self.pos_callback(self.app, rect.x(), rect.y(), True)

    def mouseReleaseEvent(self, event):
        """Fold the drag offset back into the rectangle and report the result.

        Qt moves an item by giving it a position offset rather than by changing
        its rectangle. Baking that offset into the rectangle and resetting the
        position to the origin keeps every rectangle in one coordinate system,
        which is what the canvas assumes when it converts back to screen pixels.

        A press that never travelled far enough to count as a move is a
        selection. Qt still hands over whatever offset it collected, so the
        offset is thrown away rather than baked in - otherwise clicking an app
        would shift it by a pixel or two and look like an edit.
        """
        self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        if self._handle:
            self._handle = None
            self._end_drag(True)
            return
        if not self.is_moved:
            self.setPos(0, 0)
            self._end_drag(False)
            super().mouseReleaseEvent(event)
            return
        rect = self.rect()
        offset = self.pos()
        new_x = rect.x() + offset.x()
        new_y = rect.y() + offset.y()
        self.setRect(new_x, new_y, rect.width(), rect.height())
        self.setPos(0, 0)
        if self.pos_callback:
            self.pos_callback(self.app, new_x, new_y, self.is_moved)
        self.is_moved = False
        self._end_drag(True)
        super().mouseReleaseEvent(event)

    def _end_drag(self, has_changed):
        """Tell the canvas the edit is over, so it can clear its guides.

        Whether the geometry actually changed is passed on, because a click
        that only selected the window must not be reported as having dropped it
        onto a region: the window is already sitting on whichever region it was
        saved with, and saying so again would mark the app as edited.

        Args:
            has_changed (bool): ``True`` after a real move or resize.
        """
        if self.drag_end_callback:
            self.drag_end_callback(self, has_changed)

    @staticmethod
    def _is_snapping_off():
        """Report whether the user is asking for freehand placement.

        Snapping is on by default because lining windows up is what nearly
        every drag is trying to do. Alt turns it off for the drag that wants an
        exact pixel instead. ``itemChange`` is handed no event to read the
        modifiers from, so they are asked of the application directly.

        Returns:
            bool: ``True`` while Alt is held.
        """
        modifiers = QApplication.keyboardModifiers()
        return bool(modifiers & Qt.KeyboardModifier.AltModifier)

    def nudge(self, dx, dy):
        """Move the rectangle by a fixed step, for the arrow keys.

        Args:
            dx (float): Canvas pixels to move right.
            dy (float): Canvas pixels to move down.
        """
        rect = self.rect()
        x = min(max(rect.x() + dx, self.bounds[0]), self.bounds[1] - rect.width())
        y = min(max(rect.y() + dy, self.bounds[2]), self.bounds[3] - rect.height())
        self.setRect(x, y, rect.width(), rect.height())
        if self.pos_callback:
            self.pos_callback(self.app, x, y, True)

    def stretch(self, dx, dy):
        """Grow or shrink the rectangle by a fixed step, for the arrow keys.

        Args:
            dx (float): Canvas pixels to add to the width.
            dy (float): Canvas pixels to add to the height.
        """
        rect = self.rect()
        width = min(max(rect.width() + dx, MIN_SIZE), self.bounds[1] - rect.x())
        height = min(max(rect.height() + dy, MIN_SIZE), self.bounds[3] - rect.y())
        self.setRect(rect.x(), rect.y(), width, height)
        if self.size_callback:
            self.size_callback(self.app, width, height)

    def itemChange(self, change, value):
        """Keep the rectangle inside the desktop, and line it up as it moves.

        Every candidate position passes through here, which makes it the one
        place snapping can be applied without having to be repeated for the
        mouse, the keyboard and the panel. The clamp runs first so a window can
        never be snapped out past the edge of the desktop.
        """
        if change != QGraphicsItem.GraphicsItemChange.ItemPositionChange or not self.bounds:
            return super().itemChange(change, value)

        rect = self.rect()
        offset = self._clamped(value, rect)
        if self.snap_callback and not self._is_snapping_off():
            snapped = self.snap_callback(self, rect.translated(offset), None)
            offset = self._clamped(
                QPointF(snapped.x() - rect.x(), snapped.y() - rect.y()), rect
            )

        distance = (offset.x() ** 2 + offset.y() ** 2) ** 0.5
        self.is_moved = self.is_moved or distance > DRAG_THRESHOLD
        if self.pos_callback:
            self.pos_callback(
                self.app, rect.x() + offset.x(), rect.y() + offset.y(), self.is_moved
            )
        return offset

    def _clamped(self, offset, rect):
        """Hold a position offset inside the desktop.

        Args:
            offset (QPointF): How far the drag wants to move the rectangle.
            rect (QRectF): The rectangle being moved.

        Returns:
            QPointF: The offset, trimmed so no edge leaves the desktop.
        """
        min_x = self.bounds[0] - rect.x()
        max_x = self.bounds[1] - (rect.x() + rect.width())
        min_y = self.bounds[2] - rect.y()
        max_y = self.bounds[3] - (rect.y() + rect.height())
        return QPointF(
            max(min_x, min(offset.x(), max_x)),
            max(min_y, min(offset.y(), max_y)),
        )

    def contextMenuEvent(self, event):
        """Offer deletion on right click."""
        context_menu = QMenu()
        context_menu.setStyleSheet(styles.CONTEXT_MENU)
        delete_action = QAction("🗑️ Delete App", context_menu)
        delete_action.triggered.connect(self._request_delete)
        context_menu.addAction(delete_action)
        context_menu.exec(event.screenPos())
        event.accept()

    def _request_delete(self):
        """Ask the canvas to delete this app."""
        if self.delete_callback:
            self.delete_callback(self.app)
