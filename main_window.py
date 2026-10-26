from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QPushButton, QLineEdit, QTextBrowser, QLabel,
    QInputDialog, QMenu, QMessageBox, QFileDialog
)
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
import db
import shutil
import os


class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.current_chat_id = None
        self.setWindowTitle(f"Сашаграмм - {username}")
        self.resize(1000, 700)

        self.setStyleSheet("""
            QMainWindow { background-color: #1E1E1E; }
            QWidget { background-color: #1E1E1E; color: #FFFFFF; }
            QListWidget { background-color: #2D2D2D; border: 1px solid #3C3C3C; }
            QTextBrowser { background-color: #252525; border: 1px solid #3C3C3C; }
            QLineEdit { background-color: #2D2D2D; border: 1px solid #3C3C3C; padding: 5px; }
            QPushButton { background-color: #3C3C3C; border: 1px solid #555555; padding: 5px; }
            QPushButton:hover { background-color: #4A4A4A; }
            QMenu { background-color: #2D2D2D; color: #FFFFFF; border: 1px solid #555555; }
            QMenu::item:selected { background-color: #4A4A4A; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        left = QVBoxLayout()

        profile_label = QLabel(f"👤 Профиль: {username}")
        profile_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        left.addWidget(profile_label)

        self.menu_btn = QPushButton("≡ Меню")
        self.menu = QMenu(self)

        action_new_chat = self.menu.addAction("Создать новый чат")
        action_new_chat.triggered.connect(self.create_chat)

        action_about = self.menu.addAction("О программе")
        action_about.triggered.connect(self.show_about)

        self.menu.addSeparator()

        action_exit = self.menu.addAction("Выход")
        action_exit.triggered.connect(self.close)

        self.menu_btn.setMenu(self.menu)
        left.addWidget(self.menu_btn)

        left.addWidget(QLabel("Чаты:"))
        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self.load_chat)
        left.addWidget(self.chat_list)

        layout.addLayout(left, 1)

        right = QVBoxLayout()

        self.messages = QTextBrowser()
        self.messages.setOpenLinks(False)
        self.messages.anchorClicked.connect(self.open_file)
        right.addWidget(self.messages)

        bottom = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.input_field.returnPressed.connect(self.send_message)
        bottom.addWidget(self.input_field)

        self.attach_btn = QPushButton("📎")
        self.attach_btn.clicked.connect(self.attach_file)
        bottom.addWidget(self.attach_btn)

        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_message)
        bottom.addWidget(self.send_btn)

        right.addLayout(bottom)
        layout.addLayout(right, 3)

        self.load_chats()

    def load_chats(self):
        self.chat_list.clear()
        chats = db.get_chats()
        for chat in chats:
            self.chat_list.addItem(chat["name"])
            self.chat_list.item(self.chat_list.count() - 1).setData(1, chat["id"])

        if self.chat_list.count() > 0 and self.current_chat_id is None:
            self.chat_list.setCurrentRow(0)
            self.load_chat()

    def load_chat(self, *args):
        current_item = self.chat_list.currentItem()
        if not current_item:
            return

        self.current_chat_id = current_item.data(1)
        self.messages.clear()

        history = db.get_messages(self.current_chat_id)
        for msg in history:
            self.display_message(msg['time'], msg['sender'], msg['text'])

    def display_message(self, time, sender, text):
        if text.startswith("📎 IMAGE:"):
            filename = text.replace("📎 IMAGE:", "").strip()
            path = os.path.abspath(os.path.join("uploads", filename))
            url = QUrl.fromLocalFile(path).toString()
            self.messages.append(f"[{time}] {sender}:")
            self.messages.insertHtml(f'<img src="{url}" width="200"><br><br>')
        elif text.startswith("📎 FILE:"):
            filename = text.replace("📎 FILE:", "").strip()
            path = os.path.abspath(os.path.join("uploads", filename))
            url = QUrl.fromLocalFile(path).toString()
            self.messages.append(
                f'[{time}] {sender}: отправил файл <a href="{url}" style="color: #5CA9FF;">{filename}</a><br>')
        else:
            self.messages.append(f"[{time}] {sender}: {text}")

    def open_file(self, url):
        QDesktopServices.openUrl(url)

    def create_chat(self):
        name, ok = QInputDialog.getText(self, "Новый чат", "Введите название чата:")
        if ok and name.strip():
            db.create_chat(name.strip())
            self.load_chats()

    def show_about(self):
        QMessageBox.information(self, "О программе",
                                "Сашаграмм - защищенный мессенджер.\nПроект Яндекс Лицея.\n\nРазработчик: " + self.username)

    def send_message(self):
        text = self.input_field.text().strip()
        if text == "" or self.current_chat_id is None:
            return

        db.add_message(self.current_chat_id, self.username, text)
        self.display_message("Сейчас", self.username, text)
        self.input_field.clear()

    def attach_file(self):
        if self.current_chat_id is None:
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            filename = os.path.basename(file_path)
            if not os.path.exists("uploads"):
                os.makedirs("uploads")
            shutil.copy(file_path, f"uploads/{filename}")

            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                text = f"📎 IMAGE:{filename}"
            else:
                text = f"📎 FILE:{filename}"

            db.add_message(self.current_chat_id, self.username, text)
            self.display_message("Сейчас", self.username, text)