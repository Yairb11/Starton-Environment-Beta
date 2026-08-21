"""Rebuild the saved environment: open every app and link, then place them.

Constants:
    LAUNCH_TIMEOUT: Seconds to wait for a launched program to put its window
        on screen.
    URL_OPEN_DELAY: Pause between opening browser tabs so they keep the order
        they were saved in.
    BROWSER_DELAY: Pause after the apps are placed, before the browser starts
        opening tabs.
"""

import os
import sys
import time
import webbrowser

from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QApplication

from starton import monitors
from starton.geometry import FULL_SCREEN, region_rect
from starton.installer import resolve_save_file
from starton.storage import SaveFile
from starton.startup import window_manager

LAUNCH_TIMEOUT = 10

URL_OPEN_DELAY = 0.1

BROWSER_DELAY = 1


def run():
    """Open everything saved for the monitors connected right now.

    Links the user switched off stay in the save file and are simply skipped.
    """
    apps, links = SaveFile(resolve_save_file()).read_file()
    apps = apps or []
    links = [link for link in links or [] if link.is_enabled()]
    if apps:
        open_apps(apps)
    time.sleep(BROWSER_DELAY)
    if links:
        open_urls(links)


def open_apps(apps):
    """Launch every app and move its window into place.

    Args:
        apps (list): Apps to open, in saved order.
    """
    screens, work_areas = screens_and_work_areas()
    for app in apps:
        launch_and_place(app, screens, work_areas)


def open_urls(links):
    """Open every link in the default browser.

    Args:
        links (list): Links to open, in saved order.
    """
    for link in links:
        webbrowser.open(link.get_link())
        time.sleep(URL_OPEN_DELAY)


def launch_and_place(app, screens, work_areas, timeout=LAUNCH_TIMEOUT):
    """Start one app and move the window it opens.

    Windows offers no reliable way to ask "which window belongs to the process
    I just started", so the new window is identified by diffing the set of
    visible windows before and after the launch. If nothing new appears within
    ``timeout`` the app is left alone rather than moving somebody else's
    window.

    Args:
        app (App): The app to launch.
        screens (list): Every connected monitor.
        work_areas (list): Usable area of each monitor, taskbar excluded.
        timeout (float, optional): Seconds to wait for the window. Defaults to
            :data:`LAUNCH_TIMEOUT`.
    """
    x, y, width, height, maximize = target_geometry(
        app.get_pos(), app.get_size(), screens, work_areas
    )
    known_windows = window_manager.visible_windows()
    os.startfile(f'"{app.get_app_path()}"')
    hwnd = window_manager.wait_for_new_window(known_windows, timeout)
    if hwnd is None:
        return
    window_manager.place_window(hwnd, x, y, width, height, maximize)


def target_geometry(pos, size, screens, work_areas):
    """Work out where a window should end up on screen.

    Args:
        pos (list): Saved ``[x, y]`` in virtual-desktop coordinates.
        size (WindowSize): Saved window size.
        screens (list): Every connected monitor.
        work_areas (list): Usable area of each monitor, taskbar excluded.

    Returns:
        tuple: ``(x, y, width, height, maximize)``. ``maximize`` is ``True``
        only for full-screen windows, which are maximized by Windows itself
        instead of being stretched to a computed size.
    """
    if size.get_is_list():
        width, height = size.get_size()
        return pos[0], pos[1], width, height, False

    region = size.get_size()
    work_area = work_areas[monitors.find_screen_index(screens, pos)]
    width = work_area.right() - work_area.left()
    height = work_area.bottom() - work_area.top()
    if region == FULL_SCREEN:
        return pos[0], pos[1], width // 2, height // 2, True
    x, y, width, height = region_rect(
        region, work_area.left(), work_area.top(), width, height
    )
    return x, y, width, height, False


def screens_and_work_areas():
    """Measure every monitor and the space left over once the taskbar is out.

    Qt is the only dependency here that knows about the taskbar, so a
    :class:`QApplication` is needed to read the available geometry. The
    editor already has one when it calls in to test a single app, and a
    second instance is not allowed, so an existing one is reused.

    Returns:
        tuple: ``(screens, work_areas)`` - monitors and a matching list of
        :class:`QRect` usable areas.
    """
    screens = monitors.get_screens()
    qt_app = QApplication.instance() or QApplication(sys.argv)
    work_areas = []
    for index, qt_screen in enumerate(qt_app.screens()):
        monitor = screens[index]
        geometry = qt_screen.geometry()
        available = qt_screen.availableGeometry()
        work_areas.append(
            QRect(
                geometry.x(),
                geometry.y(),
                monitor.width - (geometry.width() - available.width()),
                monitor.height - (geometry.height() - available.height()),
            )
        )
    return screens, work_areas
