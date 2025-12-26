#!/usr/bin/env python3.9
import cgi
import hashlib
import json
import os
import base64
import requests
import datetime
import subprocess
import binascii
import urllib.parse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad 
from Crypto import Random



class Functions:
    @staticmethod
    def encrypt_string(my_string, username,password):
        secret_key = hashlib.md5((username + "~:~" + password).encode()).hexdigest()

    # Generate a random IV of 8 bytes
        iv = 'c0f9e2d16031b0ce'  


    # Pad the request data and encrypt using AES-CBC with the generated key and IV
        cipher = AES.new(secret_key.encode(), AES.MODE_CBC, iv.encode())
        encrypted_data = cipher.encrypt(pad(my_string.encode(), AES.block_size))

    # Combine IV and encrypted data, then base64 encode
        data = iv + base64.b64encode(encrypted_data).decode()
    
        return data

    @staticmethod
    def encrypt_sha(data, salt):
        key = hashlib.sha256((salt + '@' + data).encode()).hexdigest()
        return key

    @staticmethod
    def decrypt_string(encrypted_data, username, password):
        secret_key = hashlib.md5((username + "~:~" + password).encode()).hexdigest()
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]

        # Decrypt the data using AES-CBC with the given IV and secret key
        cipher = AES.new(secret_key.encode(), AES.MODE_CBC, iv.encode())
        decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data))

        # Remove padding from the decrypted data
        unpadded_data = unpad(decrypted_data, AES.block_size)

        return unpadded_data.decode() 

    @staticmethod
    def checksum_cal(post_data):
        sorted_data = sorted(post_data.items(), key=lambda x: x[0])
        data = ''.join([str(value) for _, value in sorted_data])
        return Functions.calculate_checksum_helper(data + datetime.datetime.now().strftime("%Y-%m-%d"))
        

    @staticmethod
    def calculate_checksum_helper(data):
        return Functions.make_enc(data)

    @staticmethod
    def make_enc(data):
        key = hashlib.sha256(data.encode()).hexdigest()
        return key



    @staticmethod
    def send_post_data(token_url, post_data):
        try:
           response = requests.post(token_url, data=post_data)
           return response.text
        except Exception as e:
            print('Error:', e)

mercid = '247167'
username = '3072982'
password = '0764760075Ana'
secret ='JDWZ2ncNxhhTcXj7'
client_id = '2fdf34'
client_secret = '25f509db787e868538a44e1f507ef248'
token_url='https://kraken.airpay.tz/airpay/pay/v1/api/oauth2'
url='https://payments.airpay.tz/pay/v1/index.php '


# Set the content type
print("Content-type: text/html\n")

# Extract form data
form = cgi.FieldStorage()
buyer_email = form.getvalue('buyerEmail')
buyer_firstname = form.getvalue('buyerFirstName')
buyer_lastname = form.getvalue('buyerLastName')
buyer_address = form.getvalue('buyerAddress')
buyer_city = form.getvalue('buyerCity')
buyer_state = form.getvalue('buyerState')
buyer_country = form.getvalue('buyerCountry')
amount = form.getvalue('amount')
orderid = form.getvalue('orderid')
buyer_phone = form.getvalue('buyerPhone')
buyer_pincode = form.getvalue('buyerPinCode')
iso_currency = form.getvalue('isocurrency')
currency_code = form.getvalue('currency')
merchant_id =mercid

mer_dom = base64.b64encode(b'http://track.airpay.co.in').decode('utf-8')

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
    'merchant_id': merchant_id,
    'mer_dom': mer_dom
}

# Oauth2

access_token = ""
request = {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'client_credentials',
    'merchant_id': mercid
}
request_string=json.dumps(request)
secret_key = hashlib.md5((username + "~:~" + password).encode()).hexdigest()

#encrypting request
encre=Functions.encrypt_string(request_string,username, password)

req = {
    'merchant_id': request['merchant_id'],
    'encdata': encre,
    'checksum': Functions.checksum_cal(request)
}

access_token_json= Functions.send_post_data(token_url, req)

#into python dictionary
access_token_data = json.loads(access_token_json)
decrypt_data = Functions.decrypt_string(access_token_data['response'], username, password)
tokenResponse = json.loads(decrypt_data)

# Check if the response contains an error message
if 'success' in tokenResponse and not tokenResponse['success']:
    print(tokenResponse['msg'])
else:
    # Extract the access token from the decrypted data
    access_token = tokenResponse.get('access_token', None)
    if access_token:
        print("Access Token:", access_token)
    else:
        print("")

accessToken = tokenResponse['data']['access_token']
url += '?token=' + accessToken
alldata = (buyer_email or '') + (buyer_firstname or '') + (buyer_lastname or '') + (buyer_address or '') + (buyer_city or '') + (buyer_state or '' ) + (buyer_country or '' ) + (amount or '') + (orderid or '')
private_key = Functions.encrypt_sha(username + ":|:" + password, secret)
hiddenmod=""
data_json = json.dumps(post_data)
# Now data_json contains the JSON representation of the dictionary
request_data = Functions.encrypt_string(data_json, username, password)
checksum_req =Functions.checksum_cal(post_data)

# HTML response
print("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">")
print("<html xmlns=\"http://www.w3.org/1999/xhtml\">")
print("<head>")
print("<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />")
print("<title>Airpay</title>")
print("<script type=\"text/javascript\">")
print("function submitForm() {")
print("var form = document.forms[0];")
print("form.submit();")
print("}")
print("</script>")
print("</head>")
print("<body onload=\"javascript:submitForm()\">")
print("<center>")
print("<table width=\"500px;\">")
print("<tr>")
print("<td align=\"center\" valign=\"middle\">Do Not Refresh or Press Back <br/> Redirecting to Airpay</td>")
print("</tr>")
print("<tr>")
print("<td align=\"center\" valign=\"middle\">")
print("<form id=\"paymentForm\" action=\"{url}\" method=\"post\">".format(url=url))
print('<input type="hidden" name="privatekey" value="{}">'.format(private_key))
print('<input type="hidden" name="merchant_id" value="{}">'.format(mercid))
print('<input type="hidden" name="encdata" value="{}">'.format(request_data))
print('<input type="hidden" name="checksum" value="{}">'.format(checksum_req))
print('<input type="hidden" name="chmod" value="{}">'.format(hiddenmod))
print("</form>")
print("</td>") 
print("</tr>")
print("</table>")
print("</center>")
print("</html>")

 


