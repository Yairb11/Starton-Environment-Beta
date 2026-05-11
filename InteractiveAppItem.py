from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                             QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QGraphicsRectItem, QLabel, QFrame)
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QCursor
from PyQt6.QtCore import Qt
from App import *

class InteractiveAppItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, app, click_callback=None):
        super().__init__(x, y, width, height)
        self.app = app
        self.click_callback = click_callback
        
        self.setAcceptHoverEvents(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.default_color = QColor("#0078d4")
        self.hover_color = QColor("#2b88d8") 
        
        self.setBrush(QBrush(self.default_color))
        self.setPen(QPen(Qt.GlobalColor.white, 1))


    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(self.hover_color))
        super().hoverEnterEvent(event)
    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(self.default_color))
        super().hoverLeaveEvent(event)
        
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.click_callback:
                self.click_callback(self.app)
                
        super().mousePressEvent(event)
