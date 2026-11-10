from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from styles import DIALOG_STYLE


class CreateChatDialog(QDialog):
    def __init__(self, db, current_user):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.setWindowTitle("Создание чата")
        self.resize(400, 500)
        self.setStyleSheet(DIALOG_STYLE)

        self.main_layout = QVBoxLayout(self)
        self.name_label = QLabel("Название чата:", self)
        self.main_layout.addWidget(self.name_label)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Введите название...")
        self.main_layout.addWidget(self.name_input)

        self.search_label = QLabel("Поиск пользователей:", self)
        self.main_layout.addWidget(self.search_label)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Введите имя...")
        self.search_input.textChanged.connect(self.update_user_list)
        self.main_layout.addWidget(self.search_input)

        self.user_list = QListWidget(self)
        self.main_layout.addWidget(self.user_list)

        self.create_btn = QPushButton("Создать чат", self)
        self.create_btn.clicked.connect(self.accept)
        self.main_layout.addWidget(self.create_btn)

        self.update_user_list("")

    def update_user_list(self, text):
        self.user_list.clear()
        users = self.db.search_users(text)
        for user in users:
            if user != self.current_user:
                item = QListWidgetItem(user)
                item.setFlags(
                    item.flags() | Qt.ItemFlag.ItemIsUserCheckable
                )
                item.setCheckState(Qt.CheckState.Unchecked)
                self.user_list.addItem(item)

    def get_data(self):
        members = [self.current_user]
        for i in range(self.user_list.count()):
            item = self.user_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                members.append(item.text())
        return self.name_input.text().strip(), members