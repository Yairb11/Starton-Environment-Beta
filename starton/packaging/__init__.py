"""Build-time tooling: turn the editor into a distributable executable.

Nothing in here runs inside the shipped application - these modules exist for
``SetupGUI.py`` at the repository root, which freezes :mod:`GUI` into
``SetupGUI.exe`` and drops a shortcut on the Desktop.

The package is named ``packaging`` rather than ``build`` so it is never
confused with the working directory PyInstaller calls ``build``.
"""
