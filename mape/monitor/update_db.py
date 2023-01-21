import requests
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import json

# Set the symbol and interval for the API call
symbol = "BTCUSDT"
interval = "1h"

# Set the start and end timestamps for the data range
start_timestamp = 1502942400000
end_timestamp = time.time() * 1000

# Set the limit for the number of results per API call
limit = 1000

# Initialize a list to store the data points
data_points = []

# Set the initial start and end timestamps for the first API call
start_time = start_timestamp
end_time = start_time + limit * 3600000

# Make API calls until all the data has been retrieved
while start_time < end_timestamp:
    print("Fetching data from {} to {}".format(datetime.fromtimestamp(start_time / 1000), datetime.fromtimestamp(end_time / 1000)))
    # Construct the API URL with the appropriate start and end timestamps
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}&startTime={start_time}&endTime={end_time}"

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
                    "symbol": symbol,
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

# Connect to the InfluxDB database
token = "OhY1nFVtsxl0dkNRX2E6XVDFlE8BI_UMtJiGkah1FCneMQCaWWW7Zyk3LSs5aHayBXU1RJHwoU156pBhuQvOhA=="
org = "se4as"

print("Connecting to InfluxDB")
with InfluxDBClient(url="http://influx:8086", token=token, org=org) as client:
    print("Writing data to InfluxDB")
    print(json.dumps(data_points, indent=4))
    write_api = client.write_api(write_options=SYNCHRONOUS)
    for data_point in data_points:
        write_api.write(bucket="crypto", org=org, record=data_point, write_precision=WritePrecision.S)
print("Done")

