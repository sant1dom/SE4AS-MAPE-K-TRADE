import requests
import datetime
import time

class portfolio:
    def __init__(self,investment):
        self.investment = investment
        self.coins_owned = {}
        self.retrieve_last_prices()
        #self.predictions = self.request_predictions()
        
        
    def sell_all(self,coin):
        if coin in self.coins_owned:
            self.investment += self.coins_owned[coin]*self.last_prices[coin]
            self.coins_owned[coin] = 0
        
        
    def buy_10(self,coin,buy_quantity):
        # 10% of amount of availabel dollars converted to coin, after that the coin in the portfolio gets that value added 
        # if it exists otherwise it gets created with that value
        coin_value_conversion = buy_quantity/self.last_prices[coin]
        if coin in self.coins_owned:
            self.coins_owned[coin]+=coin_value_conversion
        else:
            self.coins_owned[coin]=coin_value_conversion
        self.investment-=buy_quantity
        
    def portfolio_update(self):
        self.retrieve_last_prices()
        buy_quantity = self.investment/10
        predictions = self.request_predictions()                
        for coin,buy_value in predictions.items():
            if buy_value:
                self.buy_10(coin,buy_quantity)
            else:
                self.sell_all(coin)

            
    
    def retrieve_last_prices(self):
        url = 'https://api.binance.com/api/v3/klines'

        symbols = ['ADAUSDT', 'BNBUSDT', 'BTCUSDT', 'DOGEUSDT', 'DOTUSDT', 'ETHUSDT', 'LINKUSDT', 'LTCUSDT', 'UNIUSDT', 'XRPUSDT']  
        interval = '1d'
        limit = 1

        last_prices={}

        for symbol in symbols:
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    close_price = item[4]
                    last_prices[symbol]=close_price
            else:
                print(f"Error retrieving data for symbol {symbol}. Status code: {response.status_code}")
            
            for keys in last_prices:
                last_prices[keys] = float(last_prices[keys])
        self.last_prices = last_prices
    
    def request_predictions(self):
        initialization=0
        coins = ['ADA', 'BNB', 'BTC', 'DOGE', 'DOT', 'ETH', 'LINK', 'LTC', 'UNI', 'XRP']
        coin_signals={}
        for coin in coins:
            url = f"http://planner:5020/planner_result?coin={coin}"
            response = requests.get(url)
            data = response.json()
            coin_signals[coin+"USDT"] = data["buy_sell"]
            print('Prediction_Retrieval :'+str(len(coin_signals)*100/len(coins))+"%")
        return coin_signals
    

a = portfolio(100)
while True:
    time.sleep(1)
    a.portfolio_update()
    
