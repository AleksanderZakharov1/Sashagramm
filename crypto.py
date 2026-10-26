from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def encrypt_message(text):
    key = load_key()
    f = Fernet(key)
    encrypted = f.encrypt(text.encode())
    return encrypted.decode()

def decrypt_message(encrypted_text):
    key = load_key()
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_text.encode())
    return decrypted.decode()