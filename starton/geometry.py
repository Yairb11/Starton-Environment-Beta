"""Screen-region geometry shared by the editor and the start-up runner.

A window is positioned in one of two ways: with an explicit pixel size, or by
snapping it to a named region of its monitor (a half or a quarter of the
screen). Every place that turns a region name into a rectangle goes through
:func:`region_rect`, so the editor preview and the boot-time runner can never
disagree about what ``"Left_Top"`` means.

Constants:
    FULL_SCREEN: The region covering a whole monitor.
    REGIONS: Every supported region, in the order the editor cycles them.
    CUSTOM_TITLE: Title shown when a window has a pixel size, not a region.
    REGION_TITLES: Readable title of every region, aligned with REGIONS.
    WINDOW_STATE_TITLES: Titles indexed like the editor's window-state stack -
        index 0 is the custom-size page, index n is REGIONS[n - 1].
    REGION_GRID: The regions arranged as they sit on a screen, so the editor
        can offer them as a picker shaped like the monitor itself.
"""

FULL_SCREEN = "Full"

REGIONS = (
    "Full",
    "Left",
    "Right",
    "Top",
    "Bottom",
    "Left_Top",
    "Left_Bottom",
    "Right_Top",
    "Right_Bottom",
)

CUSTOM_TITLE = "CUSTOM"

REGION_TITLES = (
    "FULL SCREEN",
    "LEFT SIDE",
    "RIGHT SIDE",
    "TOP SIDE",
    "BOTTOM SIDE",
    "LEFT TOP CORNER",
    "LEFT BOTTOM CORNER",
    "RIGHT TOP CORNER",
    "RIGHT BOTTOM CORNER",
)

WINDOW_STATE_TITLES = (CUSTOM_TITLE,) + REGION_TITLES

REGION_GRID = (
    ("Left_Top", "Top", "Right_Top"),
    ("Left", "Full", "Right"),
    ("Left_Bottom", "Bottom", "Right_Bottom"),
)

_HALF_WIDTH = frozenset(
    {"Left", "Right", "Left_Top", "Left_Bottom", "Right_Top", "Right_Bottom"}
)
_HALF_HEIGHT = frozenset(
    {"Top", "Bottom", "Left_Top", "Left_Bottom", "Right_Top", "Right_Bottom"}
)
_RIGHT_ALIGNED = frozenset({"Right", "Right_Top", "Right_Bottom"})
_BOTTOM_ALIGNED = frozenset({"Bottom", "Left_Bottom", "Right_Bottom"})


def region_rect(region, x, y, width, height):
    """Place ``region`` inside the rectangle ``(x, y, width, height)``.

    Args:
        region (str): One of :data:`REGIONS`.
        x (int): Left edge of the containing rectangle.
        y (int): Top edge of the containing rectangle.
        width (int): Width of the containing rectangle.
        height (int): Height of the containing rectangle.

    Returns:
        tuple: ``(x, y, width, height)`` of the region. Unknown regions and
        ``"Full"`` return the containing rectangle unchanged.
    """
    half_width = width // 2
    half_height = height // 2
    if region in _RIGHT_ALIGNED:
        x += half_width
    if region in _BOTTOM_ALIGNED:
        y += half_height
    if region in _HALF_WIDTH:
        width = half_width
    if region in _HALF_HEIGHT:
        height = half_height
    return x, y, width, height


def region_edges(x, y, width, height):
    """List the lines a rectangle contributes for things to line up against.

    The lines are derived from :func:`region_rect` rather than worked out
    again, so a guide can never sit somewhere other than the edge of the region
    it promises.

    Args:
        x (int): Left edge of the rectangle.
        y (int): Top edge of the rectangle.
        width (int): Width of the rectangle.
        height (int): Height of the rectangle.

    Returns:
        tuple: ``(verticals, horizontals)``, each a tuple of three
        coordinates - the two outer edges and the midline between them.
    """
    mid_x, mid_y = region_rect("Right_Bottom", x, y, width, height)[:2]
    return (x, mid_x, x + width), (y, mid_y, y + height)


def match_region(rect, container, tolerance):
    """Name the region a rectangle has been dragged onto, if it is on one.

    ``"Full"`` is tested first, so a window covering a whole monitor is never
    mistaken for one of the halves it also touches.

    Args:
        rect (tuple): ``(x, y, width, height)`` of the rectangle to name.
        container (tuple): ``(x, y, width, height)`` of the monitor it sits on.
        tolerance (float): How far each edge may be off and still count.

    Returns:
        str | None: One of :data:`REGIONS`, or ``None`` when the rectangle
        matches no region closely enough.
    """
    for region in REGIONS:
        candidate = region_rect(region, *container)
        if all(abs(edge - want) <= tolerance for edge, want in zip(rect, candidate)):
            return region
    return None


def stack_index(region):
    """Return the editor stack page showing ``region`` (page 0 is custom size).

    Args:
        region (str): One of :data:`REGIONS`.

    Returns:
        int: Index into the window-state stack.
    """
    return REGIONS.index(region) + 1


def region_at(stack_index):
    """Return the region shown on a window-state stack page.

    Args:
        stack_index (int): Page index, 1 based. Page 0 is the custom-size page
            and has no region.

    Returns:
        str: One of :data:`REGIONS`.
    """
    return REGIONS[stack_index - 1]
