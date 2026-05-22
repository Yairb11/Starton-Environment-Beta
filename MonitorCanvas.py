from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                             QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QGraphicsRectItem, QLabel, QFrame)
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QCursor
from PyQt6.QtCore import Qt
from App import *
from InteractiveAppItem import *

class MonitorCanvas(QGraphicsView):
    def __init__(self, screens, apps, update_panel_callback, drag_callback):
        super().__init__()
        self.screens = screens
        self.apps = apps
        self.update_panel_callback = update_panel_callback
        self.drag_callback = drag_callback
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.down_by = 5
        self.x_min, self.y_min, self.total_screen_area = self.get_bounds()
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setStyleSheet("background-color: #1e1e1e; border: none;")
        
        for monitor in self.screens: 
            monitor_view = QGraphicsRectItem((monitor.x - self.x_min)//self.down_by, (monitor.y - self.y_min)//self.down_by, (monitor.width)//self.down_by, (monitor.height)//self.down_by) 
            monitor_view.setBrush(QBrush(QColor("#333333")))
            monitor_view.setPen(QPen(QColor("#555555"), 5))
            self.scene.addItem(monitor_view)
        
        num_apps = len(self.apps)
        for z, app in enumerate(self.apps): 
            size = app.get_size()
            pos = app.get_pos()
            if(size):
                app_view = InteractiveAppItem((pos[0] - self.x_min) // self.down_by, (pos[1] - self.y_min) // self.down_by, size[0] // self.down_by, size[1] // self.down_by, app, num_apps - z, self.total_screen_area, click_callback=self.update_panel_callback , pos_callback=self.pos_callback)
            else: 
                screen_index = self.find_screen(pos)
                monitor = self.screens[screen_index]
                app_view = InteractiveAppItem((monitor.x - self.x_min)//self.down_by, (monitor.y - self.y_min)//self.down_by, (monitor.width)//self.down_by, (monitor.height)//self.down_by, app, num_apps - z, self.total_screen_area, click_callback=self.update_panel_callback, pos_callback=self.pos_callback)
            self.scene.addItem(app_view)
        
    def reset_app_view(self, app_selected):  
        max_items = len(self.scene.items())
        for z, view in enumerate(self.scene.items()):
            if(str(type(view)) == "<class \'InteractiveAppItem.InteractiveAppItem\'>"):
                app = view.get_app() 
                size = app.get_size()
                pos = app.get_pos()
                view.setZValue(max_items - z)

                    
                if(size):
                    view.setRect((pos[0] - self.x_min) // self.down_by, (pos[1] - self.y_min) // self.down_by, size[0] // self.down_by, size[1] // self.down_by)
                else: 
                    screen_index = self.find_screen(pos)
                    monitor = self.screens[screen_index]
                    view.setRect((monitor.x - self.x_min) // self.down_by, (monitor.y - self.y_min) // self.down_by, (monitor.width) // self.down_by, (monitor.height) // self.down_by)

                view.set_color(view.find_app_item(app_selected))
    
    def delete_app_view(self, app_deleted):
        delete_view = None
        for view in self.scene.items():
            if(str(type(view)) == "<class \'InteractiveAppItem.InteractiveAppItem\'>"):
                if(view.find_app_item(app_deleted)):
                    delete_view = view
        if delete_view:
            self.scene.removeItem(delete_view)

    def add_app_view(self, app_added):
        size = app_added.get_size()
        pos = app_added.get_pos()
        if(size):
            app_view = InteractiveAppItem((pos[0] - self.x_min) // self.down_by, (pos[1] - self.y_min) // self.down_by, size[0] // self.down_by, size[1] // self.down_by, app_added, 0, self.total_screen_area, click_callback=self.update_panel_callback, pos_callback=self.pos_callback)       
        self.scene.addItem(app_view)
    
    def get_bounds(self):
        x_min, y_min = self.screens[0].x, self.screens[0].y
        x_max, y_max = self.screens[0].x + self.screens[0].width, self.screens[0].y + self.screens[0].height
        for monitor in self.screens:
            x_min = min(x_min, monitor.x)
            y_min = min(y_min, monitor.y)
            x_max = max(x_max, monitor.x + monitor.width)
            y_max = max(y_max, monitor.y + monitor.height)
        return x_min, y_min, [0, (x_max - x_min) // self.down_by, 0, (y_max - y_min) // self.down_by]

    def find_screen(self, pos):
        for i, monitor in enumerate(self.screens):
            x, y, width, height  = monitor.x, monitor.y, monitor.width, monitor.height
            if (pos[0] >= x and pos[0] < x + width) and (pos[1] >= y and pos[1] < y + height):
                return i
        return -1
    
    def change_app_view(self, app, x, y, width, height, screen):
        monitor = self.screens[screen - 1]
        set_x = (x + monitor.x - self.x_min) // self.down_by
        set_y = (y + monitor.y - self.y_min) // self.down_by
        set_width = width // self.down_by
        set_height = height // self.down_by
        
        for z, view in enumerate(self.scene.items()):
            if(str(type(view)) == "<class \'InteractiveAppItem.InteractiveAppItem\'>"):
                if(view.find_app_item(app)):
                    view.setRect(set_x, set_y, set_width, set_height)
                    view.setZValue(len(self.scene.items()))
                else:
                    view.setZValue(z)
    
    def pos_callback(self, app, real_x, real_y):
        if self.drag_callback:
            self.drag_callback(app, (real_x * self.down_by) + self.x_min , (real_y * self.down_by) + self.y_min)

            
