"""Reading and writing the save file that holds one environment.

The file is a small XML-ish document with two sections::

    <open_apps>
    <app>
    chrome
    C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe
    [0,0]
    Left
    </app>
    </open_apps>
    <open_urls>
    GitHub https://github.com
    </open_urls>

The format is deliberately line based and unchanged from earlier versions, so
save files written by older builds keep working.
"""

import re

from starton.models import App, Link, WindowSize

APPS_TAG = "open_apps"
URLS_TAG = "open_urls"
SECTION_TAGS = (APPS_TAG, URLS_TAG)

ENABLED_FIELD = "enabled="


class SaveFile:
    """One environment on disk.

    Attributes:
        file_path (Path | str): Path to the save file.
    """

    def __init__(self, file_path):
        """Point the save file at a path.

        Args:
            file_path (Path | str): Path to read from and write to. The file is
                not touched until :meth:`read_file` or :meth:`write_file` runs.
        """
        self.file_path = file_path
        self._saved_apps = None

    def read_file(self):
        """Load the saved apps and links.

        Returns:
            tuple: ``(apps, links)``. Either is ``None`` when its section is
            empty, which is how the editor tells "nothing saved yet" apart from
            a list it can append to.
        """
        sections = self._split_sections()
        apps = self._parse_apps(sections[APPS_TAG])
        links = self._parse_links(sections[URLS_TAG])
        self._saved_apps = self.render_apps(apps)
        return apps, links

    def write_file(self, apps, links):
        """Overwrite the save file with the environment given.

        Args:
            apps (list | None): Apps to open on boot.
            links (list | None): Links to open on boot.
        """
        lines = []
        for tag, entries in ((APPS_TAG, apps), (URLS_TAG, links)):
            lines.append(f"<{tag}>")
            body = self._join(entries)
            if body:
                lines.append(body)
            lines.append(f"</{tag}>")
        self._write_text("\n".join(lines))
        self._saved_apps = self.render_apps(apps)

    @staticmethod
    def render_apps(apps):
        """Render apps as the body the save file's app section holds.

        Args:
            apps (list | None): Apps to render.

        Returns:
            str: The section body, empty when there is nothing to write.
        """
        return SaveFile._join(apps) or ""

    def apps_match(self, apps):
        """Report whether these apps are already what was last saved.

        Comparing the rendered text rather than the raw file means a save file
        edited by hand into different spacing still counts as saved, and the
        editor does not open claiming unsaved changes.

        Args:
            apps (list | None): Apps to compare against the file.

        Returns:
            bool: ``True`` when nothing about the apps has changed since the
            last read or write. Nothing having been read or written yet counts
            as a mismatch, since there is no baseline to trust.
        """
        if self._saved_apps is None:
            return False
        return self.render_apps(apps) == self._saved_apps

    def _split_sections(self):
        """Cut the file into its ``open_apps`` and ``open_urls`` bodies.

        Returns:
            dict: Section body keyed by tag name. A section that is missing
            from the file reads as empty rather than raising, so a truncated
            file still opens the editor.
        """
        text = self._read_text()
        sections = {}
        for tag in SECTION_TAGS:
            match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
            sections[tag] = match.group(1).strip() if match else ""
        return sections

    def _parse_apps(self, raw_info):
        """Turn the ``open_apps`` body into :class:`~starton.models.app.App`s.

        Args:
            raw_info (str): Body of the ``open_apps`` section.

        Returns:
            list | None: The apps, or ``None`` when the section is empty.
        """
        if not raw_info:
            return None
        return [
            self._text_to_app(block)
            for block in re.findall(r"<app>(.*?)</app>", raw_info, re.DOTALL)
        ]

    @staticmethod
    def _text_to_app(block):
        """Build one app from its saved lines.

        Only the first four lines are read, and they are positional and have
        never changed. Anything after them is an optional ``key=value`` field
        this version has no use for, so a file written by an older one loads
        without complaint and simply drops the extra field on the next save.

        Args:
            block (str): Text between an ``<app>`` and ``</app>`` pair.

        Returns:
            App: The reconstructed app.
        """
        name, path, pos, size = block.split("\n")[1:-1][:4]
        app = App(name)
        app.set_app_path(path)
        app.set_pos([int(value) for value in pos[1:-1].split(",")])
        app.set_size(WindowSize(size))
        return app

    @staticmethod
    def _read_enabled_field(fields):
        """Read the optional ``enabled`` flag out of trailing save fields.

        Args:
            fields (list): Trailing ``key=value`` strings, usually empty.

        Returns:
            bool: ``False`` only when a field explicitly disables the entry.
        """
        for field in fields:
            if field.startswith(ENABLED_FIELD):
                return field[len(ENABLED_FIELD):] != "0"
        return True

    @staticmethod
    def _parse_links(raw_info):
        """Turn the ``open_urls`` body into :class:`~starton.models.link.Link`s.

        Args:
            raw_info (str): Body of the ``open_urls`` section, one
                ``name url`` pair per line, optionally followed by
                ``enabled=0``.

        Returns:
            list | None: The links, or ``None`` when the section is empty.
        """
        if not raw_info:
            return None
        links = []
        for line in raw_info.split("\n"):
            fields = line.split(" ")
            enabled = SaveFile._read_enabled_field(fields[2:])
            links.append(Link(fields[0], fields[1], enabled=enabled))
        return links

    @staticmethod
    def _join(entries):
        """Render apps or links as the text of their section.

        Args:
            entries (list | None): Objects with a ``__str__`` of their own.

        Returns:
            str | None: One entry per line, or ``None`` when there is nothing
            to write.
        """
        if not entries:
            return None
        return "\n".join(str(entry) for entry in entries)

    def _read_text(self):
        """Read the whole save file.

        Returns:
            str: File contents.
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            return file.read()

    def _write_text(self, text):
        """Replace the save file's contents.

        Args:
            text (str): New contents.
        """
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write(text)
