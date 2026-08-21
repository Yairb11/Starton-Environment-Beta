"""Getting around the canvas: zooming, panning, and framing the desktop.

The canvas draws the desktop at a fixed scale, which is too small to work in on
a wide multi-monitor layout and wastes most of the window on a single monitor.
This class adds a view transform on top of that fixed scale and owns everything
about it, so the canvas itself stays a drawing of the desktop rather than also
becoming a viewport controller.

The canvas frames the whole desktop by itself and keeps doing so as the window
is resized, right up until the user zooms or pans. From then on the view is
theirs and nothing moves it again unless they ask for a fit.

Constants:
    ZOOM_STEP: How much one notch of the wheel multiplies the zoom by.
    MIN_ZOOM, MAX_ZOOM: How far in and out the view may go.
    FIT_MARGIN: Blank canvas left around the desktop when framing it, so the
        outermost monitor borders are not cut in half by the window edge.
    WHEEL_NOTCH: Wheel movement Qt reports for one notch.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGraphicsView

ZOOM_STEP = 1.15

MIN_ZOOM = 0.25

MAX_ZOOM = 4.0

FIT_MARGIN = 20

WHEEL_NOTCH = 120


class CanvasNavigator:
    """The zoom and scroll position of one canvas.

    Every method that handles an event answers whether it used it, so the
    canvas can hand the event on to the items when it did not: panning must
    never swallow a click meant for a window.

    Attributes:
        zoom (float): The current magnification, where 1.0 is the canvas's own
            scale.
        auto_fit (bool): Whether the view is still framing the desktop by
            itself. Any manual zoom or pan turns it off.
    """

    def __init__(self, view):
        """Take over the view's transform.

        Args:
            view (QGraphicsView): The canvas to navigate.
        """
        self.view = view
        self.zoom = 1.0
        self.auto_fit = True
        self._is_panning = False
        self._pan_origin = None
        self._is_space_held = False
        view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    def wheel(self, event):
        """Zoom towards the cursor when the wheel is turned with Ctrl held.

        A bare wheel is left alone so it keeps scrolling the view, which is
        what a scroll bar being there leads people to expect.

        Args:
            event (QWheelEvent): The wheel event.

        Returns:
            bool: ``True`` when the event was used to zoom.
        """
        if not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            return False
        self.zoom_by(ZOOM_STEP ** (event.angleDelta().y() / WHEEL_NOTCH))
        return True

    def zoom_by(self, factor):
        """Multiply the zoom, stopping at the limits.

        The factor is recalculated from the clamped result rather than applied
        as asked, so scrolling hard at either limit cannot build up a zoom the
        view then has to unwind.

        Args:
            factor (float): How much to multiply the current zoom by.
        """
        self.auto_fit = False
        target = min(max(self.zoom * factor, MIN_ZOOM), MAX_ZOOM)
        if target == self.zoom:
            return
        self.view.scale(target / self.zoom, target / self.zoom)
        self.zoom = target

    def zoom_in(self):
        """Zoom one step in."""
        self.zoom_by(ZOOM_STEP)

    def zoom_out(self):
        """Zoom one step out."""
        self.zoom_by(1 / ZOOM_STEP)

    def fit(self):
        """Scale the view so the whole desktop is on screen.

        Qt warns and misbehaves when asked to fit an empty rectangle, which
        happens on the first layout pass before the canvas has a size.
        """
        bounds = self.view.scene.itemsBoundingRect()
        if bounds.isEmpty():
            return
        self.view.fitInView(
            bounds.adjusted(-FIT_MARGIN, -FIT_MARGIN, FIT_MARGIN, FIT_MARGIN),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self.zoom = self.view.transform().m11()
        self.auto_fit = True

    def reset(self):
        """Go back to the canvas's own scale."""
        self.view.resetTransform()
        self.zoom = 1.0
        self.auto_fit = False

    def mouse_press(self, event):
        """Start a pan on the middle button, or on the left with Space held.

        Args:
            event (QMouseEvent): The press.

        Returns:
            bool: ``True`` when a pan was started.
        """
        is_space_drag = (
            self._is_space_held and event.button() == Qt.MouseButton.LeftButton
        )
        if event.button() != Qt.MouseButton.MiddleButton and not is_space_drag:
            return False
        self._is_panning = True
        self._pan_origin = event.position().toPoint()
        self.view.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
        return True

    def mouse_move(self, event):
        """Scroll the view by however far the cursor has moved.

        Args:
            event (QMouseEvent): The move.

        Returns:
            bool: ``True`` when the view was panned.
        """
        if not self._is_panning:
            return False
        self.auto_fit = False
        point = event.position().toPoint()
        delta = point - self._pan_origin
        self._pan_origin = point
        horizontal = self.view.horizontalScrollBar()
        vertical = self.view.verticalScrollBar()
        horizontal.setValue(horizontal.value() - delta.x())
        vertical.setValue(vertical.value() - delta.y())
        return True

    def mouse_release(self, event):
        """End a pan.

        Args:
            event (QMouseEvent): The release.

        Returns:
            bool: ``True`` when a pan was ended.
        """
        if not self._is_panning:
            return False
        self._is_panning = False
        self._show_pan_cursor()
        return True

    def key_press(self, event):
        """Arm the space bar so a left drag pans instead of moving a window.

        Args:
            event (QKeyEvent): The key press.

        Returns:
            bool: ``True`` when the key was used.
        """
        if event.key() != Qt.Key.Key_Space or event.isAutoRepeat():
            return False
        self._is_space_held = True
        self._show_pan_cursor()
        return True

    def key_release(self, event):
        """Disarm the space bar.

        Args:
            event (QKeyEvent): The key release.

        Returns:
            bool: ``True`` when the key was used.
        """
        if event.key() != Qt.Key.Key_Space or event.isAutoRepeat():
            return False
        self._is_space_held = False
        self._show_pan_cursor()
        return True

    def _show_pan_cursor(self):
        """Show an open hand while the space bar is held, an arrow otherwise."""
        shape = (
            Qt.CursorShape.OpenHandCursor
            if self._is_space_held
            else Qt.CursorShape.ArrowCursor
        )
        self.view.viewport().setCursor(shape)
