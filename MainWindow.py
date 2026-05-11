from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
                            QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                            QLabel, QFrame, QLineEdit, QTextEdit, QPushButton, QMessageBox, QSpinBox, QGridLayout)
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QCursor
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import Qt
from App import *
from MonitorCanvas import *
from Link import *
from LinkBlock import *
import os

SPINBOX_STYLE = """
    QSpinBox { background-color: #333333; color: white; border: 1px solid #555; padding: 4px; font-size: 13px; }
    QSpinBox::up-button, QSpinBox::down-button { background-color: #444; width: 16px; }
"""
LBL_STYLE = "color: #cccccc; font-size: 13px; font-weight: bold;"
BROWSE_BTN_STYLE = """
    QPushButton {
        background-color: #0078d4; color: white; border: none; font-size: 14px; border-radius: 2px;
    }
    QPushButton:hover {
        background-color: #2b88d8;
    }
""" 
PATH_INPUT_STYLE = "background-color: #333333; color: white; border: 1px solid #555; padding: 5px;"
TITLE_STYLE = "color: white; font-size: 25px; font-weight: bold; margin-left: auto;"
INFO_PANEL_STYLE = "background-color: #252526;"
LINK_ADD_STYLE = "background-color: #333; color: white; border: 1px solid #555; padding: 4px;"
LINK_ADD_BTN_STYLE = "QPushButton { background-color: #0078d4; color: white; border: none; border-radius: 2px; } QPushButton:hover { background-color: #2b88d8; }"
LINK_SCROLL_STYLE = """
    QScrollArea { border: 1px solid #444; background-color: #1e1e1e; }
    QScrollBar:vertical { background: #252526; width: 10px; }
    QScrollBar::handle:vertical { background: #555; min-height: 20px; border-radius: 5px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""
LINK_CONTAINER_STYLE = "background-color: #1e1e1e;"
HEADER_STYLE = "color: #aaaaaa; font-size: 15px; font-weight: bold; margin-top: 8px;"

class MainWindow(QMainWindow):
    def __init__(self, screens, apps, links):
        super().__init__()
        self.screens = screens
        self.apps = apps
        self.links = links
        
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
        self.canvas = MonitorCanvas(self.screens, self.apps, self.update_info_panel)
        main_layout.addWidget(self.canvas, stretch=3)
        self.info_panel = QFrame()
        self.info_panel.setStyleSheet(INFO_PANEL_STYLE)
        self.info_panel.setFixedWidth(500)
        panel_layout = QVBoxLayout(self.info_panel)
        panel_layout.setContentsMargins(15, 20, 15, 20)
        panel_layout.setSpacing(8)
        
        # --- TITLE ---
        self.title_label = QLabel("Select an App")
        self.title_label.setStyleSheet(TITLE_STYLE)
        
        # --- POSITION ---
        pos_layout = QGridLayout()
        pos_layout.setSpacing(10)
        self.screen_spin = QSpinBox()
        self.screen_spin.setRange(1, len(self.screens)) 
        self.screen_spin.setStyleSheet(SPINBOX_STYLE)
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 0) 
        self.x_spin.setStyleSheet(SPINBOX_STYLE)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 0)
        self.y_spin.setStyleSheet(SPINBOX_STYLE)
        screen_lbl = QLabel("Screen:")
        screen_lbl.setStyleSheet(LBL_STYLE)
        x_lbl = QLabel("X Position:")
        x_lbl.setStyleSheet(LBL_STYLE)
        y_lbl = QLabel("Y Position:")
        y_lbl.setStyleSheet(LBL_STYLE)
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
        self.height_spin = QSpinBox()
        self.height_spin.setRange(0, max_height)
        self.height_spin.setStyleSheet(SPINBOX_STYLE)
        width_lbl = QLabel("Width:")
        width_lbl.setStyleSheet(LBL_STYLE)
        height_lbl = QLabel("Height:")
        height_lbl.setStyleSheet(LBL_STYLE)
        size_layout.addWidget(width_lbl, 0, 0)
        size_layout.addWidget(self.width_spin, 0, 1)
        size_layout.addWidget(height_lbl, 1, 0)
        size_layout.addWidget(self.height_spin, 1, 1)
        
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
        
        # --- APP PATH ---
        self.app_path_input = QLineEdit()
        self.app_path_input.setPlaceholderText("APP OPEN PATH (e.g., C:\\...)")
        self.app_path_input.setStyleSheet(PATH_INPUT_STYLE)   
        self.browse_app_path_btn = QPushButton("📂")
        self.browse_app_path_btn.setToolTip("Browse for Executable")
        self.browse_app_path_btn.setFixedSize(28, 28)
        self.browse_app_path_btn.setStyleSheet(BROWSE_BTN_STYLE)
        self.browse_app_path_btn.clicked.connect(lambda: self.browse_for_executable(self.title_label.text())) 
        app_path_layout = QHBoxLayout()
        app_path_layout.setSpacing(5)
        app_path_layout.addWidget(self.app_path_input)
        app_path_layout.addWidget(self.browse_app_path_btn)
        
        # --- DIR PATH ---
        self.dir_path_input = QLineEdit()
        self.dir_path_input.setPlaceholderText("FROM FOLDER PATH (e.g., C:\\...)")
        self.dir_path_input.setStyleSheet(PATH_INPUT_STYLE) 
        self.browse_dir_path_btn = QPushButton("📂")
        self.browse_dir_path_btn.setToolTip("Browse for Executable")
        self.browse_dir_path_btn.setFixedSize(28, 28)
        self.browse_dir_path_btn.setStyleSheet(BROWSE_BTN_STYLE)
        self.browse_dir_path_btn.clicked.connect(lambda: self.browse_for_folder(self.title_label.text()))         
        dir_path_layout = QHBoxLayout()
        dir_path_layout.setSpacing(5)
        dir_path_layout.addWidget(self.dir_path_input)
        dir_path_layout.addWidget(self.browse_dir_path_btn)
        
        # --- LAYOUT ---
        panel_layout.addWidget(self.title_label)
        panel_layout.addWidget(self.create_header("APP PATH"))
        panel_layout.addLayout(app_path_layout)
        panel_layout.addWidget(self.create_header("FOLDER PATH"))
        panel_layout.addLayout(dir_path_layout)
        panel_layout.addWidget(self.create_header("POSITION"))
        panel_layout.addLayout(pos_layout)
        panel_layout.addWidget(self.create_header("WINDOW STATE"))
        panel_layout.addLayout(size_layout) 
        panel_layout.addWidget(self.create_header("START UP LINKS"))
        panel_layout.addLayout(add_link_layout)
        panel_layout.addWidget(self.link_scroll_area, stretch=1)
        panel_layout.addStretch()
        main_layout.addWidget(self.info_panel, stretch=1)
        

    def update_info_panel(self, app): 
        pos = app.get_pos()
        screen_index = self.find_screen(pos)
        screen = self.screens[screen_index] 
        pos = [(pos[0] - screen.x), (pos[1] - screen.y)]
        self.screen_spin.setValue(screen_index + 1)
        self.x_spin.setValue(pos[0])
        self.x_spin.setRange(0, screen.width)
        self.y_spin.setValue(pos[1])
        self.y_spin.setRange(0, screen.height)
        
        size = app.get_size()
        if size:
            self.width_spin.setValue(size[0])
            self.height_spin.setValue(size[1])
        else:
            self.width_spin.setValue(screen.width)
            self.height_spin.setValue(screen.height)
        
        self.title_label.setText(f"{app.get_name()}") 
        self.app_path_input.setText(f"{app.get_app_path()}")
        self.dir_path_input.setText(f"{app.get_dir_path()}")
        
                    
    def browse_for_executable(self, app_name) :
        if app_name != "Select an App":
            app = self.find_app(app_name)
            path = app.get_app_path()
            
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
                self.app_path_input.setText(normalized_path)
    
    def browse_for_folder(self, app_name) :
        if app_name != "Select an App":
            app = self.find_app(app_name)
            path = app.get_dir_path()
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
                
        
    def find_app(self, app_name):
        for app in self.apps:
            if app.get_name() == app_name:
                return app
        return None
        
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
    
    def get_max_border(self):
        min_x = self.screens[0].x
        max_x = self.screens[0].width + self.screens[0].x
        min_y = self.screens[0].y
        max_y = self.screens[0].height + self.screens[0].y
        for monitor in self.screens:
            min_x = min(min_x, monitor.x)
            min_y = min(min_y, monitor.y)
            max_x = min(max_x, monitor.x + monitor.width)
            max_y = min(max_y, monitor.y + monitor.height)         
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
    
    def add_existing_links(self):
        for link in self.links:
            existing_block = LinkBlock(link, self.delete_link)
            self.link_list_layout.addWidget(existing_block)
            self.link_name_input.clear()
            self.link_link_input.clear()

    def delete_link(self, block_widget):
        self.link_list_layout.removeWidget(block_widget)
        block_widget.deleteLater()
    
    def create_header(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(HEADER_STYLE)
        return lbl