import hashlib
import base64
import json
import zlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class Functions:

    @staticmethod
    def encrypt_string(plain_text, username, password):
        key = hashlib.md5((username + "~:~" + password).encode()).digest()
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
        return base64.b64encode(iv + encrypted).decode()

    @staticmethod
    def decrypt_string(enc_text, username, password):
        raw = base64.b64decode(enc_text)
        iv = raw[:16]
        key = hashlib.md5((username + "~:~" + password).encode()).digest()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(raw[16:]), AES.block_size)
        return decrypted.decode()

    @staticmethod
    def encrypt_sha(data, secret):
        return hashlib.sha256((data + secret).encode()).hexdigest()

    @staticmethod
    def checksum_cal(data_dict):
        raw = "|".join(str(v) for v in data_dict.values() if v)
        return zlib.crc32(raw.encode()) & 0xffffffff
