"""Every Qt style sheet used by the editor, kept in one place.

Qt style sheets are CSS-like strings. Collecting them here keeps the widget
code readable and makes the dark theme adjustable from a single file: change a
value in ``COLORS`` and update the sheets that quote it.

Constants:
    COLORS: The palette every sheet below is built from.
    CANVAS: Background of the desktop canvas.
    MINI_CANVAS: The window-state cells, which paint no border of their own:
        their outline is the monitor drawn inside them.
    EDITOR_SCROLL: The app editor's scroll area, which must not paint a box
        around itself the way the link list does.
    MONITOR_FILL, MONITOR_BORDER, MONITOR_BORDER_HOVER, MONITOR_BORDER_CHOSEN:
        Colours a monitor is drawn in; the hover and chosen variants outline a
        window-state cell under the cursor and the selected one.
    APP_DEFAULT, APP_HOVER, APP_SELECTED: Colours an app rectangle is drawn in,
        by state.
    APP_UNCHOSEN: The window drawn in a window-state cell that is not the
        chosen one.
    APP_LABEL, APP_LABEL_DIM: The app name written inside its rectangle on the
        canvas, and the fainter size line below it.
    SNAP_GUIDE: The dashed line shown while a dragged window lines up with a
        monitor edge or another window. Deliberately not a blue from the
        palette: a guide has to read as separate from the windows it crosses.
    REGION_PREVIEW, REGION_PREVIEW_ALPHA: The wash filling the screen region a
        dragged window is about to snap into, and how solid that wash is.
    INFO_PANEL, INFO_PANEL_BTN, TITLE, HEADER, BORDER, LABEL:
        The info panel, its toggle button and its text.
    SPLITTER: The draggable dividers between the canvas and the panel, and
        between the app editor and the links.
    APP_COMBO: The app picker, whose popup highlights in blue rather than the
        red CONTEXT_MENU uses for destructive entries.
    APP_CARD, APP_CARD_HOVER, APP_CARD_BROKEN, APP_CARD_NAME, APP_CARD_META:
        The cards of the opening app gallery; the broken variant marks an app
        whose path is no longer on this machine.
    GALLERY_HINT, GALLERY_EMPTY, GALLERY_ADD_BTN: The gallery's heading, its
        message when nothing is saved, and its add button.
    PATH_INPUT, PATH_INPUT_BROKEN, BROWSE_BTN, SPINBOX: The app path and
        geometry fields; the broken variant marks a path that no longer
        exists.
    SNAP_CELL, SNAP_CELL_SELECTED: The custom-size button of the window-state
        picker.
    SAVE_BTN, DELETE_BTN, TEST_BTN, RUN_BTN: The action buttons.
    LINK_INPUT, LINK_ADD_BTN, LINK_SCROLL, LINK_CONTAINER, LINK_FRAME,
        LINK_NAME, LINK_URL, LINK_URL_HTML, LINK_EDIT_BTN, LINK_DELETE_BTN:
        The link section; the edit button highlights blue where the delete
        button highlights red.
    CONTEXT_MENU: Right-click menus, whose delete entries highlight in red so
        the destructive action is obvious.
"""

COLORS = {
    "background": "#1e1e1e",
    "panel": "#252526",
    "surface": "#333333",
    "border": "#555555",
    "border_soft": "#444444",
    "accent": "#0078d4",
    "accent_hover": "#2b88d8",
    "accent_pressed": "#005a9e",
    "accent_light": "#6aaee9",
    "danger": "#c50f1f",
    "danger_pressed": "#890a15",
    "text": "white",
    "text_muted": "#cccccc",
    "text_dim": "#aaaaaa",
}

CANVAS = """
    QGraphicsView { background-color: #1e1e1e; border: none; }
    QScrollBar:vertical { background: #1e1e1e; width: 10px; }
    QScrollBar:horizontal { background: #1e1e1e; height: 10px; }
    QScrollBar::handle:vertical { background: #555; min-height: 20px; border-radius: 5px; }
    QScrollBar::handle:horizontal { background: #555; min-width: 20px; border-radius: 5px; }
    QScrollBar::add-line, QScrollBar::sub-line { width: 0px; height: 0px; }
    QScrollBar::add-page, QScrollBar::sub-page { background: none; }
"""
MINI_CANVAS = """
    QGraphicsView {
        background-color: #1e1e1e;
        border: none;
        border-radius: 3px;
    }
"""
EDITOR_SCROLL = """
    QScrollArea { border: none; background-color: #252526; }
    QScrollArea > QWidget > QWidget { background-color: #252526; }
    QScrollBar:vertical { background: #252526; width: 10px; }
    QScrollBar::handle:vertical { background: #555; min-height: 20px; border-radius: 5px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""
MONITOR_FILL = "#333333"
MONITOR_BORDER = "#555555"
MONITOR_BORDER_HOVER = "#2b88d8"
MONITOR_BORDER_CHOSEN = "#0078d4"
APP_DEFAULT = "#0078d4"
APP_HOVER = "#2b88d8"
APP_SELECTED = "#6aaee9"
APP_UNCHOSEN = "#6b6b6b"
APP_LABEL = "#ffffff"
APP_LABEL_DIM = "#d6e8f7"
SNAP_GUIDE = "#ff4f8b"
REGION_PREVIEW = "#6aaee9"
REGION_PREVIEW_ALPHA = 70

INFO_PANEL = "background-color: #252526;"
INFO_PANEL_BTN = """
            QPushButton {
                background-color: #333333;
                color: white;
                border-radius: 4px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #0078d4;
            }
        """
TITLE = "color: white; font-size: 25px; font-weight: bold;"
HEADER = "color: #aaaaaa; font-size: 16px; font-weight: bold; margin-top: 8px;"
BORDER = "border-bottom: 2px solid white;"
LABEL = "color: #cccccc; font-size: 13px; font-weight: bold;"

SPLITTER = """
    QSplitter::handle {
        background-color: #333333;
    }
    QSplitter::handle:hover {
        background-color: #0078d4;
    }
    QSplitter::handle:pressed {
        background-color: #005a9e;
    }
"""

APP_COMBO = """
    QComboBox {
        background-color: #333333;
        color: white;
        border: 1px solid #555;
        border-radius: 3px;
        padding: 6px 10px;
        font-size: 14px;
    }
    QComboBox:hover {
        border: 1px solid #0078d4;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #cccccc;
        width: 0px;
        height: 0px;
        margin-right: 8px;
    }
    QComboBox QAbstractItemView {
        background-color: #2b2b2b;
        color: #cccccc;
        border: 1px solid #444;
        outline: none;
        selection-background-color: #0078d4;
        selection-color: white;
    }
    QComboBox QAbstractItemView::item {
        min-height: 26px;
        padding: 4px 8px;
    }
"""

APP_CARD = """
    QFrame { background-color: #333333; border-radius: 4px; border: 1px solid #444; }
"""
APP_CARD_HOVER = """
    QFrame { background-color: #333333; border-radius: 4px; border: 1px solid #0078d4; }
"""
APP_CARD_BROKEN = """
    QFrame { background-color: #333333; border-radius: 4px; border: 1px solid #c50f1f; }
"""
APP_CARD_NAME = "color: white; font-weight: bold; font-size: 14px; border: none;"
APP_CARD_META = "color: #aaaaaa; font-size: 11px; border: none;"

GALLERY_HINT = "color: #aaaaaa; font-size: 16px; font-weight: bold;"
GALLERY_EMPTY = "color: #777777; font-size: 14px;"
GALLERY_ADD_BTN = """
    QPushButton {
        background-color: #333333;
        color: white;
        font-size: 14px;
        border-radius: 6px;
        padding: 8px 12px;
        border: 1px solid #555;
    }
    QPushButton:hover {
        background-color: #0078d4;
        border: 1px solid #0078d4;
    }
    QPushButton:pressed {
        background-color: #005a9e;
    }
"""

PATH_INPUT = "background-color: #333333; color: white; border: 1px solid #555; padding: 5px;"
PATH_INPUT_BROKEN = "background-color: #333333; color: white; border: 1px solid #c50f1f; padding: 5px;"
BROWSE_BTN = """
    QPushButton {
        background-color: #0078d4; color: white; border: none; font-size: 14px; border-radius: 2px;
    }
    QPushButton:hover {
        background-color: #2b88d8;
    }
    QPushButton:disabled {
        background-color: #000000;
    }
"""
SPINBOX = """
    QSpinBox { background-color: #333333; color: white; border: 1px solid #555; padding: 4px; font-size: 13px; }
    QSpinBox::up-button, QSpinBox::down-button { background-color: #444; width: 16px; }
"""

SNAP_CELL = """
    QPushButton {
        background-color: #333333;
        color: #cccccc;
        border: 1px solid #555;
        border-radius: 3px;
        font-size: 15px;
    }
    QPushButton:hover {
        background-color: #2b88d8;
        color: white;
        border: 1px solid #2b88d8;
    }
"""
SNAP_CELL_SELECTED = """
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: 1px solid #6aaee9;
        border-radius: 3px;
        font-size: 15px;
    }
    QPushButton:hover {
        background-color: #2b88d8;
    }
"""

TEST_BTN = """
    QPushButton {
        background-color: transparent;
        color: #cccccc;
        font-size: 20px;
        border-radius: 6px;
        padding: 6px 12px;
        border: 1px solid #555;
    }
    QPushButton:hover {
        background-color: #2b88d8;
        color: white;
        border: 1px solid #2b88d8;
    }
    QPushButton:pressed {
        background-color: #005a9e;
    }
    QPushButton:disabled {
        color: #777777;
        border: 1px solid #444;
    }
"""

RUN_BTN = """
    QPushButton {
        background-color: #333333;
        color: white;
        font-size: 15px;
        font-weight: bold;
        border-radius: 6px;
        padding: 8px 12px;
        border: 1px solid #555;
    }
    QPushButton:hover {
        background-color: #0078d4;
        border: 1px solid #0078d4;
    }
    QPushButton:pressed {
        background-color: #005a9e;
    }
"""

SAVE_BTN = """
    QPushButton {
        background-color: #0078d4;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 6px;
        padding: 6px 12px;
        border: none;
    }
    QPushButton:hover {
        background-color: #2b88d8;
    }
    QPushButton:pressed {
        background-color: #005a9e;
    }
"""
DELETE_BTN = """
    QPushButton {
        background-color: transparent;
        color: #cccccc;
        font-size: 20px;
        border-radius: 6px;
        padding: 6px 12px;
        border: 1px solid transparent;
    }
    QPushButton:hover {
        background-color: #c50f1f;
        color: white;
        border: 1px solid #c50f1f;
    }
    QPushButton:pressed {
        background-color: #890a15;
    }
"""

LINK_INPUT = "background-color: #333; color: white; border: 1px solid #555; padding: 4px;"
LINK_ADD_BTN = "QPushButton { background-color: #0078d4; color: white; border: none; border-radius: 2px; } QPushButton:hover { background-color: #2b88d8; }"
LINK_SCROLL = """
    QScrollArea { border: 1px solid #444; background-color: #1e1e1e; }
    QScrollBar:vertical { background: #252526; width: 10px; }
    QScrollBar::handle:vertical { background: #555; min-height: 20px; border-radius: 5px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""
LINK_CONTAINER = "background-color: #1e1e1e;"
LINK_FRAME = """
    QFrame { background-color: #333333; border-radius: 4px; border: 1px solid #444; }
"""
LINK_NAME = "color: white; font-weight: bold; font-size: 13px; border: none;"
LINK_NAME_DISABLED = "color: #777777; font-weight: bold; font-size: 13px; border: none;"
LINK_URL = "font-size: 11px; border: none;"
LINK_URL_HTML = "color: #0078d4; text-decoration: none;"
LINK_EDIT_BTN = """
    QPushButton { background-color: transparent; border: none; font-size: 14px; }
    QPushButton:hover { background-color: #0078d4; border-radius: 4px; }
"""
LINK_DELETE_BTN = """
    QPushButton { background-color: transparent; border: none; font-size: 14px; }
    QPushButton:hover { background-color: #cc0000; border-radius: 4px; }
"""

CONTEXT_MENU = """
            QMenu {
                background-color: #2b2b2b;
                color: #cccccc;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QMenu::item { padding: 6px 24px; }
            QMenu::item:selected { background-color: #c50f1f; color: white; }
        """
