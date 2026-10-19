import sys
from PyQt6.QtWidgets import QApplication
import db
from auth import AuthWindow

if __name__ == "__main__":
    db.init_db()

    app = QApplication(sys.argv)

    auth_win = AuthWindow()
    auth_win.show()

    sys.exit(app.exec())