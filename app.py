from flask import Flask, request, render_template_string
import json
import os
from your_functions import Functions

app = Flask(__name__)

# ⚠️ BADILISHA HIZI ZIWE ENV VARIABLES BAADAYE
mercid = '247167'
username = '3072982'
password = '0764760075Ana'
secret = 'JDWZ2ncNxhhTcXj7'
client_id = '2fdf34'
client_secret = '25f509db787e868538a44e1f507ef248'

PAYMENT_URL = 'https://payments.airpay.tz/pay/v1/index.php'

from flask import render_template

@app.route("/transaction")
def transaction():
    return render_template("transaction.html")


@app.route("/")
def home():
    return "Airpay Gateway Live"

# 🔑 HII NDIO ROUTE SAHIHI
@app.route("/sendtoairpay", methods=["POST"])
def send_to_airpay():

    # 1️⃣ Chukua data kutoka form / curl
    post_data = {
        'buyer_email': request.form.get('buyerEmail'),
        'buyer_firstname': request.form.get('buyerFirstName'),
        'buyer_lastname': request.form.get('buyerLastName'),
        'buyer_address': request.form.get('buyerAddress'),
        'buyer_city': request.form.get('buyerCity'),
        'buyer_state': request.form.get('buyerState'),
        'buyer_country': request.form.get('buyerCountry'),
        'buyer_phone': request.form.get('buyerPhone'),
        'buyer_pincode': request.form.get('buyerPinCode'),
        'amount': request.form.get('amount'),
        'orderid': request.form.get('orderid'),
        'iso_currency': request.form.get('isocurrency'),
        'currency_code': request.form.get('currency'),
        'merchant_id': mercid
    }

    # 2️⃣ Encrypt payload
    data_json = json.dumps(post_data)
    encdata = Functions.encrypt_string(data_json, username, password)
    checksum = Functions.checksum_cal(post_data)
    private_key = Functions.encrypt_sha(username + ":|:" + password, secret)

    # 3️⃣ HTML ya auto-submit (hakuna template file)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Redirecting to Airpay</title>
    </head>
    <body onload="document.forms[0].submit()">
        <form method="post" action="{PAYMENT_URL}">
            <input type="hidden" name="merchant_id" value="{mercid}">
            <input type="hidden" name="privatekey" value="{private_key}">
            <input type="hidden" name="encdata" value='{encdata}'>
            <input type="hidden" name="checksum" value="{checksum}">
        </form>
        <p>Redirecting to Airpay, please wait...</p>
    </body>
    </html>
    """

    return render_template_string(html)

# ✅ RENDER-READY
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
