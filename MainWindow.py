from PyQt6 import QtWidgets 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, screens):
        super().__init__()
        self.screens = screens
        self.setWindowTitle("SetupGUI")
        primary_screen = self.get_primary_screen()
        self.resize(primary_screen.width, primary_screen.height)
        self.showMaximized()

        layout = QtWidgets.QVBoxLayout()
        title_label = QtWidgets.QLabel(r"<canvas id=\"myCanvas\" width=\"200\" height=\"100\" style=\"border:1px solid #000000;\"></canvas>")
        layout.addWidget(title_label)
        layout.addStretch()
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def get_primary_screen(self):
        for monitor in self.screens:
            if(monitor.is_primary):
                return monitor