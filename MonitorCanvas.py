from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, 
                             QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QGraphicsRectItem, QLabel, QFrame)
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QCursor
from PyQt6.QtCore import Qt
from App import *
from InteractiveAppItem import *
from Size import *

DOWN_BY_CONST = 5
class MonitorCanvas(QGraphicsView):
    def __init__(self, screens, apps, update_panel_callback, drag_callback, resize_callback, delete_callback):
        super().__init__()
        self.screens = screens
        self.apps = apps
        self.update_panel_callback = update_panel_callback
        self.drag_callback = drag_callback
        self.resize_callback = resize_callback
        self.delete_callback = delete_callback
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.x_min, self.y_min, self.total_screen_area = self.get_bounds()
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setStyleSheet("background-color: #1e1e1e; border: none;")
        
        for monitor in self.screens: 
            monitor_view = QGraphicsRectItem((monitor.x - self.x_min)//DOWN_BY_CONST, (monitor.y - self.y_min)//DOWN_BY_CONST, (monitor.width)//DOWN_BY_CONST, (monitor.height)//DOWN_BY_CONST) 
            monitor_view.setBrush(QBrush(QColor("#333333")))
            monitor_view.setPen(QPen(QColor("#555555"), 5))
            self.scene.addItem(monitor_view)
        
        if self.apps:
            num_apps = len(self.apps)
            for z, app in enumerate(self.apps): 
                size_obj = app.get_size()
                size = size_obj.get_size()
                pos = app.get_pos()
                if(size_obj.get_is_list()):
                    app_view = InteractiveAppItem((pos[0] - self.x_min) // DOWN_BY_CONST, (pos[1] - self.y_min) // DOWN_BY_CONST, size[0] // DOWN_BY_CONST, size[1] // DOWN_BY_CONST, app, num_apps - z, self.total_screen_area, click_callback=self.update_panel_callback , pos_callback=self.pos_callback, size_callback=self.size_callback, delete_callback=self.delete_callback)
                else: 
                    screen_index = self.find_screen(pos)
                    monitor = self.screens[screen_index]
                    app_x, app_y, app_width, app_height = self.get_position_on_monitor(size, monitor)
                    app_view = InteractiveAppItem(app_x, app_y, app_width, app_height, app, num_apps - z, self.total_screen_area, click_callback=self.update_panel_callback, pos_callback=self.pos_callback, size_callback=self.size_callback, delete_callback=self.delete_callback)
                self.scene.addItem(app_view)
        
    def reset_app_view(self, app_selected):  
        max_items = len(self.scene.items())
        for z, view in enumerate(self.scene.items()):
            if(str(type(view)) == "<class \'InteractiveAppItem.InteractiveAppItem\'>"):
                app = view.get_app() 
                size_obj = app.get_size()
                size = size_obj.get_size()
                pos = app.get_pos()
                view.setZValue(max_items - z) 
                if(size_obj.get_is_list()):
                    view.setRect((pos[0] - self.x_min) // DOWN_BY_CONST, (pos[1] - self.y_min) // DOWN_BY_CONST, size[0] // DOWN_BY_CONST, size[1] // DOWN_BY_CONST)
                else: 
                    screen_index = self.find_screen(pos)
                    monitor = self.screens[screen_index]
                    app_x, app_y, app_width, app_height = self.get_position_on_monitor(size, monitor)
                    view.setRect(app_x, app_y, app_width, app_height)

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
        size_obj = app_added.get_size()
        pos = app_added.get_pos()
        if(size_obj.get_is_list()):
            size = size_obj.get_size()
            app_view = InteractiveAppItem((pos[0] - self.x_min) // DOWN_BY_CONST, (pos[1] - self.y_min) // DOWN_BY_CONST, size[0] // DOWN_BY_CONST, size[1] // DOWN_BY_CONST, app_added, 0, self.total_screen_area, click_callback=self.update_panel_callback, pos_callback=self.pos_callback, size_callback=self.size_callback, delete_callback=self.delete_callback)       
        self.scene.addItem(app_view)
    
    def get_bounds(self):
        x_min, y_min = self.screens[0].x, self.screens[0].y
        x_max, y_max = self.screens[0].x + self.screens[0].width, self.screens[0].y + self.screens[0].height
        for monitor in self.screens:
            x_min = min(x_min, monitor.x)
            y_min = min(y_min, monitor.y)
            x_max = max(x_max, monitor.x + monitor.width)
            y_max = max(y_max, monitor.y + monitor.height)
        return x_min, y_min, [0, (x_max - x_min) // DOWN_BY_CONST, 0, (y_max - y_min) // DOWN_BY_CONST]

    def find_screen(self, pos):
        for i, monitor in enumerate(self.screens):
            x, y, width, height  = monitor.x, monitor.y, monitor.width, monitor.height
            if (pos[0] >= x and pos[0] < x + width) and (pos[1] >= y and pos[1] < y + height):
                return i
        return -1
    
    def change_app_view(self, app, x, y, width, height, screen):
        monitor = self.screens[screen - 1]
        set_x = (x + monitor.x - self.x_min) // DOWN_BY_CONST
        set_y = (y + monitor.y - self.y_min) // DOWN_BY_CONST
        set_width = width // DOWN_BY_CONST
        set_height = height // DOWN_BY_CONST
        
        for z, view in enumerate(self.scene.items()):
            if(str(type(view)) == "<class \'InteractiveAppItem.InteractiveAppItem\'>"):
                if(view.find_app_item(app)):
                    view.setRect(set_x, set_y, set_width, set_height)
                    view.setZValue(len(self.scene.items()))
                else:
                    view.setZValue(z)
    
    def get_position_on_monitor(self, info, monitor):
        pos_x = monitor.x
        pos_y = monitor.y
        width = monitor.width
        heigth = monitor.height
        half_width = width // 2
        half_height = heigth // 2
        match info:
            case "Top":
                heigth = half_height
            case "Bottom":
                heigth = half_height
                pos_y += half_height
            case "Left":
                width = half_width
            case "Right":
                width = half_width
                pos_x += half_width
            case "Left_Top":
                width = half_width
                heigth = half_height
            case "Left_Bottom":
                width = half_width
                heigth = half_height
                pos_y += half_height
            case "Right_Top":
                width = half_width
                heigth = half_height
                pos_x += half_width
            case "Right_Bottom":
                width = half_width
                heigth = half_height
                pos_x += half_width
                pos_y += half_height
        return (pos_x - self.x_min)//DOWN_BY_CONST, (pos_y- self.y_min)//DOWN_BY_CONST, (width)//DOWN_BY_CONST, (heigth)//DOWN_BY_CONST
    
    def pos_callback(self, app, real_x, real_y, is_moved):
        if self.drag_callback:
            self.drag_callback(app, (real_x * DOWN_BY_CONST) + self.x_min , (real_y * DOWN_BY_CONST) + self.y_min, is_moved)
    
    def size_callback(self, app, new_width, new_height):
        if self.resize_callback:
            self.resize_callback(app, int(new_width * DOWN_BY_CONST), int(new_height * DOWN_BY_CONST))

            
