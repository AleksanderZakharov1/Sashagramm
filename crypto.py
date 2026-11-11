import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


def get_key():
    key = os.getenv("SECRET_KEY")
    if not key:
        raise ValueError("Ключ SECRET_KEY не найден в .env")
    return key.encode()


def encrypt_message(text):
    f = Fernet(get_key())
    return f.encrypt(text.encode()).decode()


def decrypt_message(encrypted_text):
    f = Fernet(get_key())
    return f.decrypt(encrypted_text.encode()).decode()
