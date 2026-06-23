import os
import time
import ctypes
import webbrowser
from pathlib import Path
from libraries.App import *
from libraries.Link import *
from libraries.SavingFile import *
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QScreen
import sys
from screeninfo import get_monitors

ON_SETUP_INFO_TEXT = '''<open_apps>
</open_apps>
<open_urls>
</open_urls>'''
user32 = ctypes.windll.user32
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

SW_MAXIMIZE = 3
SW_RESTORE = 9

def find_number_of_screens():
    """returns number of monitors that are connected to the computer

    Returns:
        number: number of monitors that are connected to the computer
    """
    monitors = get_monitors()
    return len(monitors)

def find_screen_combination():
    """finds each monitor layout for saving them(L - landscape, P - portrait)

    Returns:
        string: all monitor layouts
    """
    combination = ""
    monitors = get_monitors()
    for _, monitor in enumerate(monitors):
        if(monitor.width >= monitor.height):
            combination = combination + "L"
        else:
            combination = combination + "P"
    return combination

def get_full_spcae():
    """Gets full information about all the monitors

    Returns:
        list: list of all monitors information
        list: list of all monitors work space
    """
    screens = []
    monitors = get_monitors()
    for _, monitor in enumerate(monitors):
        screens.append(monitor)
        
    q_app = QApplication(sys.argv)
    q_screens = q_app.screens()
    work_areas = []
    for i, screen in enumerate(q_screens):
        monitor = screens[i]
        geometry = screen.geometry()
        available_geometry = screen.availableGeometry()
        change_in_geometry = [geometry.width() - available_geometry.width(), geometry.height() - available_geometry.height()]
        work_area = QRect(geometry.x(), geometry.y(), monitor.width - change_in_geometry[0], monitor.height - change_in_geometry[1])
        work_areas.append(work_area)
    return screens, work_areas

def find_screen(monitors, pos):
    """Find monitor with this position input,
    if it doesnt fines the monitor, then it returns -1

    Args:
        monitors (list): list of all monitors
        pos (list): position list, width and height

    Returns:
        number: index of the monitor from the monitor list
    """
    for i, monitor in enumerate(monitors):
        x, y, width, height  = monitor.x, monitor.y, monitor.width, monitor.height
        if (pos[0] >= x and pos[0] < x + width) and (pos[1] >= y and pos[1] < y + height):
            return i
    return -1

def get_all_visible_windows():
    """
    Retrieves a collection of handles for all visible top-level windows.

    This function utilizes the Windows API (via ctypes) to enumerate all top-level
    windows currently on the screen. It applies a filter to ensure only windows 
    that are both visible to the user and have an assigned window title are captured.

    Returns:
        set: A set containing the integer handles (HWND) of the visible windows.
    """
    hwnds = set()
    def callback(hwnd, lParam):
        if user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
            hwnds.add(hwnd)
        return True
    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return hwnds

def open_urls(links):
    """Opens all links from list of links

    Args:
        links (list): list of links
    """
    for link in links:
        webbrowser.open(link.get_link())
        time.sleep(0.1)
                         
def get_position_and_size(pos, size_obj, screens, workspaces):
    """Calculates the numerical values of screen position and size,
    returns this values and bool statement for if this size is a fullscreen or not

    Args:
        pos (list): list with x,y number that represent position
        size_obj (Size): size of the window
        screens (list): Screen list of all screens
        workspaces (list): Screen list of all workingspace of each screen

    Returns:
        number: x position
        number: y position
        number: widht
        number: height
        bool: is it fullscreen
    """
    size = size_obj.get_size()
    if size_obj.get_is_list():
        return pos[0] , pos[1], size[0], size[1], False
    screen_index = find_screen(screens, pos)
    monitor = workspaces[screen_index] 
    pos_x = monitor.left()
    pos_y = monitor.top()
    width = monitor.right() - monitor.left()
    height = monitor.bottom() - monitor.top()
    half_width = ((monitor.right() - monitor.left())// 2)
    half_height = ((monitor.bottom() - monitor.top())// 2)
    if(size == "Full"):
        return pos[0], pos[1], half_width, half_height, True
    match size:
        case "Top":
            height = half_height
        case "Bottom":
            height = half_height
            pos_y += half_height
        case "Left":
            width = half_width
        case "Right":
            width = half_width
            pos_x += half_width
        case "Left_Top":
            width = half_width
            height = half_height
        case "Left_Bottom":
            width = half_width
            height = half_height
            pos_y += half_height
        case "Right_Top":
            width = half_width
            height = half_height
            pos_x += half_width
        case "Right_Bottom":
            width = half_width
            height = half_height
            pos_x += half_width
            pos_y += half_height
    
    return pos_x, pos_y, width, height, False

def launch_and_resize(screens, workspaces, app,  timeout = 10):
    """launches, resizes and positions an app.

    Args:
        screens (list): list of all monitors information
        workspaces (list): list of all monitors work space
        app (App): app that will be opened
        timeout (int, optional): number of seconds for waiting until the upp is appened(if not, it'll moveon). Defaults to 10.
    """
    file_path = app.get_app_path()
    pos = app.get_pos()
    size_obj = app.get_size()
    x, y, width, height, maximize = get_position_and_size(pos, size_obj, screens, workspaces)
    before_windows = get_all_visible_windows()
    os.startfile(f'"{file_path}"')
    start_time = time.time()
    new_hwnd = None
    while time.time() - start_time < timeout:
        time.sleep(0.4) 
        current_windows = get_all_visible_windows()
        new_windows = current_windows - before_windows
        if new_windows:
            new_hwnd = list(new_windows)[0]
            break
    if not new_hwnd:
        return 
    time.sleep(0.5)
    user32.ShowWindow(new_hwnd, SW_RESTORE)
    if maximize:
        user32.MoveWindow(new_hwnd, int(x), int(y), int(width), int(height), True)
        user32.MoveWindow(new_hwnd, int(x), int(y), int(width), int(height), True)
        user32.ShowWindow(new_hwnd, SW_MAXIMIZE)
    else:
        user32.MoveWindow(new_hwnd, int(x), int(y), int(width), int(height), True)
        user32.MoveWindow(new_hwnd, int(x), int(y), int(width), int(height), True)
    
def open_apps(apps): 
    """opens all apps from the apps list, resizes them and positions them

    Args:
        apps (list): list of apps
    """
    screens, workspaces = get_full_spcae()
    for app in apps:
        launch_and_resize(screens, workspaces, app)

def is_first_time():
    """Checks if this is the first time using this application, then creates the basic structure for this app to work
    and returns path for setup environment information text file

    Returns:
        string: path for setup environment information text file
    """
    if getattr(sys, 'frozen', False):
        project_dit = Path(sys.executable).parent.resolve()
    else:
        project_dit = Path(__file__).parent.resolve()  
    number_of_screens = find_number_of_screens()
    screen_combination = find_screen_combination()
    info_files_path = project_dit / "info"
    setup_info_path = info_files_path / f"OnSetupInfo_{number_of_screens}{screen_combination}.txt"
    if os.path.exists(setup_info_path): 
        print("Exit 0")
        return setup_info_path
    setup_info_path.write_text(ON_SETUP_INFO_TEXT, encoding='utf-8')
    return setup_info_path 
        
                       
def on_start():
    """Runs the program"""
    file_path = is_first_time()
    print("Opening applications...")
    savingFile = SavingFile(file_path)
    apps, links = savingFile.read_file()
    if apps:
        open_apps(apps)
    time.sleep(1)
    if links:
        open_urls(links)  
    print("Finished")
       
if __name__ == "__main__":

    on_start()