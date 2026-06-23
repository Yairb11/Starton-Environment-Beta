from libraries.MainWindow import *
from libraries.App import *
from libraries.Link import *
from libraries.SavingFile import *
from screeninfo import get_monitors
import sys
import os
import shutil
from pathlib import Path
from PyQt6 import QtWidgets 

APPDATA_SETUP_PATH = r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
ON_SETUP_INFO_TEXT = '''<open_apps>
</open_apps>
<open_urls>
</open_urls>'''

def find_resolution():
    """Saves all monitors information into one list

    Returns:
        list: list of all monitor information
    """
    screens = []
    monitors = get_monitors()
    for _, monitor in enumerate(monitors):
        screens.append(monitor)
    return screens

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
       
def is_first_time():
    """Checks if its the first time running this .exe, it make sure that all the file exist in the right place
    then returns the path to the saveFile with all the information

    Returns:
        string: path to the saveFile with all the information
    """
    if getattr(sys, 'frozen', False):
        project_dit = Path(sys.executable).parent.resolve()
    else:
        project_dit = Path(__file__).parent.resolve()  
    number_of_screens = find_number_of_screens()
    screen_combination = find_screen_combination()
    info_files_path = project_dit / "info"
    setup_info_path = info_files_path / f"OnSetupInfo_{number_of_screens}{screen_combination}.txt"
    launch_apps_file = info_files_path / "launch_apps.bat"
    on_setup_file = project_dit / "OnSetup.py"
    startup_folder = Path(os.path.expandvars(APPDATA_SETUP_PATH))
    startup_launch_app_dest = startup_folder / "launch_apps.bat"
    bat_script = f'@echo off\nstart "" pythonw "{on_setup_file}"'
    if os.path.exists(info_files_path):
        if os.path.exists(setup_info_path): 
            print("Exit 0")
            return setup_info_path
        setup_info_path.write_text(ON_SETUP_INFO_TEXT, encoding='utf-8')
        
        if not os.path.exists(startup_launch_app_dest):
            shutil.copy(launch_apps_file, startup_launch_app_dest)
            print("Exit 1")
        else:
            print("Exit 2")
        return setup_info_path
    
    Path(info_files_path).mkdir(parents=True, exist_ok=True)
    launch_apps_file.write_text(bat_script, encoding='utf-8')
    setup_info_path.write_text(ON_SETUP_INFO_TEXT, encoding='utf-8')
    print(ON_SETUP_INFO_TEXT)
    if not os.path.exists(startup_launch_app_dest):
        shutil.copy(launch_apps_file, startup_launch_app_dest)
        print("EXit 3")
    else:
        print("Exit 4")
    return setup_info_path
        
def on_start(file_path):
    """Gets all the information from the monitors and the saveFile to start the .exe application

    Args:
        file_path (string): file path of the saveFile

    Returns:
        list: list of all screen information
        list: list of all apps information
        list: list of all links information
        SaveFile: the saveFile file
    """
    screens = find_resolution()
    saving_file = SavingFile(file_path)
    apps, links = saving_file.read_file()
    return screens, apps, links, saving_file
if __name__ == "__main__":
    """Runs when the .exe file executed and executes the window with all the information needed """
    file_path = is_first_time()
    screens, apps, links, saving_file = on_start(file_path)
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
    os.environ["QT_FONT_DPI"] = "96"
    desktop_app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(screens, apps, links, saving_file)
    window.show()
    sys.exit(desktop_app.exec())


