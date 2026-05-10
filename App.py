import re
class App:
    def __init__(self, name):
        self.name = name
        self.app_path = ""
        self.dir_path = ""
        self.pos = [0, 0]
        self.size = [0, 0]
    
    def get_name(self):
        return self.name
    
    def set_app_path(self, app_path):
        self.app_path = app_path
    
    def get_app_path(self):
        return self.app_path
    
    def set_dir_path(self, dir_path):
        self.dir_path = dir_path
    
    def get_dir_path(self):
        return self.dir_path
    
    def set_pos(self, pos):
        self.pos = pos 
    
    def get_pos(self):
        return self.pos
    
    def set_size(self, size):
        self.size = size
    
    def get_size(self):
        return self.size
    
    def __str__(self):
        return f"{self.name}: {self.app_path}, {self.dir_path}, {self.pos}, {self.size}"
