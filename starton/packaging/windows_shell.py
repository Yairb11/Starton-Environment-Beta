"""Minimal Win32 shell bindings for locating the Desktop and writing ``.lnk``.

The obvious way to write a shortcut - handing PowerShell the ``WScript.Shell``
COM object - is unusable here. That object is marshalled through the system
ANSI code page, so on a machine whose code page cannot express the characters
in the Desktop path (a Hebrew or Cyrillic folder name under an English
Windows, for instance) the path degrades to question marks and ``Save`` fails
with a file-not-found error.

These bindings call the wide-character APIs directly - ``SHGetKnownFolderPath``
and ``IShellLinkW`` - so every path stays UTF-16 from end to end. Only the few
vtable slots this project needs are bound; this is not a general COM wrapper.

Constants:
    FOLDERID_DESKTOP: Known-folder id of the current user's Desktop, which
        follows the folder when OneDrive redirects it.
    CLSID_SHELL_LINK: Class id of the shell link object.
    IID_SHELL_LINK_W: Interface id of ``IShellLinkW``.
    IID_PERSIST_FILE: Interface id of ``IPersistFile``.
    CLSCTX_INPROC_SERVER: Ask for the in-process implementation.
"""

import ctypes
from ctypes import POINTER, byref, c_int, c_void_p, c_wchar_p, wintypes
from pathlib import Path

FOLDERID_DESKTOP = "{B4BFCC3A-DB2C-424C-B029-7FE99A87C641}"

CLSID_SHELL_LINK = "{00021401-0000-0000-C000-000000000046}"

IID_SHELL_LINK_W = "{000214F9-0000-0000-C000-000000000046}"

IID_PERSIST_FILE = "{0000010B-0000-0000-C000-000000000046}"

CLSCTX_INPROC_SERVER = 1

_QUERY_INTERFACE = 0
_RELEASE = 2
_SET_DESCRIPTION = 7
_SET_WORKING_DIRECTORY = 9
_SET_ICON_LOCATION = 17
_SET_PATH = 20
_PERSIST_SAVE = 6


class _Guid(ctypes.Structure):
    """A COM ``GUID``, built from its usual brace-and-hyphen spelling."""

    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    def __init__(self, text):
        """Parse a GUID string into the structure.

        Args:
            text (str): GUID spelled as ``{XXXXXXXX-XXXX-...}``.

        Raises:
            OSError: If the string is not a valid GUID.
        """
        super().__init__()
        ctypes.oledll.ole32.CLSIDFromString(c_wchar_p(text), byref(self))


def _invoke(interface, slot, argument_types, *arguments):
    """Call one method on a COM interface by its vtable slot.

    Args:
        interface (c_void_p): Pointer to the interface.
        slot (int): Zero-based index of the method in the vtable.
        argument_types (list): ``ctypes`` types of the method's arguments,
            excluding the implicit ``this`` pointer.
        *arguments: Values matching ``argument_types``.

    Raises:
        OSError: If the method returns a failing ``HRESULT``.
    """
    vtable = ctypes.cast(interface, POINTER(POINTER(c_void_p))).contents
    prototype = ctypes.WINFUNCTYPE(ctypes.HRESULT, c_void_p, *argument_types)
    prototype(vtable[slot])(interface, *arguments)


def desktop_dir():
    """Return the current user's Desktop folder.

    Uses the known-folder id rather than ``%USERPROFILE%\\Desktop`` so the
    real location is found even when OneDrive has redirected the Desktop
    somewhere else entirely.

    Returns:
        Path: The Desktop folder.

    Raises:
        OSError: If Windows cannot resolve the known folder.
    """
    buffer = c_void_p()
    ctypes.oledll.shell32.SHGetKnownFolderPath(
        byref(_Guid(FOLDERID_DESKTOP)), 0, None, byref(buffer)
    )
    try:
        return Path(ctypes.wstring_at(buffer))
    finally:
        ctypes.windll.ole32.CoTaskMemFree(buffer)


def create_shortcut(path, target, icon=None, description="", working_directory=None):
    """Write a Windows shortcut, replacing any file already at ``path``.

    Args:
        path (Path): Where to write the ``.lnk`` file.
        target (Path): The file the shortcut opens.
        icon (Path, optional): Icon file. Defaults to the target's own icon.
        description (str, optional): Tooltip shown when hovering the shortcut.
        working_directory (Path, optional): Directory the target starts in.
            Defaults to the folder holding the target.

    Returns:
        Path: The shortcut that was written.

    Raises:
        OSError: If the shortcut cannot be created or saved.
    """
    ctypes.oledll.ole32.CoInitialize(None)

    link = c_void_p()
    ctypes.oledll.ole32.CoCreateInstance(
        byref(_Guid(CLSID_SHELL_LINK)),
        None,
        CLSCTX_INPROC_SERVER,
        byref(_Guid(IID_SHELL_LINK_W)),
        byref(link),
    )

    persist_file = c_void_p()
    try:
        _invoke(link, _SET_PATH, [c_wchar_p], c_wchar_p(str(target)))
        _invoke(
            link,
            _SET_WORKING_DIRECTORY,
            [c_wchar_p],
            c_wchar_p(str(working_directory or target.parent)),
        )
        _invoke(link, _SET_DESCRIPTION, [c_wchar_p], c_wchar_p(description))
        if icon is not None:
            _invoke(
                link,
                _SET_ICON_LOCATION,
                [c_wchar_p, c_int],
                c_wchar_p(str(icon)),
                0,
            )
        _invoke(
            link,
            _QUERY_INTERFACE,
            [c_void_p, c_void_p],
            byref(_Guid(IID_PERSIST_FILE)),
            byref(persist_file),
        )
        _invoke(
            persist_file,
            _PERSIST_SAVE,
            [c_wchar_p, c_int],
            c_wchar_p(str(path)),
            1,
        )
    finally:
        if persist_file:
            _invoke(persist_file, _RELEASE, [])
        _invoke(link, _RELEASE, [])
    return path
