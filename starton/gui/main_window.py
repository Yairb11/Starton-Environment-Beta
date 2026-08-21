"""The editor window: a canvas of the desktop plus a panel to edit one app.

Constants:
    PANEL_WIDTH: Width the info panel opens at before anyone drags it.
    PANEL_MIN_WIDTH, PANEL_MAX_WIDTH: How far the panel's splitter can be
        dragged in either direction.
    PANEL_ANIMATION_MS: How long the panel takes to slide open or shut.
    SPLITTER_HANDLE: Thickness of both draggable dividers.
    APPS_SHARE, LINKS_SHARE: How the panel's height is first divided between
        the app editor and the links, before the user drags the divider.
    TITLE_HEIGHT: Height of the app name field, whose width now follows the
        panel rather than being fixed to it.
    MAX_APPS: Cap on saved apps. Opening more than this at boot takes long
        enough that the machine feels broken.
    NEW_APP_NAME: Name given to a new app before the user picks a real one.
    CUSTOM_PAGE: Window-state page showing width and height spin boxes rather
        than a region preview.
"""

import os

from PyQt6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    Qt,
)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from starton import monitors
from starton.geometry import WINDOW_STATE_TITLES, region_at, region_rect, stack_index
from starton.gui import styles
from starton.gui.app_gallery import AppGallery
from starton.gui.app_picker import AppPicker
from starton.gui.clickable_line_edit import ClickableLineEdit
from starton.gui.link_block import LinkBlock
from starton.gui.link_dialog import LinkDialog
from starton.gui.monitor_canvas import MonitorCanvas
from starton.gui.snap_grid import SnapGrid
from starton.gui.tester import AppTester
from starton.models import App, Link, WindowSize
from starton.startup import runner, spawn

PANEL_WIDTH = 500

PANEL_MIN_WIDTH = 320

PANEL_MAX_WIDTH = 900

PANEL_ANIMATION_MS = 350

SPLITTER_HANDLE = 5

APPS_SHARE = 2

LINKS_SHARE = 1

TITLE_HEIGHT = 50

MAX_APPS = 32

NEW_APP_NAME = "new_app"

CUSTOM_PAGE = 0


class MainWindow(QMainWindow):
    """Where the environment is designed.

    The window is two halves that stay in step: a :class:`MonitorCanvas` scale
    model of the desktop on the left, and an info panel on the right holding
    the details of whichever app is selected. Dragging on the canvas updates
    the panel, editing the panel redraws the canvas, and the SAVE button writes
    the result to disk.
    """

    def __init__(self, screens, apps, links, save_file):
        """Build the window from a saved environment.

        Args:
            screens (list): Every connected monitor.
            apps (list | None): Saved apps, or ``None`` when nothing is saved.
            links (list | None): Saved links, or ``None`` when nothing is saved.
            save_file (SaveFile): Where edits are written back to.
        """
        super().__init__()
        self.screens = screens
        self.apps = apps
        self.links = links
        self.save_file = save_file
        self.activated_app = None
        self.is_panel_open = True
        self.panel_width = PANEL_WIDTH
        self.is_dirty = False
        self.tester = None
        self.window_state_page = CUSTOM_PAGE
        self.is_custom_open = False
        self.info_panel_toggle_btn = None
        self._loading = False
        self._warned_path = None

        central_widget = self._build_window()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._build_main_splitter(central_widget))

        self.apps_title_label.setDisabled(True)
        self.panel_stack.setCurrentIndex(0)
        self._refresh_app_lists()
        self._install_shortcuts()

    def _install_shortcuts(self):
        """Bind the keyboard shortcuts for the actions with buttons.

        Plain Delete is deliberately left alone: it would fire while the user
        is editing the app name.
        """
        bindings = (
            ("Ctrl+S", self.saving_app),
            ("Ctrl+N", self.create_new_app),
            ("Ctrl+Delete", self.deleting_app),
            ("Ctrl+T", self.test_app),
            ("Ctrl+R", self.run_environment),
            ("Ctrl+PgDown", self.select_next_app),
            ("Ctrl+PgUp", self.select_previous_app),
            ("F11", self.toggle_full_screen),
            ("Esc", self.leave_full_screen),
            ("Ctrl+0", self.canvas.fit_view),
            ("Ctrl+1", self.canvas.reset_zoom),
            ("Ctrl+=", self.canvas.zoom_in),
            ("Ctrl++", self.canvas.zoom_in),
            ("Ctrl+-", self.canvas.zoom_out),
        )
        for keys, slot in bindings:
            QShortcut(QKeySequence(keys), self).activated.connect(slot)

    def _build_window(self):
        """Size the window to the primary monitor and give it a central widget.

        The editor opens full screen, so this size is the one it falls back to
        when the user leaves full screen rather than the one it starts at.

        Returns:
            QWidget: The central widget every other widget lives in.
        """
        self.setWindowTitle("SetupGUI - Beta")
        primary_screen = monitors.primary_screen(self.screens)
        self.resize(primary_screen.width, primary_screen.height)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        return central_widget

    def _build_canvas(self):
        """Create the desktop canvas and wire its signals to the panel.

        Returns:
            MonitorCanvas: The canvas.
        """
        canvas = MonitorCanvas(self.screens, self.apps)
        canvas.app_selected.connect(self.update_info_panel)
        canvas.app_moved.connect(self._on_app_dragged)
        canvas.app_resized.connect(self._on_app_resized)
        canvas.app_delete_requested.connect(self._on_app_delete_requested)
        canvas.app_region_snapped.connect(self._on_app_region_snapped)
        canvas.app_add_requested.connect(self.create_app_at)
        return canvas

    def _build_main_splitter(self, central_widget):
        """Put the canvas and the panel either side of a draggable divider.

        Only the canvas is given a stretch factor, so growing the window widens
        the desktop model rather than the panel and whatever width the divider
        was left at survives a resize.

        Args:
            central_widget (QWidget): Parent for the floating toggle button.

        Returns:
            QSplitter: The splitter holding both halves of the window.
        """
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setStyleSheet(styles.SPLITTER)
        self.main_splitter.setHandleWidth(SPLITTER_HANDLE)
        self.main_splitter.setChildrenCollapsible(False)

        self.canvas = self._build_canvas()
        self.info_panel = self._build_info_panel(central_widget)
        self.main_splitter.addWidget(self.canvas)
        self.main_splitter.addWidget(self.info_panel)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 0)

        primary_screen = monitors.primary_screen(self.screens)
        self.main_splitter.setSizes(
            [primary_screen.width - PANEL_WIDTH, PANEL_WIDTH]
        )
        self.main_splitter.splitterMoved.connect(self._on_panel_resized)
        return self.main_splitter

    def _build_info_panel(self, central_widget):
        """Assemble the whole right-hand panel.

        Args:
            central_widget (QWidget): Parent for the floating toggle button,
                which is positioned by hand rather than by a layout.

        Returns:
            QFrame: The info panel.
        """
        info_panel = QFrame()
        info_panel.setStyleSheet(styles.INFO_PANEL)
        info_panel.setMinimumWidth(PANEL_MIN_WIDTH)
        info_panel.setMaximumWidth(PANEL_MAX_WIDTH)
        info_panel.setContentsMargins(0, 0, 0, 0)

        self.info_panel_toggle_btn = self._build_toggle_button(central_widget)

        panel_layout = QVBoxLayout(info_panel)
        panel_layout.setContentsMargins(15, 20, 15, 20)
        panel_layout.setSpacing(0)
        panel_layout.addWidget(self._build_panel_splitter())
        return info_panel

    def _build_panel_splitter(self):
        """Put the app editor and the links either side of a divider.

        The sizes given are a ratio rather than pixels: a splitter shares out
        whatever height it has in proportion to them, so the panel still opens
        two thirds editor and one third links however tall the window is, and
        the user can then drag the divider wherever they like.

        Returns:
            QSplitter: The splitter dividing the panel.
        """
        self.panel_splitter = QSplitter(Qt.Orientation.Vertical)
        self.panel_splitter.setStyleSheet(styles.SPLITTER)
        self.panel_splitter.setHandleWidth(SPLITTER_HANDLE)
        self.panel_splitter.setChildrenCollapsible(False)

        self.apps_section = self._build_apps_section()
        self.links_section = self._build_links_section()
        self.panel_splitter.addWidget(self.apps_section)
        self.panel_splitter.addWidget(self.links_section)
        self.panel_splitter.setStretchFactor(0, APPS_SHARE)
        self.panel_splitter.setStretchFactor(1, LINKS_SHARE)
        self.panel_splitter.setSizes([APPS_SHARE * 1000, LINKS_SHARE * 1000])
        return self.panel_splitter

    def _build_apps_section(self):
        """Build the top two thirds: the app title and the editor.

        The editor scrolls inside whatever height it is given, so the section
        never demands more room than its share of the panel.

        Returns:
            QWidget: The app section.
        """
        self.panel_stack = QStackedWidget()
        self.panel_stack.addWidget(self._build_empty_page())
        self.panel_stack.addWidget(self._build_editor_page())

        self.editor_scroll = QScrollArea()
        self.editor_scroll.setWidgetResizable(True)
        self.editor_scroll.setStyleSheet(styles.EDITOR_SCROLL)
        self.editor_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.editor_scroll.setWidget(self.panel_stack)

        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._build_app_title())
        layout.addWidget(self.editor_scroll, stretch=1)
        return section

    def _build_links_section(self):
        """Build the bottom third: everything below the divider.

        Returns:
            QWidget: The links section.
        """
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._build_separator())
        layout.addWidget(self._build_links_title())
        layout.addLayout(self._build_add_link())
        layout.addWidget(self._build_link_list(), stretch=1)
        layout.addWidget(self._build_run_button())
        return section

    def _build_toggle_button(self, central_widget):
        """Create the button that slides the info panel in and out.

        Args:
            central_widget (QWidget): Parent widget.

        Returns:
            QPushButton: The toggle button, floating above the canvas.
        """
        toggle_btn = QPushButton("☰", central_widget)
        toggle_btn.setFixedSize(35, 35)
        toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_btn.setToolTip("Toggle Info Panel")
        toggle_btn.setStyleSheet(styles.INFO_PANEL_BTN)
        toggle_btn.clicked.connect(self.toggle_info_panel)
        primary_screen = monitors.primary_screen(self.screens)
        toggle_btn.move(primary_screen.width - self.panel_width + 30, 10)
        return toggle_btn

    def _build_empty_page(self):
        """Build the page shown while no app is selected.

        Rather than asking the user to pick an app, it shows them the apps
        there are to pick from.

        Returns:
            AppGallery: The gallery of saved apps.
        """
        self.app_gallery = AppGallery()
        self.app_gallery.app_chosen.connect(self.update_info_panel)
        self.app_gallery.add_requested.connect(self.create_new_app)
        return self.app_gallery

    def _build_editor_page(self):
        """Build the page holding path, position, size and the save buttons.

        Returns:
            QWidget: The editor page.
        """
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(15, 20, 15, 20)
        editor_layout.setSpacing(8)

        editor_layout.addWidget(self._create_header("APP PATH"))
        editor_layout.addLayout(self._build_app_path())
        editor_layout.addWidget(self._create_header("POSITION"))
        editor_layout.addLayout(self._build_position())
        editor_layout.addWidget(self._build_size_title())
        editor_layout.addWidget(self._build_snap_grid())
        editor_layout.addWidget(self._build_custom_size())
        editor_layout.addLayout(self._build_save_buttons())
        editor_layout.addStretch()
        return editor_widget

    def _build_app_title(self):
        """Build the app picker, the add button and the name field.

        The picker and the name field sit on rows of their own: one chooses an
        app and the other renames it, and crowding both onto one row left the
        picker too narrow to read the names it lists.

        Returns:
            QVBoxLayout: The title block.
        """
        self.apps_title_label = QTextEdit("Select an App")
        self.apps_title_label.setStyleSheet(styles.TITLE)
        self.apps_title_label.setFixedHeight(TITLE_HEIGHT)
        self.apps_title_label.textChanged.connect(self._mark_dirty)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.addLayout(self._build_picker_row())
        title_layout.addWidget(self.apps_title_label)
        return title_layout

    def _build_picker_row(self):
        """Build the app picker beside the button that adds a new app.

        Returns:
            QHBoxLayout: The picker row.
        """
        self.app_picker = AppPicker()
        self.app_picker.app_chosen.connect(self.update_info_panel)

        add_btn = QPushButton("➕")
        add_btn.setFixedSize(28, 28)
        add_btn.setToolTip("Add an app (Ctrl+N)")
        add_btn.setStyleSheet(styles.LINK_ADD_BTN)
        add_btn.clicked.connect(self.create_new_app)

        picker_layout = QHBoxLayout()
        picker_layout.setSpacing(5)
        picker_layout.addWidget(self.app_picker, stretch=1)
        picker_layout.addWidget(add_btn)
        return picker_layout

    def _build_app_path(self):
        """Build the path field and its browse button.

        Returns:
            QHBoxLayout: The path row.
        """
        self.app_path_input = ClickableLineEdit()
        self.app_path_input.setPlaceholderText("APP OPEN PATH (e.g., C:\\...)")
        self.app_path_input.setStyleSheet(styles.PATH_INPUT)
        self.app_path_input.clicked.connect(self.browse_for_folder)
        self.app_path_input.textChanged.connect(self._mark_dirty)

        browse_btn = QPushButton("📂")
        browse_btn.setToolTip("Browse for Executable")
        browse_btn.setFixedSize(28, 28)
        browse_btn.setStyleSheet(styles.BROWSE_BTN)
        browse_btn.clicked.connect(self.browse_for_executable)

        path_layout = QHBoxLayout()
        path_layout.setSpacing(5)
        path_layout.addWidget(self.app_path_input)
        path_layout.addWidget(browse_btn)
        return path_layout

    def _build_position(self):
        """Build the monitor, X and Y spin boxes.

        Returns:
            QGridLayout: The position grid.
        """
        self.screen_spin = self._create_spin_box(1, len(self.screens))
        self.x_spin = self._create_spin_box(0, 0)
        self.y_spin = self._create_spin_box(0, 0)

        pos_layout = QGridLayout()
        pos_layout.setSpacing(10)
        for row, (text, spin) in enumerate(
            (
                ("Screen:", self.screen_spin),
                ("X Position:", self.x_spin),
                ("Y Position:", self.y_spin),
            )
        ):
            pos_layout.addWidget(self._create_label(text), row, 0)
            pos_layout.addWidget(spin, row, 1)
        return pos_layout

    def _build_size_title(self):
        """Build the WINDOW STATE header.

        The header carries the longest text in the panel once a corner is
        chosen. Left alone, a QLabel refuses to be narrower than its text and
        would push the whole editor wider than the panel, so it is allowed to
        wrap instead.

        Returns:
            QLabel: The header, retitled as the state changes.
        """
        self.size_lbl = self._create_header("WINDOW STATE")
        self.size_lbl.setWordWrap(True)
        return self.size_lbl

    def _build_snap_grid(self):
        """Build the picker that snaps the window to a region of its monitor.

        Returns:
            SnapGrid: The picker.
        """
        self.snap_grid = SnapGrid(self.screens[0])
        self.snap_grid.region_selected.connect(self._on_region_selected)
        self.snap_grid.custom_selected.connect(self._on_custom_selected)
        return self.snap_grid

    def _on_region_selected(self, region):
        """Snap the window to the region the user clicked.

        Args:
            region (str): One of :data:`starton.geometry.REGIONS`.
        """
        self._apply_window_state(stack_index(region))

    def _on_custom_selected(self):
        """Switch between typing a size and picking a region.

        Turning the toggle off only brings the picker back: the window keeps
        the size that was typed until a region is actually clicked, so a
        glance at the nine layouts costs nothing.
        """
        if self.is_custom_open:
            self._show_custom_size(False)
            return
        self._apply_window_state(CUSTOM_PAGE)

    def _build_custom_size(self):
        """Build the width and height boxes shown only for a custom size.

        The boxes stay alive while hidden: a snapped window still reports its
        width and height through them.

        Returns:
            QWidget: The custom-size row.
        """
        max_width, max_height = monitors.total_size(self.screens)
        self.width_spin = self._create_spin_box(0, max_width)
        self.height_spin = self._create_spin_box(0, max_height)

        self.custom_size_widget = QWidget()
        custom_layout = QGridLayout(self.custom_size_widget)
        custom_layout.setContentsMargins(15, 10, 15, 10)
        for row, (text, spin) in enumerate(
            (("Width:", self.width_spin), ("Height:", self.height_spin))
        ):
            custom_layout.addWidget(self._create_label(text), row, 0)
            custom_layout.addWidget(spin, row, 1)
        return self.custom_size_widget

    def _build_save_buttons(self):
        """Build the DELETE, TEST and SAVE buttons.

        Returns:
            QHBoxLayout: The button row.
        """
        self.deleting_btn = QPushButton("DELETE")
        self.deleting_btn.setToolTip("Delete this app (Ctrl+Delete)")
        self.deleting_btn.setStyleSheet(styles.DELETE_BTN)
        self.deleting_btn.clicked.connect(self.deleting_app)

        self.test_btn = QPushButton("TEST")
        self.test_btn.setToolTip("Open this app now, where the canvas shows it (Ctrl+T)")
        self.test_btn.setStyleSheet(styles.TEST_BTN)
        self.test_btn.clicked.connect(self.test_app)

        self.saving_btn = QPushButton("SAVE")
        self.saving_btn.setToolTip("Save this app (Ctrl+S)")
        self.saving_btn.setStyleSheet(styles.SAVE_BTN)
        self.saving_btn.clicked.connect(self.saving_app)

        saving_layout = QHBoxLayout()
        saving_layout.setSpacing(10)
        saving_layout.addWidget(self.deleting_btn)
        saving_layout.addWidget(self.test_btn)
        saving_layout.addWidget(self.saving_btn)
        return saving_layout

    def _build_run_button(self):
        """Build the button that opens the whole saved environment now.

        Returns:
            QPushButton: The run button.
        """
        self.run_btn = QPushButton("▶  RUN ENVIRONMENT NOW")
        self.run_btn.setToolTip("Open everything saved, as it would on boot (Ctrl+R)")
        self.run_btn.setStyleSheet(styles.RUN_BTN)
        self.run_btn.clicked.connect(self.run_environment)
        return self.run_btn

    def _build_separator(self):
        """Build the rule dividing the app editor from the link list.

        Returns:
            QLabel: An empty label carrying a bottom border.
        """
        separator = QLabel("")
        separator.setStyleSheet(styles.BORDER)
        return separator

    def _build_links_title(self):
        """Build the link section heading.

        Returns:
            QLabel: The heading.
        """
        links_title = QLabel("Start Up Links")
        links_title.setStyleSheet(styles.TITLE)
        return links_title

    def _build_add_link(self):
        """Build the name and URL fields plus the add button.

        Returns:
            QGridLayout: The add-link row.
        """
        self.link_name_input = QLineEdit()
        self.link_name_input.setPlaceholderText("Link Name (e.g., GitHub)")
        self.link_name_input.setStyleSheet(styles.LINK_INPUT)

        self.link_link_input = QLineEdit()
        self.link_link_input.setPlaceholderText("https://...")
        self.link_link_input.setStyleSheet(styles.LINK_INPUT)

        self.add_link_btn = QPushButton("➕")
        self.add_link_btn.setFixedSize(28, 28)
        self.add_link_btn.setStyleSheet(styles.LINK_ADD_BTN)
        self.add_link_btn.clicked.connect(self.add_new_link)

        add_link_layout = QGridLayout()
        add_link_layout.setSpacing(5)
        add_link_layout.addWidget(self.link_name_input, 0, 0)
        add_link_layout.addWidget(self.link_link_input, 1, 0)
        add_link_layout.addWidget(self.add_link_btn, 0, 1, 2, 1)
        return add_link_layout

    def _build_link_list(self):
        """Build the scrollable list of saved links.

        Returns:
            QScrollArea: The link list.
        """
        self.link_list_container = QWidget()
        self.link_list_container.setStyleSheet(styles.LINK_CONTAINER)
        self.link_list_layout = QVBoxLayout(self.link_list_container)
        self.link_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.link_list_layout.setSpacing(5)
        self.link_list_layout.setContentsMargins(5, 5, 5, 5)

        self.link_scroll_area = QScrollArea()
        self.link_scroll_area.setWidgetResizable(True)
        self.link_scroll_area.setStyleSheet(styles.LINK_SCROLL)
        self.link_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.link_scroll_area.setWidget(self.link_list_container)

        self.add_existing_links()
        return self.link_scroll_area

    def _create_header(self, text):
        """Create a section header label.

        Args:
            text (str): Header text.

        Returns:
            QLabel: The header.
        """
        header = QLabel(text)
        header.setStyleSheet(styles.HEADER)
        return header

    def _create_label(self, text):
        """Create a field label.

        Args:
            text (str): Label text.

        Returns:
            QLabel: The label.
        """
        label = QLabel(text)
        label.setStyleSheet(styles.LABEL)
        return label

    def _create_spin_box(self, minimum, maximum):
        """Create a spin box that redraws the canvas as it changes.

        Args:
            minimum (int): Lowest accepted value.
            maximum (int): Highest accepted value.

        Returns:
            QSpinBox: The spin box.
        """
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setStyleSheet(styles.SPINBOX)
        spin.valueChanged.connect(self.live_update_canvas)
        spin.valueChanged.connect(self._mark_dirty)
        return spin

    def toggle_info_panel(self):
        """Slide the info panel open or shut, moving its button along with it.

        The panel is a splitter child, so its width is really the splitter's to
        decide. Animating the maximum width still works - a splitter honours a
        child's limits - but the minimum has to be lifted first or it would
        stop the panel short of nothing, and both limits have to be handed back
        once the panel is open again or the divider would no longer drag.

        Whatever width the panel was last left at is remembered and restored,
        rather than snapping back to the width it first opened at.
        """
        if self.is_panel_open:
            self.panel_width = max(self.info_panel.width(), PANEL_MIN_WIDTH)
        self.is_panel_open = not self.is_panel_open
        target_panel_width = self.panel_width if self.is_panel_open else 0
        glyph = "☰" if self.is_panel_open else "⚙"
        self.info_panel.setMinimumWidth(0)

        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(
            self._animate(self.info_panel, b"maximumWidth", self.info_panel.width(), target_panel_width)
        )
        self.anim_group.addAnimation(
            self._animate(
                self.info_panel_toggle_btn,
                b"pos",
                self.info_panel_toggle_btn.pos(),
                QPoint(self._toggle_btn_x(), 10),
            )
        )
        self.anim_group.finished.connect(self._on_panel_animated)
        self.anim_group.start()
        self.info_panel_toggle_btn.setText(glyph)
        self.info_panel_toggle_btn.raise_()

    def _on_panel_animated(self):
        """Give the panel its width limits back once it has finished opening.

        Left pinned to the width the animation ended on, the panel could never
        be resized again: the splitter would find no room between its minimum
        and its maximum to move the divider into.
        """
        if not self.is_panel_open:
            return
        self.info_panel.setMinimumWidth(PANEL_MIN_WIDTH)
        self.info_panel.setMaximumWidth(PANEL_MAX_WIDTH)
        self.main_splitter.setSizes(
            [self.main_splitter.width() - self.panel_width, self.panel_width]
        )

    def _on_panel_resized(self, position, index):
        """Remember the width the divider was dragged to, and follow it.

        Args:
            position (int): Where the divider now sits.
            index (int): Which divider moved.
        """
        if self.is_panel_open:
            self.panel_width = self.info_panel.width()
        self.info_panel_toggle_btn.move(self._toggle_btn_x(), 10)

    def _toggle_btn_x(self):
        """Work out where the panel's toggle button belongs right now.

        Returns:
            int: Left edge of the button: against the panel while it is open,
            against the window's own edge once the panel is shut.
        """
        if self.is_panel_open:
            return self.width() - self.panel_width + 30
        return self.width() - self.info_panel_toggle_btn.width() - 15

    def resizeEvent(self, event):
        """Keep the toggle button beside the panel as the window changes size.

        The button is placed by hand rather than by a layout, so leaving full
        screen would otherwise strand it where the wider window had put it.

        Args:
            event (QResizeEvent): The Qt resize event.
        """
        super().resizeEvent(event)
        if self.info_panel_toggle_btn:
            self.info_panel_toggle_btn.move(self._toggle_btn_x(), 10)

    def toggle_full_screen(self):
        """Switch between full screen and a normal window."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def leave_full_screen(self):
        """Drop out of full screen, leaving a normal window alone."""
        if self.isFullScreen():
            self.showNormal()

    @staticmethod
    def _animate(target, prop, start_value, end_value):
        """Build one eased animation for the panel slide.

        Args:
            target (QObject): Object to animate.
            prop (bytes): Qt property name.
            start_value: Value to animate from.
            end_value: Value to animate to.

        Returns:
            QPropertyAnimation: The configured animation.
        """
        animation = QPropertyAnimation(target, prop)
        animation.setDuration(PANEL_ANIMATION_MS)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        return animation

    def _mark_dirty(self):
        """Recheck whether the panel still matches the saved app.

        Every widget that can change an app is wired here, but a signal firing
        only prompts the check - what counts is whether the apps now differ
        from the file. Selecting an app on the canvas, nudging it below the
        drag threshold and retyping a value it already had all fire signals
        without changing anything, and none of them should ask to save.

        Ignored while :meth:`_show_app` is filling the widgets in, where the
        panel is mid-way through being rebuilt and matches nothing.
        """
        if self._loading:
            return
        self._set_dirty(self._has_unsaved_changes())

    def _panel_app(self):
        """Build the app the panel currently describes, saved or not.

        Returns:
            App: The selected app as the widgets now show it.
        """
        return App(
            self.apps_title_label.toPlainText().lower(),
            path=self.app_path_input.text().strip(),
            pos=self._edited_position(),
            size=self._edited_size(),
        )

    def _pending_apps(self):
        """List the saved apps, with the selected one as the panel shows it.

        The selected app is found by identity rather than equality: two apps
        can render identically while being edited, and swapping both would
        hide the very difference this list exists to expose.

        Returns:
            list: Every app, including the selected one's unsaved edits.
        """
        panel_app = self._panel_app()
        return [
            panel_app if app is self.activated_app else app
            for app in self.apps or []
        ]

    def _has_unsaved_changes(self):
        """Report whether the apps differ from the last-saved file.

        Only the apps are checked. Links are written the moment they are added
        or removed, so they are never the thing left unsaved.

        Returns:
            bool: ``True`` when saving would change the file.
        """
        if not self.activated_app:
            return False
        return not self.save_file.apps_match(self._pending_apps())

    def _set_dirty(self, is_dirty):
        """Record the unsaved state and show it on the SAVE button.

        Args:
            is_dirty (bool): Whether unsaved edits exist.
        """
        self.is_dirty = is_dirty
        self.saving_btn.setText("SAVE *" if is_dirty else "SAVE")

    def _confirm_discard(self):
        """Ask what to do about unsaved edits before they are lost.

        Returns:
            bool: ``True`` to carry on with whatever prompted the question,
            ``False`` when the user cancelled.
        """
        if not self._has_unsaved_changes():
            return True
        answer = QMessageBox.warning(
            self,
            "Unsaved Changes",
            f'"{self.activated_app.get_name()}" has changes you have not saved.',
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            return False
        if answer == QMessageBox.StandardButton.Save:
            self.saving_app()
        else:
            self._set_dirty(False)
        return True

    def _refresh_app_lists(self):
        """Rebuild both places the saved apps are listed.

        The picker and the opening gallery show the same apps, so they are
        always rebuilt together: leaving one behind would offer a name that no
        longer exists or hide one that does.
        """
        self.app_picker.set_apps(self.apps, self.activated_app)
        self.app_gallery.set_apps(self.apps, self.screens)

    def update_info_panel(self, app):
        """Show one app's details, checking for unsaved edits on the way.

        Cancelling the unsaved-changes question rebuilds the lists as well as
        leaving the panel alone: the picker moves itself to whatever row was
        clicked, and would otherwise be left naming an app the panel never
        switched to.

        Args:
            app (App): The app to show.
        """
        if self.activated_app and self.activated_app == app:
            return
        if not self._confirm_discard():
            self._refresh_app_lists()
            return
        self._show_app(app)

    def _show_app(self, app):
        """Fill the panel from an app and select it on the canvas.

        Args:
            app (App): The app to show.
        """
        self._loading = True
        self.apps_title_label.setDisabled(False)
        self.panel_stack.setCurrentIndex(1)
        self.activated_app = app
        self.canvas.reset_app_view(app)

        pos = app.get_pos()
        screen_index = self._screen_index_for(pos)
        screen = self.screens[screen_index]
        self.screen_spin.setValue(screen_index + 1)
        self.x_spin.setRange(0, screen.width)
        self.y_spin.setRange(0, screen.height)
        self.x_spin.setValue(pos[0] - screen.x)
        self.y_spin.setValue(pos[1] - screen.y)

        size = app.get_size()
        if size.get_is_list():
            page = CUSTOM_PAGE
            width, height = size.get_size()
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)
            self.can_be_edited(True)
        else:
            self.can_be_edited(False)
            page = stack_index(size.get_size())
            x, y, width, height = region_rect(
                size.get_size(), 0, 0, screen.width, screen.height
            )
            self.snap_grid.set_monitor(screen)
            self.x_spin.setValue(x)
            self.y_spin.setValue(y)
            self.width_spin.setValue(width)
            self.height_spin.setValue(height)

        self._show_window_state(page)
        self.apps_title_label.setText(f"{app.get_name()}")
        self.app_path_input.setText(f"{app.get_app_path()}")
        self._refresh_app_lists()
        self._warned_path = None
        self._show_path_warning(app.path_exists())
        self._loading = False
        self._set_dirty(False)
        if not self.is_panel_open:
            self.toggle_info_panel()

    def _screen_index_for(self, pos):
        """Find the monitor a position sits on, falling back to the first.

        A saved position can land on no monitor at all once a screen is
        unplugged. Left alone the lookup answers ``-1``, which picks the last
        monitor by Python's indexing while the monitor spin box clamps to the
        first - and an app whose two halves disagree can never match what was
        saved, so it would look permanently unsaved.

        Args:
            pos (list): ``[x, y]`` in virtual-desktop coordinates.

        Returns:
            int: Index into :attr:`screens`.
        """
        index = monitors.find_screen_index(self.screens, pos)
        return 0 if index < 0 else index

    def _show_path_warning(self, path_is_valid):
        """Mark the path field when it points at something that is not there.

        Args:
            path_is_valid (bool): Whether the path exists on this machine.
        """
        if path_is_valid:
            self.app_path_input.setStyleSheet(styles.PATH_INPUT)
            self.app_path_input.setToolTip("")
            return
        self.app_path_input.setStyleSheet(styles.PATH_INPUT_BROKEN)
        self.app_path_input.setToolTip(
            "This path does not exist on this PC, so nothing will open at boot.\n"
            "The program may have moved, been uninstalled, or live on a drive\n"
            "that is not connected right now."
        )

    def _show_window_state(self, page):
        """Record the window state, retitle it and show it in the picker.

        Args:
            page (int): Window state; 0 is a custom size, and only then are the
                width and height boxes any use.
        """
        self.window_state_page = page
        self.size_lbl.setText(f"WINDOW STATE - {WINDOW_STATE_TITLES[page]}")
        self.snap_grid.set_selected(None if page == CUSTOM_PAGE else region_at(page))
        self._show_custom_size(page == CUSTOM_PAGE)

    def _show_custom_size(self, is_open):
        """Show either the width and height boxes or the region picker.

        Args:
            is_open (bool): ``True`` for the custom size, ``False`` for the
                nine regions.
        """
        self.is_custom_open = is_open
        self.custom_size_widget.setVisible(is_open)
        self.snap_grid.set_custom_open(is_open)

    def change_size_position(self, step):
        """Cycle the window state, snapping the app to the next region.

        Args:
            step (int): ``1`` for the next state, ``-1`` for the previous one.
        """
        page = (self.window_state_page + step) % len(WINDOW_STATE_TITLES)
        self._apply_window_state(page)

    def _apply_window_state(self, page):
        """Show a window state and move the app to match it.

        Args:
            page (int): Stack page; 0 leaves the geometry alone and hands the
                spin boxes back to the user.
        """
        self._show_window_state(page)
        self._mark_dirty()
        if page == CUSTOM_PAGE:
            self.can_be_edited(True)
            return

        self.can_be_edited(False)
        monitor = self.screens[self.screen_spin.value() - 1]
        self.snap_grid.set_monitor(monitor)
        x, y, width, height = region_rect(
            region_at(page), 0, 0, monitor.width, monitor.height
        )
        self.x_spin.setValue(x)
        self.y_spin.setValue(y)
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)

    def can_be_edited(self, state):
        """Enable or disable the position and size spin boxes.

        They are disabled while the window is snapped to a region, where the
        numbers are derived from the monitor rather than typed in.

        Args:
            state (bool): ``True`` to allow editing.
        """
        for spin in (self.x_spin, self.y_spin, self.width_spin, self.height_spin):
            spin.setDisabled(not state)

    def live_update_canvas(self):
        """Redraw the selected app on the canvas from the spin box values."""
        if not self.activated_app:
            return
        screen = self.screen_spin.value()
        self.canvas.change_app_view(
            self.activated_app,
            self.x_spin.value(),
            self.y_spin.value(),
            self.width_spin.value(),
            self.height_spin.value(),
            screen,
        )
        if self.window_state_page != CUSTOM_PAGE:
            self.snap_grid.set_monitor(self.screens[screen - 1])

    def _on_app_dragged(self, app, real_x, real_y, is_moved):
        """Follow a canvas drag in the panel's position fields.

        A press that has not travelled far enough to count as a move is a
        selection, not a drag, and is ignored. The canvas works in whole
        multiples of its scale, so writing its position back would round the
        app to the nearest few pixels and read as an edit the user never made.

        Args:
            app (App): The app being dragged.
            real_x (float): New left edge in desktop coordinates.
            real_y (float): New top edge in desktop coordinates.
            is_moved (bool): Whether the drag travelled far enough to count as
                a move, which drops the app out of its snapped region.
        """
        if self.activated_app != app or not is_moved:
            return
        self.can_be_edited(True)
        self._show_window_state(CUSTOM_PAGE)

        screen_index = self._screen_index_for([real_x, real_y])
        screen = self.screens[screen_index]
        self._set_silently(self.screen_spin, screen_index + 1)
        self._set_silently(self.x_spin, int(real_x - screen.x))
        self._set_silently(self.y_spin, int(real_y - screen.y))
        self._mark_dirty()

    def _on_app_region_snapped(self, app, screen_index, region):
        """Turn a window dropped onto a screen region into that region.

        A drag reports its position while it is happening, which drops the app
        onto the custom-size page; this arrives afterwards, once the window has
        been let go somewhere a region recognises, and puts it back onto the
        region page. Handing the work to :meth:`_apply_window_state` means the
        title, the region picker, the spin boxes and the unsaved marker all
        follow a drop exactly as they follow a click on the picker.

        A region survives a change of screen resolution where a pixel size does
        not, so a window that lands on one is worth saving as one.

        Args:
            app (App): The app that was dropped.
            screen_index (int): Monitor it landed on, counted from zero.
            region (str): One of :data:`starton.geometry.REGIONS`.
        """
        if self.activated_app != app:
            return
        self._set_silently(self.screen_spin, screen_index + 1)
        self._apply_window_state(stack_index(region))

    def _on_app_resized(self, app, new_width, new_height):
        """Follow a canvas resize in the panel's size fields.

        Args:
            app (App): The app being resized.
            new_width (int): New width in desktop pixels.
            new_height (int): New height in desktop pixels.
        """
        if self.activated_app != app:
            return
        self.can_be_edited(True)
        self._show_window_state(CUSTOM_PAGE)
        self._set_silently(self.width_spin, new_width)
        self._set_silently(self.height_spin, new_height)
        self._mark_dirty()

    @staticmethod
    def _set_silently(spin, value):
        """Set a spin box without letting it redraw the canvas.

        The canvas is the source of these values, so echoing them straight back
        would fight with the drag in progress.

        Args:
            spin (QSpinBox): Spin box to update.
            value (int): New value.
        """
        spin.blockSignals(True)
        spin.setValue(value)
        spin.blockSignals(False)

    def select_next_app(self):
        """Select the app after the current one, wrapping at the end."""
        self._select_app_at_offset(1, fallback_index=0)

    def select_previous_app(self):
        """Select the app before the current one, wrapping at the start."""
        self._select_app_at_offset(-1, fallback_index=-1)

    def _select_app_at_offset(self, offset, fallback_index):
        """Step through the saved apps from the selected one.

        Args:
            offset (int): How far to step, ``1`` or ``-1``.
            fallback_index (int): Which app to select when none is selected yet.
        """
        if not self.apps:
            return
        if not self.activated_app:
            self.update_info_panel(self.apps[fallback_index])
            return
        index = self._index_of_app(self.activated_app)
        if index is not None:
            self.update_info_panel(self.apps[(index + offset) % len(self.apps)])

    def _index_of_app(self, app):
        """Find an app's position in the saved list.

        Args:
            app (App): The app to look for.

        Returns:
            int | None: Its index, or ``None`` when it is not in the list.
        """
        for index, candidate in enumerate(self.apps):
            if candidate == app:
                return index
        return None

    def create_new_app(self):
        """Add an app filling the first monitor, and select it for editing."""
        monitor = self.screens[0]
        self._add_app(
            App(
                self._next_app_name(),
                path="c:\\",
                pos=[monitor.x, monitor.y],
                size=WindowSize([monitor.width, monitor.height]),
            )
        )

    def create_app_at(self, real_x, real_y):
        """Add a quarter-screen app where the canvas was right clicked.

        This is deliberately a method of its own rather than an argument to
        :meth:`create_new_app`, which is wired to a button and a shortcut: a
        button hands its slot a checked flag, and that flag would arrive as a
        position.

        Args:
            real_x (float): Left edge in desktop coordinates.
            real_y (float): Top edge in desktop coordinates.
        """
        monitor = self.screens[self._screen_index_for([real_x, real_y])]
        _, _, width, height = region_rect(
            "Right_Bottom", monitor.x, monitor.y, monitor.width, monitor.height
        )
        x = min(max(int(real_x), monitor.x), monitor.x + monitor.width - width)
        y = min(max(int(real_y), monitor.y), monitor.y + monitor.height - height)
        self._add_app(
            App(
                self._next_app_name(),
                path="c:\\",
                pos=[x, y],
                size=WindowSize([width, height]),
            )
        )

    def _add_app(self, new_app):
        """Save a newly built app, draw it, and open it in the panel.

        Args:
            new_app (App): The app to add.
        """
        if self.apps and len(self.apps) >= MAX_APPS:
            QMessageBox.warning(
                self,
                "Overflow",
                "Too much apps getting opened\nWhen the pc is starting up",
            )
            return
        if not self._confirm_discard():
            return
        if not self.apps:
            self.apps = []
        self.apps.append(new_app)
        self.canvas.add_app_view(new_app)
        self._show_app(new_app)
        self.apps_title_label.setDisabled(False)
        self.panel_stack.setCurrentIndex(1)
        self._save_to_disk()

    def _next_app_name(self):
        """Pick an unused default name for a new app.

        Returns:
            str: ``"new_app"``, or ``"new_app(2)"`` and so on when taken.
        """
        taken = {app.get_name() for app in self.apps} if self.apps else set()
        suffix = 0
        while True:
            name = NEW_APP_NAME if suffix == 0 else f"{NEW_APP_NAME}({suffix})"
            if name not in taken:
                return name
            suffix += 1

    def saving_app(self):
        """Write the panel's values back into the selected app, and to disk.

        The values come from :meth:`_panel_app`, the same reading of the
        widgets the unsaved check uses. Were the two to read the panel
        differently, saving could never satisfy the check and the editor would
        ask about unsaved changes forever.
        """
        if not self.activated_app:
            return
        panel_app = self._panel_app()
        self.activated_app.change_app(
            panel_app.get_name(),
            panel_app.get_app_path(),
            panel_app.get_pos(),
            panel_app.get_size(),
        )
        self._save_to_disk()
        self._set_dirty(False)
        self._refresh_app_lists()
        self.canvas.reset_app_view(self.activated_app)
        self._warn_about_missing_path()

    def _edited_size(self):
        """Build the size the panel currently describes.

        Returns:
            WindowSize: A pixel pair on the custom page, otherwise the region
            the snap grid has selected.
        """
        if self.window_state_page == CUSTOM_PAGE:
            return WindowSize([self.width_spin.value(), self.height_spin.value()])
        return WindowSize(region_at(self.window_state_page))

    def _edited_position(self):
        """Build the desktop position the panel currently describes.

        Returns:
            list: ``[x, y]`` in virtual-desktop coordinates.
        """
        monitor = self.screens[self.screen_spin.value() - 1]
        return [self.x_spin.value() + monitor.x, self.y_spin.value() + monitor.y]

    def _warn_about_missing_path(self):
        """Point out a path that will not open, without refusing to save it.

        The save still goes through: the target may live on a drive that is
        simply not connected right now. The red field and its tooltip are the
        standing reminder, so the dialog appears only the first time a given
        path is saved - repeating it on every save would punish someone
        deliberately keeping an app that lives on a drive they plug in.
        """
        path = self.activated_app.get_app_path()
        path_is_valid = self.activated_app.path_exists()
        self._show_path_warning(path_is_valid)
        if path_is_valid or path == self._warned_path:
            return
        self._warned_path = path
        QMessageBox.warning(
            self,
            "Path Not Found",
            f'"{path}" does not exist on this PC.\n'
            "It has been saved anyway, but nothing will open at boot unless\n"
            "the path comes back.",
        )

    def deleting_app(self):
        """Delete the selected app from the list, the canvas and the file."""
        if not self.activated_app:
            return
        index = self._index_of_app(self.activated_app)
        if index is not None:
            del self.apps[index]
            if not self.apps:
                self.apps = None
        self.canvas.delete_app_view(self.activated_app)
        self.activated_app = None
        self._set_dirty(False)
        self._refresh_app_lists()
        self.apps_title_label.setText("Select an App")
        self.apps_title_label.setDisabled(True)
        self.panel_stack.setCurrentIndex(0)
        self._save_to_disk()

    def _on_app_delete_requested(self, deleted_app):
        """Delete an app the user removed from the canvas.

        The app is selected first so the panel is not left showing something
        that no longer exists.

        Args:
            deleted_app (App): The app to delete.
        """
        if self.activated_app != deleted_app:
            was_empty_page = self.panel_stack.currentIndex() == 0
            self._show_app(deleted_app)
            if was_empty_page:
                self.toggle_info_panel()
        self.deleting_app()

    def browse_for_executable(self):
        """Pick a program to launch, naming the app after the file chosen."""
        if not self.activated_app:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Startup App",
            f"{self.activated_app.get_app_path()}",
            "All Files (*)",
            options=QFileDialog.Option.DontResolveSymlinks,
        )
        if not file_path:
            return
        normalized_path = os.path.normpath(file_path)
        name = self._name_from_path(normalized_path)
        if name is None:
            QMessageBox.warning(self, "Missing Info", "Please provide the correct path")
            return
        self.apps_title_label.setText(name)
        self.app_path_input.setText(normalized_path)

    def browse_for_folder(self):
        """Pick a folder to open in Explorer instead of a program."""
        if not self.activated_app:
            return
        file_path = QFileDialog.getExistingDirectory(
            self,
            "Select Target Folder",
            f"{self.activated_app.get_app_path_folder()}",
        )
        if file_path:
            normalized_path = os.path.normpath(file_path)
            self.app_path_input.setText(normalized_path)
            self.apps_title_label.setText(normalized_path)

    @staticmethod
    def _name_from_path(path):
        """Derive an app name from an executable path.

        Args:
            path (str): A normalised path.

        Returns:
            str | None: The file name without its extension, ``"explorer"``
            for a path ending in a separator, or ``None`` when the path has no
            file name to work from.
        """
        parts = path.split(os.sep)
        if len(parts) <= 1:
            return None
        if not parts[-1]:
            return "explorer"
        file_name = parts[-1].split(".")
        if len(file_name) <= 1:
            return None
        return file_name[0].lower()

    def add_new_link(self):
        """Add the link in the input fields to the list and to disk."""
        link_name = self.link_name_input.text().strip()
        link_url = self.link_link_input.text().strip()
        problem = Link.problem(link_name, link_url)
        if problem:
            QMessageBox.warning(self, "Missing Info", problem)
            return
        link = Link(link_name, link_url)
        self._add_link_block(link)
        self.link_name_input.clear()
        self.link_link_input.clear()
        if not self.links:
            self.links = []
        self.links.append(link)
        self._save_to_disk()

    def add_existing_links(self):
        """Fill the link list with everything already saved."""
        if not self.links:
            return
        for link in self.links:
            self._add_link_block(link)
            self.link_name_input.clear()
            self.link_link_input.clear()

    def _add_link_block(self, link):
        """Add one link card to the list.

        Args:
            link (Link): The link to show.
        """
        block = LinkBlock(link)
        block.edit_requested.connect(self.edit_link)
        block.delete_requested.connect(self.delete_link)
        self.link_list_layout.addWidget(block)

    def edit_link(self, block_widget):
        """Let the user retype a link's name and address.

        The edit is written the moment the dialog is accepted, the way adding
        and deleting a link already are, so the link list is never one of the
        things left unsaved.

        Args:
            block_widget (LinkBlock): The card the user is editing.
        """
        link = block_widget.get_link()
        dialog = LinkDialog(link, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        link.change_link(*dialog.get_values())
        block_widget.refresh()
        self._save_to_disk()

    def delete_link(self, block_widget):
        """Remove a link card, its link and the saved entry.

        Args:
            block_widget (LinkBlock): The card the user deleted.
        """
        deleted_link = block_widget.get_link()
        self.link_list_layout.removeWidget(block_widget)
        block_widget.deleteLater()
        for index, link in enumerate(self.links):
            if link == deleted_link:
                del self.links[index]
                break
        if not self.links:
            self.links = None
        self._save_to_disk()

    def run_environment(self):
        """Open the whole saved environment now, without a reboot.

        The real start-up entry point runs in its own process, so what happens
        is exactly what will happen on the next boot and the editor stays
        responsive while windows appear.
        """
        if not spawn.is_available():
            QMessageBox.warning(
                self,
                "Python Not Found",
                "pythonw could not be found on this PC.\n"
                "Starton needs it to open your environment, at boot as well as\n"
                "now, so install Python 3.12 or later and try again.",
            )
            return
        enabled_apps = self.apps or []
        enabled_links = [link for link in self.links or [] if link.is_enabled()]
        if not enabled_apps and not enabled_links:
            QMessageBox.information(
                self,
                "Nothing To Run",
                "There is nothing switched on to open yet.",
            )
            return
        if not self._confirm_run(len(enabled_apps), len(enabled_links)):
            return
        try:
            spawn.run_environment()
        except OSError as error:
            QMessageBox.warning(self, "Could Not Run", str(error))

    def _confirm_run(self, app_count, link_count):
        """Check the user really wants a screen full of windows.

        Args:
            app_count (int): How many apps will open.
            link_count (int): How many links will open.

        Returns:
            bool: ``True`` when the user said go ahead.
        """
        answer = QMessageBox.question(
            self,
            "Run Environment",
            f"This will open {app_count} app(s) and {link_count} link(s) "
            "as saved, just like a fresh boot.\n\nCarry on?",
        )
        return answer == QMessageBox.StandardButton.Yes

    def test_app(self):
        """Open just the selected app, using the geometry currently on screen.

        The app is tested as it is being edited rather than as it was last
        saved, so a layout can be checked before it is committed.
        """
        if not self.activated_app or self.tester:
            return
        candidate = App(
            self.activated_app.get_name(),
            path=self.app_path_input.text().strip(),
            pos=self._edited_position(),
            size=self._edited_size(),
        )
        if not candidate.path_exists():
            self._show_path_warning(False)
            QMessageBox.warning(
                self,
                "Path Not Found",
                f'"{candidate.get_app_path()}" does not exist on this PC,\n'
                "so there is nothing to open.",
            )
            return
        screens, work_areas = runner.screens_and_work_areas()
        self.test_btn.setEnabled(False)
        self.test_btn.setText("TESTING…")
        self.tester = AppTester(candidate, screens, work_areas, parent=self)
        self.tester.finished_test.connect(self._on_test_finished)
        self.tester.start()

    def _on_test_finished(self, error):
        """Hand the TEST button back once the app has opened.

        Args:
            error (str): What went wrong, or an empty string on success.
        """
        self.tester = None
        self.test_btn.setEnabled(True)
        self.test_btn.setText("TEST")
        if error:
            QMessageBox.warning(self, "Could Not Open", error)

    def closeEvent(self, event):
        """Offer to save unsaved app edits before the window closes.

        Args:
            event (QCloseEvent): The close event, ignored when the user
                cancels.
        """
        if self._confirm_discard():
            event.accept()
        else:
            event.ignore()

    def _save_to_disk(self):
        """Write the whole environment to the save file."""
        self.save_file.write_file(self.apps, self.links)
