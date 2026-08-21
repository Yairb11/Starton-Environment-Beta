"""An application window in a saved environment."""

import os

from starton.models.window_size import WindowSize


class App:
    """A program to launch on boot, and where to put its window.

    Attributes:
        name (str): Label shown in the editor.
        app_path (str): Path to the executable or folder to open.
        pos (list): ``[x, y]`` in virtual-desktop coordinates, so the value
            already identifies which monitor the window belongs to.
        size (WindowSize): Size of the window once it opens.
    """

    def __init__(self, name, path="", pos=None, size=None):
        """Store the app details.

        Args:
            name (str): Label shown in the editor.
            path (str, optional): Path to the executable or folder. Defaults to
                an empty string.
            pos (list, optional): ``[x, y]`` position. Defaults to ``[0, 0]``.
            size (WindowSize, optional): Window size. Defaults to a zero size.
        """
        self.name = name
        self.app_path = path
        self.pos = [0, 0] if pos is None else pos
        self.size = WindowSize([0, 0]) if size is None else size

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

    def change_app(self, name, app_path, pos, size):
        """Overwrite every field at once, as the editor's SAVE button does.

        Args:
            name (str): New label.
            app_path (str): New path to the executable or folder.
            pos (list): New ``[x, y]`` position. Copied, not referenced, so the
                caller can keep editing its own list.
            size (WindowSize): New window size.
        """
        self.name = name
        self.app_path = app_path
        self.pos = [pos[0], pos[1]]
        self.size = size

    def path_exists(self):
        """Report whether the saved path still points at something real.

        A path can rot between boots - the program gets uninstalled, or lives
        on a drive that is not mounted right now - and the only symptom at
        boot is a window that never appears.

        Returns:
            bool: ``True`` when the path exists on this machine.
        """
        return bool(self.app_path) and os.path.exists(self.app_path)

    def is_folder(self):
        """Report whether the saved path points at a folder rather than a file.

        Returns:
            bool: ``True`` when the path ends in a separator.
        """
        return self.app_path.endswith(os.sep)

    def get_app_path_folder(self):
        """Return the folder the app lives in, for seeding the file browser.

        Returns:
            str: :attr:`app_path` itself when it is already a folder, otherwise
            its parent folder.
        """
        if self.is_folder():
            return self.app_path
        return os.sep.join(self.app_path.split(os.sep)[:-1])

    def __str__(self):
        """Render the app as the block the save file stores.

        Returns:
            str: The ``<app>`` block.
        """
        return (
            f"<app>\n{self.name}\n{self.app_path}\n"
            f"[{self.pos[0]},{self.pos[1]}]\n{self.size}\n</app>"
        )

    def __eq__(self, other):
        if not isinstance(other, App):
            return NotImplemented
        return str(self) == str(other)
