from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision, QueryApi
from influxdb_client.client.write_api import ASYNCHRONOUS
import os
import time
from datetime import datetime

# Use environment variables to store InfluxDB credentials
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
INFLUXDB_URL = os.getenv("INFLUXDB_URL")

# Constants
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

# Columns to fetch from the Binance API
COLUMNS = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "kline_close_time",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base_asset_volume",
    "taker_buy_quote_asset_volume",
    "undefined",
]


def fetch_data(
    symbol: str, interval: str, start_time: int, end_time: int, limit: int = 1000
) -> pd.DataFrame or None:
    """
    Fetch data from the Binance API for a given symbol, interval, and time range.
    :param symbol: String representing the symbol to fetch data for.
    :param interval: String representing the interval of the data.
    :param start_time: Integer representing the start timestamp in milliseconds.
    :param end_time: Integer representing the end timestamp in milliseconds.
    :param limit: Integer representing the number of results to fetch per API call.
    :return: Dataframe containing the fetched data.
    """
    try:
        print(
            f"Fetching data from {datetime.fromtimestamp(start_time / 1000)} to {datetime.fromtimestamp(end_time / 1000)}"
        )
        print(f"For symbol: {symbol}")
        response = requests.get(
            BINANCE_API_URL,
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit,
                "startTime": start_time,
                "endTime": end_time,
            },
        )
        data = response.json()
        df = pd.DataFrame(data, columns=COLUMNS)
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None


def write_to_db(df: pd.DataFrame, symbol: str, interval: str):
    """
    Write data to InfluxDB.
    :param df: Dataframe containing the data to write.
    :param symbol: String representing the symbol of the data.
    :param interval: String representing the interval of the data.
    """
    if df is not None:
        try:
            print("Connecting to InfluxDB")
            points = []
            with InfluxDBClient(
                url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
            ) as client:
                write_api = client.write_api(write_options=ASYNCHRONOUS)
                # Convert dataframe to list of points
                for i, row in df.iterrows():
                    p = (
                        Point(symbol)
                        .tag("symbol", symbol)
                        .tag("interval", interval)
                        .field("open", float(row["open"]))
                        .field("high", float(row["high"]))
                        .field("low", float(row["low"]))
                        .field("close", float(row["close"]))
                        .field("volume", float(row["volume"]))
                        .field("kline_close_time", int(row["kline_close_time"]))
                        .field("quote_asset_volume", float(row["quote_asset_volume"]))
                        .field("number_of_trades", int(row["number_of_trades"]))
                        .field(
                            "taker_buy_base_asset_volume",
                            float(row["taker_buy_base_asset_volume"]),
                        )
                        .field(
                            "taker_buy_quote_asset_volume",
                            float(row["taker_buy_quote_asset_volume"]),
                        )
                        .time(int(row["timestamp"].timestamp()), WritePrecision.S)
                    )
                    points.append(p)
                # Write point to InfluxDB
                write_api.write(bucket=INFLUXDB_BUCKET, record=points)
                print("Data written to InfluxDB successfully for symbol: " + symbol)
        except Exception as e:
            print(f"An error occurred while writing data to InfluxDB: {e}")


if __name__ == "__main__":
    # Symbols to fetch data for
    symbol = {
        "BTCUSDT": 1502942400000,
        "ETHUSDT": 1502942400000,
        "BNBUSDT": 1509937200000,
        "ADAUSDT": 1523937600000,
        "XRPUSDT": 1525420800000,
        "DOGEUSDT": 1562328000000,
        "DOTUSDT": 1597791600000,
        "UNIUSDT": 1600311600000,
        "LTCUSDT": 1513134000000,
        "LINKUSDT": 1547632800000,
    }
    # Parameters for the Binance API
    interval = "1h"
    end_timestamp = int(time.time() * 1000)
    limit = 1000
    # Set up the client
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG, enable_gzip=True)

    # Query to check the last updated timestamp
    query_api = QueryApi(client)
    last_update_time = query_api.query(
        'from(bucket:"crypto") |> range(start: 0, stop: now()) |> max()'
    )
    update = False
    if len(last_update_time) > 0:
        last_update_time = last_update_time[2].records[0].get_value() + 1
        update = True
    else:
        last_update_time = 0
    client.close()

    # Check if the last updated timestamp is older than 1 hour
    current_time = int(time.time())
    current_hour = int(current_time - (current_time % 3600)) * 1000
    if current_hour > last_update_time:
        with ThreadPoolExecutor() as executor:
            futures = []
            # Fetch data for each symbol
            for key in symbol:
                # The flag is set to true if the last updated timestamp is older than 1 hour
                if update:
                    start_time = last_update_time
                else:
                    start_time = symbol[key]
                # End time is set to the next 1000-hour interval
                end_time = start_time + limit * 3600000
                while start_time < end_timestamp:
                    print(
                        "Start time: ",
                        datetime.fromtimestamp(start_time / 1000),
                        "End time: ",
                        datetime.fromtimestamp(end_time / 1000),
                        "For symbol: ",
                        key
                    )
                    # Add the future to the list
                    future = executor.submit(
                        fetch_data, key, interval, start_time, end_time, limit
                    )
                    future.add_done_callback(
                        lambda f, symbol=key: write_to_db(f.result(), symbol, interval)
                    )
                    start_time = end_time
                    end_time += limit * 3600000
    else:
        print("No new data to write to InfluxDB!")
        # Sleep until the next hour
        time.sleep(current_time - (current_time % 3600) + 3600 - current_time)