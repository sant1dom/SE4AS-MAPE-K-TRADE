import requests
from flask import Flask, jsonify #AGGIUNGERE A DOCKER

app = Flask(__name__)

@app.route("/ml_result")
def get_ml_result():
    c=0
    response = requests.get("http://ml:5050/ml_result")
    prediction = response.json()["ml_result"]

    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    data = response.json()
    last_price = float(data["price"])

    if last_price < prediction:
        c=1 #buy 
    else:
        c=0 #sell
    return jsonify({"buy_sell": c})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="5000")
