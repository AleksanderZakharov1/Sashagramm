from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
import db


class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сашаграмм - Вход")
        self.resize(300, 200)

        self.setStyleSheet("""
            QWidget { background-color: #1E1E1E; color: #FFFFFF; }
            QLineEdit { background-color: #2D2D2D; border: 1px solid #555; padding: 5px; }
            QPushButton { background-color: #3C3C3C; border: 1px solid #555; padding: 5px; }
            QPushButton:hover { background-color: #4A4A4A; }
        """)

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
        self.btn_reg.clicked.connect(self.do_register)
        layout.addWidget(self.btn_reg)

        self.setLayout(layout)

    def do_login(self):
        login = self.login_input.text()
        password = self.pass_input.text()

        username = db.login_user(login, password)
        if username:
            QMessageBox.information(self, "Успех", f"Привет, {username}!")
            self.open_main(username)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def do_register(self):
        login = self.login_input.text()
        password = self.pass_input.text()

        if len(login) < 3 or len(password) < 4:
            QMessageBox.warning(self, "Ошибка", "Логин от 3 символов, пароль от 4")
            return

        success = db.register_user(login, password, login)
        if success:
            QMessageBox.information(self, "Успех", "Аккаунт создан! Теперь войдите.")
        else:
            QMessageBox.warning(self, "Ошибка", "Этот логин уже занят")

    def open_main(self, username):
        from main_window import MainWindow
        self.main_win = MainWindow(username)
        self.main_win.show()
        self.close()