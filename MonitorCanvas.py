from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                             QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QGraphicsRectItem, QLabel, QFrame)
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QCursor
from PyQt6.QtCore import Qt
from App import *
from InteractiveAppItem import *

class MonitorCanvas(QGraphicsView):
    def __init__(self, screens, apps, update_panel_callback):
        super().__init__()
        self.screens = screens
        self.apps = apps
        self.app_type = type(InteractiveAppItem(0, 0, 0, 0, App(""), 0))
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.x_cor, self.y_cor = self.get_correction()
        self.down_by = 5
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setStyleSheet("background-color: #1e1e1e; border: none;")
        
        for monitor in self.screens: 
            monitor_view = QGraphicsRectItem((monitor.x - self.x_cor)//self.down_by, (monitor.y - self.y_cor)//self.down_by, (monitor.width)//self.down_by, (monitor.height)//self.down_by) 
            monitor_view.setBrush(QBrush(QColor("#333333")))
            monitor_view.setPen(QPen(QColor("#555555"), 5))
            self.scene.addItem(monitor_view)
            
        for z, app in enumerate(self.apps): 
            size = app.get_size()
            pos = app.get_pos()
            if(size):
                app_view = InteractiveAppItem((pos[0] - self.x_cor) // self.down_by, (pos[1] - self.y_cor) // self.down_by, size[0] // self.down_by, size[1] // self.down_by, app, z, update_panel_callback)
            else: 
                screen_index = self.find_screen(pos)
                monitor = self.screens[screen_index]
                app_view = InteractiveAppItem((monitor.x - self.x_cor)//self.down_by, (monitor.y - self.y_cor)//self.down_by, (monitor.width)//self.down_by, (monitor.height)//self.down_by, app, z, update_panel_callback)
                
            self.scene.addItem(app_view)
        
        
        
    def reset_app_view(self):  
        for z, view in enumerate(self.scene.items()):
            if(type(view) == self.app_type):
                app = view.get_app()
                size = app.get_size()
                pos = app.get_pos()
                view.setZValue(z)
                if(size):
                    view.setRect((pos[0] - self.x_cor) // self.down_by, (pos[1] - self.y_cor) // self.down_by, size[0] // self.down_by, size[1] // self.down_by)
                else: 
                    screen_index = self.find_screen(pos)
                    monitor = self.screens[screen_index]
                    view.setRect((monitor.x - self.x_cor) // self.down_by, (monitor.y - self.y_cor) // self.down_by, (monitor.width) // self.down_by, (monitor.height) // self.down_by)
                

    
    def get_correction(self):
        x_cor, y_cor = 0, 0
        for monitor in self.screens:
            x_cor = min(x_cor, monitor.x)
            y_cor = min(y_cor, monitor.y)
        return x_cor, y_cor

    def find_screen(self, pos):
        for i, monitor in enumerate(self.screens):
            x, y, width, height  = monitor.x, monitor.y, monitor.width, monitor.height
            if (pos[0] >= x and pos[0] < x + width) and (pos[1] >= y and pos[1] < y + height):
                return i
        return -1
    
    def change_app_view(self, app, x, y, width, height, screen):
        monitor = self.screens[screen - 1]
        set_x = (x + monitor.x - self.x_cor) // self.down_by
        set_y = (y + monitor.y - self.y_cor) // self.down_by
        set_width = width // self.down_by
        set_height = height // self.down_by
        
        for z, view in enumerate(self.scene.items()):
            if(type(view) == self.app_type):
                if(view.find_app_item(app)):
                    view.setRect(set_x, set_y, set_width, set_height)
                    view.setZValue(len(self.scene.items()))
                else:
                    view.setZValue(z)
                
            
