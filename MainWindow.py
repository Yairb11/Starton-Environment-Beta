from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
                            QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QCheckBox,
                            QLabel, QFrame, QLineEdit, QTextEdit, QPushButton, QMessageBox, 
                            QSpinBox, QGridLayout, QFileDialog, QStackedWidget)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint
from PyQt6.QtWidgets import QFileDialog
from App import *
from MonitorCanvas import *
from Link import *
from LinkBlock import *
from SavingFile import *
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
        self.setWindowTitle("SetupGUI")
        primary_screen = self.get_primary_screen()
        self.resize(primary_screen.width, primary_screen.height)
        self.showMaximized()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- CANVAS ---
        self.canvas = MonitorCanvas(self.screens, self.apps, self.update_info_panel, self.live_update_panel_from_drag)
        main_layout.addWidget(self.canvas, stretch=3)
        self.info_panel = QFrame()
        self.info_panel.setStyleSheet(INFO_PANEL_STYLE)
        self.info_panel.setMaximumWidth(MAX_INFO_PANEL_WIDTH) 
        self.info_panel.setMinimumWidth(0)
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
        self.app_path_input = QLineEdit()
        self.app_path_input.setPlaceholderText("APP OPEN PATH (e.g., C:\\...)")
        self.app_path_input.setStyleSheet(PATH_INPUT_STYLE)   
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
        
        # --- DIR PATH ---
        self.dir_path_input = QLineEdit()
        self.dir_path_input.setPlaceholderText("FROM FOLDER PATH (e.g., C:\\...)")
        self.dir_path_input.setStyleSheet(PATH_INPUT_STYLE) 
        self.browse_dir_path_btn = QPushButton("📂")
        self.browse_dir_path_btn.setToolTip("Browse for Executable")
        self.browse_dir_path_btn.setFixedSize(28, 28)
        self.browse_dir_path_btn.setStyleSheet(BROWSE_BTN_STYLE)
        self.browse_dir_path_btn.clicked.connect(self.browse_for_folder)      
        self.disable_dir_path = QCheckBox("None")
        self.disable_dir_path.setStyleSheet(CHECK_STYLE)
        self.disable_dir_path.toggled.connect(self.handle_dir_disable)
        dir_lbl = self.create_header("FOLDER PATH")
        dir_path_layout = QHBoxLayout()
        dir_path_layout.setSpacing(5)
        dir_path_layout.addWidget(self.dir_path_input)
        dir_path_layout.addWidget(self.browse_dir_path_btn)
        dir_path_layout.addWidget(self.disable_dir_path)
        
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
        size_layout = QGridLayout()
        size_layout.setSpacing(10)
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
        size_lbl = self.create_header("WINDOW STATE")
        self.full_screen = QCheckBox("Full Screen")
        self.full_screen.setStyleSheet(CHECK_STYLE)
        self.full_screen.toggled.connect(self.handle_full_screen)
        size_layout.addWidget(width_lbl, 0, 0)
        size_layout.addWidget(self.width_spin, 0, 1)
        size_layout.addWidget(self.full_screen, 0, 5)
        size_layout.addWidget(height_lbl, 1, 0)
        size_layout.addWidget(self.height_spin, 1, 1)
        
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
        editor_layout.addWidget(dir_lbl)
        editor_layout.addLayout(dir_path_layout)
        editor_layout.addWidget(position_lbl)
        editor_layout.addLayout(pos_layout)
        editor_layout.addWidget(size_lbl)
        editor_layout.addLayout(size_layout) 
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
        if not(self.activated_app) or self.activated_app.get_name() != app.get_name():
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
            
            size = app.get_size()
            if size:
                self.full_screen.setChecked(False)
                self.width_spin.setValue(size[0])
                self.height_spin.setValue(size[1])
            else:
                self.full_screen.setChecked(True)
                self.width_spin.setValue(screen.width)
                self.height_spin.setValue(screen.height)
            
            self.apps_title_label.setText(f"{app.get_name()}") 
            self.app_path_input.setText(f"{app.get_app_path()}")
            
            if(app.get_dir_path()):
                self.disable_dir_path.setChecked(False)
                self.dir_path_input.setText(f"{app.get_dir_path()}")
            else:
                self.disable_dir_path.setChecked(True)
            if(not self.is_panel_open):
                self.toggle_info_panel()
                
    def live_update_canvas(self):
        if self.activated_app: 
            x = self.x_spin.value()
            y = self.y_spin.value()
            width = self.width_spin.value()
            height = self.height_spin.value()
            screen = self.screen_spin.value()
            self.canvas.change_app_view(self.activated_app, x, y, width, height, screen)
    
    def live_update_panel_from_drag(self, app, real_x, real_y):
        if self.activated_app == app:
            screen_index = self.find_screen([real_x, real_y])
            x = int(real_x - self.screens[screen_index].x)
            y = int(real_y - self.screens[screen_index].y)
            
            self.x_spin.blockSignals(True)
            self.y_spin.blockSignals(True)
            self.screen_spin.blockSignals(True)
            self.screen_spin.setValue(screen_index + 1)
            self.x_spin.setValue(x)
            self.y_spin.setValue(y)
            self.x_spin.blockSignals(False)
            self.y_spin.blockSignals(False)
            self.screen_spin.blockSignals(False)
            
    
    def change_app_up(self):
        if not self.activated_app:
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
        
    
    def handle_full_screen(self, checked):
        if self.activated_app:
            self.width_spin.setDisabled(checked)
            self.height_spin.setDisabled(checked)
            self.x_spin.setDisabled(checked)
            self.y_spin.setDisabled(checked)
            screen = self.screen_spin.value()
            monitor = self.screens[screen - 1]
            if checked:
                self.width_spin.setValue(monitor.width)
                self.height_spin.setValue(monitor.height)
                self.x_spin.setValue(0)
                self.y_spin.setValue(0)
                self.canvas.change_app_view(self.activated_app, 0, 0, monitor.width, monitor.height, screen)
            else:
                pos = self.activated_app.get_pos()
                pos = [(pos[0] - monitor.x), (pos[1] - monitor.y)]
                self.x_spin.setValue(pos[0])
                self.x_spin.setRange(0, monitor.width)
                self.y_spin.setValue(pos[1])
                self.y_spin.setRange(0, monitor.height)
                size = self.activated_app.get_size()
                if size:
                    self.width_spin.setValue(size[0])
                    self.height_spin.setValue(size[1])
                else:
                    self.width_spin.setValue(monitor.width)
                    self.height_spin.setValue(monitor.height)
        
    def handle_dir_disable(self, checked):
        if self.activated_app:
            self.dir_path_input.setDisabled(checked)
            self.browse_dir_path_btn.setDisabled(checked)
            if checked:
                self.dir_path_input.setText("None")
            else:
                if(self.activated_app.get_dir_path()):
                    self.dir_path_input.setText(self.activated_app.get_dir_path())
                else:
                    self.dir_path_input.setText("C:\\")
                      
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
            path = self.activated_app.get_dir_path()
            if not(path):
                path = r"C:\\"
            
            file_path = QFileDialog.getExistingDirectory(
                self,
                "Select Target Folder",
                f"{path}",
            )
            if file_path:
                normalized_path = os.path.normpath(file_path)
                self.dir_path_input.setText(normalized_path)
    
    def saving_app(self):
        if self.activated_app:
            name = self.apps_title_label.toPlainText().lower()
            path = self.app_path_input.text().strip()
            dir = self.dir_path_input.text().strip()
            screen = self.screen_spin.value() - 1
            x = self.x_spin.value()
            y = self.y_spin.value()
            width = self.width_spin.value()
            height = self.height_spin.value() 
            if not path or not dir:
                QMessageBox.warning(self, "Missing Info", "Please provide all app information")
            if dir == "None":
                dir = None
            pos = self.calculate_pos(screen, x, y)
            size = [width, height]
            self.activated_app.change_app(name, path, dir, pos, size)
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
            self.canvas.delete_app_view(self.activated_app)
            self.activated_app = None
            self.apps_title_label.setText("Select an App")
            self.apps_title_label.setDisabled(True)
            self.panel_stack.setCurrentIndex(0)
            self.writing_file()
    
    def create_new_app(self):
        if(len(self.apps) < 32):
            name = self.get_new_name()
            path = "c:\\"
            dir = None
            monitor = self.screens[0]
            pos = [monitor.x, monitor.y] 
            size = [monitor.width, monitor.height]
            new_app = App(name, path=path, dir=dir, pos=pos, size=size)
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
        self.writing_file()
    
    def add_existing_links(self):
        for link in self.links:
            existing_block = LinkBlock(link, self.delete_link)
            self.link_list_layout.addWidget(existing_block)
            self.link_name_input.clear()
            self.link_link_input.clear()
    
    def get_new_name(self):
        n = 0
        while(n < len(self.apps)):
            exist = False
            for app in self.apps:
                if(n == 0):
                    if(app.get_name() == "new app"):
                        exist = True
                        break
                else:
                    if(app.get_name() == f"new app({n})"):
                        exist = True
                        break          
            if not exist:
                break
            n += 1
        if n == 0:
            return "new app"
        return f"new app({n})"
    
    
    def create_header(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(HEADER_STYLE)
        return lbl

    def calculate_pos(self, screen, x, y):
        monitor = self.screens[screen]
        pos = [x + monitor.x, y + monitor.y]
        return pos
    
    def writing_file(self):
        if False:
            self.saving_file.write_file(self.apps, self.links)