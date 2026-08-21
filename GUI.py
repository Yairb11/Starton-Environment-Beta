"""Entry point for the editor - run this to design your environment.

This is the file PyInstaller builds ``SetupGUI.exe`` from. All of the work
lives in :mod:`starton.gui.editor`; keeping this launcher tiny means the
executable and ``python SetupGUI.py`` behave identically.
"""

import sys

from starton.gui.editor import run

if __name__ == "__main__":
    sys.exit(run())
