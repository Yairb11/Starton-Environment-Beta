class Link:
    """Stores information about the link that would be oppend on setup environment\
    
    Attributes:
        name(string): name of the link
        link(strinf): the link itself
    """
    def __init__(self, name, link):
        """Initializes link information

        Args:
            name(string): name of the link
            link(string): the link itself
        """
        self.name = name
        self.link = link
    
    def get_name(self):
        return self.name
    
    def get_link(self):
        return self.link
    
    def __str__(self):
        return f"{self.name} {self.link}"
    
    def __eq__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.name == other.name and self.link == other.link