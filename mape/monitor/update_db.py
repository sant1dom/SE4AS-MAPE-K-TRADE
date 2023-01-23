import requests
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import json
import os
def check_db():
        try:
            with open("data.json", "r") as f:
                data = json.load(f)
                if data[-1]["time"] - int(data[-1]["time"] % 3600) == int(time.time()) - (int(time.time()) % 3600):
                    return False
                else:
                    return True
        except:
            return True

def write_to_file():
    # Set the symbol and interval for the API call
    symbol = {
        "BTCUSDT": 1502942400000,
        #"ETHUSDT": 1502942400000,
        #"BNBUSDT": 1509937200000,
        #"ADAUSDT": 1523937600000,
        #"XRPUSDT": 1525420800000,
        #"DOGEUSDT": 1562328000000,
        #"DOTUSDT": 1597791600000,
        #"UNIUSDT": 1600311600000,
        #"LTCUSDT": 1513134000000,
        #"LINKUSDT": 1547632800000
    }
    interval = "1h"

    # Set the end timestamps for the data range
    end_timestamp = time.time() * 1000

    # Set the limit for the number of results per API call
    limit = 1000

    # Make API calls until all the data has been retrieved
    print("Starting to fetch data from Binance")
    for key in symbol:
        data_points = []
        start_time = symbol[key]
        end_time = start_time + limit * 3600000
        while start_time < end_timestamp:
            print("Fetching data from {} to {}".format(datetime.fromtimestamp(start_time / 1000),
                                                       datetime.fromtimestamp(end_time / 1000)))
            print("For symbol: {}".format(key))
            # Construct the API URL with the appropriate start and end timestamps
            url = f"https://api.binance.com/api/v3/klines?symbol={key}&interval={interval}&limit={limit}&startTime={start_time}&endTime={end_time}"
            # Make the API call
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(f'HTTP error occurred: {err}')
            except requests.exceptions.RequestException as err:
                print(f'Other error occurred: {err}')
            else:
                # Process the data from the API call and add it to the data points list
                for datapoint in response.json():
                    timestamp = int(datapoint[0]) // 1000
                    open_price = float(datapoint[1])
                    high_price = float(datapoint[2])
                    low_price = float(datapoint[3])
                    close_price = float(datapoint[4])
                    volume = float(datapoint[5])
                    kline_close_time = int(datapoint[6])
                    quote_asset_volume = float(datapoint[7])
                    number_of_trades = int(datapoint[8])
                    taker_buy_base_asset_volume = float(datapoint[9])
                    taker_buy_quote_asset_volume = float(datapoint[10])

                    data_point = {
                        "measurement": "binance_candles",
                        "tags": {
                            "symbol": key,
                            "interval": interval
                        },
                        "time": timestamp,
                        "fields": {
                            "open": open_price,
                            "high": high_price,
                            "low": low_price,
                            "close": close_price,
                            "volume": volume,
                            "kline_close_time": kline_close_time,
                            "quote_asset_volume": quote_asset_volume,
                            "number_of_trades": number_of_trades,
                            "taker_buy_base_asset_volume": taker_buy_base_asset_volume,
                            "taker_buy_quote_asset_volume": taker_buy_quote_asset_volume
                        }
                    }
                    data_points.append(data_point)

            # Update the start and end timestamps for the next API call
            start_time = end_time
            end_time = start_time + limit * 3600000
            with open("data.json", "a") as f:
                json.dump(data_points, f, indent=4)
    update_db()
def update_db():
    # Initialize the parameters for InfuxDB
    token = os.getenv("INFLUXDB_TOKEN")
    org = os.getenv("INFLUXDB_ORG")
    bucket = os.getenv("INFLUXDB_BUCKET")
    url = os.getenv("INFLUXDB_URL")
    print("Connecting to InfluxDB")
    with InfluxDBClient(url=url, token=token, org=org) as client:
        print("Writing data to InfluxDB")
        write_api = client.write_api(write_options=SYNCHRONOUS)
        with open("data.json", "r") as f:
            data = json.load(f)
            write_api.write(bucket=bucket, record=data, org=org, precision=WritePrecision.S)

if __name__ == '__main__':
    if check_db():
        write_to_file()

