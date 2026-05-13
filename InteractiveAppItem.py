from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                             QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QGraphicsRectItem, QLabel, QFrame)
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QCursor
from PyQt6.QtCore import Qt
from App import *

class InteractiveAppItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, app, z, click_callback=None):
        super().__init__(x, y, width, height)
        self.app = app
        self.click_callback = click_callback
        
        self.setAcceptHoverEvents(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.default_color = QColor("#0078d4")
        self.hover_color = QColor("#2b88d8") 
        self.selected_color = QColor("#6aaee9") 
        self.is_selected = False
        
        self.setBrush(QBrush(self.default_color))
        self.setPen(QPen(Qt.GlobalColor.white, 1))
        
        self.setZValue(z)

    def hoverEnterEvent(self, event):
        if(not self.is_selected):
            self.setBrush(QBrush(self.hover_color))
        super().hoverEnterEvent(event)
    def hoverLeaveEvent(self, event):
        if(not self.is_selected):
            self.setBrush(QBrush(self.default_color))
        super().hoverLeaveEvent(event)
        
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        click_pos = event.scenePos()
        app_under_cursor = self.scene().items(click_pos)
        front_app = app_under_cursor[0].get_app()
        if event.button() == Qt.MouseButton.LeftButton:
            if(front_app.get_name() == self.app.get_name()):
                if self.click_callback:
                    self.click_callback(self.app)
            
    def find_app_item(self, app):
        return self.app.get_name() == app.get_name()
    
    def get_app(self):
        return self.app
    
    def set_app(self, app):
        self.app = app
        
    def set_color(self, is_selected):
        self.is_selected = is_selected
        if(self.is_selected):
            self.setBrush(QBrush(self.selected_color))
        else:
            self.setBrush(QBrush(self.default_color))
            