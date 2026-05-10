from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QMainWindow
from PyQt6.QtGui import QBrush, QColor, QPen, QPainter, QCursor
from PyQt6.QtCore import Qt
from App import *

class InteractiveAppItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, app):
        super().__init__(x, y, width, height)
        self.app = app
        self.setAcceptHoverEvents(True)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.default_color = QColor("#0078d4")
        self.hover_color = QColor("#2b88d8") 
        
        self.setBrush(QBrush(self.default_color))
        self.setPen(QPen(Qt.GlobalColor.white, 1))


    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(self.hover_color))
        print(f"Hovering over: {self.app.get_name()}")
        super().hoverEnterEvent(event)
    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(self.default_color))
        super().hoverLeaveEvent(event)

class MonitorCanvas(QGraphicsView):
    def __init__(self, screens, apps):
        super().__init__()
        self.screens = screens
        self.apps = apps
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        x_cor, y_cor = self.get_correction()
        down_by = 5
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setStyleSheet("background-color: #1e1e1e; border: none;")
        
        for monitor in self.screens: 
            monitor_view = QGraphicsRectItem((monitor.x - x_cor)//down_by, (monitor.y - y_cor)//down_by, (monitor.width)//down_by, (monitor.height)//down_by) 
            monitor_view.setBrush(QBrush(QColor("#333333")))
            monitor_view.setPen(QPen(QColor("#555555"), 5))
            self.scene.addItem(monitor_view)
            
        for app in self.apps: 
            size = app.get_size()
            pos = app.get_pos()
            if(size):
                app_view = InteractiveAppItem((pos[0] - x_cor) // down_by, (pos[1] - y_cor) // down_by, size[0] // down_by, size[1] // down_by, app)
            else: 
                screen_index = self.find_screen(pos)
                monitor = self.screens[screen_index]
                app_view = InteractiveAppItem((monitor.x - x_cor)//down_by, (monitor.y - y_cor)//down_by, (monitor.width)//down_by, (monitor.height)//down_by, app)
                
            self.scene.addItem(app_view)

    
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
        
class MainWindow(QMainWindow):
    def __init__(self, screens, apps, urls):
        super().__init__()
        self.screens = screens
        self.apps = apps
        self.urls = urls
        
        self.setWindowTitle("SetupGUI")
        primary_screen = self.get_primary_screen()
        self.resize(primary_screen.width, primary_screen.height)
        self.showMaximized()
        self.setCentralWidget(MonitorCanvas(self.screens, self.apps))


    
    def get_primary_screen(self):
        for monitor in self.screens:
            if(monitor.is_primary):
                return monitor