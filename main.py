import sys
import traceback
from PyQt6.QtWidgets import QApplication
from db import DatabaseManager
from auth import AuthWindow

def error_handler(exctype, value, tb):
    traceback.print_exception(exctype, value, tb)

sys.excepthook = error_handler

if __name__ == "__main__":
    db = DatabaseManager()
    app = QApplication(sys.argv)
    auth_win = AuthWindow(db)
    auth_win.show()
    sys.exit(app.exec())