import json
import hashlib
import os
import crypto
from datetime import datetime

DB_FILE = "database.json"


def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": [], "chats": [], "messages": []}, f)


def load_data():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "chats" not in data: data["chats"] = []
    if "messages" not in data: data["messages"] = []
    return data


def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(login, password, username):
    data = load_data()
    for user in data["users"]:
        if user["login"] == login:
            return False
    new_user = {"login": login, "password": hash_password(password), "username": username}
    data["users"].append(new_user)
    save_data(data)
    return True


def login_user(login, password):
    data = load_data()
    hashed = hash_password(password)
    for user in data["users"]:
        if user["login"] == login and user["password"] == hashed:
            return user["username"]
    return None


def get_chats():
    data = load_data()
    if not data["chats"]:
        data["chats"] = [{"id": 1, "name": "Общий чат"}]
        save_data(data)
    return data["chats"]


def create_chat(name):
    data = load_data()
    new_id = len(data["chats"]) + 1
    data["chats"].append({"id": new_id, "name": name})
    save_data(data)


def add_message(chat_id, sender, text):
    data = load_data()
    time_now = datetime.now().strftime("%H:%M")
    encrypted_text = crypto.encrypt_message(text)

    new_msg = {
        "chat_id": chat_id,
        "sender": sender,
        "text": encrypted_text,
        "time": time_now
    }
    data["messages"].append(new_msg)
    save_data(data)


def get_messages(chat_id):
    data = load_data()
    chat_msgs = []
    for msg in data["messages"]:
        if msg["chat_id"] == chat_id:
            try:
                decrypted = crypto.decrypt_message(msg["text"])
            except:
                decrypted = "[Ошибка расшифровки]"

            chat_msgs.append({
                "sender": msg["sender"],
                "text": decrypted,
                "time": msg["time"]
            })
    return chat_msgs