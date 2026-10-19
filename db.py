import json
import hashlib
import os

DB_FILE = "database.json"


def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": []}, f)


def load_data():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


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

    new_user = {
        "login": login,
        "password": hash_password(password),
        "username": username
    }
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