import sqlite3
import crypto
import datetime
import os
from utils import hash_password

DB_NAME = "messenger.db"


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False, timeout=10)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, login TEXT UNIQUE NOT NULL, password TEXT NOT NULL, avatar_path TEXT)")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS members (chat_id INTEGER, login TEXT, last_read_msg_id INTEGER DEFAULT 0, PRIMARY KEY (chat_id, login), FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE, FOREIGN KEY (login) REFERENCES users(login) ON DELETE CASCADE)")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER, sender TEXT, msg_text TEXT, msg_time TEXT, FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE, FOREIGN KEY (sender) REFERENCES users(login) ON DELETE CASCADE)")
        self.conn.commit()

    def register_user(self, login, password):
        self.login = login.strip()
        self.password = password
        if not self.login or not self.password:
            return False
        self.cursor.execute("SELECT id FROM users WHERE login = ?", (self.login,))
        self.user = self.cursor.fetchone()
        if self.user:
            return False
        self.cursor.execute("INSERT INTO users (login, password) VALUES (?, ?)",
                            (self.login, hash_password(self.password)))
        self.conn.commit()
        return True

    def login_user(self, login, password):
        self.login = login.strip()
        self.password = password
        self.cursor.execute("SELECT login FROM users WHERE login = ? AND password = ?",
                            (self.login, hash_password(self.password)))
        self.user = self.cursor.fetchone()
        if self.user:
            return self.user[0]
        return None

    def get_avatar(self, login):
        self.cursor.execute("SELECT avatar_path FROM users WHERE login = ?", (login,))
        self.row = self.cursor.fetchone()
        if self.row and self.row[0]:
            return self.row[0]
        return None

    def update_avatar(self, login, path):
        self.cursor.execute("UPDATE users SET avatar_path = ? WHERE login = ?", (path, login))
        self.conn.commit()

    def get_all_users(self):
        self.cursor.execute("SELECT login FROM users ORDER BY login")
        self.rows = self.cursor.fetchall()
        self.users = []
        for self.row in self.rows:
            self.users.append(self.row[0])
        return self.users

    def search_users(self, text):
        self.text = text
        self.cursor.execute("SELECT login FROM users WHERE login LIKE ?", (f"%{self.text}%",))
        self.rows = self.cursor.fetchall()
        self.users = []
        for self.row in self.rows:
            self.users.append(self.row[0])
        return self.users

    def get_chats(self, username):
        self.username = username
        self.cursor.execute("SELECT id FROM chats WHERE name = 'Общий чат'")
        self.general_chat = self.cursor.fetchone()

        if not self.general_chat:
            self.cursor.execute("INSERT INTO chats (name) VALUES ('Общий чат')")
            self.general_chat_id = self.cursor.lastrowid
            self.conn.commit()
        else:
            self.general_chat_id = self.general_chat[0]

        self.cursor.execute("SELECT 1 FROM members WHERE chat_id = ? AND login = ?",
                            (self.general_chat_id, self.username))
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO members (chat_id, login, last_read_msg_id) VALUES (?, ?, 0)",
                                (self.general_chat_id, self.username))
            self.conn.commit()

        self.cursor.execute(
            "SELECT c.id, c.name FROM chats c JOIN members m ON c.id = m.chat_id WHERE m.login = ? ORDER BY c.id ASC",
            (self.username,))
        self.chats = self.cursor.fetchall()
        return self.chats

    def create_chat(self, name, members):
        self.name = name
        self.members = members
        self.cursor.execute("INSERT INTO chats (name) VALUES (?)", (self.name,))
        self.chat_id = self.cursor.lastrowid
        for self.member in self.members:
            self.cursor.execute("INSERT INTO members (chat_id, login, last_read_msg_id) VALUES (?, ?, 0)",
                                (self.chat_id, self.member))
        self.conn.commit()

    def add_message(self, chat_id, sender, text):
        self.chat_id = chat_id
        self.sender = sender
        self.text = text
        self.time_str = datetime.datetime.now().strftime("%H:%M")
        self.enc_text = crypto.encrypt_message(self.text)
        self.cursor.execute("INSERT INTO messages (chat_id, sender, msg_text, msg_time) VALUES (?, ?, ?, ?)",
                            (self.chat_id, self.sender, self.enc_text, self.time_str))
        self.conn.commit()

        self.cursor.execute("SELECT MAX(id) FROM messages WHERE chat_id = ?", (self.chat_id,))
        self.max_id = self.cursor.fetchone()[0]
        self.cursor.execute("UPDATE members SET last_read_msg_id = ? WHERE chat_id = ? AND login = ?",
                            (self.max_id, self.chat_id, self.sender))
        self.conn.commit()

    def get_messages(self, chat_id):
        self.chat_id = chat_id
        self.cursor.execute("SELECT id, sender, msg_text, msg_time FROM messages WHERE chat_id = ? ORDER BY id",
                            (self.chat_id,))
        self.rows = self.cursor.fetchall()

        self.messages = []
        for self.row in self.rows:
            try:
                self.dec_text = crypto.decrypt_message(self.row[2])
            except Exception:
                self.dec_text = "[Ошибка]"
            self.messages.append({"id": self.row[0], "sender": self.row[1], "text": self.dec_text, "time": self.row[3]})
        return self.messages

    def get_unread_count(self, chat_id, username):
        self.chat_id = chat_id
        self.username = username
        self.cursor.execute("SELECT last_read_msg_id FROM members WHERE chat_id = ? AND login = ?",
                            (self.chat_id, self.username))
        self.row = self.cursor.fetchone()
        self.last_read = self.row[0] if self.row else 0

        self.cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = ? AND id > ? AND sender != ?",
                            (self.chat_id, self.last_read, self.username))
        return self.cursor.fetchone()[0]

    def mark_as_read(self, chat_id, username):
        self.chat_id = chat_id
        self.username = username
        self.cursor.execute("SELECT MAX(id) FROM messages WHERE chat_id = ?", (self.chat_id,))
        self.max_id = self.cursor.fetchone()[0]
        if self.max_id:
            self.cursor.execute("UPDATE members SET last_read_msg_id = ? WHERE chat_id = ? AND login = ?",
                                (self.max_id, self.chat_id, self.username))
            self.conn.commit()