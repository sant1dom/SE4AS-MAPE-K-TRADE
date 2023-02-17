import requests
from flask import Flask, jsonify #AGGIUNGERE A DOCKER
from ml import *

app = Flask(__name__)

@app.route("/planner_result")
def get_ml(coin):
    c=0
    print('coin')
    prediction = get_ml_result(coin=coin)

    url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}USDT"
    response = requests.get(url)
    data = response.json()
    last_price = float(data["price"])

    if last_price < prediction:
        c=1 #buy 
    else:
        c=0 #sell
    return jsonify({"prediction": prediction,"buy_sell": c})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="5020")

