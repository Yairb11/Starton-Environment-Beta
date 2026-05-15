import re
from App import *
from Link import *

XML_TAGS = ["open_apps", "open_urls"]

class SavingFile:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def read_file(self):
        chanks = self.get_from_file()
        apps = self.get_apps(chanks[XML_TAGS[0]])
        links = self.get_links(chanks[XML_TAGS[1]])
        return apps, links
    
    def write_file(self, apps, links):
        apps_str = self.set_apps(apps)
        links_str = self.set_links(links)
        file_list =[
            f"<{XML_TAGS[0]}>" ,
            f"{apps_str}",
            f"</{XML_TAGS[0]}>",
            f"<{XML_TAGS[1]}>",
            f"{links_str}",
            f"</{XML_TAGS[1]}>"
        ]
        self.set_file_text("\n".join(file_list))
    
    def get_from_file(self):
        file_info = self.get_file_text()
        chanks = {}
        for xml_tag in XML_TAGS:
            pattern = rf"<{xml_tag}>(.*?)</{xml_tag}>"
            info = re.search(pattern, file_info, re.DOTALL)
            if info:
                info_text = info.group(1).strip()
                chanks[xml_tag] = info_text
            else:
                print(f"{xml_tag} not found.")
        return chanks

    
    def get_apps(self, raw_info):
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
    
    def get_links(self, raw_info):
        links = []
        links_info = raw_info.split("\n")
        for link_raw_info in links_info:
            link_info = link_raw_info.split(" ")
            link = Link(link_info[0], link_info[1])
            links.append(link)
        return links
    
    def set_apps(self, apps):
        apps_list = []
        for app in apps:
            apps_list.append(str(app))
        return "\n".join(apps_list)
    
    def set_links(self, links):
        links_list = []
        for link in links:
            links_list.append(str(link))
        return "\n".join(links_list)
    
    def get_file_text(self):
        file = open(self.file_path, "r")
        text = file.read()
        file.close()
        return text
    
    def set_file_text(self, text):
        file = open(self.file_path, "w")
        file.write(text)
        file.close()
