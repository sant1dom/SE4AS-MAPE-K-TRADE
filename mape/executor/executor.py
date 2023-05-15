import requests
import datetime
import time
import os
import influxdb_client


INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")


def portfolio_bucket_creation(url,token,org):
    # Set up the connection to your InfluxDB instance
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

    # Get the buckets API instance
    buckets_api = client.buckets_api()


    name = "portfolio"

    # Create a new bucket named 'portfolio'
    if not buckets_api.find_bucket_by_name("portfolio"):
        bucket = buckets_api.create_bucket(bucket_name=name)
        

    # Create the schema for the bucket
    schema = """
        measurement:string,
        quantity:integer
    """

    # Set up the InfluxDB client to use the new bucket and retention policy
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, bucket=name)

    # Create a new point with measurement 'example' and fields 'value1' and 'value2'
    point = {
        "measurement": "investment",
        "fields": {
            "quantity": float(100)
        },
    }

    # Write the point to the bucket
    write_api = client.write_api()
    write_api.write(bucket=name, record=point)

portfolio_bucket_creation(INFLUXDB_URL,INFLUXDB_TOKEN,INFLUXDB_ORG)


class portfolio:
    def __init__(self,investment,url,token,org):
        self.investment = investment
        self.url = url
        self.org = org
        self.token = token
        self.coins_owned = {}
        self.last_prices = self.retrieve_last_prices()
        #self.predictions = self.request_predictions()
        
        
    def sell_all(self,coin):
        if coin in self.coins_owned:
            self.investment += self.coins_owned[coin]*self.last_prices[coin]
            self.coins_owned[coin] = 0
        
        
    def buy_10(self,coin,buy_quantity):
        # 10% of amount of available dollars converted to coin, after that the coin in the portfolio gets that value added 
        # if it exists otherwise it gets created with that value
        coin_value_conversion = buy_quantity/self.last_prices[coin]
        if coin in self.coins_owned:
            self.coins_owned[coin]+=coin_value_conversion
        else:
            self.coins_owned[coin]=coin_value_conversion
        self.investment-=buy_quantity
    
    def retrieve_last_prices(self):
        url = 'https://api.binance.com/api/v3/klines'

        symbols = ['ADAUSDT', 'BNBUSDT']#, 'BTCUSDT', 'DOGEUSDT', 'DOTUSDT', 'ETHUSDT', 'LINKUSDT', 'LTCUSDT', 'UNIUSDT', 'XRPUSDT']  
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
        return last_prices
    
    def request_predictions(self):
        initialization=0
        coins = ['ADA', 'BNB']#, 'BTC', 'DOGE', 'DOT', 'ETH', 'LINK', 'LTC', 'UNI', 'XRP']
        coin_signals={}
        for coin in coins:
            url = f"http://planner:5020/planner_result?coin={coin}"
            response = requests.get(url)
            data = response.json()
            coin_signals[coin+"USDT"] = data["buy_sell"]
            print('Prediction_Retrieval :'+str(len(coin_signals)*100/len(coins))+"%")
        return coin_signals
    
    def bucket_update(self,coin_or_investment,quantity,bucket_name='portfolio'):
        client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org,bucket=bucket_name)

        # Define the data point to write to the bucket
        point = {
            "measurement": coin_or_investment,
            "fields": {
                "quantity": quantity
            }
        }
        
        write_api = client.write_api()
        write_api.write(bucket=bucket_name, record=point)
    
    
    def portfolio_update(self):
        self.last_prices = self.retrieve_last_prices()
        buy_quantity = self.investment/11
        predictions = self.request_predictions()                
        for coin,buy_value in predictions.items():
            if buy_value:
                self.buy_10(coin,buy_quantity)
            else:
                self.sell_all(coin)
            
        for coin,value in self.coins_owned.items():
            self.bucket_update(bucket_name='portfolio',coin_or_investment=coin,quantity=float(value))
        self.bucket_update( bucket_name='portfolio',coin_or_investment='investment',quantity=float(self.investment))


time.sleep(90)
a=portfolio(100,INFLUXDB_URL,INFLUXDB_TOKEN,INFLUXDB_ORG)
while True:    
    a.portfolio_update()
    print('portfolio_updated')
    time.sleep(30)
    
    
    
