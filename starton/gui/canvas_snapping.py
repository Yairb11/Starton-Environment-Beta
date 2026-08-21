"""Making a dragged window line up with the things around it.

A window dropped by hand almost never lands where the user meant it to: a few
pixels of overhang past a monitor edge, or a gap against the window beside it.
The engine here pulls a rectangle onto whichever line it is already close to -
a monitor edge, a monitor midline, or the edge or centre of another window -
and reports the guides to draw so the user can see why it moved.

Monitor lines come from :func:`starton.geometry.region_edges`, so the line a
window snaps to is by construction the same line the ``"Left"`` region is
measured from.

Constants:
    SNAP_TOLERANCE: How close an edge must come, in canvas pixels, before it is
        pulled onto a line.
"""

from starton.geometry import region_edges

SNAP_TOLERANCE = 8


class SnapEngine:
    """The lines on the canvas worth lining a window up against.

    Targets are held in two sets. The monitors never move, so their lines are
    worked out once. The other windows move whenever one is dragged, so their
    lines are rebuilt at the start of each drag - and the window being dragged
    is left out of them, since a rectangle is always exactly on its own edges.

    Attributes:
        tolerance (float): How close an edge must come to be pulled in.
    """

    def __init__(self, tolerance=SNAP_TOLERANCE):
        """Start with no targets at all.

        Args:
            tolerance (float): How close an edge must come, in canvas pixels.
        """
        self.tolerance = tolerance
        self._monitor_lines = ([], [])
        self._app_lines = ([], [])

    def set_monitors(self, rects):
        """Record the lines the monitors contribute.

        Args:
            rects (list): One ``QRectF`` per monitor, in canvas coordinates.
        """
        self._monitor_lines = ([], [])
        for rect in rects:
            verticals, horizontals = region_edges(
                rect.x(), rect.y(), rect.width(), rect.height()
            )
            self._add(rect, verticals, horizontals, self._monitor_lines)

    def set_apps(self, rects):
        """Record the lines the other windows contribute.

        Args:
            rects (list): One ``QRectF`` per window, in canvas coordinates,
                excluding the window being dragged.
        """
        self._app_lines = ([], [])
        for rect in rects:
            verticals = (rect.left(), rect.center().x(), rect.right())
            horizontals = (rect.top(), rect.center().y(), rect.bottom())
            self._add(rect, verticals, horizontals, self._app_lines)

    @staticmethod
    def _add(rect, verticals, horizontals, lines):
        """Store one rectangle's lines together with how far they run.

        The span is kept so a guide can be drawn long enough to touch both the
        dragged window and whatever it lined up with, rather than crossing the
        whole canvas.

        Args:
            rect (QRectF): The rectangle the lines come from.
            verticals (tuple): X coordinates it contributes.
            horizontals (tuple): Y coordinates it contributes.
            lines (tuple): The ``(verticals, horizontals)`` pair to append to.
        """
        for value in verticals:
            lines[0].append((value, rect.top(), rect.bottom()))
        for value in horizontals:
            lines[1].append((value, rect.left(), rect.right()))

    def _targets(self, axis):
        """Return every line on one axis, monitors and windows together.

        Args:
            axis (int): ``0`` for vertical lines, ``1`` for horizontal ones.

        Returns:
            list: ``(value, span_start, span_end)`` triples.
        """
        return self._monitor_lines[axis] + self._app_lines[axis]

    def _closest(self, edges, axis):
        """Find the line nearest any of a rectangle's edges.

        Args:
            edges (tuple): The coordinates to test, in canvas pixels.
            axis (int): ``0`` for vertical lines, ``1`` for horizontal ones.

        Returns:
            tuple: ``(delta, target)`` where delta is how far to move to land
            on the line and target is the matching triple, or ``(0.0, None)``
            when nothing is close enough.
        """
        best_delta = 0.0
        best_target = None
        best_distance = self.tolerance
        for target in self._targets(axis):
            for edge in edges:
                distance = abs(target[0] - edge)
                if distance <= best_distance:
                    best_distance = distance
                    best_delta = target[0] - edge
                    best_target = target
        return best_delta, best_target

    def snap_move(self, rect):
        """Pull a whole rectangle onto the nearest lines without resizing it.

        Both axes are decided separately, so a window can settle onto a monitor
        edge horizontally while lining up with another window vertically.

        Args:
            rect (QRectF): Where the drag would put the window.

        Returns:
            tuple: ``(dx, dy, guides)``; the guides are the lines to draw, as
            ``(x1, y1, x2, y2)``.
        """
        dx, vertical = self._closest(
            (rect.left(), rect.center().x(), rect.right()), 0
        )
        dy, horizontal = self._closest(
            (rect.top(), rect.center().y(), rect.bottom()), 1
        )
        moved = rect.translated(dx, dy)
        return dx, dy, self._guides(moved, vertical, horizontal)

    def snap_resize(self, rect, edges):
        """Pull only the edges under the cursor onto the nearest lines.

        Args:
            rect (QRectF): The rectangle the resize has produced.
            edges (tuple): ``(vertical_edge, horizontal_edge)`` as returned by
                :func:`starton.gui.canvas_handles.moving_edges`.

        Returns:
            tuple: ``(dx, dy, guides)`` where the deltas apply to those edges
            alone.
        """
        vertical_edge, horizontal_edge = edges
        sides = {
            "left": rect.left(),
            "right": rect.right(),
            "top": rect.top(),
            "bottom": rect.bottom(),
        }
        dx, vertical = 0.0, None
        dy, horizontal = 0.0, None
        if vertical_edge:
            dx, vertical = self._closest((sides[vertical_edge],), 0)
        if horizontal_edge:
            dy, horizontal = self._closest((sides[horizontal_edge],), 1)
        return dx, dy, self._guides(rect, vertical, horizontal)

    @staticmethod
    def _guides(rect, vertical, horizontal):
        """Turn the lines that matched into segments long enough to see.

        Args:
            rect (QRectF): Where the window has ended up.
            vertical (tuple | None): The vertical line it snapped to.
            horizontal (tuple | None): The horizontal line it snapped to.

        Returns:
            list: ``(x1, y1, x2, y2)`` segments in canvas coordinates.
        """
        guides = []
        if vertical:
            value, start, end = vertical
            guides.append(
                (value, min(start, rect.top()), value, max(end, rect.bottom()))
            )
        if horizontal:
            value, start, end = horizontal
            guides.append(
                (min(start, rect.left()), value, max(end, rect.right()), value)
            )
        return guides
