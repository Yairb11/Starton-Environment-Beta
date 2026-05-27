from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt

CANVAS_VIEW_STYLE = """
            QGraphicsView {
                background-color: #1e1e1e; 
            }
        """
DOWN_BY = 10
SIZE_OPTIONS = {"Full": 0, "Left": 1, "Right": 2, "Top": 3, "Bottom": 4, "Left_Top": 5, "Left_Bottom": 6, "Right_Top": 7, "Right_Bottom": 8}

class MiniCanvas(QGraphicsView):
    def __init__(self, option, monitor):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.monitor = monitor
        self.option = SIZE_OPTIONS[option]
        self.setFixedHeight(150) 
        self.setStyleSheet(CANVAS_VIEW_STYLE)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.draw_test_shapes()

    def set_monitor(self, monitor):
        self.monitor = monitor
        self.draw_test_shapes()

    def draw_test_shapes(self):
        if self.monitor:
            app_x, app_y, app_width, app_height = self.get_app_position()
            monitor_view = QGraphicsRectItem(0, 0, self.monitor.width // DOWN_BY, self.monitor.height // DOWN_BY)
            monitor_view.setBrush(QBrush(QColor("#333333")))
            monitor_view.setPen(QPen(QColor("#555555"), 5))
            app_view = QGraphicsRectItem(app_x, app_y, app_width, app_height)
            app_view.setBrush(QBrush(QColor("#0078d4")))
            app_view.setPen(QPen(Qt.GlobalColor.white, 1))
            self.scene.addItem(monitor_view)
            self.scene.addItem(app_view)
    def get_app_position(self):
        app_x = 0
        app_y = 0
        app_width = self.monitor.width
        app_height = self.monitor.height
        if self.option == 2 or self.option == 7 or self.option == 8:
            app_x = self.monitor.width // 2
        if self.option == 4 or self.option == 6 or self.option == 8:
            app_y = self.monitor.height // 2
        if not(self.option == 0 or self.option == 3 or self.option == 4):
            app_width = self.monitor.width // 2
        if not(self.option == 0 or self.option == 1 or self.option == 2):
            app_height = self.monitor.height // 2
        return app_x // DOWN_BY, app_y // DOWN_BY, app_width // DOWN_BY, app_height // DOWN_BY