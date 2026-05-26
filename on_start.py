import os
import time
import pygetwindow as gw 
import webbrowser
from App import *
from Link import *
from SavingFile import *
import sys
from PyQt6.QtWidgets import QApplication
from screeninfo import get_monitors

FILE_PATH = r"C:\Users\yairb\on_start_gui\on_start_info.txt"   


def get_full_spcae():
    # An application instance is required to query the screens
    q_app = QApplication(sys.argv)
    q_screens = q_app.screens()
    work_areas = []
    for i, screen in enumerate(q_screens):
        # availableGeometry() calculates the space minus taskbars/docks
        work_rect = screen.availableGeometry()
        work_areas.append({
            "monitor_id": i + 1,
            "x": work_rect.x(),
            "y": work_rect.y(),
            "width": work_rect.width(),
            "height": work_rect.height()
        })
        
    screens = []
    monitors = get_monitors()
    for _, monitor in enumerate(monitors):
        screens.append(monitor)
    return screens, work_areas

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

def open_apps(apps): 
    for app in apps:
        if app.get_dir_path():
            os.chdir(app.get_dir_path())
        os.startfile(f'"{app.get_app_path()}"')
        time.sleep(0.1)
    
def open_urls(links):
    for link in links:
        webbrowser.open(link.get_link())
        time.sleep(0.1)
   
def position_apps(apps):
    screens, workspaces = get_full_spcae()
    
    windows = gw.getAllWindows()
    for win in windows:
        for app in apps:
            if(app.is_folder() and (window_name_for(app.get_app_path()) == win.title.lower())) or ((not app.is_folder()) and (app.get_name().lower() in win.title.lower())):
                size_obj = app.get_size()
                size = size_obj.get_size()
                pos = app.get_pos()
                win.restore()
                if size_obj.get_is_list():
                    win.moveTo(pos[0], pos[1])
                    win.resizeTo(size[0], size[1])
                else:
                    if(size == "Full"):
                        win.moveTo(pos[0], pos[1])
                        win.maximize()
                    else:
                        if win.isMaximized or win.isMinimized:
                            win.restore()
                        screen_index = find_screen(screens, pos)
                        work_area = workspaces[screen_index]
                        pos_x = work_area["x"]
                        pos_y = work_area["y"]
                        width = work_area["width"]
                        heigth = work_area["height"]
                        half_width = work_area["width"] // 2
                        half_height = work_area["height"] // 2
                        match size:
                            case "Top":
                                heigth = half_height
                            case "Bottom":
                                heigth = half_height
                                pos_y += half_height
                            case "Left":
                                width = half_width
                            case "Right":
                                width = half_width
                                pos_x += half_width
                            case "Left_Top":
                                width = half_width
                                heigth = half_height
                            case "Left_Bottom":
                                width = half_width
                                heigth = half_height
                                pos_y += half_height
                            case "Right_Top":
                                width = half_width
                                heigth = half_height
                                pos_x += half_width
                            case "Right_Bottom":
                                width = half_width
                                heigth = half_height
                                pos_x += half_width
                                pos_y += half_height
                        win.moveTo(pos_x, pos_y)
                        win.resizeTo(width, heigth)
                        
def on_start():       
    print("Opening applications...")
    savingFile = SavingFile(FILE_PATH)
    apps, links = savingFile.read_file()
    if apps:
        open_apps(apps)
        time.sleep(3)
        position_apps(apps)  
    time.sleep(1)  
    if links:
        open_urls(links)  
    print("Finished")
    
    
    
if __name__ == "__main__":
    on_start()