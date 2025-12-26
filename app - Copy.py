from flask import Flask, request, render_template_string
import json
import time
from your_functions import Functions  # hakikisha hii ipo kwenye project yako

app = Flask(__name__)

# ⚠️ Hard-coded production credentials (badilisha unapohitaji)
MERCID = '247167'
USERNAME = '3072982'
PASSWORD = '0764760075Ana'
SECRET = 'JDWZ2ncNxhhTcXj7'
CLIENT_ID = '2fdf34'
CLIENT_SECRET = '25f509db787e868538a44e1f507ef248'

PAYMENT_URL = 'https://payments.airpay.tz/pay/v1/index.php'

@app.route("/")
def home():
    return "Airpay Gateway Live"

@app.route("/sendtoairpay", methods=["POST"])
def send_to_airpay():
    try:
        # 1️⃣ Chukua data kutoka form
        amount_raw = float(request.form.get('amount', 0))
        orderid_raw = request.form.get('orderid', f"ORD{int(time.time()) % 1000000}")[:20]

        post_data = {
            'buyer_email': request.form.get('buyerEmail'),
            'buyer_firstname': request.form.get('buyerFirstName'),
            'buyer_lastname': request.form.get('buyerLastName'),
            'buyer_address': request.form.get('buyerAddress') or "N/A",
            'buyer_city': request.form.get('buyerCity') or "Dar es Salaam",
            'buyer_state': request.form.get('buyerState') or "Dar es Salaam",
            'buyer_country': request.form.get('buyerCountry') or "Tanzania",
            'buyer_phone': request.form.get('buyerPhone'),
            'buyer_pincode': request.form.get('buyerPinCode') or "123456",
            'amount': f"{amount_raw:.2f}",
            'orderid': orderid_raw,
            'iso_currency': request.form.get('isocurrency', "TZS"),
            'currency_code': request.form.get('currency', "834"),
            'merchant_id': MERCID
        }

        # 2️⃣ Encrypt payload
        data_json = json.dumps(post_data)
        encdata = Functions.encrypt_string(data_json, USERNAME, PASSWORD)
        checksum = Functions.checksum_cal(post_data)
        private_key = Functions.encrypt_sha(f"{USERNAME}:|:{PASSWORD}", SECRET)

        # 3️⃣ Debug console
        print("===== AIRPAY DEBUG =====")
        print("Post Data:", json.dumps(post_data, indent=4))
        print("EncData:", encdata)
        print("Checksum:", checksum)
        print("PrivateKey:", private_key)
        print("========================")

        # 4️⃣ Auto-submit HTML
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


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
