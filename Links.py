import winreg

ASSOCSTR_EXECUTABLE = 2

class Links:
    def __init__(self, urls = {}):
        self.links = []
        for link_name in urls:
            link = Link(link_name, urls[link_name])
            self.links.append(link)
        prog_name = self.get_default_browser_progid()
        browser_names = {
            "ChromeHTML": "chrome",
            "MSEdgeHTM": "edge",
            "FirefoxURL": "firefox",
            "BraveHTML": "brave",
            "OperaStable": "opera",
            "VivaldiHTM": "vivaldi"
        }
        self.default_app = browser_names.get(prog_name, prog_name)
    
    def get_default_browser_progid(self):
        try:
            reg_path = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                prog_id, _ = winreg.QueryValueEx(key, "ProgId")     
            return prog_id
        except FileNotFoundError:
            return None
        except Exception as e:
            return f"Error: {e}"
    
    def get_default_browser(self):
        return self.default_app

    def is_empty(self):
        return len(self.links) == 0
    
    def __str__(self):
        str_links = ""
        for link in self.links:
            str_links = str_links + "\n" + str(link)
        return str_links

class Link:
    def __init__(self, name, link):
        self.name = name
        self.link = link
    
    def __str__(self):
        return f"{self.name}: {self.link}"

