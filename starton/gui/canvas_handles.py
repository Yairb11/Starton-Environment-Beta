"""The eight grips around a window on the canvas.

A window used to be resizable from its bottom-right corner alone, which meant
moving its left edge took a drag followed by a correction to both the position
and the width. Every side and every corner now has a grip, and the maths for
all eight lives here rather than in the item: it is ordinary rectangle
arithmetic with no Qt widgets involved, so it can be read and reasoned about on
its own.

Constants:
    HANDLES: Every grip, named for where it sits on the rectangle. Corners are
        named vertical-first, so ``"top_left"`` and never ``"left_top"``.
    MARGIN_SHARE: The largest share of a side a grip may cover. Without it the
        grips of a small window would overlap in the middle and a press there
        would resize from whichever side happened to be tested first.
"""

from PyQt6.QtCore import QRectF, Qt

HANDLES = (
    "top_left",
    "top",
    "top_right",
    "right",
    "bottom_right",
    "bottom",
    "bottom_left",
    "left",
)

MARGIN_SHARE = 1 / 3

_CURSORS = {
    "top_left": Qt.CursorShape.SizeFDiagCursor,
    "bottom_right": Qt.CursorShape.SizeFDiagCursor,
    "top_right": Qt.CursorShape.SizeBDiagCursor,
    "bottom_left": Qt.CursorShape.SizeBDiagCursor,
    "top": Qt.CursorShape.SizeVerCursor,
    "bottom": Qt.CursorShape.SizeVerCursor,
    "left": Qt.CursorShape.SizeHorCursor,
    "right": Qt.CursorShape.SizeHorCursor,
}


def handle_at(rect, point, margin):
    """Name the grip a point falls on.

    Args:
        rect (QRectF): The rectangle being grabbed, in item coordinates.
        point (QPointF): Where the cursor is, in item coordinates.
        margin (float): How thick a grip is.

    Returns:
        str | None: One of :data:`HANDLES`, or ``None`` when the point is in
        the middle of the rectangle and should start a drag instead.
    """
    if not rect.contains(point):
        return None
    margin = min(margin, rect.width() * MARGIN_SHARE, rect.height() * MARGIN_SHARE)
    vertical = ""
    horizontal = ""
    if point.y() - rect.top() <= margin:
        vertical = "top"
    elif rect.bottom() - point.y() <= margin:
        vertical = "bottom"
    if point.x() - rect.left() <= margin:
        horizontal = "left"
    elif rect.right() - point.x() <= margin:
        horizontal = "right"
    if vertical and horizontal:
        return f"{vertical}_{horizontal}"
    return vertical or horizontal or None


def cursor_for(handle):
    """Pick the cursor that shows which way a grip resizes.

    Args:
        handle (str | None): One of :data:`HANDLES`, or ``None``.

    Returns:
        Qt.CursorShape: The arrow for that grip, or the open hand used
        everywhere a press would drag the window instead.
    """
    return _CURSORS.get(handle, Qt.CursorShape.OpenHandCursor)


def resize_rect(rect, handle, point, min_size, bounds):
    """Work out the rectangle a grip drag has produced.

    Only the edges the grip belongs to move; the opposite edges stay where they
    are, which is what makes a top-left drag change the position as well as the
    size.

    Args:
        rect (QRectF): The rectangle before the drag.
        handle (str): One of :data:`HANDLES`.
        point (QPointF): Where the cursor is, in item coordinates.
        min_size (float): Smallest width or height the result may have.
        bounds (list): ``[min_x, max_x, min_y, max_y]`` the rectangle may not
            leave.

    Returns:
        QRectF: The resized rectangle.
    """
    left, top = rect.left(), rect.top()
    right, bottom = rect.right(), rect.bottom()
    if "left" in handle:
        left = min(max(point.x(), bounds[0]), right - min_size)
    if "right" in handle:
        right = max(min(point.x(), bounds[1]), left + min_size)
    if "top" in handle:
        top = min(max(point.y(), bounds[2]), bottom - min_size)
    if "bottom" in handle:
        bottom = max(min(point.y(), bounds[3]), top + min_size)
    return QRectF(left, top, right - left, bottom - top)


def moving_edges(handle):
    """Report which edges of a rectangle a grip drags.

    Snapping asks this so that resizing only ever pulls the edges under the
    cursor onto a guide, and leaves the anchored edges untouched.

    Args:
        handle (str): One of :data:`HANDLES`.

    Returns:
        tuple: ``(vertical_edge, horizontal_edge)`` where each is
        ``"left"``/``"right"``, ``"top"``/``"bottom"``, or ``None``.
    """
    vertical = "left" if "left" in handle else "right" if "right" in handle else None
    horizontal = "top" if "top" in handle else "bottom" if "bottom" in handle else None
    return vertical, horizontal
