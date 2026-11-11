import sys

from PyQt6.QtWidgets import QApplication

from auth import AuthWindow
from db import DatabaseManager

if __name__ == "__main__":
    db = DatabaseManager()
    app = QApplication(sys.argv)
    auth_win = AuthWindow(db)
    auth_win.show()
    sys.exit(app.exec())