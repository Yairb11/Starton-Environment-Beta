"""A label that shortens its own text instead of widening what holds it.

A long link name or address would otherwise set the width of its card, push the
link list wider than the panel and leave the user scrolling sideways to read a
list that is meant to be scanned. Text too long for the space is cut with an
ellipsis instead, and the whole of it stays available in the tooltip.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QSizePolicy

from starton.gui import styles


class ElidedLabel(QLabel):
    """A label showing as much of its text as the space allows.

    The text is re-cut every time the label is resized, so widening the panel
    reveals more of it and narrowing the panel gives more away again. A label
    carrying a URL stays a working link: only the text shown is shortened, and
    the address behind it is always the full one.
    """

    def __init__(self, text, url=None):
        """Build the label around the text it should show.

        Args:
            text (str): The full text, however long.
            url (str, optional): Address to link the text to. Defaults to
                ``None``, which shows the text as plain text.
        """
        super().__init__()
        self.full_text = text
        self.url = url
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(0)
        self._show_elided()

    def set_content(self, text, url=None):
        """Show different text, for instance after the link has been edited.

        Args:
            text (str): The new full text.
            url (str, optional): New address to link to. Defaults to ``None``.
        """
        self.full_text = text
        self.url = url
        self._show_elided()

    def resizeEvent(self, event):
        """Re-cut the text to whatever width the label now has.

        Args:
            event (QResizeEvent): The Qt resize event.
        """
        super().resizeEvent(event)
        self._show_elided()

    def _show_elided(self):
        """Draw as much of the text as fits, ending in an ellipsis if cut."""
        elided = self.fontMetrics().elidedText(
            self.full_text, Qt.TextElideMode.ElideRight, self.width()
        )
        if self.url:
            self.setText(
                f'<a href="{self.url}" style="{styles.LINK_URL_HTML}">{elided}</a>'
            )
        else:
            self.setText(elided)
        self.setToolTip(self.full_text)
