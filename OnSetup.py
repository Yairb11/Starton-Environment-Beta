"""Entry point for the boot-time runner - opens the saved environment.

``launch_apps.bat`` in the Windows start-up folder runs this file with
``pythonw`` on every boot, so it must stay at the root of the project under
this name. All of the work lives in :mod:`starton.startup.runner`.
"""

from starton.startup.runner import run

if __name__ == "__main__":
    run()
