from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QPushButton, QLineEdit, QTextEdit, QLabel
)

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"Сашаграмм - {username}")
        self.resize(1000, 700)

        self.setStyleSheet("""
            QMainWindow { background-color: #1E1E1E; }
            QWidget { background-color: #1E1E1E; color: #FFFFFF; }
            QListWidget { background-color: #2D2D2D; border: 1px solid #3C3C3C; }
            QTextEdit { background-color: #252525; border: 1px solid #3C3C3C; }
            QLineEdit { background-color: #2D2D2D; border: 1px solid #3C3C3C; padding: 5px; }
            QPushButton { background-color: #3C3C3C; border: 1px solid #555555; padding: 5px; }
            QPushButton:hover { background-color: #4A4A4A; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        left = QVBoxLayout()
        left.addWidget(QLabel("Чаты"))

        self.chat_list = QListWidget()
        self.chat_list.addItems(["Николай", "Друзья", "Саша"])
        self.chat_list.itemClicked.connect(self.load_chat)
        left.addWidget(self.chat_list)

        self.new_chat_btn = QPushButton("+ Новый чат")
        left.addWidget(self.new_chat_btn)

        right = QVBoxLayout()
        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        self.messages.setText("Выберите чат...")
        right.addWidget(self.messages)

        bottom = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.input_field.returnPressed.connect(self.send_message)
        bottom.addWidget(self.input_field)

        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_message)
        bottom.addWidget(self.send_btn)

        self.attach_btn = QPushButton("📎")
        bottom.addWidget(self.attach_btn)

        right.addLayout(bottom)
        layout.addLayout(left, 1)
        layout.addLayout(right, 3)

    def load_chat(self):
        self.messages.setText("Загрузка сообщений из чата... (пока в разработке)")

    def send_message(self):
        text = self.input_field.text().strip()
        if text == "":
            return
        self.messages.append(f"{self.username}: {text}")
        self.input_field.clear()