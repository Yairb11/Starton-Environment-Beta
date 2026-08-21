"""Plain data objects describing a saved environment.

These carry no Qt and no Windows dependency: the editor, the save file and the
boot-time runner all speak in terms of :class:`~starton.models.app.App`,
:class:`~starton.models.link.Link` and
:class:`~starton.models.window_size.WindowSize`.
"""

from starton.models.app import App
from starton.models.link import Link
from starton.models.window_size import WindowSize

__all__ = ["App", "Link", "WindowSize"]
