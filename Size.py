CONS_OPTIONS = ["Full", "Top", "Bottom", "Left", "Right", "Left_Top", "Right_Top", "Left_Bottom", "Right_Bottom"]

class Size:
    def __init__(self, size_info):
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