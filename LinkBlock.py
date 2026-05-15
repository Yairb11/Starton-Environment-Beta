from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                             QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QLabel, QFrame, QLineEdit, QPushButton, QSpinBox, 
                             QGridLayout, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt

LINK_LINK_HTML_STYLE = "color: #0078d4; text-decoration: none;"
LINK_LINK_STYLE = "font-size: 11px; border: none;"
LINK_NAME_STYLE = "color: white; font-weight: bold; font-size: 13px; border: none;"
LINK_FRAME_STYLE = """
            QFrame { background-color: #333333; border-radius: 4px; border: 1px solid #444; }
        """
LINK_DELETE_STYLE = """
            QPushButton { background-color: transparent; border: none; font-size: 14px; }
            QPushButton:hover { background-color: #cc0000; border-radius: 4px; }
        """

class LinkBlock(QFrame):
    def __init__(self, link, delete_callback):
        # --- FRAME LINK --- 
        super().__init__()
        self.link = link
        self.setStyleSheet(LINK_FRAME_STYLE)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        name_lbl = QLabel(link.get_name())
        name_lbl.setStyleSheet(LINK_NAME_STYLE)
        link_lbl = QLabel(f'<a href="{self.link.get_link()}" style="{LINK_LINK_HTML_STYLE}">{self.link.get_link()}</a>')
        link_lbl.setOpenExternalLinks(True)
        link_lbl.setStyleSheet(LINK_LINK_STYLE)
        text_layout.addWidget(name_lbl)
        text_layout.addWidget(link_lbl)

        # --- DELETE BTN --
        self.del_btn = QPushButton("🗑️")
        self.del_btn.setFixedSize(28, 28)
        self.del_btn.setToolTip("Delete URL")
        self.del_btn.setStyleSheet(LINK_DELETE_STYLE)
        self.del_btn.clicked.connect(lambda: delete_callback(self))

        # --- LAYOUT ---
        layout.addLayout(text_layout)
        layout.addWidget(self.del_btn)
    
    def get_link(self):
        return self.link