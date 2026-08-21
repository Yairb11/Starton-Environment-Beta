"""A browser link opened when the environment starts."""


class Link:
    """A named URL to open on boot.

    Attributes:
        name (str): Label shown in the editor, for example ``"GitHub"``.
        link (str): The URL itself.
        enabled (bool): Whether the link opens on boot. A disabled link stays
            in the list and simply sits the next boot out.
    """

    def __init__(self, name, link, enabled=True):
        """Store the link details.

        Args:
            name (str): Label shown in the editor.
            link (str): The URL to open.
            enabled (bool, optional): Whether the link opens on boot. Defaults
                to ``True``.
        """
        self.name = name
        self.link = link
        self.enabled = enabled

    def get_name(self):
        return self.name

    def get_link(self):
        return self.link

    def change_link(self, name, link):
        """Overwrite the name and the address at once, as an edit does.

        Args:
            name (str): New label.
            link (str): New URL to open.
        """
        self.name = name
        self.link = link

    @staticmethod
    def problem(name, link):
        """Describe what is wrong with a name and address, if anything.

        Spaces are refused because the save file holds a link as a single
        ``name url`` line and reads it back by splitting on spaces, so a
        spaced name would come back as a different link entirely.

        Args:
            name (str): Candidate label.
            link (str): Candidate URL.

        Returns:
            str: What to tell the user, or an empty string when the pair is
            fine to save.
        """
        if not name or not link:
            return "Please provide both a name and a link."
        if " " in name or " " in link:
            return "A name and a link cannot contain spaces."
        return ""

    def is_enabled(self):
        return self.enabled

    def set_enabled(self, enabled):
        self.enabled = enabled

    def __str__(self):
        """Render the link as the line the save file stores.

        The ``enabled`` field is written only when the link is disabled, so a
        file where nothing has been switched off matches what earlier versions
        wrote.

        Returns:
            str: The saved line.
        """
        flag = "" if self.enabled else " enabled=0"
        return f"{self.name} {self.link}{flag}"

    def __eq__(self, other):
        if not isinstance(other, Link):
            return NotImplemented
        return self.name == other.name and self.link == other.link
