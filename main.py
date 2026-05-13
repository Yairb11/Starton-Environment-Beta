from screeninfo import get_monitors
import re
import sys
from PyQt6 import QtWidgets 
from  MainWindow import *
from App import *
from Link import *


FILE_PATH = r"X:\code\python\on_start\on_start_info.txt"
screens = []

def find_resolution():
    monitors = get_monitors()
    for _, monitor in enumerate(monitors):
        screens.append(monitor)
        
def get_file_text():
    file = open(FILE_PATH, "r")
    text = file.read()
    file.close()
    return text


def set_file_text(text):
    file = open(FILE_PATH, "w")
    file.write(text)
    file.close()

def get_from_file():
    file_info = get_file_text()
    chanks = {}
    xml_tags = ["open_apps", "oepn_urls"]
    for xml_tag in xml_tags:
        pattern = rf"<{xml_tag}>(.*?)</{xml_tag}>"
        info = re.search(pattern, file_info, re.DOTALL)
        if info:
            info_text = info.group(1).strip()
            chanks[xml_tag] = info_text
        else:
            print(f"{xml_tag} not found.")
    return chanks

def get_apps(raw_info):
    apps = []  
    apps_info = raw_info.split("\n")
    for app_raw_info in apps_info:
        app_info = app_raw_info.split(" ")
        
        app = App(app_info[0])
        app.set_app_path(app_info[1])
        
        if(app_info[2] == "None"):
            app.set_dir_path(None)
        else:
            app.set_dir_path(app_info[2])
            
        pos_raw_info = app_info[3]
        pos_info = (pos_raw_info[1:-1]).split(",")
        pos = [int(pos_info[i]) for i in range(len(pos_info))]
        app.set_pos(pos)
        
        size_raw_info = app_info[4]
        if(size_raw_info != "None"):
            size_info = (size_raw_info[1:-1]).split(",")
            app.set_size([int(size_info[i]) for i in range(len(size_info))])
        else:
            app.set_size(None)
        apps.append(app)
  
    return apps

def get_links(raw_info):
    links = []
    links_info = raw_info.split("\n")
    for link_raw_info in links_info:
        link_info = link_raw_info.split(" ")
        link = Link(link_info[0], link_info[1])
        links.append(link)
    return links

def on_start():
    find_resolution()
    chanks = get_from_file()
    apps = get_apps(chanks["open_apps"])
    links = get_links(chanks["oepn_urls"])
    return apps, links

if __name__ == "__main__":
    apps, links = on_start()
    desktop_app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(screens, apps, links)
    window.show()
    desktop_app.exec()


