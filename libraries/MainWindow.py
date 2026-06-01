from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QCheckBox,
                            QLabel, QFrame, QLineEdit, QTextEdit, QPushButton, QMessageBox, 
                            QSpinBox, QGridLayout, QFileDialog, QStackedWidget, QScrollArea)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint
from PyQt6.QtWidgets import QFileDialog
from libraries.App import *
from libraries.MonitorCanvas import *
from libraries.Link import *
from libraries.LinkBlock import *
from libraries.SavingFile import *
from libraries.Size import *
from libraries.MiniCavas import *
from libraries.ClickableLineEdit import *
import os

INFO_PANEL_STYLE = "background-color: #252526;" 
INFO_PANEL_BTN_STYLE = """
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
TITLE_STYLE = "color: white; font-size: 25px; font-weight: bold;"
TITLE_BTN_STYLE =  """
    QPushButton {
        font-size: 35px;
    }
    QPushButton:hover {
        border: 1px solid #0078d4
    }
""" 
HEADER_STYLE = "color: #aaaaaa; font-size: 16px; font-weight: bold; margin-top: 8px;"
PATH_INPUT_STYLE = "background-color: #333333; color: white; border: 1px solid #555; padding: 5px;"
BROWSE_BTN_STYLE = """
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
LBL_STYLE = "color: #cccccc; font-size: 13px; font-weight: bold;"
SPINBOX_STYLE = """
    QSpinBox { background-color: #333333; color: white; border: 1px solid #555; padding: 4px; font-size: 13px; }
    QSpinBox::up-button, QSpinBox::down-button { background-color: #444; width: 16px; }
"""
CHECK_STYLE = """QCheckBox {
                spacing: 8px;
                color: #cccccc; 
                font-size: 13px; 
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 9px;
                border: 1px solid #888888;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #0078D4;
                background-color: #0078D4;
            }
            QCheckBox::indicator:hover {
                border-color: #005A9E;
            }
                                       """
BORDER_STYLE = "border-bottom: 2px solid white;"
LINK_ADD_STYLE = "background-color: #333; color: white; border: 1px solid #555; padding: 4px;"
LINK_ADD_BTN_STYLE = "QPushButton { background-color: #0078d4; color: white; border: none; border-radius: 2px; } QPushButton:hover { background-color: #2b88d8; }"
LINK_SCROLL_STYLE = """
    QScrollArea { border: 1px solid #444; background-color: #1e1e1e; }
    QScrollBar:vertical { background: #252526; width: 10px; }
    QScrollBar::handle:vertical { background: #555; min-height: 20px; border-radius: 5px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""
LINK_CONTAINER_STYLE = "background-color: #1e1e1e;"
DELETE_BTN_STYLE = """
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
SAVE_BTN_STYLE = """
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

MAX_INFO_PANEL_WIDTH = 500
SIZE_TITLE_OPTIONS = ["CUSTOM", "FULL SCREEN", "LEFT SIDE", "RIGHT SIDE", "TOP SIDE", "BOTTOM SIDE", "LEFT TOP CORNER", "LEFT BOTTOM CORNER", "RIGHT TOP CORNER", "RIGHT BOTTOM CORNER"]
SIZE_STACK_OPTIONS = {"Full": 1, "Left": 2, "Right": 3, "Top": 4, "Bottom": 5, "Left_Top": 6, "Left_Bottom": 7, "Right_Top": 8, "Right_Bottom": 9}
SIZE_NANE_OPTIONS = ["Full", "Left", "Right", "Top", "Bottom", "Left_Top", "Left_Bottom", "Right_Top", "Right_Bottom"]

class MainWindow(QMainWindow):
    def __init__(self, screens, apps, links, saving_file):
        super().__init__()
        self.screens = screens
        self.apps = apps
        self.links = links
        self.saving_file = saving_file
        self.activated_app = None
        self.is_panel_open = True
        
        
        # --- WINDOW ---
        self.setWindowTitle("SetupGUI - Beta")
        primary_screen = self.get_primary_screen()
        self.resize(primary_screen.width, primary_screen.height)
        self.showMaximized()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- CANVAS ---
        self.canvas = MonitorCanvas(self.screens, self.apps, self.update_info_panel, self.live_update_panel_from_drag, self.live_update_panel_from_resize, self.handle_deleting_app)
        main_layout.addWidget(self.canvas, stretch=3)
        self.info_panel = QFrame()
        self.info_panel.setStyleSheet(INFO_PANEL_STYLE)
        self.info_panel.setMaximumWidth(MAX_INFO_PANEL_WIDTH)
        self.info_panel.setContentsMargins(0, 0, 0, 0)
        self.info_panel_toggle_btn = QPushButton("☰", central_widget)
        self.info_panel_toggle_btn.setFixedSize(35, 35)
        self.info_panel_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.info_panel_toggle_btn.setToolTip("Toggle Info Panel")
        self.info_panel_toggle_btn.setStyleSheet(INFO_PANEL_BTN_STYLE)
        self.info_panel_toggle_btn.clicked.connect(self.toggle_info_panel)
        self.info_panel_toggle_btn.move(primary_screen.width - MAX_INFO_PANEL_WIDTH + 30, 10) 
        
        # --- INFO_PANEL ---
        panel_layout = QVBoxLayout(self.info_panel)
        panel_layout.setContentsMargins(15, 20, 15, 20)
        self.panel_stack = QStackedWidget()
        panel_layout.addWidget(self.panel_stack)
        
        # --- EMPTY INFO PANEL ---
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setContentsMargins(15, 20, 15, 20)
        self.empty_label = QLabel("No App is selected\nPlease select an App")
        self.empty_label.setStyleSheet(HEADER_STYLE)
        empty_layout.setSpacing(8)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # --- EDITOR INFO PANEL ---
        self.editor_widget = QWidget()
        editor_layout = QVBoxLayout(self.editor_widget)
        editor_layout.setContentsMargins(15, 20, 15, 20)
        editor_layout.setSpacing(8)
        
        # --- TITLE ---
        app_title_layout = QHBoxLayout()
        app_title_layout.setSpacing(5)
        app_title_layout.setContentsMargins(40, 0, 0, 0)
        self.apps_title_label = QTextEdit("Select an App")
        self.apps_title_label.setStyleSheet(TITLE_STYLE)
        self.apps_title_label.setFixedSize(MAX_INFO_PANEL_WIDTH - 40 * 4, 50)
        app_title_add_btn = QPushButton("➕")
        app_title_add_btn.setFixedSize(28, 28)
        app_title_add_btn.setStyleSheet(LINK_ADD_BTN_STYLE)
        app_title_add_btn.clicked.connect(self.create_new_app)
        app_title_arrows_layout = QVBoxLayout()
        app_title_arrows_layout.setSpacing(5)
        app_title_up_btn = QPushButton("🔼")
        app_title_up_btn.setFixedSize(28, 28)
        app_title_up_btn.setStyleSheet(TITLE_BTN_STYLE)
        app_title_up_btn.clicked.connect(self.change_app_up) 
        app_title_down_btn = QPushButton("🔽")
        app_title_down_btn.setFixedSize(28, 28)
        app_title_down_btn.setStyleSheet(TITLE_BTN_STYLE)
        app_title_down_btn.clicked.connect(self.change_app_down) 
        app_title_arrows_layout.addWidget(app_title_up_btn)
        app_title_arrows_layout.addWidget(app_title_down_btn)
        app_title_layout.addLayout(app_title_arrows_layout)
        app_title_layout.addWidget(self.apps_title_label)
        app_title_layout.addWidget(app_title_add_btn)
        
        # --- APP PATH ---
        self.app_path_input = ClickableLineEdit()
        self.app_path_input.setPlaceholderText("APP OPEN PATH (e.g., C:\\...)")
        self.app_path_input.setStyleSheet(PATH_INPUT_STYLE)   
        self.app_path_input.clicked.connect(self.browse_for_folder)
        browse_app_path_btn = QPushButton("📂")
        browse_app_path_btn.setToolTip("Browse for Executable")
        browse_app_path_btn.setFixedSize(28, 28)
        browse_app_path_btn.setStyleSheet(BROWSE_BTN_STYLE)
        browse_app_path_btn.clicked.connect(self.browse_for_executable) 
        path_lbl = self.create_header("APP PATH")
        app_path_layout = QHBoxLayout()
        app_path_layout.setSpacing(5)
        app_path_layout.addWidget(self.app_path_input)
        app_path_layout.addWidget(browse_app_path_btn)
        
        # --- POSITION ---
        pos_layout = QGridLayout()
        pos_layout.setSpacing(10)
        self.screen_spin = QSpinBox()
        self.screen_spin.setRange(1, len(self.screens)) 
        self.screen_spin.setStyleSheet(SPINBOX_STYLE)
        self.screen_spin.valueChanged.connect(self.live_update_canvas)
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 0) 
        self.x_spin.setStyleSheet(SPINBOX_STYLE)
        self.x_spin.valueChanged.connect(self.live_update_canvas)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 0)
        self.y_spin.setStyleSheet(SPINBOX_STYLE)
        self.y_spin.valueChanged.connect(self.live_update_canvas)
        screen_lbl = QLabel("Screen:")
        screen_lbl.setStyleSheet(LBL_STYLE)
        x_lbl = QLabel("X Position:")
        x_lbl.setStyleSheet(LBL_STYLE)
        y_lbl = QLabel("Y Position:")
        y_lbl.setStyleSheet(LBL_STYLE)
        position_lbl = self.create_header("POSITION")
        pos_layout.addWidget(screen_lbl, 0, 0)
        pos_layout.addWidget(self.screen_spin, 0, 1)
        pos_layout.addWidget(x_lbl, 1, 0)
        pos_layout.addWidget(self.x_spin, 1, 1)
        pos_layout.addWidget(y_lbl, 2, 0)
        pos_layout.addWidget(self.y_spin, 2, 1)
        
        # --- SIZE ---
        max_width, max_height = self.get_max_border()
        self.size_stack = QStackedWidget()
        size_costum_widget = QWidget()
        size_costum_layout = QGridLayout(size_costum_widget)
        size_costum_layout.setContentsMargins(15, 20, 15, 20)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(0, max_width) 
        self.width_spin.setStyleSheet(SPINBOX_STYLE)
        self.width_spin.valueChanged.connect(self.live_update_canvas)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(0, max_height)
        self.height_spin.setStyleSheet(SPINBOX_STYLE)
        self.height_spin.valueChanged.connect(self.live_update_canvas)
        width_lbl = QLabel("Width:")
        width_lbl.setStyleSheet(LBL_STYLE)
        height_lbl = QLabel("Height:")
        height_lbl.setStyleSheet(LBL_STYLE)
        size_costum_layout.addWidget(width_lbl, 0, 0)
        size_costum_layout.addWidget(self.width_spin, 0, 1)
        size_costum_layout.addWidget(height_lbl, 1, 0)
        size_costum_layout.addWidget(self.height_spin, 1, 1)
        
        self.size_lbl = self.create_header("WINDOW STATE")
        size_title = QHBoxLayout()
        size_title_arrows_layout = QVBoxLayout()
        size_title_arrows_layout.setSpacing(5)
        size_title_up_btn = QPushButton("🔼")
        size_title_up_btn.setFixedSize(28, 28)
        size_title_up_btn.setStyleSheet(TITLE_BTN_STYLE)
        size_title_up_btn.clicked.connect(lambda: self.change_size_position(1)) 
        size_title_down_btn = QPushButton("🔽")
        size_title_down_btn.setFixedSize(28, 28)
        size_title_down_btn.setStyleSheet(TITLE_BTN_STYLE)
        size_title_down_btn.clicked.connect(lambda: self.change_size_position(-1)) 
        size_title_arrows_layout.addWidget(size_title_up_btn)
        size_title_arrows_layout.addWidget(size_title_down_btn)
        size_title.addWidget(self.size_lbl)
        size_title.addLayout(size_title_arrows_layout)
           
        self.size_stack.addWidget(size_costum_widget)
        self.size_stack_widgets = []
        for i in range(9):
            size_stack_widget = MiniCanvas(SIZE_NANE_OPTIONS[i], self.screens[0])
            self.size_stack.addWidget(size_stack_widget)
            self.size_stack_widgets.append(size_stack_widget)
        self.size_stack.setCurrentIndex(0)  
        
        # --- SAVING ---
        saving_layout = QHBoxLayout()
        saving_layout.setSpacing(10)
        self.saving_btn = QPushButton("SAVE")
        self.saving_btn.clicked.connect(self.saving_app)
        self.saving_btn.setStyleSheet(SAVE_BTN_STYLE)
        self.deleting_btn = QPushButton("DELETE")
        self.deleting_btn.clicked.connect(self.deleting_app)
        self.deleting_btn.setStyleSheet(DELETE_BTN_STYLE)
        saving_layout.addWidget(self.deleting_btn)
        saving_layout.addWidget(self.saving_btn)
        
        # --- BORDER ---
        border_lbl = QLabel("")
        border_lbl.setStyleSheet(BORDER_STYLE)
        
        # --- LINKS ---
        add_link_layout = QGridLayout()
        add_link_layout.setSpacing(5)
        self.link_name_input = QLineEdit()
        self.link_name_input.setPlaceholderText("Link Name (e.g., GitHub)")
        self.link_name_input.setStyleSheet(LINK_ADD_STYLE)
        self.link_link_input = QLineEdit()
        self.link_link_input.setPlaceholderText("https://...")
        self.link_link_input.setStyleSheet(LINK_ADD_STYLE)
        self.add_link_btn = QPushButton("➕")
        self.add_link_btn.setFixedSize(28, 28)
        self.add_link_btn.setStyleSheet(LINK_ADD_BTN_STYLE)
        self.add_link_btn.clicked.connect(self.add_new_link)
        add_link_layout.addWidget(self.link_name_input, 0, 0)
        add_link_layout.addWidget(self.link_link_input, 1, 0)
        add_link_layout.addWidget(self.add_link_btn, 0, 1, 2, 1)
        self.link_scroll_area = QScrollArea()
        self.link_scroll_area.setWidgetResizable(True)
        self.link_scroll_area.setStyleSheet(LINK_SCROLL_STYLE)
        self.link_list_container = QWidget()
        self.link_list_container.setStyleSheet(LINK_CONTAINER_STYLE)
        self.link_list_layout = QVBoxLayout(self.link_list_container)
        self.link_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.link_list_layout.setSpacing(5)
        self.link_list_layout.setContentsMargins(5, 5, 5, 5)        
        self.link_scroll_area.setWidget(self.link_list_container)
        self.add_existing_links()
        links_title_label = QLabel("Start Up Links")
        links_title_label.setStyleSheet(TITLE_STYLE)
        
        # --- EMPTY LAYOUT ---
        empty_layout.addWidget(self.empty_label)
        
        # --- EDITOR LAYOUT ---
        editor_layout.addWidget(path_lbl)
        editor_layout.addLayout(app_path_layout)
        editor_layout.addWidget(position_lbl)
        editor_layout.addLayout(pos_layout)
        editor_layout.addLayout(size_title)
        editor_layout.addWidget(self.size_stack) 
        editor_layout.addLayout(saving_layout)
        editor_layout.addStretch()
        
        # --- FINAL LAYOUT --- 
        self.panel_stack.addWidget(self.empty_widget)
        self.panel_stack.addWidget(self.editor_widget)
        panel_layout.addLayout(app_title_layout)
        panel_layout.addWidget(self.panel_stack, stretch=1)
        panel_layout.addWidget(border_lbl)
        panel_layout.addWidget(links_title_label)
        panel_layout.addLayout(add_link_layout)
        panel_layout.addWidget(self.link_scroll_area, stretch=1)
        main_layout.addWidget(self.info_panel, stretch=1)
        
        # --- FINAL SETUP ---
        self.apps_title_label.setDisabled(True)
        self.panel_stack.setCurrentIndex(0)  
        self.toggle_info_panel()
        
    def toggle_info_panel(self):
        self.is_panel_open = not self.is_panel_open
        if not(self.is_panel_open):
            target_panel_width = 0
            target_btn_x = self.width() - self.info_panel_toggle_btn.width() - 15
            btn_str = "⚙"
        else:
            target_panel_width = MAX_INFO_PANEL_WIDTH
            target_btn_x = self.width() - target_panel_width + 30
            btn_str = "☰"
        info_panel_anim = QPropertyAnimation(self.info_panel, b"maximumWidth")
        info_panel_anim.setDuration(350)
        info_panel_anim.setStartValue(self.info_panel.width())
        info_panel_anim.setEndValue(target_panel_width)
        info_panel_anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        info_panel_btn_anim = QPropertyAnimation(self.info_panel_toggle_btn, b"pos")
        info_panel_btn_anim.setDuration(350)
        info_panel_btn_anim.setStartValue(self.info_panel_toggle_btn.pos())
        info_panel_btn_anim.setEndValue(QPoint(target_btn_x, 10))
        info_panel_btn_anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(info_panel_anim)
        self.anim_group.addAnimation(info_panel_btn_anim)
        self.anim_group.start()
        self.info_panel_toggle_btn.setText(btn_str)
        self.info_panel_toggle_btn.raise_()
        
    def update_info_panel(self, app): 
        if not(self.activated_app) or self.activated_app != app:
            self.apps_title_label.setDisabled(False)
            self.panel_stack.setCurrentIndex(1)
            self.activated_app = app
            self.canvas.reset_app_view(app)
            pos = app.get_pos()
            screen_index = self.find_screen(pos)
            screen = self.screens[screen_index] 
            pos = [(pos[0] - screen.x), (pos[1] - screen.y)]
            self.screen_spin.setValue(screen_index + 1) 
            self.x_spin.setRange(0, screen.width)
            self.y_spin.setRange(0, screen.height)
            self.x_spin.setValue(pos[0])
            self.y_spin.setValue(pos[1])
            
            size_obj = app.get_size()
            size = size_obj.get_size()
            size_stack_pos = 0
            if(size_obj.get_is_list()):
                self.width_spin.setValue(size[0])
                self.height_spin.setValue(size[1])
                self.can_be_edited(True)
            else:
                self.can_be_edited(False)
                app_x, app_y, app_width, app_height = self.get_position_on_monitor(size, screen)
                size_stack_pos = SIZE_STACK_OPTIONS[size]
                self.size_stack_widgets[size_stack_pos - 1].set_monitor(screen)
                self.x_spin.setValue(app_x)
                self.y_spin.setValue(app_y)
                self.width_spin.setValue(app_width)
                self.height_spin.setValue(app_height)
            self.size_stack.setCurrentIndex(size_stack_pos)
            self.size_lbl.setText(f"WINDOW STATE - {SIZE_TITLE_OPTIONS[size_stack_pos]}")
            self.apps_title_label.setText(f"{app.get_name()}") 
            self.app_path_input.setText(f"{app.get_app_path()}")
            if(not self.is_panel_open):
                self.toggle_info_panel()
    
    def change_size_position(self, diff):
        size_state = self.size_stack.currentIndex()
        max_state = len(SIZE_TITLE_OPTIONS)
        new_size_state = (size_state + diff) % max_state
        self.size_stack.setCurrentIndex(new_size_state)
        self.size_lbl.setText(f"WINDOW STATE - {SIZE_TITLE_OPTIONS[new_size_state]}")
        if(new_size_state == 0):
            self.can_be_edited(True)
            return 
        self.can_be_edited(False)
        monitor = self.screens[self.screen_spin.value() - 1]
        self.size_stack_widgets[new_size_state - 1].set_monitor(monitor)
        new_x = 0
        new_y = 0
        new_width = monitor.width
        new_height = monitor.height
        if new_size_state == 3 or new_size_state == 8 or new_size_state == 9:
            new_x = monitor.width // 2
        if new_size_state == 5 or new_size_state == 7 or new_size_state == 9:
            new_y = monitor.height // 2
        if not(new_size_state == 4 or new_size_state == 5 or new_size_state == 1):
            new_width = monitor.width // 2  
        if not(new_size_state == 2 or new_size_state == 3 or new_size_state == 1):
            new_height = monitor.height // 2  
        self.x_spin.setValue(new_x)
        self.y_spin.setValue(new_y)
        self.width_spin.setValue(new_width)
        self.height_spin.setValue(new_height)

    def live_update_canvas(self):
        if self.activated_app: 
            x = self.x_spin.value()
            y = self.y_spin.value()
            width = self.width_spin.value()
            height = self.height_spin.value()
            screen = self.screen_spin.value()
            self.canvas.change_app_view(self.activated_app, x, y, width, height, screen)
            size_state = self.size_stack.currentIndex()
            monitor = self.screens[screen - 1]
            self.size_stack_widgets[size_state - 1].set_monitor(monitor)
    
    def live_update_panel_from_drag(self, app, real_x, real_y, is_moved):
        if self.activated_app == app:
            screen_index = self.find_screen([real_x, real_y])
            x = int(real_x - self.screens[screen_index].x)
            y = int(real_y - self.screens[screen_index].y)
            
            if(is_moved):
                self.can_be_edited(True)
                self.size_stack.setCurrentIndex(0)
                self.size_lbl.setText(f"WINDOW STATE - {SIZE_TITLE_OPTIONS[0]}")
            
            self.x_spin.blockSignals(True)
            self.y_spin.blockSignals(True)
            self.screen_spin.blockSignals(True)
            self.screen_spin.setValue(screen_index + 1)
            self.x_spin.setValue(x)
            self.y_spin.setValue(y)
            self.x_spin.blockSignals(False)
            self.y_spin.blockSignals(False)
            self.screen_spin.blockSignals(False)
            
    def live_update_panel_from_resize(self, app, new_width, new_height):
        if self.activated_app == app:
            self.can_be_edited(True)
            self.size_stack.setCurrentIndex(0)
            self.size_lbl.setText(f"WINDOW STATE - {SIZE_TITLE_OPTIONS[0]}")
            self.width_spin.blockSignals(True)
            self.height_spin.blockSignals(True)
            self.width_spin.setValue(new_width)
            self.height_spin.setValue(new_height)
            self.width_spin.blockSignals(False)
            self.height_spin.blockSignals(False)
            
    def change_app_up(self):
        if not self.activated_app:
            if self.apps:
                if(len(self.apps) > 0):
                    self.update_info_panel(self.apps[0])
        else:
            index = 0
            app_count = len(self.apps)
            while index < app_count:
                if(self.activated_app == self.apps[index]):
                    break
                index += 1
            if(index < app_count):
                self.update_info_panel(self.apps[(index + 1) % app_count])
    
    def change_app_down(self):
        if not self.activated_app:
            if self.apps:
                if(len(self.apps) > 0):
                    self.update_info_panel(self.apps[-1])
        else:
            index = 0
            app_count = len(self.apps)
            while index < app_count:
                if(self.activated_app == self.apps[index]):
                    break
                index += 1
            if(index < app_count):
                self.update_info_panel(self.apps[(index - 1) % app_count])
                
    def handle_deleting_app(self, deleted_app):
        if not self.activated_app == deleted_app:
            info_panel_state = self.panel_stack.currentIndex()
            self.update_info_panel(deleted_app)
            if(info_panel_state == 0):
                self.toggle_info_panel()
        self.deleting_app()
                      
    def browse_for_executable(self) :
        if self.activated_app:
            path = self.activated_app.get_app_path()
            options = QFileDialog.Option.DontResolveSymlinks
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Startup App",
                f"{path}",
                "All Files (*)",
                options=options
            )
            if file_path:
                normalized_path = os.path.normpath(file_path)
                error, name = self.get_name_from_path(normalized_path)
                if(error == -1):
                    QMessageBox.warning(self, "Missing Info", "Please provide the correct path")
                else:
                    self.apps_title_label.setText(name)
                    self.app_path_input.setText(normalized_path)
    
    def browse_for_folder(self) :
        if self.activated_app:
            path = self.activated_app.get_app_path_folder()
            file_path = QFileDialog.getExistingDirectory(
                self,
                "Select Target Folder",
                f"{path}",
            )
            if file_path:
                normalized_path = os.path.normpath(file_path)
                self.app_path_input.setText(normalized_path)
                self.apps_title_label.setText(normalized_path)
    
    def saving_app(self):
        if self.activated_app:
            name = self.apps_title_label.toPlainText().lower()
            path = self.app_path_input.text().strip()
            screen = self.screen_spin.value() - 1
            x = self.x_spin.value()
            y = self.y_spin.value()
            width = self.width_spin.value()
            height = self.height_spin.value() 
            size_stack_index = self.size_stack.currentIndex()
            pos = self.calculate_pos(screen, x, y)
            if(size_stack_index == 0):
                size = Size([width, height])
            else:
                size = Size(SIZE_NANE_OPTIONS[size_stack_index - 1])
            self.activated_app.change_app(name, path, pos, size)
            self.writing_file()
        
    def deleting_app(self):
        if self.activated_app:
            index = 0
            while(index < len(self.apps)):
                if(self.apps[index] == self.activated_app):
                    break
                index += 1
            if(index < len(self.apps)):
                del self.apps[index]
                if(len(self.apps) == 0):
                    self.apps = None
            self.canvas.delete_app_view(self.activated_app)
            self.activated_app = None
            self.apps_title_label.setText("Select an App")
            self.apps_title_label.setDisabled(True)
            self.panel_stack.setCurrentIndex(0)
            self.writing_file()
    
    def create_new_app(self):
        if(not self.apps or len(self.apps) < 32):
            name = self.get_new_name()
            path = "c:\\"
            monitor = self.screens[0]
            pos = [monitor.x, monitor.y] 
            size = Size([monitor.width, monitor.height])
            new_app = App(name, path=path, pos=pos, size=size)
            if not self.apps:
                self.apps = []
            self.apps.append(new_app)
            self.canvas.add_app_view(new_app)
            self.update_info_panel(new_app)
            self.apps_title_label.setDisabled(False)
            self.panel_stack.setCurrentIndex(1)
            self.writing_file()
        else:
            QMessageBox.warning(self, "Overflow", "Too much apps getting opened\nWhen the pc is starting up")
            
                
    def get_links_list(self):
        return f"{str(self.links)}"
    
    def get_primary_screen(self):
        for monitor in self.screens:
            if(monitor.is_primary):
                return monitor
        
    def find_screen(self, pos):
        for i, monitor in enumerate(self.screens):
            x, y, width, height  = monitor.x, monitor.y, monitor.width, monitor.height
            if (pos[0] >= x and pos[0] < x + width) and (pos[1] >= y and pos[1] < y + height):
                return i
        return -1
    
    def get_name_from_path(self, path):
        path_list = path.split("\\")
        if(len(path_list) <= 1):
            return -1, self.activated_app.get_name()
        if path_list[-1]:
            file_name_list = (path_list[-1]).split(".")
            if(len(file_name_list) <= 1):
                return -1, self.activated_app.get_name()
            return 0, file_name_list[0].lower()
        return 0, "explorer"
    
    def get_max_border(self):
        min_x = self.screens[0].x
        max_x = self.screens[0].width + self.screens[0].x
        min_y = self.screens[0].y
        max_y = self.screens[0].height + self.screens[0].y
        for monitor in self.screens:
            min_x = min(min_x, monitor.x)
            min_y = min(min_y, monitor.y)
            max_x = max(max_x, monitor.x + monitor.width)
            max_y = max(max_y, monitor.y + monitor.height)         
        return max_x - min_x, max_y - min_y
    
    def add_new_link(self):
        link_name = self.link_name_input.text().strip()
        link_link = self.link_link_input.text().strip()
        if not link_name or not link_link:
            QMessageBox.warning(self, "Missing Info", "Please provide both a name and a link.")
        else:
            link = Link(link_name, link_link)
            new_block = LinkBlock(link, self.delete_link)
            self.link_list_layout.addWidget(new_block)
            self.link_name_input.clear()
            self.link_link_input.clear()
            if not self.links:
                self.links = []
            self.links.append(link)
            self.writing_file()

    def delete_link(self, block_widget):
        link_deleted = block_widget.get_link()
        self.link_list_layout.removeWidget(block_widget)
        block_widget.deleteLater()
        index = 0
        while index < len(self.links):
            if(self.links[index] == link_deleted):
                break
            index += 1
        del self.links[index]
        if(len(self.links) == 0):
            self.links = None
        self.writing_file()
    
    def add_existing_links(self):
        if self.links:
            for link in self.links:
                existing_block = LinkBlock(link, self.delete_link)
                self.link_list_layout.addWidget(existing_block)
                self.link_name_input.clear()
                self.link_link_input.clear()
    
    def get_new_name(self):
        n = 0
        if self.apps:
            while(n < len(self.apps)):
                exist = False
                for app in self.apps:
                    if(n == 0):
                        if(app.get_name() == "new_app"):
                            exist = True
                            break
                    else:
                        if(app.get_name() == f"new_app({n})"):
                            exist = True
                            break          
                if not exist:
                    break
                n += 1
        if n == 0:
            return "new_app"
        return f"new_app({n})"
    
    
    def create_header(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(HEADER_STYLE)
        return lbl

    def calculate_pos(self, screen, x, y):
        monitor = self.screens[screen]
        pos = [x + monitor.x, y + monitor.y]
        return pos

    def get_position_on_monitor(self, info, monitor):
        pos_x = 0
        pos_y = 0
        width = monitor.width
        heigth = monitor.height
        half_width = width // 2
        half_height = heigth // 2
        match info:
            case "Top":
                heigth = half_height
            case "Bottom":
                heigth = half_height
                pos_y += half_height
            case "Left":
                width = half_width
            case "Right":
                width = half_width
                pos_x += half_width
            case "Left_Top":
                width = half_width
                heigth = half_height
            case "Left_Bottom":
                width = half_width
                heigth = half_height
                pos_y += half_height
            case "Right_Top":
                width = half_width
                heigth = half_height
                pos_x += half_width
            case "Right_Bottom":
                width = half_width
                heigth = half_height
                pos_x += half_width
                pos_y += half_height
        return (pos_x), (pos_y), (width), (heigth)
    
    def can_be_edited(self, state):
        self.x_spin.setDisabled(not state)
        self.y_spin.setDisabled(not state)
        self.width_spin.setDisabled(not state)
        self.height_spin.setDisabled(not state)
    def writing_file(self):
        self.saving_file.write_file(self.apps, self.links)