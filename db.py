import datetime
import sqlite3

from cryptography.fernet import InvalidToken

import crypto
from utils import hash_password

DB_NAME = "messenger.db"


class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.create_tables()

    def get_connection(self):
        self.conn = sqlite3.connect(
            DB_NAME, check_same_thread=False, timeout=10
        )
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def create_tables(self):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                avatar_path TEXT
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                chat_id INTEGER,
                login TEXT,
                last_read_msg_id INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, login),
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
                FOREIGN KEY (login) REFERENCES users(login) ON DELETE CASCADE
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                sender TEXT,
                msg_text TEXT,
                msg_time TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
                FOREIGN KEY (sender) REFERENCES users(login) ON DELETE CASCADE
            )
            """
        )
        self.conn.commit()
        self.conn.close()

    def register_user(self, login, password):
        login = login.strip()
        if not login or not password:
            return False

        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT id FROM users WHERE login = ?", (login,)
        )
        user = self.cursor.fetchone()

        if user:
            self.conn.close()
            return False

        self.cursor.execute(
            "INSERT INTO users (login, password) VALUES (?, ?)",
            (login, hash_password(password)),
        )
        self.conn.commit()
        self.conn.close()
        return True

    def login_user(self, login, password):
        login = login.strip()
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT login FROM users WHERE login = ? AND password = ?",
            (login, hash_password(password)),
        )
        user = self.cursor.fetchone()
        self.conn.close()
        return user[0] if user else None

    def get_avatar(self, login):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT avatar_path FROM users WHERE login = ?", (login,)
        )
        row = self.cursor.fetchone()
        self.conn.close()
        return row[0] if row and row[0] else None

    def update_avatar(self, login, path):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "UPDATE users SET avatar_path = ? WHERE login = ?",
            (path, login),
        )
        self.conn.commit()
        self.conn.close()

    def get_all_users(self):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT login FROM users ORDER BY login")
        rows = self.cursor.fetchall()
        self.conn.close()
        return [row[0] for row in rows]

    def search_users(self, text):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT login FROM users WHERE login LIKE ?", (f"%{text}%",)
        )
        rows = self.cursor.fetchall()
        self.conn.close()
        return [row[0] for row in rows]

    def get_chats(self, username):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT id FROM chats WHERE name = 'Общий чат'"
        )
        general_chat = self.cursor.fetchone()

        if not general_chat:
            self.cursor.execute(
                "INSERT INTO chats (name) VALUES ('Общий чат')"
            )
            general_chat_id = self.cursor.lastrowid
        else:
            general_chat_id = general_chat[0]

        self.cursor.execute(
            "SELECT 1 FROM members WHERE chat_id = ? AND login = ?",
            (general_chat_id, username),
        )
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO members "
                "(chat_id, login, last_read_msg_id) VALUES (?, ?, 0)",
                (general_chat_id, username),
            )
        self.conn.commit()

        self.cursor.execute(
            "SELECT c.id, c.name FROM chats c "
            "JOIN members m ON c.id = m.chat_id "
            "WHERE m.login = ? ORDER BY c.id ASC",
            (username,),
        )
        chats = self.cursor.fetchall()
        self.conn.close()
        return chats

    def create_chat(self, name, members):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute("INSERT INTO chats (name) VALUES (?)", (name,))
        chat_id = self.cursor.lastrowid

        for member in members:
            self.cursor.execute(
                "INSERT INTO members "
                "(chat_id, login, last_read_msg_id) VALUES (?, ?, 0)",
                (chat_id, member),
            )
        self.conn.commit()
        self.conn.close()

    def add_message(self, chat_id, sender, text):
        time_str = datetime.datetime.now().strftime("%H:%M")
        enc_text = crypto.encrypt_message(text)

        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "INSERT INTO messages "
            "(chat_id, sender, msg_text, msg_time) VALUES (?, ?, ?, ?)",
            (chat_id, sender, enc_text, time_str),
        )
        self.conn.commit()

        self.cursor.execute(
            "SELECT MAX(id) FROM messages WHERE chat_id = ?", (chat_id,)
        )
        max_id = self.cursor.fetchone()[0]

        self.cursor.execute(
            "UPDATE members SET last_read_msg_id = ? "
            "WHERE chat_id = ? AND login = ?",
            (max_id, chat_id, sender),
        )
        self.conn.commit()
        self.conn.close()

    def get_messages(self, chat_id):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT id, sender, msg_text, msg_time FROM messages "
            "WHERE chat_id = ? ORDER BY id",
            (chat_id,),
        )
        rows = self.cursor.fetchall()
        self.conn.close()

        messages = []
        for row in rows:
            try:
                dec_text = crypto.decrypt_message(row[2])
            except (InvalidToken, ValueError, TypeError):
                dec_text = "[Ошибка]"
            messages.append(
                {
                    "id": row[0],
                    "sender": row[1],
                    "text": dec_text,
                    "time": row[3],
                }
            )
        return messages

    def get_unread_count(self, chat_id, username):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT last_read_msg_id FROM members "
            "WHERE chat_id = ? AND login = ?",
            (chat_id, username),
        )
        row = self.cursor.fetchone()
        last_read = row[0] if row else 0

        self.cursor.execute(
            "SELECT COUNT(*) FROM messages "
            "WHERE chat_id = ? AND id > ? AND sender != ?",
            (chat_id, last_read, username),
        )
        count = self.cursor.fetchone()[0]
        self.conn.close()
        return count

    def mark_as_read(self, chat_id, username):
        self.conn = self.get_connection()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "SELECT MAX(id) FROM messages WHERE chat_id = ?", (chat_id,)
        )
        max_id = self.cursor.fetchone()[0]

        if max_id:
            self.cursor.execute(
                "UPDATE members SET last_read_msg_id = ? "
                "WHERE chat_id = ? AND login = ?",
                (max_id, chat_id, username),
            )
            self.conn.commit()
        self.conn.close()