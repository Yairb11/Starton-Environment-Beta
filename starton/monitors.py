"""Discovery of the physical monitors attached to the machine.

Everything here is a thin wrapper around :mod:`screeninfo` so the rest of the
project never has to care where monitor data comes from.
"""

from screeninfo import get_monitors


def get_screens():
    """List every connected monitor.

    Returns:
        list: ``screeninfo`` monitor objects, in the order the OS reports them.
    """
    return list(get_monitors())


def screen_count():
    """Count the connected monitors.

    Returns:
        int: Number of monitors.
    """
    return len(get_monitors())


def layout_signature():
    """Describe the orientation of every monitor as a short string.

    The signature is part of the save-file name, so a laptop docked to two
    landscape screens keeps a different environment from the same laptop on
    its own.

    Returns:
        str: One character per monitor - ``"L"`` for landscape, ``"P"`` for
        portrait. Two landscape screens give ``"LL"``.
    """
    return "".join(
        "L" if monitor.width >= monitor.height else "P" for monitor in get_monitors()
    )


def primary_screen(screens):
    """Return the monitor Windows treats as the primary one.

    Args:
        screens (list): Monitors to search.

    Returns:
        The primary monitor, or ``None`` if no monitor is flagged as primary.
    """
    for monitor in screens:
        if monitor.is_primary:
            return monitor
    return None


def find_screen_index(screens, pos):
    """Find which monitor a virtual-desktop position falls on.

    Args:
        screens (list): Monitors to search.
        pos (list): ``[x, y]`` in virtual-desktop coordinates.

    Returns:
        int: Index into ``screens``, or ``-1`` when the position is off screen.
    """
    for index, monitor in enumerate(screens):
        on_screen_x = monitor.x <= pos[0] < monitor.x + monitor.width
        on_screen_y = monitor.y <= pos[1] < monitor.y + monitor.height
        if on_screen_x and on_screen_y:
            return index
    return -1


def bounding_box(screens):
    """Measure the rectangle that encloses every monitor.

    Args:
        screens (list): Monitors to measure.

    Returns:
        tuple: ``(min_x, min_y, max_x, max_y)`` in virtual-desktop coordinates.
    """
    min_x = min(monitor.x for monitor in screens)
    min_y = min(monitor.y for monitor in screens)
    max_x = max(monitor.x + monitor.width for monitor in screens)
    max_y = max(monitor.y + monitor.height for monitor in screens)
    return min_x, min_y, max_x, max_y


def total_size(screens):
    """Measure how much room every monitor takes up together.

    Args:
        screens (list): Monitors to measure.

    Returns:
        tuple: ``(width, height)`` of the whole virtual desktop.
    """
    min_x, min_y, max_x, max_y = bounding_box(screens)
    return max_x - min_x, max_y - min_y
