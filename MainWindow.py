from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
                            QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                            QLabel, QFrame, QLineEdit, QTextEdit, QPushButton, QMessageBox, QSpinBox, QGridLayout)
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QCursor
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtCore import Qt
from App import *
from MonitorCanvas import *
from Links import *
import os


class MainWindow(QMainWindow):
    def __init__(self, screens, apps, links):
        def create_header(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #aaaaaa; font-size: 15px; font-weight: bold; margin-top: 8px;")
            return lbl
        super().__init__()
        self.screens = screens
        self.apps = apps
        self.links = links
        spinbox_style = """
            QSpinBox { background-color: #333333; color: white; border: 1px solid #555; padding: 4px; font-size: 13px; }
            QSpinBox::up-button, QSpinBox::down-button { background-color: #444; width: 16px; }
        """
        lbl_style = "color: #cccccc; font-size: 13px; font-weight: bold;"
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
        self.info_panel.setStyleSheet("background-color: #252526;")
        self.info_panel.setFixedWidth(300)
        panel_layout = QVBoxLayout(self.info_panel)
        panel_layout.setContentsMargins(15, 20, 15, 20)
        panel_layout.setSpacing(8)
        
        # --- TITLE ---
        self.title_label = QLabel("Select an App")
        self.title_label.setStyleSheet("color: white; font-size: 25px; font-weight: bold; margin-left: auto;")
        
        # --- POSITION ---
        pos_layout = QGridLayout()
        pos_layout.setSpacing(10)
        self.screen_spin = QSpinBox()
        self.screen_spin.setRange(1, len(self.screens)) 
        self.screen_spin.setStyleSheet(spinbox_style)
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 0) 
        self.x_spin.setStyleSheet(spinbox_style)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 0)
        self.y_spin.setStyleSheet(spinbox_style)
        lbl_style = "color: #cccccc; font-size: 13px; font-weight: bold;"
        screen_lbl = QLabel("Screen:")
        screen_lbl.setStyleSheet(lbl_style)
        x_lbl = QLabel("X Position:")
        x_lbl.setStyleSheet(lbl_style)
        y_lbl = QLabel("Y Position:")
        y_lbl.setStyleSheet(lbl_style)
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
        self.width_spin.setStyleSheet(spinbox_style)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(0, max_height)
        self.height_spin.setStyleSheet(spinbox_style)
        width_lbl = QLabel("Width:")
        width_lbl.setStyleSheet(lbl_style)
        height_lbl = QLabel("Height:")
        height_lbl.setStyleSheet(lbl_style)
        size_layout.addWidget(width_lbl, 0, 0)
        size_layout.addWidget(self.width_spin, 0, 1)
        size_layout.addWidget(height_lbl, 1, 0)
        size_layout.addWidget(self.height_spin, 1, 1)
        
        # --- LINKS ---
        self.links_label = QLabel("")
        self.links_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold; margin-left: auto;")
        
        # --- APP PATH ---
        self.app_path_input = QLineEdit()
        self.app_path_input.setPlaceholderText("APP OPEN PATH (e.g., C:\\...)")
        self.app_path_input.setStyleSheet("background-color: #333333; color: white; border: 1px solid #555; padding: 5px;")   
        self.browse_app_path_btn = QPushButton("📂")
        self.browse_app_path_btn.setToolTip("Browse for Executable")
        self.browse_app_path_btn.setFixedSize(28, 28)
        self.browse_app_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4; color: white; border: none; font-size: 14px; border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #2b88d8;
            }
        """)
        self.browse_app_path_btn.clicked.connect(lambda: self.browse_for_executable(self.title_label.text())) 
        app_path_layout = QHBoxLayout()
        app_path_layout.setSpacing(5)
        app_path_layout.addWidget(self.app_path_input)
        app_path_layout.addWidget(self.browse_app_path_btn)
        
        # --- DIR PATH ---
        self.dir_path_input = QLineEdit()
        self.dir_path_input.setPlaceholderText("FROM FOLDER PATH (e.g., C:\\...)")
        self.dir_path_input.setStyleSheet("background-color: #333333; color: white; border: 1px solid #555; padding: 5px;") 
        self.browse_dir_path_btn = QPushButton("📂")
        self.browse_dir_path_btn.setToolTip("Browse for Executable")
        self.browse_dir_path_btn.setFixedSize(28, 28)
        self.browse_dir_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4; color: white; border: none; font-size: 14px; border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #2b88d8;
            }
        """)
        self.browse_dir_path_btn.clicked.connect(lambda: self.browse_for_folder(self.title_label.text()))         
        dir_path_layout = QHBoxLayout()
        dir_path_layout.setSpacing(5)
        dir_path_layout.addWidget(self.dir_path_input)
        dir_path_layout.addWidget(self.browse_dir_path_btn)
        
        # --- LAYOUT ---
        panel_layout.addWidget(self.title_label)
        panel_layout.addWidget(create_header("APP PATH"))
        panel_layout.addLayout(app_path_layout)
        panel_layout.addWidget(create_header("FOLDER PATH"))
        panel_layout.addLayout(dir_path_layout)
        panel_layout.addWidget(create_header("POSITION"))
        panel_layout.addLayout(pos_layout)
        panel_layout.addWidget(create_header("WINDOW STATE"))
        panel_layout.addLayout(size_layout)
        panel_layout.addWidget(create_header("LINKS"))
        panel_layout.addWidget(self.links_label)
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
        
        if(app.get_name() != self.links.get_default_browser()) or (self.links.is_empty()):
            self.links_label.setText("")
        else:
            self.links_label.setText(f"{self.get_links_list()}")

                    
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