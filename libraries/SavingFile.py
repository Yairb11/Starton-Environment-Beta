import re
from libraries.App import *
from libraries.Link import *
from libraries.Size import *

XML_TAGS = ["open_apps", "open_urls"]

class SavingFile:
    """Stores information about savingFile, its path  and how to read it, or write to it
    
    Attributes:
        file_path = path of the file
    """
    def __init__(self, file_path):
        """Initiates saveFile with file path

        Args:
            file_path (string): path of the file
        """
        self.file_path = file_path
        
    def read_file(self):
        """Reads the saveFile and returns list of all windows and links that will be openned
        on setup environment

        Returns:
            list: list of all window's apps that will be oppend on setup environment 
            list: list of all links that will be oppend on setup environment 
        """
        chanks = self.get_from_file()
        apps = self.get_apps(chanks[XML_TAGS[0]])
        links = self.get_links(chanks[XML_TAGS[1]])
        return apps, links
    
    def write_file(self, apps, links):
        """Writes into saveFile the windows and links that will be saved and oppend
        on setup environment

        Args:
            apps (list): list of all apps that will be oppend on setup environment
            links (list): list of all links that will be oppend on setup environment
        """
        apps_str = self.set_apps(apps)
        links_str = self.set_links(links)
        file_list = []
        file_list.append(f"<{XML_TAGS[0]}>")
        if apps_str:
            file_list.append(f"{apps_str}")
        file_list.append(f"</{XML_TAGS[0]}>")
        file_list.append(f"<{XML_TAGS[1]}>")
        if links_str:
            file_list.append(f"{links_str}")
        file_list.append(f"</{XML_TAGS[1]}>")
        self.set_file_text("\n".join(file_list))
    
    def get_from_file(self):
        """Splits the information from the saveFile into 2 chanks
        apps part, links part

        Returns:
            dict: splitted information
        """
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
        """Gets the splitted apps part from the saveFile and then
        gets from it apps information 

        Args:
            raw_info (string): splitted apps part from the saveFile

        Returns:
            list: list of apps information 
        """
        apps = []  
        if(raw_info != ""):
            pattern = rf"<app>(.*?)</app>"
            infos = re.findall(pattern, raw_info, re.DOTALL)
            for info in infos:
                app = self.text_to_app(info)
                apps.append(app)
            return apps
        return None
    
    def text_to_app(self,info):
        """Gets string as app information and returns app object with this information

        Args:
            info (string): app information

        Returns:
            App: app that is created from this app information
        """
        app_info = info.split("\n")[1:-1]
        app = App(app_info[0])
        app.set_app_path(app_info[1])
        pos_raw_info = app_info[2]
        pos_info = (pos_raw_info[1:-1]).split(",")
        pos = [int(pos_info[i]) for i in range(len(pos_info))]
        app.set_pos(pos)
        size_raw_info = app_info[3]
        app.set_size(Size(size_raw_info))  
        return app 
    
    def get_links(self, raw_info):
        """Gets the splitted links part from the saveFile and then
        gets from it links information 
        
        Args:
            raw_info (string): splitted links part from the saveFile

        Returns:
            list: list of links with the link information
        """
        links = []
        if(raw_info != ""):
            links_info = raw_info.split("\n")
            for link_raw_info in links_info:
                link_info = link_raw_info.split(" ")
                link = Link(link_info[0], link_info[1])
                links.append(link)
            return links
        return None
    
    def set_apps(self, apps): 
        """Gets list of apps and turns them into strings to save in saveFile

        Args:
            apps (list): list of apps

        Returns:
            string: string of all apps to be apps information in the saveFile
        """
        if apps:
            apps_list = []
            for app in apps:
                apps_list.append(str(app))
            return "\n".join(apps_list)
        return None
        
    
    def set_links(self, links):
        """Gets list of links and turns them into strings to save in saveFile

        Args:
            links (list): list of links

        Returns:
            string: string of all links to be apps information in the saveFile
        """
        if links:
            links_list = []
            for link in links:
                links_list.append(str(link))
            return "\n".join(links_list)
        return None
    
    def get_file_text(self):
        """Gets text from saveFile

        Returns:
            string: text from the file
        """
        file = open(self.file_path, "r", encoding='utf-8')
        text = file.read()
        file.close()
        return text
    
    def set_file_text(self, text):
        """Sets text into file

        Args:
            text (string): text that will be saved in the saveFile
        """
        file = open(self.file_path, "w", encoding='utf-8')
        file.write(text)
        file.close()
