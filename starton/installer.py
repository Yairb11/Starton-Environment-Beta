"""First-run setup: create the save file and register Starton with Windows.

The editor calls :func:`prepare_environment` before it opens a window; the
boot-time runner calls :func:`resolve_save_file`, which only ever touches the
save file. Registering with Windows means dropping ``launch_apps.bat`` into the
per-user start-up folder - deleting that one file is all it takes to
uninstall, so it is never re-created for a monitor setup that has already been
saved.
"""

import shutil

from starton import config, monitors


def _current_save_file():
    """Return the save-file path matching the monitors connected right now.

    Returns:
        Path: Path to the save file, which may not exist yet.
    """
    return config.save_file_path(monitors.screen_count(), monitors.layout_signature())


def prepare_environment():
    """Make sure the editor has everything it needs on disk.

    Creates the ``info`` folder, the launch script and an empty save file the
    first time Starton runs on a given monitor setup, then copies the launch
    script into the Windows start-up folder if it is not already there.

    Returns:
        Path: Path to the save file for the current monitor setup.
    """
    save_file = _current_save_file()
    if save_file.exists():
        return save_file

    info_dir = config.info_dir()
    is_first_run = not info_dir.exists()
    if is_first_run:
        info_dir.mkdir(parents=True, exist_ok=True)
        config.launch_script_source().write_text(
            config.launch_script_contents(), encoding="utf-8"
        )

    save_file.write_text(config.EMPTY_SAVE_FILE, encoding="utf-8")
    _register_with_windows()
    return save_file


def _register_with_windows():
    """Copy the launch script into the start-up folder unless it is there."""
    if not is_registered():
        register()


def is_registered():
    """Report whether Windows will run Starton on the next boot.

    Returns:
        bool: ``True`` when the launch script sits in the start-up folder.
    """
    return config.launch_script_target().exists()


def register():
    """Add the start-up entry, rebuilding the launch script if it is missing.

    The script is re-created rather than assumed, so switching start-up back
    on still works after an uninstall removed it.
    """
    source = config.launch_script_source()
    if not source.exists():
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(config.launch_script_contents(), encoding="utf-8")
    shutil.copy(source, config.launch_script_target())


def unregister():
    """Remove the start-up entry, leaving the saved environment untouched."""
    config.launch_script_target().unlink(missing_ok=True)


def resolve_save_file():
    """Return the save file for the current monitors, creating it if missing.

    Unlike :func:`prepare_environment` this never registers anything with
    Windows: by the time the runner executes, the start-up entry obviously
    already exists.

    Returns:
        Path: Path to an existing save file.
    """
    save_file = _current_save_file()
    if not save_file.exists():
        save_file.parent.mkdir(parents=True, exist_ok=True)
        save_file.write_text(config.EMPTY_SAVE_FILE, encoding="utf-8")
    return save_file
