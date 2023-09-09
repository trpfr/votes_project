import os

from Crypto.Cipher import AES
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import base64


# Функция генерации случайно мастер-фразу для ZKP
def generate_phrase():
    phrase = os.urandom(32)
    return str(phrase)


# Функция генерации ключей для шифрования голосов
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return public_key, private_key


# Функции сериализации приватных и публичных ключей
def serialize_private_key(private_key):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()


def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

def sign_results(results, private_key):
    try:
        # Создание подписи
        signature = private_key.sign(
            results.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        # Возвращаем подпись в формате base64 для удобства
        return base64.b64encode(signature).decode()
    except:
        return None


def verify_signature(results, signature, public_key):
    try:
        # Декодирование подписи из формата base64
        signature_bytes = base64.b64decode(signature)
        # Верификация подписи
        public_key.verify(
            signature_bytes,
            results.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False
# Функции шифрования и расшифровки голосов
def encrypt_vote(vote, public_key):
    try:
        encrypted_vote = public_key.encrypt(
            str(vote).encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_vote).decode()
    except:
        return None


def decrypt_vote(encrypted_vote, private_key):
    try:
        decoded_vote = base64.b64decode(encrypted_vote)
        decrypted_vote = private_key.decrypt(
            decoded_vote,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_vote.decode()
    except Exception as e:
        print(e)
        return None
