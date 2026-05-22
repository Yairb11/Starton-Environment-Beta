from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                             QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QGraphicsRectItem, QLabel, QFrame, QGraphicsItem)
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QCursor
from PyQt6.QtCore import Qt, QPointF, QRectF
from App import *

class InteractiveAppItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, app, z, bounds, click_callback=None, pos_callback=None):
        super().__init__(x, y, width, height)
        self.app = app
        self.click_callback = click_callback
        self.pos_callback = pos_callback
        self.bounds = bounds
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        self.setAcceptHoverEvents(True)
        self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        
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
        self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        super().mouseReleaseEvent(event)
        
        current_rect = self.rect()
        offset = self.pos()
        new_x = current_rect.x() + offset.x()
        new_y = current_rect.y() + offset.y()
        self.setRect(new_x, new_y, current_rect.width(), current_rect.height())
        self.setPos(0, 0)
        if self.pos_callback:
            self.pos_callback(self.app, new_x, new_y)
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        click_pos = event.scenePos()
        app_under_cursor = self.scene().items(click_pos)
        smallest_index = 0
        while(smallest_index < len(app_under_cursor)):
            if(str(type(app_under_cursor[smallest_index])) == "<class \'InteractiveAppItem.InteractiveAppItem\'>"):
                break
            smallest_index += 1
        if(smallest_index < len(app_under_cursor)):
            front_app = app_under_cursor[smallest_index].get_app()
            if event.button() == Qt.MouseButton.LeftButton:
                if(front_app.get_name() == self.app.get_name()):
                    self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                    self.setBrush(QBrush(QColor("#005a9e")))
                    if self.click_callback:
                        self.click_callback(self.app)
            
    def itemChange(self, change, value):
            if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.bounds:
                new_pos = value 
                rect = self.rect()
                min_x = self.bounds[0] - rect.x()
                max_x = self.bounds[1] - (rect.x() + rect.width())
                min_y = self.bounds[2] - rect.y()
                max_y = self.bounds[3] - (rect.y() + rect.height())
                clamped_x = max(min_x, min(new_pos.x(), max_x))
                clamped_y = max(min_y, min(new_pos.y(), max_y))
                
                if self.pos_callback:
                    self.pos_callback(self.app, (rect.x() + clamped_x), (rect.y() + clamped_y))
                
                return QPointF(clamped_x, clamped_y)
                
            return super().itemChange(change, value)
    
    def find_app_item(self, app):
        return self.app == app
    
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
            