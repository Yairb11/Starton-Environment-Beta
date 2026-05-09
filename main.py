
from screeninfo import get_monitors
import re
import sys
from PyQt6 import QtWidgets 
from  MainWindow import *



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
    apps_path = {}
    dirs_path = {} 
    poses = {}
    sizes = {}   
    apps_info = raw_info.split("\n")
    for app_raw_info in apps_info:
        app_info = app_raw_info.split(" ")
        
        apps_path[app_info[0]] = app_info[1]
        
        if(app_info[2] == "None"):
            dirs_path[app_info[0]] = None
        else:
            dirs_path[app_info[0]] = app_info[2]
            
        pos_raw_info = app_info[3]
        pos_info = (pos_raw_info[1:-1]).split(",")
        pos = [int(pos_info[i]) for i in range(len(pos_info))]
        poses[app_info[0]] = pos
        
        size_raw_info = app_info[4]
        if(size_raw_info != "None"):
            size_info = (size_raw_info[1:-1]).split(",")
            size = [int(size_info[i]) for i in range(len(size_info))]
        else:
            size = None
        sizes[app_info[0]] = size
  
    return apps_path, dirs_path, poses, sizes

def get_urls(raw_info):
    urls = {}
    urls_info = raw_info.split("\n")
    for url_raw_info in urls_info:
        url_info = url_raw_info.split(" ")
        urls[url_info[0]] = url_info[1]
    return urls

def on_start():
    find_resolution()
    chanks = get_from_file()
    apps_path, dirs_path, poses, sizes = get_apps(chanks["open_apps"])
    urls = get_urls(chanks["oepn_urls"])

    

if __name__ == "__main__":
    on_start()
    
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(screens)
    window.show()
    app.exec()


