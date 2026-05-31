import os
import time
import ctypes
import webbrowser
from pathlib import Path
from libraries.App import *
from libraries.Link import *
from libraries.SavingFile import *
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
    monitors = get_monitors()
    return len(monitors)

def get_full_spcae():
    screens = []
    monitors = get_monitors()
    for _, monitor in enumerate(monitors):
        screens.append(monitor)
    return screens

def find_screen(monitors, pos):
    for i, monitor in enumerate(monitors):
        x, y, width, height  = monitor.x, monitor.y, monitor.width, monitor.height
        if (pos[0] >= x and pos[0] < x + width) and (pos[1] >= y and pos[1] < y + height):
            return i
    return -1

def window_name_for(path):
    if(path[-2] == ":"):
        return f"{path} - File Explorer".lower()
    return f"{path[:-1]} - File Explorer".lower()

def get_all_visible_windows():
    """Returns a set of window handles (HWNDs) for all visible top-level windows."""
    hwnds = set()
    def callback(hwnd, lParam):
        if user32.IsWindowVisible(hwnd) and user32.GetWindowTextLengthW(hwnd) > 0:
            hwnds.add(hwnd)
        return True
    user32.EnumWindows(EnumWindowsProc(callback), 0)
    return hwnds

def open_urls(links):
    for link in links:
        webbrowser.open(link.get_link())
        time.sleep(0.1)
                         
def get_position_and_size(pos, size_obj, screens):
    size = size_obj.get_size()
    if size_obj.get_is_list():
        return pos[0], pos[1], size[0], size[1], False
    screen_index = find_screen(screens, pos)
    monitor = screens[screen_index] 
    pos_x = monitor.x
    pos_y = monitor.y
    width = monitor.width
    height = monitor.height
    half_width = monitor.width // 2
    half_height = monitor.height // 2
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

def launch_and_resize(screens, app,  timeout = 10):
    file_path = app.get_app_path()
    pos = app.get_pos()
    size_obj = app.get_size()
    x, y, width, height, maximize = get_position_and_size(pos, size_obj, screens)
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
        user32.MoveWindow(new_hwnd, x, y, width, height, True)
        user32.ShowWindow(new_hwnd, SW_MAXIMIZE)
    else:
        user32.MoveWindow(new_hwnd, x, y, width, height, True)
    
def open_apps(apps): 
    screens = get_full_spcae()
    for app in apps:
        launch_and_resize(screens, app)
    

def is_first_time():
    if getattr(sys, 'frozen', False):
        project_dit = Path(sys.executable).parent.resolve()
    else:
        project_dit = Path(__file__).parent.resolve()  
    info_files_path = project_dit / "info"
    setup_info_path = info_files_path / f"OnSetupInfo_{find_number_of_screens()}.txt"
    if os.path.exists(setup_info_path): 
        print("Exit 0")
        return setup_info_path
    setup_info_path.write_text(ON_SETUP_INFO_TEXT, encoding='utf-8')
    return setup_info_path
        
                       
def on_start():       
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