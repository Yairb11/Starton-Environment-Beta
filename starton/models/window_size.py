"""The size of a window in a saved environment."""

from starton.geometry import REGIONS


class WindowSize:
    """How large a window should be when it opens.

    A size is one of two things: an explicit ``[width, height]`` pixel pair, or
    the name of a screen region such as ``"Left_Top"`` that is resolved against
    whichever monitor the window lands on. Region sizes survive a change of
    resolution; pixel sizes do not, which is why the editor offers both.

    Attributes:
        size (list | str): ``[width, height]`` or a region name.
        is_list (bool): ``True`` when :attr:`size` is a pixel pair.
    """

    def __init__(self, size_info):
        """Build a size from either a pixel pair or a saved string.

        Args:
            size_info (list | str): ``[width, height]``, a region name, or the
                ``"[width,height]"`` text form used in the save file.
        """
        if isinstance(size_info, str):
            if size_info in REGIONS:
                self.size = size_info
                self.is_list = False
            else:
                self.size = self._parse_pair(size_info)
                self.is_list = True
        else:
            self.size = [size_info[0], size_info[1]]
            self.is_list = True

    @staticmethod
    def _parse_pair(text):
        """Read the ``"[width,height]"`` form written to the save file.

        Args:
            text (str): The bracketed pair.

        Returns:
            list: ``[width, height]`` as integers.
        """
        return [int(value) for value in text[1:-1].split(",")]

    def get_is_list(self):
        return self.is_list

    def get_size(self):
        return self.size

    def __str__(self):
        if self.is_list:
            return f"[{self.size[0]},{self.size[1]}]"
        return self.size
