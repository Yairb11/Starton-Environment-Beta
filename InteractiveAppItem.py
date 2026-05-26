from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                             QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QGraphicsRectItem, QLabel, QFrame, QGraphicsItem, QMenu)
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QCursor, QAction
from PyQt6.QtCore import Qt, QPointF, QRectF
from App import *

MENU_STYLE = """
            QMenu {
                background-color: #2b2b2b;
                color: #cccccc;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QMenu::item { padding: 6px 24px; }
            QMenu::item:selected { background-color: #c50f1f; color: white; }
        """
DEFAULT_COLOR = QColor("#0078d4")
HOVER_COLOR = QColor("#2b88d8")
SELECTED_COLOR = QColor("#6aaee9")  

class InteractiveAppItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, app, z, bounds, click_callback=None, pos_callback=None, size_callback=None, delete_callback=None):
        super().__init__(x, y, width, height)
        self.app = app
        self.click_callback = click_callback
        self.pos_callback = pos_callback
        self.size_callback = size_callback
        self.delete_callback = delete_callback
        self.bounds = bounds
        self.is_moved = False
        self._is_resizing = False
        self._resize_margin = 12
        
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        self.setAcceptHoverEvents(True)
        self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.is_selected = False
        
        self.setBrush(QBrush(DEFAULT_COLOR))
        self.setPen(QPen(Qt.GlobalColor.white, 1))
        
        self.setZValue(z)

    def hoverEnterEvent(self, event):
        if(not self.is_selected):
            self.setBrush(QBrush(HOVER_COLOR))
        super().hoverEnterEvent(event)
    def hoverLeaveEvent(self, event):
        if(not self.is_selected):
            self.setBrush(QBrush(DEFAULT_COLOR))
        super().hoverLeaveEvent(event)
    def hoverMoveEvent(self, event):
        rect = self.rect()
        if (rect.right() - self._resize_margin <= event.pos().x() <= rect.right() and rect.bottom() - self._resize_margin <= event.pos().y() <= rect.bottom()):
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))  
        super().hoverMoveEvent(event)    
        
    def mouseReleaseEvent(self, event):
        self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        if self._is_resizing:
            self._is_resizing = False
        else:
            current_rect = self.rect()
            offset = self.pos()
            new_x = current_rect.x() + offset.x()
            new_y = current_rect.y() + offset.y()
            self.setRect(new_x, new_y, current_rect.width(), current_rect.height())
            self.setPos(0, 0)
            if self.pos_callback:
                self.pos_callback(self.app, new_x, new_y, self.is_moved)
            self.is_moved = False
            super().mouseReleaseEvent(event) 
    
    def mousePressEvent(self, event):
        self.is_moved = False
        click_pos = event.scenePos()
        app_under_cursor = self.scene().items(click_pos)
        smallest_index = 0
        while(smallest_index < len(app_under_cursor)):
            if(str(type(app_under_cursor[smallest_index])) == "<class \'InteractiveAppItem.InteractiveAppItem\'>"):
                break
            smallest_index += 1
        if(smallest_index < len(app_under_cursor)):
            front_app = app_under_cursor[smallest_index].get_app()
            if event.button() == Qt.MouseButton.LeftButton and front_app.get_name() == self.app.get_name():
                rect = self.rect()
                if (rect.right() - self._resize_margin <= event.pos().x() <= rect.right() and rect.bottom() - self._resize_margin <= event.pos().y() <= rect.bottom()):
                    self._is_resizing = True
                else:
                    self._is_resizing = False
                    self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                    self.setBrush(QBrush(QColor(SELECTED_COLOR)))
                    super().mousePressEvent(event)
                if self.click_callback:
                    self.click_callback(self.app)
                       
    def mouseMoveEvent(self, event):
        if self._is_resizing:
            rect = self.rect()
            new_width =  min(max(event.pos().x() - rect.x(), self._resize_margin + 8), self.bounds[1] - rect.x())
            new_height = min(max(event.pos().y() - rect.y(), self._resize_margin + 8), self.bounds[3] - rect.y())
            self.setRect(rect.x(), rect.y(), new_width, new_height)
            if self.size_callback:
                self.size_callback(self.app, new_width, new_height)
        else:
            super().mouseMoveEvent(event)
            
    def contextMenuEvent(self, event):
        context_menu = QMenu()
        context_menu.setStyleSheet(MENU_STYLE)
        delete_action = QAction("🗑️ Delete App", context_menu)
        delete_action.triggered.connect(self.execute_delete)
        context_menu.addAction(delete_action)
        context_menu.exec(event.screenPos())
        event.accept()

    def execute_delete(self):
        if self.delete_callback:
            self.delete_callback(self.app)
            
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
                distance = (clamped_x**2 + clamped_y**2)**0.5
                self.is_moved = self.is_moved or distance < 10
                if self.pos_callback:
                    self.pos_callback(self.app, (rect.x() + clamped_x), (rect.y() + clamped_y), self.is_moved)
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
            self.setBrush(QBrush(SELECTED_COLOR))
        else:
            self.setBrush(QBrush(DEFAULT_COLOR))
            