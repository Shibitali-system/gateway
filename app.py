from flask import Flask, request, render_template_string
import json
import time

# Simulate your_functions
class Functions:
    @staticmethod
    def encrypt_string(data, username, password):
        return "encrypted_data_mock"

    @staticmethod
    def checksum_cal(data):
        return "checksum_mock"

    @staticmethod
    def encrypt_sha(data, secret):
        return "privatekey_mock"

app = Flask(__name__)

# Hard-coded credentials (Production)
MERCID = "247167"
USERNAME = "3072982"
PASSWORD = "0764760075Ana"
SECRET = "JDWZ2ncNxhhTcXj7"

PAYMENT_URL = "https://payments.airpay.tz/pay/v1/index.php"

@app.route("/")
def home():
    return "Airpay Gateway Live"

@app.route("/sendtoairpay", methods=["POST"])
def send_to_airpay():
    try:
        amount_raw = float(request.form.get("amount", 0))
        orderid_raw = request.form.get("orderid", f"ORD{int(time.time()) % 1000000}")

        post_data = {
            "buyer_email": request.form.get("buyerEmail"),
            "buyer_firstname": request.form.get("buyerFirstName"),
            "buyer_lastname": request.form.get("buyerLastName"),
            "buyer_address": request.form.get("buyerAddress") or "N/A",
            "buyer_city": request.form.get("buyerCity") or "Dar es Salaam",
            "buyer_state": request.form.get("buyerState") or "Dar es Salaam",
            "buyer_country": request.form.get("buyerCountry") or "Tanzania",
            "buyer_phone": request.form.get("buyerPhone"),
            "buyer_pincode": request.form.get("buyerPinCode") or "123456",
            "amount": f"{amount_raw:.2f}",
            "orderid": orderid_raw[:20],
            "iso_currency": request.form.get("isocurrency", "TZS"),
            "currency_code": request.form.get("currency", "834"),
            "merchant_id": MERCID,
        }

        data_json = json.dumps(post_data)
        encdata = Functions.encrypt_string(data_json, USERNAME, PASSWORD)
        checksum = Functions.checksum_cal(post_data)
        private_key = Functions.encrypt_sha(f"{USERNAME}:|:{PASSWORD}", SECRET)

        print("===== AIRPAY DEBUG =====")
        print("Post Data:", json.dumps(post_data, indent=4))
        print("EncData:", encdata)
        print("Checksum:", checksum)
        print("PrivateKey:", private_key)
        print("========================")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redirecting to Airpay</title>
        </head>
        <body onload="document.forms[0].submit()">
            <form method="post" action="{PAYMENT_URL}">
                <input type="hidden" name="merchant_id" value="{MERCID}">
                <input type="hidden" name="privatekey" value="{private_key}">
                <input type="hidden" name="encdata" value='{encdata}'>
                <input type="hidden" name="checksum" value="{checksum}">
            </form>
            <p>Redirecting to Airpay, please wait...</p>
        </body>
        </html>
        """
        return render_template_string(html)

    except Exception as e:
        print("Error in send_to_airpay:", str(e))
        return f"Error: {str(e)}", 500
