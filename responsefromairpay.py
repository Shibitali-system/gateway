from flask import Flask, request, render_template, render_template_string
import os, json, hashlib, zlib
from your_functions import Functions

app = Flask(__name__)

# Environment variables
MERCID = os.environ.get("AIRPAY_MERCHANT_ID")
USERNAME = os.environ.get("AIRPAY_USERNAME")
PASSWORD = os.environ.get("AIRPAY_PASSWORD")
SECRET = os.environ.get("AIRPAY_SECRET")
CLIENT_ID = os.environ.get("AIRPAY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("AIRPAY_CLIENT_SECRET")
TOKEN_URL = 'https://kraken.airpay.tz/airpay/pay/v1/api/oauth2'
PAY_URL = 'https://payments.airpay.tz/pay/v1/index.php'

@app.route('/')
def index():
    return render_template('transaction.html')

@app.route('/send', methods=['POST'])
def send_to_airpay():
    # Collect form data
    post_data = {k: request.form.get(k) for k in [
        'buyerEmail','buyerFirstName','buyerLastName','buyerAddress','buyerCity',
        'buyerState','buyerCountry','amount','orderid','buyerPhone','buyerPinCode',
        'isocurrency','currency'
    ]}
    post_data['merchant_id'] = MERCID

    # Prepare OAuth2 request
    request_dict = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'merchant_id': MERCID
    }
    request_string = json.dumps(request_dict)
    encrypted_request = Functions.encrypt_string(request_string, USERNAME, PASSWORD)
    checksum_req = Functions.checksum_cal(post_data)
    data_json = json.dumps(post_data)
    request_data = Functions.encrypt_string(data_json, USERNAME, PASSWORD)
    private_key = Functions.encrypt_sha(USERNAME + ":|:" + PASSWORD, SECRET)

    # Get access token
    req = {
        'merchant_id': MERCID,
        'encdata': encrypted_request,
        'checksum': Functions.checksum_cal(request_dict)
    }
    token_json = Functions.send_post_data(TOKEN_URL, req)
    token_data = json.loads(token_json)
    decrypt_data = Functions.decrypt_string(token_data['response'], USERNAME, PASSWORD)
    token_response = json.loads(decrypt_data)
    access_token = token_response['data']['access_token']

    pay_url = PAY_URL + "?token=" + access_token

    # Auto-submit HTML
    html_content = f"""
    <html>
    <head><title>Redirecting to Airpay</title></head>
    <body onload="document.forms[0].submit()">
        <form method="post" action="{pay_url}">
            <input type="hidden" name="privatekey" value="{private_key}">
            <input type="hidden" name="merchant_id" value="{MERCID}">
            <input type="hidden" name="encdata" value='{request_data}'>
            <input type="hidden" name="checksum" value="{checksum_req}">
        </form>
        <p>Redirecting to Airpay... Please do not refresh or press back</p>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/response', methods=['POST'])
def airpay_response():
    try:
        response_data = request.form.get('response')
        if not response_data:
            return "Response is empty.", 400

        decrypted_data = Functions.decrypt_string(response_data, USERNAME, PASSWORD)
        data_dict = json.loads(decrypted_data)
        data = data_dict.get('data', {})

        TRANSACTIONID = data.get('orderid', '').strip()
        APTRANSACTIONID = data.get('ap_transactionid', '').strip()
        AMOUNT = data.get('amount', '').strip()
        TRANSACTIONSTATUS = data.get('transaction_status', '').strip()
        MESSAGE = data.get('message', '').strip()
        CUSTOMVAR = data.get('custom_var', '').strip() if 'custom_var' in data else ""
        CHMOD = data.get('chmod', '').strip() if 'chmod' in data else ""
        CUSTOMERVPA = ":" + data["CUSTOMERVPA"].strip() if CHMOD.lower() == "upi" and "CUSTOMERVPA" in data else ""
        ap_SecureHash = str(data.get('ap_securehash', '')).strip()

        # Merchant secure hash
        hash_string = f"{TRANSACTIONID}:{APTRANSACTIONID}:{AMOUNT}:{TRANSACTIONSTATUS}:{MESSAGE}:{MERCID}:{USERNAME}{CUSTOMERVPA}"
        merchant_secure_hash = zlib.crc32(hash_string.encode()) & 0xffffffff

        html_content = f"""
        <h2 class='{'tdsuccess' if TRANSACTIONSTATUS=='200' else 'tdfail'}'>
            {'SUCCESS TRANSACTION' if TRANSACTIONSTATUS=='200' else 'FAILED TRANSACTION'}
        </h2>
        <table>
        <tr><th>Variable Name</th><th>Value</th></tr>
        <tr><td>TRANSACTIONID</td><td>{TRANSACTIONID}</td></tr>
        <tr><td>APTRANSACTIONID</td><td>{APTRANSACTIONID}</td></tr>
        <tr><td>AMOUNT</td><td>{AMOUNT}</td></tr>
        <tr><td>TRANSACTIONSTATUS</td><td>{TRANSACTIONSTATUS}</td></tr>
        <tr><td>MESSAGE</td><td>{MESSAGE}</td></tr>
        <tr><td>CUSTOMVAR</td><td>{CUSTOMVAR}</td></tr>
        <tr><td>CHMOD</td><td>{CHMOD}</td></tr>
        <tr><td>CUSTOMERVPA</td><td>{CUSTOMERVPA}</td></tr>
        <tr><td>AP_SECUREHASH</td><td>{ap_SecureHash}</td></tr>
        <tr><td>Merchant Secure Hash</td><td>{merchant_secure_hash}</td></tr>
        </table>
        """
        return render_template_string(html_content)

    except Exception as e:
        return f"<p style='color:red;'>Error: {str(e)}</p>", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
