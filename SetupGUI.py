from screeninfo import get_monitors
import sys
import os
import shutil
from pathlib import Path
from PyQt6 import QtWidgets 
from libraries.MainWindow import *
from libraries.App import *
from libraries.Link import *
from libraries.SavingFile import *

APPDATA_SETUP_PATH = r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
ON_SETUP_INFO_TEXT = '''<open_apps>
</open_apps>
<open_urls>
</open_urls>'''

def find_resolution():
    screens = []
    monitors = get_monitors()
    for _, monitor in enumerate(monitors):
        screens.append(monitor)
    return screens

def find_number_of_screens():
    monitors = get_monitors()
    return len(monitors)
        
def is_first_time():
    if getattr(sys, 'frozen', False):
        project_dit = Path(sys.executable).parent.resolve()
    else:
        project_dit = Path(__file__).parent.resolve()  
    info_files_path = project_dit / "info"
    setup_info_path = info_files_path / f"OnSetupInfo_{find_number_of_screens()}.txt"
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

    if not os.path.exists(startup_launch_app_dest):
        shutil.copy(launch_apps_file, startup_launch_app_dest)
        print("EXit 3")
    else:
        print("Exit 4")
    return setup_info_path
        
def on_start(file_path):
    screens = find_resolution()
    saving_file = SavingFile(file_path)
    apps, links = saving_file.read_file()
    return screens, apps, links, saving_file
if __name__ == "__main__":
    file_path = is_first_time()
    screens, apps, links, saving_file = on_start(file_path)
    desktop_app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(screens, apps, links, saving_file)
    window.show()
    desktop_app.exec()


