"""The scale model of the desktop the environment is arranged on.

Constants:
    SCALE: Pixels of real desktop per pixel of canvas.
    REGION_TOLERANCE: How far, in desktop pixels, a dropped window may be from
        a screen region and still be counted as having landed on it.
    SCENE_MARGIN: Blank canvas kept around the desktop, so a window on the very
        edge of a monitor is not flush against the end of the scroll.
    NUDGE_STEP, NUDGE_STEP_LARGE: How far one arrow key press moves or resizes
        a window, in canvas pixels, on its own and with Shift held.
"""

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsView, QMenu

from starton import monitors
from starton.geometry import match_region, region_rect
from starton.gui import styles
from starton.gui.canvas_handles import moving_edges
from starton.gui.canvas_navigation import CanvasNavigator
from starton.gui.canvas_snapping import SnapEngine
from starton.gui.interactive_app_item import MIN_SIZE, InteractiveAppItem

SCALE = 5

REGION_TOLERANCE = 4 * SCALE

SCENE_MARGIN = 40

NUDGE_STEP = 1

NUDGE_STEP_LARGE = 10

_ARROWS = {
    Qt.Key.Key_Left: (-1, 0),
    Qt.Key.Key_Right: (1, 0),
    Qt.Key.Key_Up: (0, -1),
    Qt.Key.Key_Down: (0, 1),
}


class MonitorCanvas(QGraphicsView):
    """Every monitor, drawn to scale, with a rectangle per saved app.

    The canvas owns the conversion between real desktop pixels and canvas
    pixels: the items inside it only ever work in canvas coordinates, and
    everything reported outwards is back in desktop coordinates.

    It also owns everything an item cannot know on its own. Snapping needs the
    monitors and the other windows, and naming the region a window has been
    dropped onto needs the screen layout, so both are answered here through the
    callbacks the items are handed.

    Guides and the region preview are painted in the foreground rather than
    added to the scene on purpose: stacking order is worked out from the
    positions of the items in the scene, and decoration added alongside them
    would shift every window's z value.

    Signals:
        app_selected: Emitted with an app when its rectangle is clicked.
        app_moved: Emitted with ``(app, x, y, moved)`` while dragging, in
            desktop coordinates.
        app_resized: Emitted with ``(app, width, height)`` while resizing, in
            desktop pixels.
        app_delete_requested: Emitted with an app when it is deleted.
        app_region_snapped: Emitted with ``(app, screen_index, region)`` when a
            drag ends on a screen region, so the app can be saved as that
            region rather than as a pixel size.
        app_add_requested: Emitted with ``(x, y)`` in desktop coordinates when
            a new app is asked for from the canvas's own menu.
    """

    app_selected = pyqtSignal(object)
    app_moved = pyqtSignal(object, float, float, bool)
    app_resized = pyqtSignal(object, int, int)
    app_delete_requested = pyqtSignal(object)
    app_region_snapped = pyqtSignal(object, int, str)
    app_add_requested = pyqtSignal(float, float)

    def __init__(self, screens, apps):
        """Draw the monitors and the saved apps.

        Args:
            screens (list): Every connected monitor.
            apps (list | None): Saved apps, or ``None`` when nothing is saved.
        """
        super().__init__()
        self.screens = screens
        self.apps = apps

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setStyleSheet(styles.CANVAS)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        min_x, min_y, max_x, max_y = monitors.bounding_box(screens)
        self.x_min = min_x
        self.y_min = min_y
        self.total_screen_area = [0, (max_x - min_x) // SCALE, 0, (max_y - min_y) // SCALE]

        self._guides = []
        self._preview = None
        self._dragging_item = None
        self._snap = SnapEngine()
        self._navigator = CanvasNavigator(self)

        self._draw_monitors()
        self._draw_apps()
        self._snap.set_monitors(self._monitor_rects())
        self.setSceneRect(
            self.scene.itemsBoundingRect().adjusted(
                -SCENE_MARGIN, -SCENE_MARGIN, SCENE_MARGIN, SCENE_MARGIN
            )
        )

    def _monitor_rects(self):
        """Measure every monitor in canvas coordinates.

        Returns:
            list: One ``QRectF`` per monitor.
        """
        return [
            QRectF(
                (monitor.x - self.x_min) // SCALE,
                (monitor.y - self.y_min) // SCALE,
                monitor.width // SCALE,
                monitor.height // SCALE,
            )
            for monitor in self.screens
        ]

    def _draw_monitors(self):
        """Draw one grey rectangle per monitor."""
        for rect in self._monitor_rects():
            monitor_view = QGraphicsRectItem(rect)
            monitor_view.setBrush(QBrush(QColor(styles.MONITOR_FILL)))
            monitor_view.setPen(QPen(QColor(styles.MONITOR_BORDER), 5))
            self.scene.addItem(monitor_view)

    def _draw_apps(self):
        """Draw a rectangle for every saved app, first app in front."""
        if not self.apps:
            return
        app_count = len(self.apps)
        for index, app in enumerate(self.apps):
            self.scene.addItem(self._create_item(app, app_count - index))

    def _create_item(self, app, z):
        """Build the canvas rectangle for one app.

        Args:
            app (App): The app to draw.
            z (int): Stacking order; higher rectangles sit in front.

        Returns:
            InteractiveAppItem: The rectangle, not yet added to the scene.
        """
        x, y, width, height = self._canvas_rect(app)
        return InteractiveAppItem(
            x,
            y,
            width,
            height,
            app,
            z,
            self.total_screen_area,
            scale=SCALE,
            click_callback=self.app_selected.emit,
            pos_callback=self._on_item_moved,
            size_callback=self._on_item_resized,
            delete_callback=self.app_delete_requested.emit,
            snap_callback=self._snap_item,
            drag_end_callback=self._on_drag_ended,
        )

    def _canvas_rect(self, app):
        """Convert an app's saved geometry into canvas coordinates.

        Args:
            app (App): The app to measure.

        Returns:
            tuple: ``(x, y, width, height)`` in canvas pixels.
        """
        size = app.get_size()
        pos = app.get_pos()
        if size.get_is_list():
            width, height = size.get_size()
            return (
                (pos[0] - self.x_min) // SCALE,
                (pos[1] - self.y_min) // SCALE,
                width // SCALE,
                height // SCALE,
            )
        monitor = self.screens[monitors.find_screen_index(self.screens, pos)]
        x, y, width, height = region_rect(
            size.get_size(), monitor.x, monitor.y, monitor.width, monitor.height
        )
        return (
            (x - self.x_min) // SCALE,
            (y - self.y_min) // SCALE,
            width // SCALE,
            height // SCALE,
        )

    def _app_items(self):
        """Iterate over the app rectangles in the scene, monitors excluded.

        Yields:
            tuple: ``(index, item)`` where the index counts every scene item,
            matching the stacking order the canvas assigns.
        """
        for index, item in enumerate(self.scene.items()):
            if isinstance(item, InteractiveAppItem):
                yield index, item

    def _selected_item(self):
        """Find the rectangle of the app the panel is currently editing.

        Returns:
            InteractiveAppItem | None: The highlighted rectangle, if any.
        """
        for _, item in self._app_items():
            if item.is_selected:
                return item
        return None

    def reset_app_view(self, app_selected):
        """Redraw every rectangle from its app, and highlight the selected one.

        Args:
            app_selected (App): The app that is now selected.
        """
        item_count = len(self.scene.items())
        for index, item in self._app_items():
            app = item.get_app()
            item.setZValue(item_count - index)
            item.setRect(*self._canvas_rect(app))
            item.set_color(item.find_app_item(app_selected))

    def change_app_view(self, app, x, y, width, height, screen):
        """Move and resize one rectangle, and bring it to the front.

        Args:
            app (App): The app being edited.
            x (int): Left edge relative to its monitor, in desktop pixels.
            y (int): Top edge relative to its monitor, in desktop pixels.
            width (int): Width in desktop pixels.
            height (int): Height in desktop pixels.
            screen (int): Monitor number as shown in the editor, 1 based.
        """
        monitor = self.screens[screen - 1]
        item_count = len(self.scene.items())
        for index, item in self._app_items():
            if item.find_app_item(app):
                item.setRect(
                    (x + monitor.x - self.x_min) // SCALE,
                    (y + monitor.y - self.y_min) // SCALE,
                    width // SCALE,
                    height // SCALE,
                )
                item.setZValue(item_count)
            else:
                item.setZValue(index)

    def add_app_view(self, app_added):
        """Draw a rectangle for a newly created app, in front of the rest.

        Args:
            app_added (App): The new app.
        """
        self.scene.addItem(self._create_item(app_added, 0))

    def delete_app_view(self, app_deleted):
        """Remove an app's rectangle from the canvas.

        Args:
            app_deleted (App): The app that was deleted.
        """
        doomed = None
        for _, item in self._app_items():
            if item.find_app_item(app_deleted):
                doomed = item
        if doomed:
            self.scene.removeItem(doomed)

    def _on_item_moved(self, app, x, y, is_moved):
        """Re-emit a drag in desktop coordinates.

        Args:
            app (App): The app being dragged.
            x (float): Left edge in canvas coordinates.
            y (float): Top edge in canvas coordinates.
            is_moved (bool): Whether the drag travelled far enough to count.
        """
        self.app_moved.emit(
            app, (x * SCALE) + self.x_min, (y * SCALE) + self.y_min, is_moved
        )

    def _on_item_resized(self, app, width, height):
        """Re-emit a resize in desktop pixels.

        Args:
            app (App): The app being resized.
            width (float): New width in canvas pixels.
            height (float): New height in canvas pixels.
        """
        self.app_resized.emit(app, int(width * SCALE), int(height * SCALE))

    def _snap_item(self, item, rect, handle):
        """Line a window up with the monitors and the windows around it.

        The other windows are collected the first time an item asks during a
        drag rather than on every call: they cannot move while one of them is
        being dragged, and the item being dragged has to be left out or it
        would snap to its own edges and never move at all.

        Args:
            item (InteractiveAppItem): The window being edited.
            rect (QRectF): Where the edit would put it.
            handle (str | None): The resize grip being dragged, or ``None``
                when the whole window is being moved.

        Returns:
            QRectF: The rectangle after snapping.
        """
        if item is not self._dragging_item:
            self._dragging_item = item
            self._snap.set_apps(
                [other.rect() for _, other in self._app_items() if other is not item]
            )

        if handle:
            dx, dy, guides = self._snap.snap_resize(rect, moving_edges(handle))
            snapped = self._resized(rect, handle, dx, dy)
        else:
            dx, dy, guides = self._snap.snap_move(rect)
            snapped = rect.translated(dx, dy)

        self._guides = guides
        self._preview = self._preview_rect(snapped)
        self.viewport().update()
        return snapped

    @staticmethod
    def _resized(rect, handle, dx, dy):
        """Apply a snap to the edges a grip is dragging.

        A snap that would pull an edge past the smallest allowed size is
        dropped rather than clamped: refusing to line up is the lesser
        surprise, where a clamp would leave the window on a guide it does not
        actually touch.

        Args:
            rect (QRectF): The rectangle the resize produced.
            handle (str): The grip being dragged.
            dx (float): How far the vertical edge must move to snap.
            dy (float): How far the horizontal edge must move to snap.

        Returns:
            QRectF: The snapped rectangle.
        """
        snapped = QRectF(rect)
        if "left" in handle:
            snapped.setLeft(rect.left() + dx)
        if "right" in handle:
            snapped.setRight(rect.right() + dx)
        if "top" in handle:
            snapped.setTop(rect.top() + dy)
        if "bottom" in handle:
            snapped.setBottom(rect.bottom() + dy)
        if snapped.width() < MIN_SIZE or snapped.height() < MIN_SIZE:
            return rect
        return snapped

    def _match_region(self, rect):
        """Name the screen region a rectangle has been dropped onto.

        Args:
            rect (QRectF): The rectangle, in canvas coordinates.

        Returns:
            tuple: ``(screen_index, region)``, or ``(None, None)`` when the
            rectangle is not on a region or not on a monitor at all.
        """
        center = rect.center()
        index = monitors.find_screen_index(
            self.screens,
            [center.x() * SCALE + self.x_min, center.y() * SCALE + self.y_min],
        )
        if index < 0:
            return None, None
        monitor = self.screens[index]
        region = match_region(
            (
                rect.x() * SCALE + self.x_min,
                rect.y() * SCALE + self.y_min,
                rect.width() * SCALE,
                rect.height() * SCALE,
            ),
            (monitor.x, monitor.y, monitor.width, monitor.height),
            REGION_TOLERANCE,
        )
        return (index, region) if region else (None, None)

    def _preview_rect(self, rect):
        """Measure the region a rectangle is about to land on.

        Args:
            rect (QRectF): The rectangle, in canvas coordinates.

        Returns:
            QRectF | None: The region to wash over, in canvas coordinates, or
            ``None`` when the rectangle is not on one.
        """
        index, region = self._match_region(rect)
        if region is None:
            return None
        monitor = self.screens[index]
        x, y, width, height = region_rect(
            region, monitor.x, monitor.y, monitor.width, monitor.height
        )
        return QRectF(
            (x - self.x_min) / SCALE,
            (y - self.y_min) / SCALE,
            width / SCALE,
            height / SCALE,
        )

    def _on_drag_ended(self, item, has_changed):
        """Clear the guides and report a window dropped onto a region.

        Args:
            item (InteractiveAppItem): The window that was being edited.
            has_changed (bool): ``True`` when the window was actually moved or
                resized, rather than only clicked.
        """
        self._dragging_item = None
        self._guides = []
        self._preview = None
        self.viewport().update()
        if not has_changed:
            return
        index, region = self._match_region(item.rect())
        if region is not None:
            self.app_region_snapped.emit(item.get_app(), index, region)

    def drawForeground(self, painter, rect):
        """Paint the alignment guides and the region a window will land on.

        Args:
            painter (QPainter): The painter the scene is being drawn with.
            rect (QRectF): The area being redrawn, which is the whole viewport
                here because guides span it.
        """
        super().drawForeground(painter, rect)
        if self._preview:
            wash = QColor(styles.REGION_PREVIEW)
            wash.setAlpha(styles.REGION_PREVIEW_ALPHA)
            painter.fillRect(self._preview, QBrush(wash))
        if not self._guides:
            return
        painter.setPen(QPen(QColor(styles.SNAP_GUIDE), 0, Qt.PenStyle.DashLine))
        for x1, y1, x2, y2 in self._guides:
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def fit_view(self):
        """Scale the view so the whole desktop is on screen."""
        self._navigator.fit()

    def reset_zoom(self):
        """Go back to the canvas's own scale."""
        self._navigator.reset()

    def zoom_in(self):
        """Zoom one step in."""
        self._navigator.zoom_in()

    def zoom_out(self):
        """Zoom one step out."""
        self._navigator.zoom_out()

    def resizeEvent(self, event):
        """Keep framing the desktop until the user takes the view over."""
        super().resizeEvent(event)
        if self._navigator.auto_fit:
            self._navigator.fit()

    def wheelEvent(self, event):
        if not self._navigator.wheel(event):
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if not self._navigator.mouse_press(event):
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self._navigator.mouse_move(event):
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if not self._navigator.mouse_release(event):
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """Pan with the space bar, or nudge the selected window with the arrows.

        A nudge moves by whole canvas pixels, which is :data:`SCALE` desktop
        pixels: the canvas has no way to express a finer step, and the panel's
        spin boxes remain the way to reach an exact desktop pixel.
        """
        if self._navigator.key_press(event):
            return
        step = _ARROWS.get(event.key())
        item = self._selected_item()
        if step is None or item is None:
            super().keyPressEvent(event)
            return
        distance = (
            NUDGE_STEP_LARGE
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            else NUDGE_STEP
        )
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            item.stretch(step[0] * distance, step[1] * distance)
        else:
            item.nudge(step[0] * distance, step[1] * distance)

    def keyReleaseEvent(self, event):
        if not self._navigator.key_release(event):
            super().keyReleaseEvent(event)

    def contextMenuEvent(self, event):
        """Offer the canvas's own actions on a right click over empty space.

        A view that overrides this stops forwarding the event to the scene, so
        a click over a window has to be handed on by hand - otherwise adding a
        menu here would quietly take the delete menu off every app.
        """
        if isinstance(self.itemAt(event.pos()), InteractiveAppItem):
            super().contextMenuEvent(event)
            return

        context_menu = QMenu()
        context_menu.setStyleSheet(styles.CONTEXT_MENU)
        scene_pos = self.mapToScene(event.pos())
        entries = (
            ("➕ Add App Here", lambda: self._request_add(scene_pos)),
            ("🔍 Fit to View", self.fit_view),
            ("💯 Actual Size", self.reset_zoom),
        )
        for title, slot in entries:
            action = QAction(title, context_menu)
            action.triggered.connect(slot)
            context_menu.addAction(action)
        context_menu.exec(event.globalPos())
        event.accept()

    def _request_add(self, scene_pos):
        """Ask for a new app where the canvas was right clicked.

        Args:
            scene_pos (QPointF): Where the click landed, in canvas coordinates.
        """
        self.app_add_requested.emit(
            (scene_pos.x() * SCALE) + self.x_min, (scene_pos.y() * SCALE) + self.y_min
        )
