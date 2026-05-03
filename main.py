import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("My App")
    window.setGeometry(100, 100, 280, 80)
    hello_msg = QLabel("<button>hello</button>", parent=window)
    hello_msg.move(60, 15)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
