import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def read_key(filename):
    file = open(filename, 'rb')
    file_key = file.read();
    file.close();
    return file_key

def generate_key(password_provided):
    password = password_provided.encode()
    salt = b'\xe9\x1e9\x81T\x8b\x08\xfcl\x93R\xacr\x8a\xac\xa4'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256,
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    generated_key = base64.urlsafe_b64encode(kdf.derive(password))
    return generated_key

def encryptString(key, message):
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message

def decryptToBytes(key, message):
    f = Fernet(key)
    decrypted_message = f.decrypt(message)
    return decrypted_message.decode()
