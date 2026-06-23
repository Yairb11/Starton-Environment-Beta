CONS_OPTIONS = ["Full", "Top", "Bottom", "Left", "Right", "Left_Top", "Right_Top", "Left_Bottom", "Right_Bottom"]

class Size:
    """Stores information about size of a window
    
    Attributes:
        is_list(list): is the window size is constant
        size(str / list): is the size of a window, if it constatn size then list of width and height size, else one of CONS_OPTIONS
    """
    def __init__(self, size_info):
        """From the size_info decides if size is constant or one of CONS_OPTIONS, then initiates size state

        Args:
            size_info (str / list): size information of a window
        """
        if(str(type(size_info)) == "<class \'str'>"):
            if(size_info in CONS_OPTIONS):
                self.size = size_info
                self.is_list = False
            else:
                sub_size_info = (size_info[1:-1]).split(",")
                self.size = [int(sub_size_info[i]) for i in range(len(sub_size_info))]
                self.is_list = True
        else:
            self.is_list = True
            self.size = []
            self.size.append(size_info[0])
            self.size.append(size_info[1])
    
    def get_is_list(self):
        return self.is_list
    
    def get_size(self):
        return self.size
    
    def __str__(self):
        if self.is_list:
            return f"[{self.size[0]},{self.size[1]}]"
        return self.size