from flask import Flask, request, render_template_string
import json
import hashlib
from your_functions import Functions  # Class yako ya Functions

app = Flask(__name__)

mercid = '247167'
username = '3072982'
password = '0764760075Ana'
secret ='JDWZ2ncNxhhTcXj7'
client_id = '2fdf34'
client_secret = '25f509db787e868538a44e1f507ef248'
token_url='https://kraken.airpay.tz/airpay/pay/v1/api/oauth2'
url='https://payments.airpay.tz/pay/v1/index.php '

@app.route('/send', methods=['POST'])
def send_to_airpay():
    # Extract form data
    buyer_email = request.form.get('buyerEmail')
    buyer_firstname = request.form.get('buyerFirstName')
    buyer_lastname = request.form.get('buyerLastName')
    buyer_address = request.form.get('buyerAddress')
    buyer_city = request.form.get('buyerCity')
    buyer_state = request.form.get('buyerState')
    buyer_country = request.form.get('buyerCountry')
    amount = request.form.get('amount')
    orderid = request.form.get('orderid')
    buyer_phone = request.form.get('buyerPhone')
    buyer_pincode = request.form.get('buyerPinCode')
    iso_currency = request.form.get('isocurrency')
    currency_code = request.form.get('currency')

    # Prepare post data
    post_data = {
        'buyer_email': buyer_email,
        'buyer_firstname': buyer_firstname,
        'buyer_lastname': buyer_lastname,
        'buyer_address': buyer_address,
        'buyer_city': buyer_city,
        'buyer_state': buyer_state,
        'buyer_country': buyer_country,
        'amount': amount,
        'orderid': orderid,
        'buyer_phone': buyer_phone,
        'buyer_pincode': buyer_pincode,
        'iso_currency': iso_currency,
        'currency_code': currency_code,
        'merchant_id': mercid,
    }

    # Example: get access token and encrypt data like your script
    request_dict = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'merchant_id': mercid
    }
    request_string=json.dumps(request_dict)
    encrypted_request = Functions.encrypt_string(request_string, username, password)
    checksum_req = Functions.checksum_cal(post_data)

    # Encrypt post_data
    data_json = json.dumps(post_data)
    request_data = Functions.encrypt_string(data_json, username, password)
    private_key = Functions.encrypt_sha(username + ":|:" + password, secret)

    url_with_token = url + "?token=" + "ACCESS_TOKEN_HERE"  # Replace with real access token

    # Render auto-submit HTML
    html_content = f"""
    <html>
    <head><title>Airpay Redirect</title></head>
    <body onload="document.forms[0].submit()">
        <form method="post" action="{url_with_token}">
            <input type="hidden" name="privatekey" value="{private_key}">
            <input type="hidden" name="merchant_id" value="{mercid}">
            <input type="hidden" name="encdata" value='{request_data}'>
            <input type="hidden" name="checksum" value="{checksum_req}">
        </form>
        <p>Redirecting to Airpay... Please do not refresh or press back</p>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
