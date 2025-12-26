import hashlib, base64, json, zlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class Functions:
    @staticmethod
    def encrypt_string(my_string, username, password):
        secret_key = hashlib.md5((username + "~:~" + password).encode()).hexdigest()
        iv = 'c0f9e2d16031b0ce'
        cipher = AES.new(secret_key.encode(), AES.MODE_CBC, iv.encode())
        encrypted_data = cipher.encrypt(pad(my_string.encode(), AES.block_size))
        return iv + base64.b64encode(encrypted_data).decode()

    @staticmethod
    def decrypt_string(encrypted_data, username, password):
        secret_key = hashlib.md5((username + "~:~" + password).encode()).hexdigest()
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]
        cipher = AES.new(secret_key.encode(), AES.MODE_CBC, iv.encode())
        decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data))
        return unpad(decrypted_data, AES.block_size).decode()

    @staticmethod
    def encrypt_sha(data, salt):
        return hashlib.sha256((salt + '@' + data).encode()).hexdigest()

    @staticmethod
    def checksum_cal(post_data):
        sorted_data = sorted(post_data.items(), key=lambda x: x[0])
        data = ''.join([str(v) for _, v in sorted_data])
        return hashlib.sha256((data).encode()).hexdigest()

    @staticmethod
    def send_post_data(url, post_data):
        import requests
        try:
            response = requests.post(url, data=post_data)
            return response.text
        except Exception as e:
            return json.dumps({"error": str(e)})
