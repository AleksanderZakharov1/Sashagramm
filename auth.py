from PyQt6.QtWidgets import (
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AuthWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Сашаграмм - Вход")
        self.resize(300, 200)

        self.setStyleSheet(
            """
            QWidget { background-color: #121212; color: #FFFFFF; }
            QLineEdit {
                background-color: #1E1E1E; border: 1px solid #333;
                padding: 8px; border-radius: 5px; color: white;
                outline: none;
            }
            QLineEdit:focus { border: 1px solid #555555; }
            QPushButton {
                background-color: #0088cc; border: none; padding: 8px;
                border-radius: 5px; font-weight: bold; color: white;
                outline: none;
            }
            QPushButton:hover { background-color: #0077b3; }
            QPushButton:focus { outline: none; border: none; }
            """
        )

        layout = QVBoxLayout()
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        layout.addWidget(self.login_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Пароль")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_input)

        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.do_login)
        layout.addWidget(self.btn_login)

        self.btn_reg = QPushButton("Зарегистрироваться")
        self.btn_reg.setStyleSheet("background-color: #333;")
        self.btn_reg.clicked.connect(self.do_register)
        layout.addWidget(self.btn_reg)
        self.setLayout(layout)

    def do_login(self):
        login = self.login_input.text()
        password = self.pass_input.text()

        username = self.db.login_user(login, password)
        if username:
            from main_window import MainWindow

            self.main_win = MainWindow(self.db, username)
            self.main_win.show()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def do_register(self):
        login = self.login_input.text()
        password = self.pass_input.text()

        if self.db.register_user(login, password):
            QMessageBox.information(self, "Успех", "Аккаунт создан!")
        else:
            QMessageBox.warning(
                self, "Ошибка", "Логин занят или пустые поля"
            )