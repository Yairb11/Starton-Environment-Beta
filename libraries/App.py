from libraries.Size import *
class App:
    """Stores information about the app that would be oppend on setup environment\
    
    Attributes:
        name(string): name of the app
        app_path(string): path to the app
        pos(list): list of the position of the window on the screen
        size(Size): size of the window on the screen
    """
    def __init__(self, name, path = "", pos = [0, 0], size = Size([0,0])):
        """Initializes app information

        Args:
            name(string): name of the app
            app_path(string): path to the app
            pos(list): list of the position of the window on the screen
            size(Size, optional): size of the window on the screen. Defaults to Size([0,0]).
        """
        self.name = name
        self.app_path = path
        self.pos = pos
        self.size = size
    
    def get_name(self):
        return self.name
    
    def set_app_path(self, app_path):
        self.app_path = app_path
    
    def get_app_path(self):
        return self.app_path
    
    def set_pos(self, pos):
        self.pos = pos 
    
    def get_pos(self):
        return self.pos
    
    def set_size(self, size):
        self.size = size
    
    def get_size(self):
        return self.size
    
    def __str__(self):
        pos_str = f"[{self.pos[0]},{self.pos[1]}]"
        return f"<app>\n{self.name}\n{self.app_path}\n{pos_str}\n{str(self.size)}\n</app>"
    
    def change_app(self, name, app_path, pos, size):
        """Changes information about the app

        Args:
            name(string): name of the app
            app_path(string): path to the app
            pos(list): list of the position of the window on the screen
            size(Size): size of the window on the screen
        """
        self.name = name
        self.app_path = app_path
        self.pos = []
        self.pos.append(pos[0])
        self.pos.append(pos[1])
        self.size = size
    
    def __eq__(self, other):
        if not isinstance(other, App):
            return NotImplemented
        return str(self) == str(other)
    
    def is_folder(self):
        """Checks if the app is a folder

        Returns:
            bool: if the app is a folder
        """
        if(self.app_path[-1] == "\\"):
            return True
        return False
    
    def get_app_path_folder(self):
        """Gets the folder that the app sits in

        Returns:
            string: folder path
        """
        if self.is_folder():
            return self.app_path
        folders = self.app_path.split("\\")[:-1]
        full_folder = "\\".join(folders)
        return full_folder
        
    
        
