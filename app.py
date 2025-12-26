from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Airpay Gateway Live!"

@app.route("/transaction.html")
def transaction():
    return render_template("transaction.html")

@app.route("/responsefromairpay", methods=["POST"])
def responsefromairpay():
    # process POST data from Airpay
    response_data = request.form.get("response")
    return f"Received: {response_data}"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
