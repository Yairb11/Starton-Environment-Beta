"""Moving and resizing top-level windows through the Win32 API.

Python has no portable way to place another program's window, so this module
talks to ``user32.dll`` directly with :mod:`ctypes`. It is the only Windows
specific code in the project.

Constants:
    SW_MAXIMIZE, SW_RESTORE: ``ShowWindow`` commands from the Win32 API.
    _POLL_INTERVAL: Seconds between polls while a program starts up.
    _SETTLE_DELAY: Pause after a window appears, giving it time to finish
        drawing itself before it is moved.
"""

import ctypes
import time

_user32 = ctypes.windll.user32
_ENUM_WINDOWS_PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

SW_MAXIMIZE = 3
SW_RESTORE = 9

_POLL_INTERVAL = 0.4

_SETTLE_DELAY = 0.5


def visible_windows():
    """Collect the handles of every visible, titled top-level window.

    Untitled windows are skipped because they are usually invisible helper
    windows rather than something the user launched.

    Returns:
        set: Window handles (HWNDs).
    """
    hwnds = set()

    def collect(hwnd, _lparam):
        if _user32.IsWindowVisible(hwnd) and _user32.GetWindowTextLengthW(hwnd) > 0:
            hwnds.add(hwnd)
        return True

    _user32.EnumWindows(_ENUM_WINDOWS_PROC(collect), 0)
    return hwnds


def wait_for_new_window(known_windows, timeout):
    """Wait for a window that was not open before, and return its handle.

    Args:
        known_windows (set): Handles captured before the program was launched.
        timeout (float): Seconds to keep waiting.

    Returns:
        int | None: Handle of the new window, or ``None`` if none appeared in
        time - a program that was already running, for instance.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(_POLL_INTERVAL)
        new_windows = visible_windows() - known_windows
        if new_windows:
            return next(iter(new_windows))
    return None


def place_window(hwnd, x, y, width, height, maximize):
    """Restore a window, move it, and optionally maximize it.

    Args:
        hwnd (int): Handle of the window to place.
        x (float): Left edge, in virtual-desktop coordinates.
        y (float): Top edge, in virtual-desktop coordinates.
        width (float): Window width.
        height (float): Window height.
        maximize (bool): Maximize the window after moving it, which is how a
            full-screen app ends up filling the monitor it was moved onto.

    Notes:
        The move is issued twice on purpose. Applications that are still
        initialising tend to ignore the first one and snap back to their own
        default geometry.
    """
    time.sleep(_SETTLE_DELAY)
    _user32.ShowWindow(hwnd, SW_RESTORE)
    for _ in range(2):
        _user32.MoveWindow(hwnd, int(x), int(y), int(width), int(height), True)
    if maximize:
        _user32.ShowWindow(hwnd, SW_MAXIMIZE)
