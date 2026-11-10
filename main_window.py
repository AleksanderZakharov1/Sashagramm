import os
import shutil

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QAction, QDesktopServices, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from dialogs import CreateChatDialog
from styles import MAIN_STYLE


class MainWindow(QMainWindow):
    def __init__(self, db, username):
        super().__init__()
        self.db = db
        self.username = username
        self.current_chat_id = None
        self.all_chats = []
        self.last_unread = {}
        self.filename = ""
        self.text = ""
        self.path = ""
        self.url = ""

        self.banner_timer = QTimer(self)
        self.banner_timer.setSingleShot(True)
        self.banner_timer.timeout.connect(self.hide_banner)

        self.setWindowTitle(f"Сашаграмм - {self.username}")
        self.resize(1000, 700)

        self.setup_menu_bar()
        self.setup_ui()
        self.load_data()
        self.load_avatar()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_notifications)
        self.timer.start(2000)

    def setup_menu_bar(self):
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet(
            "background-color: #1E1E1E; color: #FFFFFF;"
        )

        self.file_menu = self.menubar.addMenu("Файл")

        self.export_action = QAction("Экспорт чата в TXT", self)
        self.export_action.triggered.connect(self.export_chat)
        self.file_menu.addAction(self.export_action)

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
        self.setStyleSheet(MAIN_STYLE)

        self.central = QWidget(self)
        self.setCentralWidget(self.central)

        self.outer_layout = QVBoxLayout(self.central)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)

        self.banner = QLabel("Вам пришло новое сообщение!", self)
        self.banner.setStyleSheet(
            "background-color: #0088cc; color: white; "
            "font-size: 16px; font-weight: bold; padding: 10px;"
        )
        self.banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner.hide()
        self.outer_layout.addWidget(self.banner)

        self.content_widget = QWidget(self)
        self.outer_layout.addWidget(self.content_widget)

        self.main_layout = QHBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget(self)
        self.tabs.setFixedWidth(320)

        self.tab_chats = QWidget(self)
        self.tab_chats_layout = QVBoxLayout(self.tab_chats)

        self.profile_label = QLabel(f"👤 {self.username}", self)
        self.profile_label.setStyleSheet(
            "font-weight: bold; font-size: 16px; color: #0088cc;"
        )
        self.profile_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tab_chats_layout.addWidget(self.profile_label)

        self.avatar_label = QLabel(self)
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setStyleSheet(
            "border-radius: 40px; background-color: #333; "
            "color: white; font-size: 40px;"
        )
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setScaledContents(True)
        self.tab_chats_layout.addWidget(
            self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.change_avatar_btn = QPushButton("Сменить аватар", self)
        self.change_avatar_btn.setStyleSheet(
            "background-color: #333; font-size: 12px; padding: 5px;"
        )
        self.change_avatar_btn.clicked.connect(self.change_avatar)
        self.tab_chats_layout.addWidget(self.change_avatar_btn)

        self.search_chat_input = QLineEdit(self)
        self.search_chat_input.setPlaceholderText("Поиск чатов...")
        self.search_chat_input.textChanged.connect(self.filter_chats)
        self.tab_chats_layout.addWidget(self.search_chat_input)

        self.chat_list = QListWidget(self)
        self.chat_list.itemClicked.connect(self.load_chat)
        self.tab_chats_layout.addWidget(self.chat_list)

        self.tab_users = QWidget(self)
        self.tab_users_layout = QVBoxLayout(self.tab_users)

        self.users_label = QLabel("Зарегистрированные пользователи:", self)
        self.tab_users_layout.addWidget(self.users_label)

        self.users_table = QTableWidget(self)
        self.users_table.setColumnCount(1)
        self.users_table.setHorizontalHeaderLabels(["Логин"])
        self.users_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.users_table.verticalHeader().setVisible(False)
        self.users_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.tab_users_layout.addWidget(self.users_table)

        self.tabs.addTab(self.tab_chats, "Мои чаты")
        self.tabs.addTab(self.tab_users, "Пользователи")
        self.main_layout.addWidget(self.tabs)

        self.right_layout = QVBoxLayout()
        self.right_layout.setSpacing(10)

        self.messages = QTextBrowser(self)
        self.messages.setOpenLinks(False)
        self.messages.anchorClicked.connect(self.open_file)
        self.right_layout.addWidget(self.messages)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.setSpacing(10)

        self.attach_btn = QPushButton("📎", self)
        self.attach_btn.setFixedSize(40, 40)
        self.attach_btn.clicked.connect(self.attach_file)
        self.bottom_layout.addWidget(self.attach_btn)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.input_field.returnPressed.connect(self.send_message)
        self.bottom_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Отправить", self)
        self.send_btn.clicked.connect(self.send_message)
        self.bottom_layout.addWidget(self.send_btn)

        self.right_layout.addLayout(self.bottom_layout)
        self.main_layout.addLayout(self.right_layout, 3)

    def show_banner(self, text):
        self.banner.setText(text)
        self.banner.show()
        self.banner_timer.start(3000)

    def hide_banner(self):
        self.banner.hide()

    def show_startup_banner(self):
        self.show_banner(self.startup_text)

    def check_notifications(self):
        has_new = False
        for chat_id, chat_name in self.all_chats:
            unread = self.db.get_unread_count(chat_id, self.username)
            last = self.last_unread.get(chat_id, 0)

            if unread > last:
                if chat_id == self.current_chat_id:
                    self.messages.clear()
                    history = self.db.get_messages(self.current_chat_id)
                    for msg in history:
                        self.display_message(
                            msg["time"], msg["sender"], msg["text"]
                        )
                    self.messages.moveCursor(
                        self.messages.textCursor().MoveOperation.End
                    )
                else:
                    self.show_banner(
                        f"Новое сообщение в чате '{chat_name}'!"
                    )
                    QApplication.alert(self, 0)
                has_new = True

            self.last_unread[chat_id] = unread

        if has_new:
            self.update_chat_list()

    def load_avatar(self):
        avatar_path = self.db.get_avatar(self.username)
        if avatar_path and os.path.exists(avatar_path):
            pixmap = QPixmap(avatar_path)
            self.avatar_label.setPixmap(pixmap)
            self.avatar_label.setText("")
        else:
            self.avatar_label.setText("👤")
            self.avatar_label.setStyleSheet(
                "border-radius: 40px; background-color: #333; "
                "color: white; font-size: 40px; text-align: center;"
            )

    def change_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите аватар", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            if not os.path.exists("avatars"):
                os.makedirs("avatars")
            filename = os.path.basename(file_path)
            new_path = os.path.join("avatars", filename)
            shutil.copy(file_path, new_path)
            self.db.update_avatar(self.username, new_path)
            self.load_avatar()

    def load_data(self):
        self.all_chats = self.db.get_chats(self.username)
        self.update_chat_list()

        users = self.db.get_all_users()
        self.users_table.setRowCount(len(users))
        for i, user in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(user))

        has_startup_unread = False
        self.startup_text = ""
        for chat_id, chat_name in self.all_chats:
            unread = self.db.get_unread_count(chat_id, self.username)
            self.last_unread[chat_id] = unread
            if unread > 0:
                has_startup_unread = True
                self.startup_text = (
                    f"У вас {unread} непрочитанных сообщений "
                    f"в чате '{chat_name}'!"
                )

        if has_startup_unread:
            QTimer.singleShot(500, self.show_startup_banner)

        if self.chat_list.count() > 0 and self.current_chat_id is None:
            self.chat_list.setCurrentRow(0)
            self.load_chat()

    def update_chat_list(self):
        current_id = self.current_chat_id
        self.chat_list.clear()

        for chat_id, chat_name in self.all_chats:
            unread = self.db.get_unread_count(chat_id, self.username)
            if unread > 0:
                display_name = f"{chat_name} ({unread})"
            else:
                display_name = chat_name

            self.chat_list.addItem(display_name)
            self.chat_list.item(self.chat_list.count() - 1).setData(
                1, chat_id
            )

        if current_id is not None:
            for i in range(self.chat_list.count()):
                if self.chat_list.item(i).data(1) == current_id:
                    self.chat_list.setCurrentRow(i)
                    break

    def filter_chats(self, text):
        self.chat_list.clear()
        for chat_id, chat_name in self.all_chats:
            if text.lower() in chat_name.lower():
                unread = self.db.get_unread_count(chat_id, self.username)
                if unread > 0:
                    display_name = f"{chat_name} ({unread})"
                else:
                    display_name = chat_name

                self.chat_list.addItem(display_name)
                self.chat_list.item(self.chat_list.count() - 1).setData(
                    1, chat_id
                )

    def load_chat(self, *args):
        current_item = self.chat_list.currentItem()
        if not current_item:
            return

        self.current_chat_id = current_item.data(1)
        self.db.mark_as_read(self.current_chat_id, self.username)
        self.update_chat_list()
        self.messages.clear()

        history = self.db.get_messages(self.current_chat_id)
        for msg in history:
            self.display_message(msg["time"], msg["sender"], msg["text"])

        self.messages.moveCursor(
            self.messages.textCursor().MoveOperation.End
        )

    def display_message(self, time, sender, text):
        if text.startswith("📎 IMAGE:"):
            self.filename = text.replace("📎 IMAGE:", "").strip()
            self.path = os.path.abspath(
                os.path.join("uploads", self.filename)
            )
            self.url = QUrl.fromLocalFile(self.path).toString()

            self.messages.append(f"<b>[{time}] {sender}:</b>")
            self.messages.insertHtml(
                f'<img src="{self.url}" width="250" '
                f'style="border-radius: 10px; margin-bottom: 10px;"><br>'
            )
        elif text.startswith("📎 FILE:"):
            self.filename = text.replace("📎 FILE:", "").strip()
            self.path = os.path.abspath(
                os.path.join("uploads", self.filename)
            )
            self.url = QUrl.fromLocalFile(self.path).toString()

            self.messages.append(
                f"<b>[{time}] {sender}:</b> отправил файл "
                f'<a href="{self.url}" style="color: #0088cc; '
                f'text-decoration: none;">{self.filename}</a><br>'
            )
        else:
            self.messages.append(f"<b>[{time}] {sender}:</b> {text}<br>")

    def open_file(self, url):
        QDesktopServices.openUrl(url)

    def create_chat(self):
        dialog = CreateChatDialog(self.db, self.username)
        if dialog.exec():
            name, members = dialog.get_data()
            if name:
                self.db.create_chat(name, members)
                self.current_chat_id = None
                self.load_data()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Введите название чата"
                )

    def show_about(self):
        QMessageBox.information(
            self,
            "О программе",
            f"Сашаграмм\nПользователь: {self.username}",
        )

    def export_chat(self):
        if self.current_chat_id is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить чат", "", "Text files (*.txt)"
        )
        if file_path:
            history = self.db.get_messages(self.current_chat_id)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("История чата:\n\n")
                f.writelines(
                    f"[{msg['time']}] {msg['sender']}: {msg['text']}\n"
                    for msg in history
                )
            QMessageBox.information(self, "Успех", "Чат экспортирован!")

    def send_message(self):
        text = self.input_field.text().strip()
        if not text or self.current_chat_id is None:
            return

        self.db.add_message(self.current_chat_id, self.username, text)
        self.input_field.clear()

        self.messages.append(
            f"<b>[Сейчас] {self.username}:</b> {text}<br>"
        )
        self.messages.moveCursor(
            self.messages.textCursor().MoveOperation.End
        )

        self.last_unread[self.current_chat_id] = 0
        self.update_chat_list()

    def attach_file(self):
        if self.current_chat_id is None:
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Файл слишком большой! Максимум 50 МБ.",
                )
                return

            filename = os.path.basename(file_path)
            if not os.path.exists("uploads"):
                os.makedirs("uploads")

            shutil.copy(file_path, os.path.join("uploads", filename))

            if filename.lower().endswith(
                (".png", ".jpg", ".jpeg", ".gif")
            ):
                text = f"📎 IMAGE:{filename}"
            else:
                text = f"📎 FILE:{filename}"

            self.db.add_message(self.current_chat_id, self.username, text)

            if text.startswith("📎 IMAGE:"):
                self.filename = text.replace("📎 IMAGE:", "").strip()
                self.path = os.path.abspath(
                    os.path.join("uploads", self.filename)
                )
                self.url = QUrl.fromLocalFile(self.path).toString()

                self.messages.append(
                    f"<b>[Сейчас] {self.username}:</b>"
                )
                self.messages.insertHtml(
                    f'<img src="{self.url}" width="250" '
                    f'style="border-radius: 10px; '
                    f'margin-bottom: 10px;"><br>'
                )
            else:
                self.filename = text.replace("📎 FILE:", "").strip()
                self.path = os.path.abspath(
                    os.path.join("uploads", self.filename)
                )
                self.url = QUrl.fromLocalFile(self.path).toString()

                self.messages.append(
                    f"<b>[Сейчас] {self.username}:</b> отправил файл "
                    f'<a href="{self.url}" style="color: #0088cc; '
                    f'text-decoration: none;">{self.filename}</a><br>'
                )

            self.messages.moveCursor(
                self.messages.textCursor().MoveOperation.End
            )
            self.last_unread[self.current_chat_id] = 0
            self.update_chat_list()