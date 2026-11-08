from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QDialog,
    QListWidget, QListWidgetItem, QPushButton, QLineEdit, QTextBrowser,
    QLabel, QMessageBox, QFileDialog, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QApplication
)
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QDesktopServices, QAction, QPixmap
import shutil
import os


class CreateChatDialog(QDialog):
    def __init__(self, db, current_user):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.setWindowTitle("Создание чата")
        self.resize(400, 500)
        self.setStyleSheet("""
            QDialog { background-color: #121212; }
            QLabel { color: #FFFFFF; font-size: 14px; font-weight: bold; }
            QLineEdit { background-color: #1E1E1E; border: 1px solid #333; padding: 8px; border-radius: 5px; color: #FFFFFF; outline: none; }
            QLineEdit:focus { border: 1px solid #555555; }
            QListWidget { background-color: #1E1E1E; border: 1px solid #333; border-radius: 5px; color: #FFFFFF; outline: none; }
            QListWidget::item { padding: 5px; }
            QListWidget::item:selected { background-color: #333333; color: white; }
            QPushButton { background-color: #0088cc; border: none; padding: 10px; border-radius: 5px; font-weight: bold; color: #FFFFFF; outline: none; }
            QPushButton:hover { background-color: #0077b3; }
            QPushButton:focus { outline: none; border: none; }
        """)

        self.layout = QVBoxLayout(self)
        self.name_label = QLabel("Название чата:")
        self.layout.addWidget(self.name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите название...")
        self.layout.addWidget(self.name_input)
        self.search_label = QLabel("Поиск пользователей:")
        self.layout.addWidget(self.search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите имя...")
        self.search_input.textChanged.connect(self.update_user_list)
        self.layout.addWidget(self.search_input)
        self.user_list = QListWidget()
        self.layout.addWidget(self.user_list)
        self.create_btn = QPushButton("Создать чат")
        self.create_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.create_btn)
        self.update_user_list("")

    def update_user_list(self, text):
        self.user_list.clear()
        self.users = self.db.search_users(text)
        for self.user in self.users:
            if self.user != self.current_user:
                self.item = QListWidgetItem(self.user)
                self.item.setFlags(self.item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                self.item.setCheckState(Qt.CheckState.Unchecked)
                self.user_list.addItem(self.item)

    def get_data(self):
        self.members = [self.current_user]
        for self.i in range(self.user_list.count()):
            self.item = self.user_list.item(self.i)
            if self.item.checkState() == Qt.CheckState.Checked:
                self.members.append(self.item.text())
        return self.name_input.text().strip(), self.members


class MainWindow(QMainWindow):
    def __init__(self, db, username):
        super().__init__()
        self.db = db
        self.username = username
        self.current_chat_id = None
        self.all_chats = []
        self.last_unread = {}

        self.setWindowTitle(f"Сашаграмм - {self.username}")
        self.resize(1000, 700)

        self.setup_menu_bar()
        self.setup_ui()
        self.load_data()
        self.load_avatar()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_notifications)
        self.timer.start(2000)

    def setup_menu_bar(self):
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet("background-color: #1E1E1E; color: #FFFFFF;")
        self.file_menu = self.menubar.addMenu("Файл")
        self.exit_action = QAction("Выход", self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        self.chat_menu = self.menubar.addMenu("Чат")
        self.new_chat_action = QAction("Создать чат", self)
        self.new_chat_action.triggered.connect(self.create_chat)
        self.chat_menu.addAction(self.new_chat_action)
        self.help_menu = self.menubar.addMenu("Справка")
        self.about_action = QAction("О программе", self)
        self.about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(self.about_action)

    def setup_ui(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QWidget { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI', Arial; }
            QListWidget { background-color: #1E1E1E; border: none; border-radius: 8px; padding: 5px; outline: none; }
            QListWidget::item { padding: 10px; border-radius: 5px; }
            QListWidget::item:selected { background-color: #333333; color: white; }
            QTextBrowser { background-color: #1E1E1E; border: none; border-radius: 8px; padding: 10px; selection-background-color: #444444; selection-color: white; outline: none; }
            QLineEdit { background-color: #1E1E1E; border: 1px solid #333333; padding: 10px; border-radius: 8px; color: #FFFFFF; outline: none; }
            QLineEdit:focus { border: 1px solid #555555; }
            QPushButton { background-color: #0088cc; border: none; padding: 10px; border-radius: 8px; font-weight: bold; color: #FFFFFF; outline: none; }
            QPushButton:hover { background-color: #0077b3; }
            QPushButton:focus { outline: none; border: none; }
            QTabWidget::pane { border: 1px solid #333; background-color: #121212; }
            QTabBar::tab { background-color: #1E1E1E; color: #FFFFFF; padding: 10px; outline: none; }
            QTabBar::tab:selected { background-color: #333333; }
            QTableWidget { background-color: #1E1E1E; color: #FFFFFF; border: none; outline: none; }
            QHeaderView::section { background-color: #333333; color: #FFFFFF; padding: 5px; border: none; }
        """)

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.outer_layout = QVBoxLayout(self.central)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        self.banner = QLabel("Вам пришло новое сообщение!")
        self.banner.setStyleSheet(
            "background-color: #0088cc; color: white; font-size: 16px; font-weight: bold; padding: 10px;")
        self.banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner.hide()
        self.outer_layout.addWidget(self.banner)

        self.content_widget = QWidget()
        self.outer_layout.addWidget(self.content_widget)

        self.main_layout = QHBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget()
        self.tabs.setFixedWidth(320)

        self.tab_chats = QWidget()
        self.tab_chats_layout = QVBoxLayout(self.tab_chats)

        self.profile_label = QLabel(f"👤 {self.username}")
        self.profile_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #0088cc;")
        self.profile_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tab_chats_layout.addWidget(self.profile_label)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setStyleSheet("border-radius: 40px; background-color: #333; color: white; font-size: 40px;")
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setScaledContents(True)
        self.tab_chats_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.change_avatar_btn = QPushButton("Сменить аватар")
        self.change_avatar_btn.setStyleSheet("background-color: #333; font-size: 12px; padding: 5px;")
        self.change_avatar_btn.clicked.connect(self.change_avatar)
        self.tab_chats_layout.addWidget(self.change_avatar_btn)

        self.search_chat_input = QLineEdit()
        self.search_chat_input.setPlaceholderText("Поиск чатов...")
        self.search_chat_input.textChanged.connect(self.filter_chats)
        self.tab_chats_layout.addWidget(self.search_chat_input)

        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self.load_chat)
        self.tab_chats_layout.addWidget(self.chat_list)

        self.tab_users = QWidget()
        self.tab_users_layout = QVBoxLayout(self.tab_users)
        self.users_label = QLabel("Зарегистрированные пользователи:")
        self.tab_users_layout.addWidget(self.users_label)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(1)
        self.users_table.setHorizontalHeaderLabels(["Логин"])
        self.users_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab_users_layout.addWidget(self.users_table)

        self.tabs.addTab(self.tab_chats, "Мои чаты")
        self.tabs.addTab(self.tab_users, "Пользователи")
        self.main_layout.addWidget(self.tabs)

        self.right_layout = QVBoxLayout()
        self.right_layout.setSpacing(10)

        self.messages = QTextBrowser()
        self.messages.setOpenLinks(False)
        self.messages.anchorClicked.connect(self.open_file)
        self.right_layout.addWidget(self.messages)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.setSpacing(10)

        self.attach_btn = QPushButton("📎")
        self.attach_btn.setFixedSize(40, 40)
        self.attach_btn.clicked.connect(self.attach_file)
        self.bottom_layout.addWidget(self.attach_btn)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.input_field.returnPressed.connect(self.send_message)
        self.bottom_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_message)
        self.bottom_layout.addWidget(self.send_btn)

        self.right_layout.addLayout(self.bottom_layout)
        self.main_layout.addLayout(self.right_layout, 3)

    def show_banner(self, text):
        self.banner.setText(text)
        self.banner.show()
        if hasattr(self, 'banner_timer'):
            self.banner_timer.stop()
        self.banner_timer = QTimer()
        self.banner_timer.setSingleShot(True)
        self.banner_timer.timeout.connect(self.banner.hide)
        self.banner_timer.start(3000)

    def check_notifications(self):
        self.has_new = False
        for self.chat_id, self.chat_name in self.all_chats:
            self.unread = self.db.get_unread_count(self.chat_id, self.username)
            self.last = self.last_unread.get(self.chat_id, 0)

            if self.unread > self.last:
                if self.chat_id == self.current_chat_id:
                    self.messages.clear()
                    self.history = self.db.get_messages(self.current_chat_id)
                    for self.msg in self.history:
                        self.display_message(self.msg['time'], self.msg['sender'], self.msg['text'])
                    self.messages.moveCursor(self.messages.textCursor().MoveOperation.End)
                else:
                    self.show_banner(f"Вам пришло новое сообщение в чат '{self.chat_name}'!")
                    QApplication.alert(self, 0)
                self.has_new = True

            self.last_unread[self.chat_id] = self.unread

        if self.has_new:
            self.update_chat_list()

    def load_avatar(self):
        self.avatar_path = self.db.get_avatar(self.username)
        if self.avatar_path and os.path.exists(self.avatar_path):
            self.pixmap = QPixmap(self.avatar_path)
            self.avatar_label.setPixmap(self.pixmap)
            self.avatar_label.setText("")
        else:
            self.avatar_label.setText("👤")
            self.avatar_label.setStyleSheet(
                "border-radius: 40px; background-color: #333; color: white; font-size: 40px; text-align: center;")

    def change_avatar(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Выберите аватар", "", "Images (*.png *.jpg *.jpeg)")
        if self.file_path:
            if not os.path.exists("avatars"):
                os.makedirs("avatars")
            self.filename = os.path.basename(self.file_path)
            self.new_path = os.path.join("avatars", self.filename)
            shutil.copy(self.file_path, self.new_path)
            self.db.update_avatar(self.username, self.new_path)
            self.load_avatar()

    def load_data(self):
        self.all_chats = self.db.get_chats(self.username)
        self.update_chat_list()
        self.users = self.db.get_all_users()
        self.users_table.setRowCount(len(self.users))
        for self.i, self.user in enumerate(self.users):
            self.users_table.setItem(self.i, 0, QTableWidgetItem(self.user))

        for self.chat_id, self.chat_name in self.all_chats:
            self.last_unread[self.chat_id] = self.db.get_unread_count(self.chat_id, self.username)

        if self.chat_list.count() > 0 and self.current_chat_id is None:
            self.chat_list.setCurrentRow(0)
            self.load_chat()

    def update_chat_list(self):
        current_id = self.current_chat_id
        self.chat_list.clear()
        for self.chat_id, self.chat_name in self.all_chats:
            self.unread = self.db.get_unread_count(self.chat_id, self.username)
            if self.unread > 0:
                self.display_name = f"{self.chat_name} ({self.unread})"
            else:
                self.display_name = self.chat_name

            self.chat_list.addItem(self.display_name)
            self.chat_list.item(self.chat_list.count() - 1).setData(1, self.chat_id)

        if current_id is not None:
            for self.i in range(self.chat_list.count()):
                if self.chat_list.item(self.i).data(1) == current_id:
                    self.chat_list.setCurrentRow(self.i)
                    break

    def filter_chats(self, text):
        self.chat_list.clear()
        for self.chat_id, self.chat_name in self.all_chats:
            if text.lower() in self.chat_name.lower():
                self.unread = self.db.get_unread_count(self.chat_id, self.username)
                if self.unread > 0:
                    self.display_name = f"{self.chat_name} ({self.unread})"
                else:
                    self.display_name = self.chat_name
                self.chat_list.addItem(self.display_name)
                self.chat_list.item(self.chat_list.count() - 1).setData(1, self.chat_id)

    def load_chat(self, *args):
        self.current_item = self.chat_list.currentItem()
        if not self.current_item:
            return
        self.current_chat_id = self.current_item.data(1)
        self.db.mark_as_read(self.current_chat_id, self.username)
        self.update_chat_list()
        self.messages.clear()
        self.history = self.db.get_messages(self.current_chat_id)
        for self.msg in self.history:
            self.display_message(self.msg['time'], self.msg['sender'], self.msg['text'])

        self.messages.moveCursor(self.messages.textCursor().MoveOperation.End)

    def display_message(self, time, sender, text):
        if text.startswith("📎 IMAGE:"):
            self.filename = text.replace("📎 IMAGE:", "").strip()
            self.path = os.path.abspath(os.path.join("uploads", self.filename))
            self.url = QUrl.fromLocalFile(self.path).toString()
            self.messages.append(f"<b>[{time}] {sender}:</b>")
            self.messages.insertHtml(
                f'<img src="{self.url}" width="250" style="border-radius: 10px; margin-bottom: 10px;"><br>')
        elif text.startswith("📎 FILE:"):
            self.filename = text.replace("📎 FILE:", "").strip()
            self.path = os.path.abspath(os.path.join("uploads", self.filename))
            self.url = QUrl.fromLocalFile(self.path).toString()
            self.messages.append(
                f'<b>[{time}] {sender}:</b> отправил файл <a href="{self.url}" style="color: #0088cc; text-decoration: none;">{self.filename}</a><br>')
        else:
            self.messages.append(f"<b>[{time}] {sender}:</b> {text}<br>")

    def open_file(self, url):
        QDesktopServices.openUrl(url)

    def create_chat(self):
        self.dialog = CreateChatDialog(self.db, self.username)
        if self.dialog.exec():
            self.name, self.members = self.dialog.get_data()
            if self.name:
                self.db.create_chat(self.name, self.members)
                self.current_chat_id = None
                self.load_data()
            else:
                QMessageBox.warning(self, "Ошибка", "Введите название чата")

    def show_about(self):
        QMessageBox.information(self, "О программе", f"Сашаграмм\nПользователь: {self.username}")

    def send_message(self):
        self.text = self.input_field.text().strip()
        if not self.text or self.current_chat_id is None:
            return
        self.db.add_message(self.current_chat_id, self.username, self.text)
        self.input_field.clear()

        self.messages.append(f"<b>[Сейчас] {self.username}:</b> {self.text}<br>")
        self.messages.moveCursor(self.messages.textCursor().MoveOperation.End)

        self.last_unread[self.current_chat_id] = 0
        self.update_chat_list()

    def attach_file(self):
        if self.current_chat_id is None:
            return
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if self.file_path:
            self.file_size = os.path.getsize(self.file_path)
            if self.file_size > 50 * 1024 * 1024:
                QMessageBox.warning(self, "Ошибка", "Файл слишком большой! Максимум 50 МБ.")
                return

            self.filename = os.path.basename(self.file_path)
            if not os.path.exists("uploads"):
                os.makedirs("uploads")
            shutil.copy(self.file_path, os.path.join("uploads", self.filename))

            if self.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                self.text = f"📎 IMAGE:{self.filename}"
            else:
                self.text = f"📎 FILE:{self.filename}"

            self.db.add_message(self.current_chat_id, self.username, self.text)

            if self.text.startswith("📎 IMAGE:"):
                self.filename = self.text.replace("📎 IMAGE:", "").strip()
                self.path = os.path.abspath(os.path.join("uploads", self.filename))
                self.url = QUrl.fromLocalFile(self.path).toString()
                self.messages.append(f"<b>[Сейчас] {self.username}:</b>")
                self.messages.insertHtml(
                    f'<img src="{self.url}" width="250" style="border-radius: 10px; margin-bottom: 10px;"><br>')
            else:
                self.filename = self.text.replace("📎 FILE:", "").strip()
                self.path = os.path.abspath(os.path.join("uploads", self.filename))
                self.url = QUrl.fromLocalFile(self.path).toString()
                self.messages.append(
                    f'<b>[Сейчас] {self.username}:</b> отправил файл <a href="{self.url}" style="color: #0088cc; text-decoration: none;">{self.filename}</a><br>')

            self.messages.moveCursor(self.messages.textCursor().MoveOperation.End)
            self.last_unread[self.current_chat_id] = 0
            self.update_chat_list()