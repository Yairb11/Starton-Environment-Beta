"""Build script - run this to package the editor as ``SetupGUI.exe``.

Freezes :mod:`GUI` into a single console-less executable at the root of the
project and puts a shortcut to it on the Desktop. All of the work lives in
:mod:`starton.packaging.builder`.

Run it with ``uv run python SetupGUI.py``.
"""

import sys

from starton.packaging.builder import build

if __name__ == "__main__":
    sys.exit(build())
