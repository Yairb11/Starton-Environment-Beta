"""Starton Environment - recreate your desktop layout on every boot.

The package is split into four layers:

``starton.models``
    Plain data objects (an app window, a link, a window size) with no
    dependency on Qt or on Windows.
``starton.storage``
    Reading and writing the save file those objects are persisted to.
``starton.startup``
    The boot-time runner that opens and positions everything.
``starton.gui``
    The PyQt6 editor used to design the environment.

``starton.geometry``, ``starton.monitors`` and ``starton.config`` hold the
rules the GUI and the runner must agree on: what a screen region means, where
the monitors are, and where files live on disk.
"""

__version__ = "0.1.0"
