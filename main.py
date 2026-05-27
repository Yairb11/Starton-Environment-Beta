from screeninfo import get_monitors
import sys
from PyQt6 import QtWidgets 
from  MainWindow import *
from App import *
from Link import *
from SavingFile import *


FILE_PATH = r"<full path to on_start_info.txt>"

def find_resolution():
    screens = []
    monitors = get_monitors()
    for _, monitor in enumerate(monitors):
        screens.append(monitor)
    return screens
        
def on_start():
    screens = find_resolution()
    saving_file = SavingFile(FILE_PATH)
    apps, links = saving_file.read_file()
    return screens, apps, links, saving_file
if __name__ == "__main__":
    screens, apps, links, saving_file = on_start()
    desktop_app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(screens, apps, links, saving_file)
    window.show()
    desktop_app.exec()


