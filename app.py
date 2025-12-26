# app.py
from flask import Flask, render_template, request, redirect, url_for
import os
import json
import hashlib
import base64
import zlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

app = Flask(__name__)

# === Load environment variables ===
MERCID = os.environ.get("MERCID", "247167")
USERNAME = os.environ.get("USERNAME", "3072982")
PASSWORD = os.environ.get("PASSWORD", "0764760075Ana")
SECRET = os.environ.get("SECRET", "JDWZ2ncNxhhTcXj7")
CLIENT_ID = os.environ.get("CLIENT_ID", "2fdf34")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "25f509db787e868538a44e1f507ef248")
TOKEN_URL = os.environ.get("TOKEN_URL", "https://kraken.airpay.tz/airpay/pay/v1/api/oauth2")
PAYMENT_URL = os.environ.get("PAYMENT_URL", "https://payments.airpay.tz/pay/v1/index.php")

# === Helper functions ===
class Functions:
    @staticmethod
    def encrypt_string(my_string, username, password):
        secret_key = hashlib.md5((username + "~:~" + password).encode()).hexdigest()
        iv = 'c0f9e2d16031b0ce'
        cipher = AES.new(secret_key.encode(), AES.MODE_CBC, iv.encode())
        encrypted_data = cipher.encrypt(pad(my_string.encode(), AES.block_size))
        data = iv + base64.b64encode(encrypted_data).decode()
        return data

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
        data = ''.join([str(value) for _, value in sorted_data])
        return hashlib.sha256(data.encode()).hexdigest()

# === Routes ===
@app.route("/")
def home():
    return "Airpay Gateway Live!"

@app.route("/transaction.html")
def transaction():
    return render_template("transaction.html")

@app.route("/sendtoairpay", methods=["POST"])
def sendtoairpay():
    # Collect form data
    form = request.form
    post_data = {
        'buyer_email': form.get('buyerEmail'),
        'buyer_firstname': form.get('buyerFirstName'),
        'buyer_lastname': form.get('buyerLastName'),
        'buyer_address': form.get('buyerAddress'),
        'buyer_city': form.get('buyerCity'),
        'buyer_state': form.get('buyerState'),
        'buyer_country': form.get('buyerCountry'),
        'amount': form.get('amount'),
        'orderid': form.get('orderid'),
        'buyer_phone': form.get('buyerPhone'),
        'buyer_pincode': form.get('buyerPinCode'),
        'iso_currency': form.get('isocurrency'),
        'currency_code': form.get('currency'),
        'merchant_id': MERCID,
        'mer_dom': base64.b64encode(b'http://track.airpay.co.in').decode('utf-8')
    }

    # Encrypt request data
    data_json = json.dumps(post_data)
    request_data = Functions.encrypt_string(data_json, USERNAME, PASSWORD)
    checksum_req = Functions.checksum_cal(post_data)

    # Render auto-submit form to Airpay
    return render_template("sendtoairpaypage.html",
                           encdata=request_data,
                           checksum=checksum_req,
                           privatekey=Functions.encrypt_sha(USERNAME + ":|:" + PASSWORD, SECRET),
                           merchant_id=MERCID,
                           url=PAYMENT_URL)

@app.route("/responsefromairpay", methods=["POST"])
def responsefromairpay():
    response_data = request.form.get("response")
    if not response_data:
        return "No response received from Airpay", 400

    try:
        decrypted = Functions.decrypt_string(response_data, USERNAME, PASSWORD)
        data = json.loads(decrypted)
        return render_template("response.html", data=data)
    except Exception as e:
        return f"Error decoding response: {str(e)}", 500

# === Run App ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
